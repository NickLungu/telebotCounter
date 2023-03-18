from datetime import datetime
from calendar import monthrange
import regex as re


def calculate_difference(time_query):
    check_format = date_point_check_format(time_query)
    if check_format:
        end = datetime(
            time_query['year'],
            time_query['month'],
            time_query['day'],
            time_query['hour'],
            time_query['minute'],
            0
        )
        start = datetime(
            datetime.now().year,
            datetime.now().month,
            datetime.now().day,
            datetime.now().hour,
            datetime.now().minute,
            0
        )
        delta = end - start
        total_seconds = int(delta.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 86400) % 3600 // 60
        check_difference = True
        if days < 0 or hours < 0 or minutes < 0:
            check_difference = False
        return check_difference and check_format, {'days': days, 'hours': hours, 'minutes': minutes}

    return False, {}


def parse_query(query):
    try:
        date_point = re.findall(r'[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+', query)[0]
        title = ' '.join(query.split(' ')[:-1])
        splitted = date_point.split('-')
        return True, date_point, title, splitted
    except:
        return False, None, None, None


def date_point_check_format(date_point):

    if date_point["year"] < datetime.now().year:
        return False
    if date_point["month"] < 1 or date_point["month"] > 12:
        return False
    if date_point["day"] < 1 or date_point["day"] > monthrange(date_point["year"], date_point["month"])[1]:
        return False
    if date_point["hour"] < 0 or date_point["hour"] > 24:
        return False
    if date_point["minute"] < 0 or date_point["minute"] > 60:
        return False
    return True
