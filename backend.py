import sqlite3


def get_data(chat_id, type_get='g'):

    error = False
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    if type_get == 'g':
        sql = "SELECT systolic, diastolic, date, hand FROM measurements WHERE id_chat = ? ORDER BY id;"
    elif type_get == 'a':
        sql = "SELECT * FROM measurements WHERE id_chat = ? ORDER BY id;"
    try:
        cursor.execute(sql, (chat_id,))
    except Exception as e:
        error = f'{e}'
    data = list(cursor)
    cursor.close()

    return error, data


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
