from datetime import datetime, timedelta


def time_string_to_minutes_decimal(time_str):
    colon_count = time_str.count(":")

    # Blank
    if len(time_str.strip()) == 0:
        raise ValueError('Time string is blank')

    if colon_count == 1:
        time_str = '0:' + time_str
    elif colon_count != 2:
        raise ValueError('Time string has wrong number of colons')

    if '.' not in time_str:
        time_str += '.0'

    try:
        t = datetime.strptime(time_str, "%H:%M:%S.%f")
        return datetime_to_timedelta(t).total_seconds() / 60.0
    except Exception as e:
        raise e


def datetime_to_timedelta(dt):
    return timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
