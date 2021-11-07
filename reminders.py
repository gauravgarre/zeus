import requests
from datetime import datetime
import datetime as dt
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import time
import threading
import sqlite3
import time

def check_reminders():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM reminders")
    output = mycursor.fetchall()

    current_day = datetime.today().day
    current_month = datetime.today().month
    current_hour = datetime.today().hour
    weather_conditions = {1: "temp", 2: "pop", 3: "clouds", 4: "wind_spd", 5: "uv", 6: "vis", 7: "rh"}
    weather_units = {1: "°C", 2: "%", 3: "%", 4: "m/s", 5: "", 6: "km", 7: "%"}

    for reminder in output:
        if reminder[5] == "daily" and int(reminder[3]) == current_hour and int(reminder[4]) == current_day:
            options = reminder[2]
            options = [int(d) for d in str(options)]
            mymsg = ""

            for option in options:

                if option == 1:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val <= -4:
                        desc = "Take a heavy jacket with you. It's cold!"
                    elif -3 <= val <= 6:
                        desc = "Take a jacket with you!"
                    elif 7 <= val <= 17:
                        desc = "Consider taking a light jacket. It's a bit chilly!"
                    elif 18 <= val <= 26:
                        desc = "Wear lighter clothes. It's pretty warm!"
                    elif 27 <= val:
                        desc = "Wear shorts. It's hot today!"
                    mymsg += "It's " + str(val) + weather_units[option] + ". " + desc + "\n\n"

                elif option == 2:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val < 30:
                        desc = " Clear day out, huh?"
                    elif val > 60:
                        desc = " Don't forget an umbrella!"
                    mymsg += "There's a " + str(val) + weather_units[option] + " chance of rain." + desc + "\n\n"

                elif option == 3:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val < 30:
                        desc = " Take some sunglasses with you. It's pretty sunny out!"
                    mymsg += "The cloudiness is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 4:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val > 10:
                        desc = " Grab a wind breaker. It's windy!"
                    mymsg += "The wind is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 5:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    high = ""
                    val = round(val, 1)
                    if 0 <= val <= 2:
                        desc = "Low"
                    elif 3 <= val <= 5:
                        desc = "Medium"
                    elif 6 <= val <= 7:
                        desc = "High"
                        high = " Don't forget sunscreen!"
                    elif 8 <= val <= 10:
                        desc = "Very High"
                        high = " Don't forget sunscreen!"
                    elif 11 <= val:
                        desc = "Extremely High"
                        high = " Don't forget sunscreen!"
                    mymsg += "The UV index is " + desc + " today." + high + "\n\n"

                elif option == 6:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val < 20:
                        desc = " Low visibility out there today. Be careful driving!"
                    mymsg += "The visibility is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 7:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    if val > 70:
                        desc = " High humidity today. It's might be hotter than normal!"
                    mymsg += "The humidity is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 8:
                    val = get_air_quality(reminder[1])
                    desc = ""
                    high = ""
                    if 0 <= val <= 50:
                        desc = "Good"
                    elif 51 <= val <= 100:
                        desc = "Moderate"
                    elif 101 <= val <= 200:
                        desc = "Unhealthy"
                        high = " Take a mask with you!"
                    elif 201 <= val <= 300:
                        desc = "Very Unhealthy"
                        high = " Take a mask with you!"
                    elif 301 <= val:
                        desc = "Hazardous"
                        high = " Air is not looking good. Take a mask with you!"

                    mymsg += "The air quality today is " + desc + high + "\n\n"


            send_sms_message(reminder[0], mymsg)

            next_day = (datetime.today() + dt.timedelta(days=1)).day
            sql = "UPDATE reminders SET day = ? WHERE phone = ? AND type = ?"
            val = (str(next_day), reminder[0], reminder[5])
            mycursor.execute(sql, val)
            mydb.commit()
        elif reminder[5] == "alerts" and int(reminder[3]) == current_hour and int(reminder[4]) < 24:
            print('passed alerts')
            options = reminder[2]
            options = [int(d) for d in str(options)]

            mymsg = ""

            for option in options:

                if option == 1:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    if val <= 0:
                        desc = "Below freezing temperatures!"
                        mymsg += "It's " + str(val) + weather_units[option] + ". " + desc + "\n\n"
                    elif val >= 38:
                        desc = "It's scalding hot!"
                        mymsg += "It's " + str(val) + weather_units[option] + ". " + desc + "\n\n"

                elif option == 2:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    if val >= 60:
                        desc = " It's going to rain soon!"
                        mymsg += "There's a " + str(val) + weather_units[option] + " chance of rain." + desc + "\n\n"

                # elif option == 3:
                #     val = get_weather_condition(weather_conditions[option], reminder[1])
                #     desc = ""
                #     if val < 30:
                #         desc = " Take some sunglasses with you. It's pretty sunny out!"
                #     mymsg += "The cloudiness is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 4:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    if val > 10:
                        desc = " It's getting very windy!"
                        mymsg += "The wind is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 5:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    desc = ""
                    high = ""
                    val = round(val, 1)
                    if 6 <= val <= 7:
                        desc = "High"
                        high = " Find some shade and reapply sunscreen!"
                        mymsg += "The UV index is " + desc + " right now." + high + "\n\n"
                    elif 8 <= val <= 10:
                        desc = "Very High"
                        high = " Get under some shade. UV index is very high!"
                        mymsg += "The UV index is " + desc + " right now." + high + "\n\n"
                    elif 11 <= val:
                        desc = "Extremely High"
                        high = " Get under some shade. UV index is very high!"
                        mymsg += "The UV index is " + desc + " right now." + high + "\n\n"

                # elif option == 6:
                #     val = get_weather_condition(weather_conditions[option], reminder[1])
                #     desc = ""
                #     if val < 20:
                #         desc = " Low visibility out there today. Be careful driving!"
                #     mymsg += "The visibility is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 7:
                    val = get_weather_condition(weather_conditions[option], reminder[1])
                    if val <= 20:
                        desc = " Low humidity! Apply some lotion."
                        mymsg += "The humidity is " + str(val) + weather_units[option] + "." + desc + "\n\n"

                elif option == 8:
                    val = get_air_quality(reminder[1])
                    desc = ""
                    high = ""
                    if 101 <= val <= 200:
                        desc = "Unhealthy"
                        high = " Move indoors into a well-ventilated environment!"
                        mymsg += "The air quality right now is " + desc + high + "\n\n"
                    elif 201 <= val <= 300:
                        desc = "Very Unhealthy"
                        high = " Move indoors into a well-ventilated environment!"
                        mymsg += "The air quality right now is " + desc + high + "\n\n"
                    elif 301 <= val:
                        desc = "Hazardous"
                        high = " Move indoors into a well-ventilated environment!"
                        mymsg += "The air quality right now is " + desc + high + "\n\n"

            if mymsg != "":
                send_sms_message(reminder[0], mymsg)

            next_day = int(reminder[4]) + 1
            sql = "UPDATE reminders SET day = ? WHERE phone = ? AND type = ?"
            val = (str(next_day), reminder[0], reminder[5])
            mycursor.execute(sql, val)
            mydb.commit()

            next_hour = (int(reminder[3]) + 1) % 23
            sql = "UPDATE reminders SET hour = ? WHERE phone = ? AND type = ?"
            val = (str(next_hour), reminder[0], reminder[5])
            mycursor.execute(sql, val)
            mydb.commit()





def get_air_quality(location):
    weatherBitKey = "key"
    city, state = location.split(",")
    result = requests.get(
        "https://api.weatherbit.io/v2.0/forecast/airquality?city=" + city + "," + state + "&hours=24&key=" + weatherBitKey)
    formatted = result.json()
    return formatted["data"][0]["aqi"]


def get_weather_condition(type, location):
    weatherBitKey = "key"
    city, state = location.split(",")
    result = requests.get(
        "https://api.weatherbit.io/v2.0/forecast/hourly/?city=" + city + "," + state + "&hours=24&key=" + weatherBitKey)
    formatted = result.json()
    return formatted["data"][0][type]


def send_sms_message(number, message):
    account_sid = 'sid'
    auth_token = 'token'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=message,
        from_='+18013370504',
        to=number
    )

    print(message.sid)

while True:
    check_reminders()
    print("called")
    time.sleep(5)
