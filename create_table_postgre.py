import psycopg2
import json


def create_tables():
    """ create table in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE measurements (
            id serial PRIMARY KEY,
            chat_id INTEGER,
            hand VARCHAR(1) NOT NULL,
            systolic INTEGER,
            diastolic INTEGER,
            pulse integer default NULL,
            comment VARCHAR(255) NOT NULL,
            date timestamp
        )
        """,
    )
    conn = None
    try:
        # read the connection parameters
        with open('db.json') as json_data_file:
            params = json.load(json_data_file)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
