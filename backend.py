import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


def get_data(chat_id, type_get='g'):

    error = False
    measurements = []
    sql = "SELECT systolic, diastolic, date, hand FROM measurements WHERE chat_id = %s ORDER BY id;"
    if type_get == 'a':
        sql = "SELECT * FROM measurements WHERE chat_id = %s ORDER BY id;"

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(sql, (chat_id,))
        measurements = list(cur)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as e:
        error = f'{e}'
    finally:
        if conn is not None:
            conn.close()

    return error, measurements


def set_data(measurements):

    error = False
    sql = """INSERT INTO measurements 
    (chat_id, hand, systolic, diastolic, pulse, comment, date) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(sql, measurements)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as e:
        error = f'{e}'
    finally:
        if conn is not None:
            conn.close()

    return error


if __name__ == '__main__':
    # import pandas as pd
    # from datetime import datetime
    #
    # with open('data.json', 'r') as f:
    #     df = pd.read_json(f, orient='lines')
    #
    # df.sort_index(inplace=True)
    # for index, row in df.iterrows():
    #  t = set_data((row[1], row[7], row[2], row[3], row[5], row[6], datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")))
    #  print(t)
    t, data = get_data(123)
    print(data)
    print(t)
