from typing import Tuple, Union, List

from sqlalchemy.exc import DatabaseError

from db import Session
from db.modles import Measurement


def get_data(chat_id: int, type_get='g') -> Tuple[Union[bool, str], List[Measurement]]:
    error = False
    measurements = []
    session = Session()
    try:
        measurements = session.query(
            Measurement.systolic,
            Measurement.diastolic,
            Measurement.date,
            Measurement.hand
        ).filter_by(chat_id=chat_id).order_by(Measurement.id).all()
        if type_get == 'a':
            measurements = session.query(Measurement).filter_by(chat_id=chat_id).order_by(Measurement.id).all()
    except (Exception, DatabaseError) as e:
        error = f'{e}'
    finally:
        session.close()

    return error, measurements


def set_data(measurements: list):
    error = False
    chat_id, hand, systolic, diastolic, pulse, comment, date = measurements
    session = Session()
    try:
        measurement = Measurement(
            chat_id=chat_id,
            hand=hand,
            systolic=systolic,
            diastolic=diastolic,
            pulse=pulse,
            comment=comment,
            date=date
        )
        session.add(measurement)
        session.commit()
        session.close()
    except (Exception, DatabaseError) as e:
        error = f'{e}'
    finally:
        session.close()

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
