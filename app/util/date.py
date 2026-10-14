import time
from time import struct_time
from datetime import datetime

def date_time_normal(date_string: str) -> str:
  date_object: datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

  formatted_date: str = date_object.strftime("%m/%d/%Y %I:%M:%S %p")

  return formatted_date

def time_normal(fdate_string: str) -> str:
  date_string: str = fdate_string
  date_object: datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
  formatted_date: str = date_object.strftime("%I:%M:%S %p")
  return formatted_date

def date_normal(date_string: str) -> str:  
  #date_string = "2023-05-08"
  date_object: datetime = datetime.strptime(date_string, "%Y-%m-%d")

  formatted_date: str = date_object.strftime("%m/%d/%Y")

  return formatted_date

def date_time(timezone: int = 8) -> str:
  ts: float = time.time() + (3600 * timezone) # 8 is the timezome
  x: struct_time = time.gmtime(ts)
  month: int = x.tm_mon
  day: int = x.tm_mday
  hour: int = x.tm_hour
  mins: int = x.tm_min
  sec: int = x.tm_sec
  if x.tm_mon < 10:
    month = "0" + str(x.tm_mon)
  if x.tm_mday < 10:
    day = "0" + str(x.tm_mday)
  if x.tm_hour < 10:
    hour = "0" + str(x.tm_hour)
  if x.tm_min < 10:
    mins = "0" + str(x.tm_min)
  if x.tm_sec < 10:
    sec = "0" + str(x.tm_sec)
  return str(x.tm_year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(mins) + ":" + str(sec)

def dt(timezone: int = 8) -> str:
  ts: float = time.time() + (3600 * timezone) # 8 is the timezome
  x: struct_time = time.gmtime(ts)
  month: int = x.tm_mon
  day: int = x.tm_mday
  hour: int = x.tm_hour
  mins: int = x.tm_min
  sec: int = x.tm_sec
  if x.tm_mon < 10:
    month = "0" + str(x.tm_mon)
  if x.tm_mday < 10:
    day = "0" + str(x.tm_mday)
  if x.tm_hour < 10:
    hour = "0" + str(x.tm_hour)
  if x.tm_min < 10:
    mins = "0" + str(x.tm_min)
  if x.tm_sec < 10:
    sec = "0" + str(x.tm_sec)
  return str(x.tm_year) + "-" + str(month) + "-" + str(day)



arr: list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

arr_val: list = [
  31,
  28,
  31,
  30,
  31,
  30,
  31,
  31,
  30,
  31,
  30,
  31
] 

arr_name: list = [
  "January", 
  "February", 
  "March", 
  "April", 
  "May", 
  "June", 
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
]


def abbr() -> list:
  return [month[:3] for month in arr_name]

def get_arr_val(index) -> int:
  return arr_val[index]

def month_name(index) -> str:
  return arr_name[index]

def int2zero(num: int) -> str:
    # this function allow you to 
    # add a function 
    oint: str = ""
    if num < 10:
        oint += '0' + str(num)
    else:
        oint = str(num)
    return oint

def cdate_last_date(date_t) -> str:
  d: list = date_t.split("-")
  year: int = int(d[0])
  month: int = int(d[1])

  if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
    arr_val[1] = 29

  return str(year) + "-" + int2zero(month) + "-" + int2zero(arr_val[month - 1])


def cdate_last_date_r(date_t) -> tuple:
  d: list = date_t.split("-")
  year: int = int(d[0])
  month: int = int(d[1])

  if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
    arr_val[1] = 29

  # return str(year) + "-" + int2zero(month) + "-" + int2zero(arr_val[month - 1])
  return (str(year), int2zero(month), int2zero(arr_val[month - 1]))



def datetime_implement(dt1, datecreated):

    # this is for the new implementation
    d1 = datetime.strptime(dt1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(datecreated, "%Y-%m-%d %H:%M:%S")

    total = (d2 - d1).total_seconds()
    
    return total > 0