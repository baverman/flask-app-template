import logging
import os.path

ROOT = os.path.dirname(os.path.dirname(__file__))
jroot = lambda *parts: os.path.join(ROOT, *parts)

def update_globals(data):
    globals().update((k, v) for k, v in data.items() if not k.startswith('__'))

# Default settings
from settings.default import *

# Settings from $CONFIG file
if 'CONFIG' in os.environ:
    import runpy
    ctx = runpy.run_path(os.environ['CONFIG'])
    update_globals(ctx)

# Local settings
if os.path.exists(jroot('settings', 'local.py')):
    from .local import *

# Check required settings
invalid_opts = [k for k, v in globals().items() if v == 'UNDEFINED']
if invalid_opts:
    raise RuntimeError('Following options must be defined: {}'.format(sorted(invalid_opts)))

# Configure logging
if LOGGING:
    import logging.config
    logging.config.dictConfig(LOGGING)
else:
    logging.basicConfig(level=LOGGING_LEVEL)

# Configure Sentry
if SENTRY:
    from raven import Client
    from raven.handlers.logging import SentryHandler

    sentry_client = Client(SENTRY)
    sentry_handler = SentryHandler(sentry_client)
    sentry_handler.setLevel('ERROR')
    logging.getLogger().addHandler(sentry_handler)
