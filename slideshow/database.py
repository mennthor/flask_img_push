from peewee import SqliteDatabase, Model, DateTimeField, TextField

database = SqliteDatabase(None)


class Post(Model):
    name = TextField()
    timestamp = DateTimeField()
    comment = TextField()

    class Meta:
        database = database
