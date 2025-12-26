from server.core.webserver import App
from server.core.database import Database


def get_database(app: App) -> Database:
    return app.database


