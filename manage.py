#!/usr/bin/env python
import sys
import os.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from click_lock import lock_group

cli = lock_group()


@cli.command('print-routes')
def print_routes():
    """Print all project routes"""
    from my_project import web
    web.app.print_routes()


if __name__ == '__main__':
    cli()
