"""
Database table setup.
"""

from peewee import SqliteDatabase, Model, DateTimeField, TextField

database = SqliteDatabase(None)


class Post(Model):
    """ Class defines a table layout in the posts database """
    name = TextField()
    timestamp = DateTimeField()
    comment = TextField()

    class Meta:
        database = database


def get_max_id():
    """ Get max id from database """
    try:
        max_id = max([msi.id for msi in Post.select()])
    except Exception:
        max_id = None
    return max_id
