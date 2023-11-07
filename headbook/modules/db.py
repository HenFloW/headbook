from .utils import debug
import apsw
from flask import g

db = None


def get_cursor():
    if "cursor" not in g:
        g.cursor = db.cursor()
    return g.cursor


def sql_execute(stmt, *args, **kwargs):
    debug(stmt, args or "", kwargs or "")
    return get_cursor().execute(stmt, (*args,), **kwargs)


def sql_init():
    from .user import User

    global db
    db = apsw.Connection("./users.db")

    if db.pragma("user_version") == 0:
        sql_execute(
            """CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY, 
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            info JSON NOT NULL);"""
        )
        sql_execute(
            """CREATE TABLE IF NOT EXISTS tokens (
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            token TEXT NOT NULL UNIQUE,
            name TEXT
            );"""
        )
        sql_execute(
            """CREATE TABLE IF NOT EXISTS buddies (
            user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            PRIMARY KEY (user1_id, user2_id)
            );"""
        )
        alice = User(
            {
                "username": "alice",
                "password": "password123",
                "color": "green",
                "picture_url": "https://git.app.uib.no/uploads/-/system/user/avatar/788/avatar.png",
            }
        )
        alice.save(db)
        alice.add_token("example")
        bob = User({
            "username": "bob",
            "password": "bananas",
            "color": "red"})
        bob.save(db)
        bob.add_token("test")
        sql_execute(
            f"INSERT INTO buddies (user1_id, user2_id) VALUES ({alice.id}, {bob.id}), ({bob.id}, {alice.id});"
        )
        sql_execute("PRAGMA user_version = 1;")
