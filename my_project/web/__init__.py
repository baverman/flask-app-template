from flaskish import Flask

import settings

app = Flask('my_project')

# Provide additional context for errors inside request scope
if settings.SENTRY:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, client=settings.sentry_client)

# close session after request
from .. import db
app.teardown_request(db.remove_session)

# import views
from . import views
