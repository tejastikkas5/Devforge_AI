"""
Experiment No. 9: Program to Demonstrate an SQL Injection Attack

AIM:
To demonstrate SQL Injection on a local sample database and the parameterized-query fix
that prevents it.

REQUIREMENTS:
Python 3.x with the built-in sqlite3 library.
"""

import sqlite3

# Set up in-memory SQLite database
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE users (u TEXT, p TEXT)")
cur.execute("INSERT INTO users VALUES ('admin','secret123')")


def vulnerable(u, p):
    # Vulnerable login: direct string interpolation allows SQL injection
    q = f"SELECT * FROM users WHERE u='{u}' AND p='{p}'"
    cur.execute(q)
    return cur.fetchone() is not None


def secure(u, p):
    # Secure login: parameterized query treats input strictly as data
    cur.execute("SELECT * FROM users WHERE u=? AND p=?", (u, p))
    return cur.fetchone() is not None


if __name__ == "__main__":
    attack = "' OR '1'='1"
    print("SQL Injection Payload :", attack)
    print("Vulnerable login result:", vulnerable(attack, attack))
    print("Secure login result    :", secure(attack, attack))
