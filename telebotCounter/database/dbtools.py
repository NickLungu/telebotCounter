import psycopg2
import time
from datetime import datetime, timezone
import os


# Connect to db on google cloud
def connection():
    """
        :rtype: database connection
        :return: database connection
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'))
    return conn


def insert_date_point(data_):
    """
        insert data into database "DataPoints" table
        :param data_: list [image path on the server, message id]
    """
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_insert_query = """ INSERT INTO datepoints (chat_id, year, month, day, hour, minute, title, is_done)
                                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""

        # insert command_id, chat_id, command_name, date_reg
        record_to_insert = (data_[0],
                            data_[1],
                            data_[2],
                            data_[3],
                            data_[4],
                            data_[5],
                            data_[6],
                            data_[7])
        cursor.execute(postgres_insert_query, record_to_insert)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Cannot insert," + str(e))


def select_date_point(user_id):
    """
        :param user_id: user id
        :type user_id: int
        :rtype: string
        :return: return date points
    """
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_get_query = "SELECT year, month, day, hour, minute, title FROM datepoints " \
                             "WHERE chat_id = %s AND is_done = False " \
                             % str(user_id)
        cursor.execute(postgres_get_query)
        record = cursor.fetchall()
        cursor.close()
        conn.close()
        date_point = record
        return date_point
    except Exception as e:
        print(e)
        return "oooops"