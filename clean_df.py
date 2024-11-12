def binHr(x):
  if 6 <= x < 12:
    return "Morning"
  elif 12 <= x < 17:
    return "Afternoon"
  elif 17 <= x < 21:
    return "Evening"
  else:
    return "Night"


def binRush(x):
  if 7 <= x < 9:
    return "Rush"
  elif 17 <= x < 19:
    return "Rush"
  else:
    return "Not Rush"

def binWind(x):
  if x < 10:
    return "Low"
  elif 10 <= x < 20:
    return "Medium"
  else:
    return "High"
  
def dow_map(day):
    days = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }
    return days[day]

def binSeason(new_month):
    if new_month in [3,4,5]:
          season = 1
    elif new_month in [6,7,8]:
        season = 2
    elif new_month in [6,7,8]:
        season = 3
    else:
        season = 4

    return season