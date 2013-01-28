import errno
import fnmatch
import logging
import multiprocessing
import os.path
import sys
import subprocess

log = logging.getLogger("komodo.ci.indexer")
#log.setLevel(logging.DEBUG)

try:
    sys.path.insert(0, os.path.dirname(__file__))
    from utils import fix_module_path
finally:
    sys.path.remove(os.path.dirname(__file__))

def pre_process(tree, environ):
    """
    DXR plugin hook: run before building the tree
    """
    pass # nothing to be done here

def post_process(tree, conn):
    """
    DXR plugin hook: run after building the tree
    """
    cix_dir = os.path.join(tree.temp_folder, "plugins", "komodo_codeintel")
    try:
        os.makedirs(cix_dir)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise
    cmd = [sys.executable, __file__, "--source-folder", tree.source_folder,
           "--output", cix_dir, "--threads", tree.config.nb_jobs,
           "--log-level", str(log.getEffectiveLevel())]
    for pattern in tree.ignore_patterns:
        cmd.extend(["--ignore-patterns", pattern])
    for path in tree.ignore_paths:
        cmd.extend(["--ignore-paths", path])
    subprocess.check_call(cmd)

def parse_args(argv=None):
    """
    Parse command line arguments
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", action="store")
    parser.add_argument("--source-folder", "-s", action="store")
    parser.add_argument("--ignore-patterns", action="append", default=[])
    parser.add_argument("--ignore-paths", action="append", default=[])
    parser.add_argument("--threads", "-j", nargs="?", action="append",
                        default=[], type=int)
    parser.add_argument("--log-level", action="store", default=logging.INFO, type=int)
    args = parser.parse_args(argv if argv is not None else sys.argv)
    if args.threads == [None]:
        # -j with no arguments
        args.threads = multiprocessing.cpu_count()
    else:
        args.threads = max([sum(map(lambda n: 1 if n is None else n, args.threads)), 1])
    log.setLevel(args.log_level)
    return args

def walk_tree(args, queue):
    """
    Walk the source tree and look for files to process
    """
    for root, folders, files in os.walk(args.source_folder, True):
        # Find relative path
        rel_path = os.path.relpath(root, args.source_folder)
        if rel_path == '.':
            rel_path = ""

        for f in files:
            # Ignore file if it matches an ignore pattern
            if any((fnmatch.fnmatchcase(f, e) for e in args.ignore_patterns)):
                continue # Ignore the file

            # file_path and path
            file_path = os.path.join(root, f)
            path = os.path.join(rel_path, f)

            # Ignore file if its path (relative to the root) matches an ignore path
            if any((fnmatch.fnmatchcase("/" + path.replace(os.sep, "/"), e)
                    for e in args.ignore_paths)):
                continue # Ignore the file

            queue.put(file_path)

        # Exclude folders that match an ignore pattern
        # (The top-down walk allows us to do this)
        for folder in folders[:]:
            if any((fnmatch.fnmatchcase(folder, e) for e in args.ignore_patterns)):
                folders.remove(folder)
            else:
                folder_relpath = "/" + os.path.join(rel_path, folder).replace(os.sep, "/") + "/"
                if any((fnmatch.fnmatchcase(folder_relpath, e) for e in args.ignore_paths)):
                    folders.remove(folder)
    queue.put(None) # sentinel to indicate completion

def worker(queue, lock, cix_dir, root="/"):
    """
    worker procedure
    """
    fix_module_path()
    import dxr.mime
    from codeintel2.citadel import CitadelBuffer
    from codeintel2.common import CodeIntelError
    from codeintel2.manager import Manager
    from codeintel2.util import guess_lang_from_path

    logging.getLogger("codeintel").setLevel(logging.ERROR)
    log.info("starting indexing using %s", multiprocessing.current_process().name)

    mgr = Manager(db_base_dir=cix_dir)
    #mgr.upgrade()
    mgr.initialize()

    while True:
        file_path = queue.get()
        if file_path is None:
            # marker for end of list
            queue.put(None) # put it back so others can quit too
            break

        rel_path = os.path.relpath(file_path, root)

        try:
            lang = guess_lang_from_path(file_path)
        except CodeIntelError:
            log.info("%s: Cannot determine language, skipping", rel_path)
            continue

        # the file
        with open(file_path, "r") as source_file:
            data = source_file.read()

        # Discard non-text files
        if not dxr.mime.is_text(file_path, data):
            continue

        try:
            buf = mgr.buf_from_path(file_path, lang=lang)
        except CodeIntelError as ex:
            if ex.message.startswith("File too big."):
                log.info("%s: %s", file_path, ex.message)
                continue # Nothing we can do about that, and the user can't
                         # fix this ever.
            raise
        if not isinstance(buf, CitadelBuffer):
            log.info("%s: language %s does not have CIX, skipping",
                     rel_path, lang)
            continue

        log.info("%s: Using language %s", rel_path, lang)

        buf.scan()

    mgr.finalize()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout)
    queue = multiprocessing.Queue()
    lock = multiprocessing.Lock()

    args = parse_args(sys.argv[1:])

    processes = set()
    for i in range(1, args.threads):
        process = multiprocessing.Process(target=worker,
                                          name="codeintel scanner %s" % (i,),
                                          args=(queue, lock, args.output),
                                          kwargs={"root": args.source_folder})
        processes.add(process)
        process.start()

    walk_tree(args, queue)

    for process in processes:
        process.join()
        assert process.exitcode == 0
    processes.clear()

    if args.threads < 2:
        # We never spawned a worker process; scan in-process instead
        worker(queue, lock, args.output)
else:
    # we're running under dxr, or we're a worker process...
    try:
        import dxr.plugins
        __all__ = dxr.plugins.indexer_exports()
    except ImportError:
        pass # Nope, we're a worker process
