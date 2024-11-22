import sqlite3

def initialize_db():
    conn = sqlite3.connect('employes.db')
    with open('initialize_db.sql', 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
    print("Database initialized.")
