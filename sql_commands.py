CREATE_TABLE_USERS = """
                CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
                )
                """

CREATE_TABLE_USERS_SCORES = """
                CREATE TABLE IF NOT EXISTS Scores (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                score INTEGER NOT NULL
                )
                """
#                 FOREIGN KEY (user_id) REFERENCES Users(id)

CREATE_USER = """
            INSERT INTO Users (username, password) VALUES ('{login}', '{password_hash}')
            """

GET_USERS = """
SELECT * FROM Users WHERE username='{login}' AND password='{password}'
"""

GET_USER = """
SELECT * FROM Users WHERE username='{login}'
"""
