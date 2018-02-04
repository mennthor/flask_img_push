from peewee import SqliteDatabase, Model, DateTimeField, TextField

database = SqliteDatabase(None)


class Post(Model):
    image_path = TextField()
    timestamp = DateTimeField()
    comment = TextField()

    class Meta:
        database = database
