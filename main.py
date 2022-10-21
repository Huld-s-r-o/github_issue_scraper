from datetime import datetime
from datetime import timedelta

def date_fnc(hours_shift):
    now_t = datetime.now()
    delta_h = timedelta(hours=hours_shift)
    new_time = now_t + delta_h
    return new_time


def t_printer(dt_obj):
    print(f"Current time is: {dt_obj}")


if __name__ == "__main__":
    to = date_fnc(2)
    t_printer(to)
