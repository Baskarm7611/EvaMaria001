from collections import OrderedDict


INTERVALS = OrderedDict([
    ('millennium', 31536000000),  # 60 * 60 * 24 * 365 * 1000
    ('century', 3153600000),      # 60 * 60 * 24 * 365 * 100
    ('year', 31536000),           # 60 * 60 * 24 * 365
    ('month', 2627424),           # 60 * 60 * 24 * 30.41 (assuming 30.41 days in a month)
    ('week', 604800),             # 60 * 60 * 24 * 7
    ('day', 86400),               # 60 * 60 * 24
    ('hour', 3600),               # 60 * 60
    ('minute', 60),
    ('second', 1)
])


def human_time(seconds, decimals=1):
    '''Human-readable time from seconds (ie. 5 days and 2 hours).

    Examples:
        >>> human_time(15)
        '15 seconds'
        >>> human_time(3600)
        '1 hour'
        >>> human_time(3720)
        '1 hour and 2 minutes'
        >>> human_time(266400)
        '3 days and 2 hours'
        >>> human_time(-1.5)
        '-1.5 seconds'
        >>> human_time(0)
        '0 seconds'
        >>> human_time(0.1)
        '100 milliseconds'
        >>> human_time(1)
        '1 second'
        >>> human_time(1.234, 2)
        '1.23 seconds'

    Args:
        seconds (int or float): Duration in seconds.
        decimals (int): Number of decimals.

    Returns:
        str: Human-readable time.
    '''
    if seconds < 0 or seconds != 0 and not 0 < seconds < 1 and 1 < seconds < INTERVALS['minute']:
        input_is_int = isinstance(seconds, int)
        return f'{str(seconds if input_is_int else round(seconds, decimals))} seconds'
    elif seconds == 0:
        return '0 seconds'
    elif 0 < seconds < 1:
        # Return in milliseconds.
        ms = int(seconds * 1000)
        return '%i millisecond%s' % (ms, 's' if ms != 1 else '')
    res = []
    for interval, count in INTERVALS.items():
        quotient, remainder = divmod(seconds, count)
        if quotient >= 1:
            seconds = remainder
            if quotient > 1:
                # Plurals.
                if interval == 'millennium':
                    interval = 'millennia'
                elif interval == 'century':
                    interval = 'centuries'
                else:
                    interval += 's'
            res.append('%i %s' % (int(quotient), interval))
        if remainder == 0:
            break

    return f'{res[0]} and {res[1]}' if len(res) >= 2 else res[0]
