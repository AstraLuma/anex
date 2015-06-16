#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    sys.path += [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anex.server.server.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
