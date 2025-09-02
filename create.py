import sqlite3

login = input("Введите ваш логин: ")
tg_id = input("Введите ваш tg_id: ")


conn = sqlite3.connect('asic.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    tg_id INTEGER NOT NULL
);
''')

cursor.execute('''
    INSERT INTO users (nickname, tg_id) VALUES (?, ?)
''', (login, tg_id))

conn.commit()
conn.close()

print(f"Пользователь {login} успешно создан с ID {tg_id}")

