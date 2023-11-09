import json
from .hashing import hash_password
from flask_login import UserMixin
import secrets
from box import Box
from .db import sql_execute


class User(UserMixin, Box):
    def __init__(self, user_data):
        super().__init__(user_data)

    def save(self):
        from .db import db

        """Save this user object to the database"""
        info = json.dumps(
            {k: self[k]
                for k in self if k not in ["username", "password", "id"]}
        )

        if "id" in self:
            sql_execute(
                f"UPDATE users SET username=?, password=?, info=? WHERE id=?;", self.username, self.password, info, self.id
            )
        else:
            sql_execute(
                f"INSERT INTO users (username, password, info) VALUES (?, ?, ?);", self.username, hash_password(
                    self.password), info
            )
            self.id = db.last_insert_rowid()

    def add_token(self, name=""):
        """Add a new access token for a user"""
        token = secrets.token_urlsafe(32)
        sql_execute(
            f"INSERT INTO tokens (user_id, token, name) VALUES (?, ?, ?);", self.id, token, name
        )

    def delete_token(self, token):
        """Delete an access token"""
        sql_execute(
            f"DELETE FROM tokens WHERE user_id = ? AND token = ?", self.id, token
        )

    def get_tokens(self):
        """Retrieve all access tokens belonging to a user"""
        return sql_execute(
            f"SELECT token, name FROM tokens WHERE user_id = ?", self.id
        ).fetchall()

    def add_buddy(self, buddy):
        """Add a buddy to a user's buddy list"""
        return sql_execute(
            f"INSERT INTO buddies (user1_id, user2_id) VALUES (?, ?)", self.id, buddy.id
        )

    def delete_buddy(self, buddy):
        """Delete a buddy from a user's buddy list"""
        sql_execute(
            f"DELETE FROM buddies WHERE user1_id = ? AND user2_id = ?", self.id, buddy.id
        )
        sql_execute(
            f"DELETE FROM buddies WHERE user1_id = ? AND user2_id = ?", buddy.id, self.id
        )

    def friend_status(self, buddy):
        """Check if a user is a buddy of another user"""

        added = sql_execute(
            f"SELECT * FROM buddies WHERE user1_id = ? AND user2_id = ?", self.id, buddy.id
        ).fetchone() != None

        received = sql_execute(
            f"SELECT * FROM buddies WHERE user1_id = ? AND user2_id = ?", buddy.id, self.id
        ).fetchone() != None

        if (self.id == buddy.id):
            return "self"
        if (added and received):
            return "friends"
        if (added):
            return "pending"
        if (received):
            return "requested"

        return "none"

    @staticmethod
    def get_token_user(token):
        """Retrieve the user who owns a particular access token"""
        user_id = sql_execute(
            f"SELECT user_id FROM tokens WHERE token = ?", token).get
        if user_id != None:
            return User.get_user(user_id)

    @staticmethod
    def get_user(userid):
        if type(userid) == int or userid.isnumeric():
            sql = f"SELECT id, username, password, info FROM users WHERE id = ?;"
        else:
            sql = f"SELECT id, username, password, info FROM users WHERE username = ?;"
        row = sql_execute(sql, userid).fetchone()
        if row:
            user = User(json.loads(row[3]))
            user.update({"id": row[0], "username": row[1], "password": row[2]})
            return user
