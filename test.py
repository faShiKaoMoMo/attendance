import sqlite3

from views.constants.constants import *

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("DELETE FROM attendance_token;")
conn.commit()
