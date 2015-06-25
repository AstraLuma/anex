#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if root not in sys.path:
        sys.path += [root]
    try:
        sys.path.remove('')
    except ValueError:
        pass
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anex.server.server.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
