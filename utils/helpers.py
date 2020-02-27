def digit_string_2_array(string_value, converter=int):
    """ converts a tuple-like string and convert it to a :<class List>: type """
    string_value = string_value[1: - 1]
    return [converter(digit) for digit in string_value.split(',')]


def format_media_timestamp(timestamp):
    """ reshape the timestamp provided to look like a count-down timer """
    stamp_hours = timestamp // 3600
    stamp_minutes = (timestamp % 3600) // 60
    stamp_seconds = (timestamp % 3600) % 60

    if not stamp_hours:
        # formatted_stamp = '{:02.0f}:{:02.0f}'.format(minutes, seconds)
        formatted_stamp = f'{stamp_minutes}:{stamp_seconds}'
    else:
        # formatted_stamp = '{:.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)
        formatted_stamp = f'{stamp_hours}:{stamp_minutes}:{stamp_seconds}'

    return formatted_stamp
