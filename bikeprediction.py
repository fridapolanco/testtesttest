#BIKE PREDICTION
import streamlit as st
import joblib
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import pycaret
from pycaret.classification import *

from math import floor

from clean_df import binHr, binRush, binWind, dow_map, binSeason


#page configuration
#st.set_page_config(page_title="Bike Prediction", layout="wide", page_icon="🚲")

# Loading the trained model
# with open("model.pkl", 'rb') as pickle_in:
#     model = joblib.load(pickle_in)

model = load_model(model_name='my_bike_model')

def generate_data(df, datetime):
  avg_weather, avg_atemp, avg_temp, avg_hum, avg_windspeed = df.weathersit.mean(), df.atemp.mean(), df.temp.mean(), df.hum.mean(), df.windspeed.mean()
  last_date = df.date.max()
  hours_to_predict = int((datetime-last_date).total_seconds()//60**2)

  new_df = pd.DataFrame(df.sort_values(by="date", ascending=True).iloc[-1]).T

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

  cnt = 0

  for i in range(1, hours_to_predict+1):
    curr_date = pd.to_datetime(last_date + pd.Timedelta(hours=i))
    print(curr_date)
    new_hr = curr_date.hour
    new_dow = curr_date.day_name()
    new_month = curr_date.month
    cnt = predict_model(model, pd.DataFrame([
        {
        "weathersit": avg_weather,
        "atemp": avg_atemp,
        "temp": avg_temp,
        "hum": avg_hum,
        "windspeed": avg_windspeed,
        "date": curr_date,
        "weekday": dow_map(new_dow),
        "season": binSeason(new_month),
        "holiday": 0,
        "workingday": not (new_dow in ['Saturday', 'Sunday']),
        "TOD": binHr(new_hr),
        "Rush": binRush(new_hr),
        "Wind": binWind(avg_windspeed),
        "prev_count": new_df.iloc[-1]["cnt"]
      }]))
    
    cnt['cnt'] = cnt['prediction_label']
    cnt = cnt.drop(columns=["prediction_label"])
    new_df = pd.concat([new_df, cnt])

  return new_df[new_df['date'] == new_df['date'].max()]["cnt"].iloc[0]


TRAINING_DF = df = pd.read_csv("data.csv")
TRAINING_DF["date"] = pd.to_datetime(TRAINING_DF["datetime"])
TRAINING_DF = TRAINING_DF.drop(columns=["datetime"])

# defining the function which will make the prediction using the data which the user inputs TRANSFORMATIONS & RUNNING MODEL
def prediction(date,season,yr,mnth,hr,holiday,weekday,workingday,weathersit,temp,atemp,hum,windspeed,tod,rush,wind, predict_time):

    predict_time = predict_time - pd.Timedelta(days=floor(365.25*11))

    if (predict_time - TRAINING_DF.date.max()).total_seconds()//60**2 > 1:
        return generate_data(TRAINING_DF, predict_time)
    elif predict_time < TRAINING_DF.date.max():
        prev_count = TRAINING_DF[TRAINING_DF["datetime"] < predict_time].iloc[-1]["cnt"].iloc[0]
    else:
        prev_count = TRAINING_DF[TRAINING_DF["date"] == TRAINING_DF.date.max()]["cnt"].iloc[0]

    if dt.date.weekday in [3,4,5]:
        season = 1
    elif dt.date.weekday in [6,7,8]:
        season = 2
    elif dt.date.weekday in [6,7,8]:
        season = 3
    else:
        season = 4

    if holiday == "No":
        holiday = 0
    else:
        holiday = 1

    weekday = dt.date.weekday

    if (dt.date.month in [1,2,3,4,5]) and (holiday == 0):
        workingday = 1
    else:
        workingday = 0

    if weathersit == "Clear/Sunny":
        weathersit = 1
    elif weathersit == "Cloudy/Misty":
        weathersit = 2
    elif weathersit == "Light Snow/Rain":
        weathersit = 3
    else:
        weathersit = 4

    temp = temp/41
    atemp = atemp/50
    hum = hum/100
    windspeed = windspeed/100


    ################################

    data = {
        'date' : date,
        'season': season,
        'yr': yr,  
        'mnth': mnth,  
        'hr': hr,  
        'holiday' : holiday,
        'weekday': weekday,
        'workingday' : workingday,
        'weathersit': weathersit,
        'temp': temp,
        'atemp' : atemp,
        'hum': hum,
        'windspeed': windspeed, 
        'TOD': tod,
        'Rush': rush,
        'Wind': wind,
        'prev_count': prev_count
    }


    # Convert data into dataframe
    df = pd.DataFrame.from_dict([data])
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    predicted_value = predict_model(model,df)
    predicted_value = pd.DataFrame(predicted_value)
    prediction2 = predicted_value["prediction_label"][0]


    return prediction2
    

##############################s

# This is the main function in which we define our webpage FRONT END 
def main_bikeprediction():       
    # Front-end elements of the web page 
    html_temp = """
    <div style="background-color:tomato;padding:10px">
    <h2 style="color:white;text-align:center;">Bike availability checker</h2>
    </div>"""

    st.markdown(html_temp, unsafe_allow_html=True)

    #Title of our webapp
    st.title("Washington Bike Prediction")
    st.write("Welcome to your bike prediction!")

    # Create a text prompt
    st.title("Please fill the form below to find bike availability.")

################################
          
    # Following lines create input fields for prediction 
    date = st.date_input("What date would you like your bike?", format="YYYY-MM-DD", value="today")
    time = st.time_input("What time would you like your prediction?: ", value="now", step=3600)

    predict_time = pd.to_datetime(str(date) +" "+ str(time))

    holiday = st.selectbox('Is it a holiday?', ("Yes", "No"))

    tods = ("Morning","Afternoon","Evening","Night")
    tod = st.selectbox('What time of day do you need the bike?', tods)

    rush = st.selectbox('Is it rush hour?', ("Rush", "Not Rush"))

    winds = ("Low","Medium","High")
    wind = st.selectbox('How windy is it?', winds)

    weathers = ('Clear/Sunny' , 'Cloudy/Misty' , 'Light Snow/Rain','Heavy Rain/Snow')
    weathersit = ('How is the weather?', weathers)

    temp = st.slider('What is the temperature in Celcius?', -30, 50, 1)
    atemp = st.slider('What is the temperature feeling in Celcius?', -30, 50, 1)
    hum = st.slider('What is the humidity level percentage?', 0, 100, 1)

    #variables that are ignored in Pycaret so we don't care about the value; only included to have the full DF
    yr=0
    mnth=0
    hr=0
    workingday=0
    windspeed = 0

    #variables that will be calculated afterwards
    weekday=0
    season = 0

    result = ""
    # when 'Predict' is clicked, make the prediction and store it 
    if st.button("Predict"): 
        result = prediction(date, season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed, tod, rush, wind, predict_time)
        #st.success(result)

        st.success(f"The amount of available bikes for the date selected is {1000 - result}")

        
      
if __name__ == '__main__':
    main_bikeprediction()