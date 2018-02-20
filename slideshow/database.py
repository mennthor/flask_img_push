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
