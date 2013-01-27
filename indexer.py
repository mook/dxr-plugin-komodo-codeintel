import dxr.mime
import dxr.plugins
import fnmatch
import os.path
import pprint
import sys
import subprocess

def pre_process(tree, environ):
    pass # nothing to be done here

def post_process(tree, conn):
    cix_dir = os.path.join(tree.temp_folder, "komodo_codeintel", tree.name)
    os.makedirs(cix_dir)
    cmd = [sys.argv, __file__, "--source-folder", tree.source_folder,
           "--output", cix_dir, "--threads", tree.config.nb_jobs]
    for pattern in tree.ignore_patterns:
        cmd.extend(["--ignore-pattern", pattern])
    for path in tree.ignore_paths:
        cmd.extend(["--ignore-path", path])
    subprocess.call(cmd)

__all__ = dxr.plugins.indexer_exports()

def fix_module_path():
    """
    Fix module include paths to make codeintel work
    """
    for relpath in (
            ("obj", "pylib"),
            ("komodo-bits", "schemes"),
            ("komodo-bits", "python-sitelib"),
            ("codeintel", "src", "lib"),
            ):
        sys.path.append(os.path.join(os.path.dirname(__file__), *relpath))
    
    # ciElementTree's bootstrap is completely broken; it looked for 'ElementTree'
    # and 'elementtree.ElementTree', but not 'xml.etree.ElementTree'.  Fake it out
    # here so that it runs the bootstrap code, marking it as patched for komodo
    import xml.etree.ElementTree
    sys.modules['ElementTree'] = sys.modules['xml.etree.ElementTree']
    import codeintel2.manager

def parse_args(argv=None):
    """
    Parse command line arguments
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", action="store")
    parser.add_argument("--source-folder", "-s", action="store")
    parser.add_argument("--ignore-pattern", action="append")
    parser.add_argument("--ignore-path", action="append")
    parser.add_argument("--threads", "-j", nargs="?", action="append",
                        default=[], type=int)
    args = parser.parse_args(argv if argv is not None else sys.argv)
    args.threads = min([sum(map(lambda n: 1 if n is None else n, args.threads)), 1])
    return args

def walk_tree(args):
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

            # the file
            with open(file_path, "r") as source_file:
                data = source_file.read()

            # Discard non-text files
            if not dxr.mime.is_text(file_path, data):
                continue

            scan_file(file_path, args.output)

        # Exclude folders that match an ignore pattern
        # (The top-down walk allows us to do this)
        for folder in folders[:]:
            if any((fnmatch.fnmatchcase(folder, e) for e in args.ignore_patterns)):
                folders.remove(folder)
            else:
                folder_relpath = "/" + os.path.join(rel_path, folder).replace(os.sep, "/") + "/"
                if any((fnmatch.fnmatchcase(folder_relpath, e) for e in args.ignore_paths)):
                    folders.remove(folder)

def scan_file(file_name, cix_dir):
    pass

if __name__ == '__main__':
    args = parse_args(sys.argv)
    fix_module_path()
    walk_tree(args)
