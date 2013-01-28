__all__ = ["fix_module_path"]

import os.path
import sys

def fix_module_path():
    """
    Fix module include paths to make codeintel work
    """
    for relpath in (
            ("obj", "pylib"),
            ("komodo-bits", "schemes"),
            ("komodo-bits", "python-sitelib"),
            ):
        sys.path.append(os.path.join(os.path.dirname(__file__), *relpath))
    # this one is for dxr - going up directories doesn't work due to symlinks
    sys.path.append(os.sep.join(__file__.split(os.sep)[:-3]))

    # ciElementTree's bootstrap is completely broken; it looked for 'ElementTree'
    # and 'elementtree.ElementTree', but not 'xml.etree.ElementTree'.  Fake it out
    # here so that it runs the bootstrap code, marking it as patched for komodo
    import xml.etree
    sys.modules['elementtree'] = sys.modules['xml.etree']
    import ciElementTree
    sys.modules['cElementTree'] = sys.modules['ciElementTree']
