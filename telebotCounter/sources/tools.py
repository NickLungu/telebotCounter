from datetime import datetime, timedelta
import time
from calendar import monthrange
import regex as re


def calculate_difference(time_query):
        check_format = date_point_check_format(time_query)
        if check_format:
            now_ = datetime.utcnow()
            end = datetime(
                time_query['year'],
                time_query['month'],
                time_query['day'],
                time_query['hour'],
                time_query['minute'],
                0
            )
            start = datetime(
                now_.year,
                now_.month,
                now_.day,
                now_.hour,
                now_.minute,
                0
            )
            start = start + timedelta(hours=int(time_query['timezone']))
            delta = end - start
            total_seconds = int(delta.total_seconds())
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 86400) % 3600 // 60
            check_difference = True
            if days < 0 or hours < 0 or minutes < 0:
                check_difference = False
            return check_difference, {'days': days, 'hours': hours, 'minutes': minutes}

        return False, {}


def parse_calculate_query(query):
    try:
        date_points = re.findall(r'[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+', query)
        return True, date_points[0], date_points[1]
    except:
        return False, None, None


def parse_query(query):
    if query != 'echo':
        print(query)
        try:
            date_points = re.findall(r'[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+', query)
            date_point = date_points[0]
            print(date_point)
            title = ' '.join(query.split(' ')[:-1])
            print(title)
            splitted = date_point.split('-')
            print(splitted)
            return True, date_point, title, splitted
        except:
            print("debug: wrong format")
            return False, None, None, None

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


def make_dict_from_splitted_date(splitted):
    return {
        'year': int(splitted[0]),
        'month': int(splitted[1]),
        'day': int(splitted[2]),
        'hour': int(splitted[3]),
        'minute': int(splitted[4])
    }