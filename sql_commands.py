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
                user_name INTEGER NOT NULL,
                score INTEGER NOT NULL,
                time FLOAT NOT NULL
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

UPDATE_SCORES = """
INSERT INTO Scores (user_name, score, time) VALUES ('{user_name}', '{score}', '{time}')
"""

GET_SCORES = """
SELECT * FROM Scores
"""

GET_SCORES_SORTED_BY_USER = """
SELECT * FROM Scores ORDER BY user_name DESC
"""


GET_SCORES_SORTED_BY_SCORE = """
SELECT * FROM Scores ORDER BY score DESC
"""

GET_SCORES_SORTED_BY_TIME = """
SELECT * FROM Scores ORDER BY time ASC
"""
