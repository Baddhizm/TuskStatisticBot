import sqlite3
from datetime import datetime


def get_data(chat_id):

    error = False
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    sql = "SELECT systolic, diastolic, date, hand FROM measurements WHERE id_chat = ? ORDER BY id;"
    try:
        cursor.execute(sql, (chat_id,))
    except Exception as e:
        error = f'{e}'

    y1, y2, x, hand = zip(*cursor)
    cursor.close()

    x = list(map(lambda y: datetime.strptime(y, "%Y-%m-%d %H:%M:%S.%f"), x))

    return error, x, y1, y2, hand


def set_data(measurements):

    error = False
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    sql = """INSERT INTO measurements 
    (id_chat, hand, systolic, diastolic, pulse, comment, date) 
    VALUES (?, ?, ?, ?, ?, ?, ?)"""

    try:
        cursor.execute(sql, tuple(measurements))
    except Exception as e:
        error = f'{e}'

    connection.commit()
    cursor.close()

    return error
