

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.realpath(path))


if __name__ == "__main__":
    import bNyan

    sys.exit(bNyan.main())
    # sys.exit(bNyan.m3u8_test())

