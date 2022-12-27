import sqlite3 as sql

conn = sql.connect('test.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')