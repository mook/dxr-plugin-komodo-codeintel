import dxr.plugins
import logging
import os.path
import sys

from argparse import Namespace
from urllib import urlencode

try:
    sys.path.insert(0, os.path.dirname(__file__))
    from utils import fix_module_path
finally:
    sys.path.remove(os.path.dirname(__file__))

opts = Namespace()
log = logging.getLogger("komodo.ci.htmlifier")
#log.setLevel(logging.DEBUG)

# Try to set up logging if it isn't already
logging.basicConfig(stream=sys.stdout)

def load(tree, conn):
    fix_module_path()
    opts.db_path = os.path.join(tree.temp_folder, "plugins", "komodo_codeintel")
    opts.root = tree.source_folder
    opts.wwwroot = tree.config.wwwroot
    opts.name = tree.name
    log.info("reading from db %s", opts.db_path)

    from codeintel2.manager import Manager
    opts.mgr = Manager(db_base_dir=opts.db_path)
    opts.mgr.initialize()

class CiHtmlifier(object):
    def __init__(self, buf):
        self.buf = buf

    @staticmethod
    def urlify(relpath, anchor=None):
        url = "/".join([opts.wwwroot, opts.name, relpath])
        if anchor is not None:
            url += "#" + str(anchor)
        return url

    def refs(self):
        from codeintel2.common import CodeIntelError, NotATriggerError, EvalError, EvalTimeout, EvalController

        for token in self.buf.accessor.gen_tokens():
            styles = self.buf.style_names_from_style_num(token["style"])
            for style_name in ("identifiers",):
                if style_name in styles:
                    break
            else:
                # no whitelisted style name found
                continue # next token
            log.debug("%r: %r", token, styles)
            menu = []
            try:
                trg = self.buf.defn_trg_from_pos(token["start_index"])
                log.debug("trg form: %s", trg.form if trg else "<none>")
                # seems like we keep getting old definitions if we reuse the
                # eval controller :|
                defns = self.buf.defns_from_trg(trg, ctlr=EvalController()) or []
                for defn in defns:
                    log.debug("got defn %r for %s at %s~%s", defn,
                              token["text"], token["start_index"], token["end_index"])
                    path = getattr(defn, "path", None)
                    if not path:
                        continue # not a file!?
                    relpath = os.path.relpath(path, opts.root)
                    log.debug("path: %s -> %s", path, relpath)
                    if relpath.startswith(".." + os.sep):
                        # outside of the source tree
                        continue
                    log.debug("props: %r", dir(defn))
                    line = getattr(defn, "line", None)
                    name = getattr(defn, "name", None)
                    menu.append({
                        "text": "Go to definition of %s" % (name,),
                        "title": "%s is defined in %s" % (name, relpath),
                        "href": self.urlify(relpath, ("l%s" % (line,)) if line else None),
                        "icon": "field",
                        })
            except CodeIntelError as ex:
                log.debug("%s", ex)
            except NotATriggerError as ex:
                log.debug("not a trigger: %s", ex)
            except EvalTimeout:
                log.debug("eval time out")
            except (EvalError, NotImplementedError) as ex:
                log.debug("other error: %s", ex)

            yield (token["start_index"], token["end_index"] + 1, menu)

    def regions(self):
        if False:
            yield None
    def annotations(self):
        if False:
            yield None
    def links(self):
        if False:
            yield None

def htmlify(rel_path, text):
    from codeintel2.citadel import CitadelBuffer
    from codeintel2.common import CodeIntelError
    from codeintel2.util import guess_lang_from_path
    path = os.path.join(opts.root, rel_path)
    try:
        lang = guess_lang_from_path(path)
    except CodeIntelError:
        return None
    buf = opts.mgr.buf_from_path(path, lang=lang)
    if not isinstance(buf, CitadelBuffer):
        log.info("%s: language %s does not have CIX, not htmlifying",
                 rel_path, lang)
        return None
    if lang == "Tcl":
        # Tcl is busted, it has no async_eval_at_trg; Komodo just plain has a
        # different system for handling tcl...
        return None
    log.info("htmlifying %s as %s", rel_path, lang)
    return CiHtmlifier(buf)

__all__ = dxr.plugins.htmlifier_exports()
