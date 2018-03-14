"""
Database table setup.
"""

import numpy as np
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


def get_rnd_db_entries(N=5):
    """
    Pulls N random filenames and comments from the db, resamples when entries in
    db < N and uses palceholder if db is empty yet.

    Returns
    -------
    filenames : list
        N filename entries, not the full paths.
    comments: list
        N comments, belonging to the filenames.
    """
    max_id = get_max_id()

    if max_id is not None:
        if max_id < N:
            # Need to show with replacement because too few images
            ids = np.random.choice(np.arange(1, max_id + 1),
                                   replace=True, size=N)
            # These are returned unique so we have to rebroadcast them again
            query = Post.select().where(Post.id << ids.tolist())
            filenames = [msi.name for msi in query]
            comments = [msi.comment for msi in query]
            # Build a mapping from ids to [0, 1, 2, ...]
            n_ids = len(filenames)
            assert n_ids == len(np.unique(ids))
            id_map = {i: _id for i, _id in zip(np.unique(ids),
                                               np.arange(n_ids))}
            _ids = np.array([id_map[i] for i in ids])
            filenames = np.array(filenames)[_ids]
            comments = np.array(comments)[_ids]
        else:
            ids = np.random.choice(np.arange(1, max_id + 1),
                                   replace=False, size=N).tolist()
            # Fetch names from db and pass to template
            query = Post.select().where(Post.id << ids)
            ids = np.arange(N)
            np.random.shuffle(ids)
            filenames = np.array([msi.name for msi in query])[ids]
            comments = np.array([msi.comment for msi in query])[ids]
    else:
        # No imgs added yet or eror, only show placeholder
        filenames = N * ["_placeholder_.jpg"]
        comments = N * ["comment"]

    return filenames, comments
