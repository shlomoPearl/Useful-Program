from datetime import datetime, timedelta, date
import calendar
import random


def adjust_date(date_str, increment=True):
    print(datetime.max)
    date_object = datetime.strptime(date_str, '%d/%m/%Y')
    adjustment = timedelta(days=31) if increment else timedelta(days=-31)
    new_date = date_object + adjustment
    print(new_date)
    next_month = (date_object.month + 1) if increment else (date_object.month - 1)
    next_year = date_object.year if next_month <= 12 else (date_object.year + 1)
    next_month = next_month % 12 if next_month <= 12 else 1
    next_month_days = (datetime(next_year, next_month + 1, 1) - datetime(next_year, next_month, 1)).days
    if new_date.day > next_month_days:
        new_date = new_date.replace(day=next_month_days)
    new_date_str = new_date.strftime('%d/%m/%Y')
    return new_date_str


def increment_date(date_str):
    date_object = datetime.strptime(date_str, '%d/%m/%Y')
    day_obj = date_object.day
    month_obj = date_object.month
    next_month = (month_obj + 1) % 12 if (month_obj + 1) % 12 > 0 else 12
    year_obj = date_object.year
    num_day_current = calendar.monthrange(year_obj, month_obj)[1]
    num_day_next = calendar.monthrange(year_obj, next_month)[1]
    new_date = date_object + timedelta(days=num_day_next if day_obj == num_day_current else num_day_current)
    new_date_str = new_date.strftime('%d/%m/%Y')
    return new_date_str


def decrement_date(date_str):
    date_object = datetime.strptime(date_str, '%d/%m/%Y')
    day_obj = date_object.day
    month_obj = date_object.month
    before_month = (month_obj - 1) % 12 if (month_obj - 1) % 12 > 0 else 12
    year_obj = date_object.year
    num_day_current = calendar.monthrange(year_obj, month_obj)[1]
    num_day_before = calendar.monthrange(year_obj, before_month)[1]
    new_date = date_object + timedelta(days=-(num_day_current if day_obj == num_day_current else num_day_before))
    new_date_str = new_date.strftime('%d/%m/%Y')
    return new_date_str


date_lst = ["01/01/2023", "01/01/2024", "31/01/2023", "28/02/2023", "31/12/2023", "28/12/2022", "30/11/2023"]
for d in date_lst:
    print(d, "~~~~~~>>>", increment_date(d))
# print(datetime.strftime())
# for i in range(20):
#     month_r = random.randint(1, 12)
#     year_r = random.randint(2020, 2024)
#     try:
#         print(f"{month_r}/{year_r} ---->", decrement_date(f"{month_r}/{year_r}"))
#     except Exception as e:
#         print(e)

# incremented_date_str = adjust_date(input_date_str, increment=True)
# print("Incremented date:", incremented_date_str)  # Output: 28/02/2023

# input_date_str = "31/12/2022"
# incremented_date_str = adjust_date(input_date_str, increment=True)
# print("Incremented date:", incremented_date_str)  # Output: 31/01/2023
