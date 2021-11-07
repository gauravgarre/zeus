from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
import requests
from datetime import datetime
app = Flask(__name__)


@app.route('/bot', methods=['GET', 'POST'])
def bot():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    incoming_msg = request.form.get('Body').lower().strip()
    phone_no = request.form.get('From')
    print(phone_no)
    print(incoming_msg)
    resp = MessagingResponse()
    msg = resp.message()
    weather_conditions = {1: "temp", 2: "pop", 3: "clouds", 4: "wind_spd", 5: "uv", 6: "vis", 7: "rh"}
    weather_labels = {1: "Temperature", 2: "Chance of Precipitation", 3:  "Cloud Coverage", 4: "Wind Speed",
                      5: "UV Index", 6: "Visibility", 7: "Humidity"}
    weather_units = {1: "°C", 2: "%", 3: "%", 4: "m/s", 5: "", 6: "km", 7: "%"}

    sql = "SELECT location FROM userdata WHERE phone = ?"
    val = (phone_no,)
    mycursor.execute(sql, val)
    out = mycursor.fetchall()

    if (in_db_overall(phone_no) == 0 and incoming_msg == 'start'):
        sql = "INSERT INTO userdata (phone, status, location) VALUES (?, ?, ?)"
        val = (phone_no, "location", "none")
        mycursor.execute(sql, val)
        mydb.commit()
        msg.body("Welcome to Zeus! Receive SMS reminders and alerts for UV, Air Quality, and much more.\n\nEnter your location in the format (city, state abbreviation):")
    elif incoming_msg == 'help me':
        help_str = "Here are the available commands:\nSTART\nMENU\nCHANGE LOCATION\nDELETE REMINDERS\nHELP ME"
        msg.body(help_str)
    elif incoming_msg == "change location":
        update_status(phone_no, "location", mydb, mycursor)
        msg.body("Enter the location you would like to change to (city, state abbreviation):")
    elif incoming_msg == 'delete reminders':
        sql = "DELETE FROM reminders WHERE phone = ?"
        val = (phone_no, )
        mycursor.execute(sql, val)
        mydb.commit()
        update_status(phone_no, "menu", mydb, mycursor)
        msg.body("Reminders successfully deleted!\n\nPlease choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit")
    elif incoming_msg == "menu":
        msg.body("Please choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit")
    elif in_db(phone_no, "location"):
        sql = "UPDATE userdata SET location = ? WHERE phone = ?"
        val = (incoming_msg, phone_no)
        mycursor.execute(sql, val)
        update_status(phone_no, "menu", mydb, mycursor)
        msg.body("Please choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit")
    elif in_db(phone_no, "menu") and incoming_msg == "1":
        update_status(phone_no, "current", mydb, mycursor)
        msg.body("Please enter the weather conditions you’d like to know right now. (“ex: 123467”)\n(1) Temperature\n(2) Chance of Precipitation\n(3) Cloud Coverage\n(4) Wind Speed\n(5) UV Index\n(6) Visibility\n(7) Humidity\n(8) Air Quality")
    elif in_db(phone_no, "menu") and incoming_msg == "2":
        update_status(phone_no, "daily", mydb, mycursor)
        msg.body("Please enter the weather conditions you’d like to be informed of daily. (“ex: 123467”)\n(1) Temperature\n(2) Chance of Precipitation\n(3) Cloud Coverage\n(4) Wind Speed\n(5) UV Index\n(6) Visibility\n(7) Humidity\n(8) Air Quality")
    elif in_db(phone_no, "menu") and incoming_msg == "3":
        update_status(phone_no, "alerts", mydb, mycursor)
        msg.body("Please enter the weather conditions you’d like to be alerted about. (“ex: 123467”)\n(1) Temperature\n(2) Chance of Precipitation\n(3) Cloud Coverage\n(4) Wind Speed\n(5) UV Index\n(6) Visibility\n(7) Humidity\n(8) Air Quality")
    elif in_db(phone_no, "menu") and incoming_msg == "4":
        update_status(phone_no, "location", mydb, mycursor)
        msg.body("Thanks for using Zeus! If you need to contact me again, respond with HELP ME.")
    elif in_db(phone_no, "current"):
        options = [int(d) for d in str(incoming_msg)]
        mymsg = ""

        for option in options:

            if option == 8:
                val = get_air_quality(out[0][0])
                desc = ""
                if 0 <= val <= 50:
                    desc = "Good"
                elif 51 <= val <= 100:
                    desc = "Moderate"
                elif 101 <= val <= 200:
                    desc = "Unhealthy"
                elif 201 <= val <= 300:
                    desc = "Very Unhealthy"
                elif 301 <= val:
                    desc = "Hazardous"

                mymsg += "Air Quality Index: " + str(val) + " " + desc + "\n"
            elif option == 5:
                val = get_weather_condition(weather_conditions[option], out[0][0])
                desc = ""
                val = round(val, 1)
                if 0 <= val <= 2:
                    desc = "Low"
                elif 3 <= val <= 5:
                    desc = "Medium"
                elif 6 <= val <= 7:
                    desc = "High"
                elif 8 <= val <= 10:
                    desc = "Very High"
                elif 11 <= val:
                    desc = "Extremely High"
                mymsg += "UV Index: " + str(val) + " " + desc + "\n"
            else:
                mymsg += weather_labels[option] + ": " + str(get_weather_condition(weather_conditions[option], out[0][0])) + " " + weather_units[option] + "\n"
        print(mymsg)
        mymsg += "\nPlease choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit"
        msg.body(mymsg)
        update_status(phone_no, "menu", mydb, mycursor)

    elif in_db(phone_no, "daily"):
        sql = "INSERT INTO reminders (phone, location, options, hour, day, type) VALUES (?, ?, ?, ?, ?, ?)"
        current_day = datetime.today().day
        val = (phone_no, out[0][0], incoming_msg, "-1", str(current_day), "daily")
        mycursor.execute(sql, val)
        mydb.commit()

        update_status(phone_no, "daily1", mydb, mycursor)
        msg.body("Which hour of the day would you like to be reminded (0-23) in EST?")
    elif in_db(phone_no, "daily1"):

        sql = "UPDATE reminders SET hour = ? WHERE phone = ? AND type = ? AND hour = ?"
        val = (incoming_msg, phone_no, "daily", "-1")
        mycursor.execute(sql, val)
        mydb.commit()

        update_status(phone_no, "menu", mydb, mycursor)
        msg.body("Your word is my command. Reminders created successfully!\n\nPlease choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit")
    elif in_db(phone_no, "alerts"):
        sql = "INSERT INTO reminders (phone, location, options, hour, day, type) VALUES (?, ?, ?, ?, ?, ?)"
        current_day = datetime.today().day
        current_hour = datetime.today().hour
        val = (phone_no, out[0][0], incoming_msg, current_hour, "0", "alerts")
        mycursor.execute(sql, val)
        mydb.commit()

        update_status(phone_no, "menu", mydb, mycursor)
        msg.body("Your word is my command. Alerts created successfully!\n\nPlease choose what kind of notifications you'd like:\n(1) Current\n(2) Daily\n(3) Alerts\n(4) Exit")
    else:
        msg.body("Invalid response. Reply with HELP ME for more information and commands.")
    return str(resp)

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

def in_db(phone, status):
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE phone = ? AND status = ?"
    val = (phone, status)
    mycursor.execute(sql, val)
    out = mycursor.fetchall()
    mycursor.close()
    return out

def in_db_overall(phone):
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()
    sql = "SELECT * FROM userdata WHERE phone = ?"
    val = (phone,)
    mycursor.execute(sql, val)
    out = mycursor.fetchall()
    mycursor.close()
    return len(out)

def send_call_message(phone, message):
    account_sid = 'sid'
    auth_token = 'token'
    client = Client(account_sid, auth_token)
    msg = message
    call = client.calls.create(
        twiml=f'<Response><Pause length="3"/><Say>{msg}</Say></Response>',
        to=phone,
        from_='+18013370504'
    )
    print(call.sid)

def get_weather_condition(type, location):
    weatherBitKey = "key"
    city, state = location.split(",")
    result = requests.get(
        "https://api.weatherbit.io/v2.0/forecast/hourly/?city=" + city + "," + state + "&hours=24&key=" + weatherBitKey)
    formatted = result.json()
    return formatted["data"][0][type]

def get_air_quality(location):
    weatherBitKey = "key"
    city, state = location.split(",")
    result = requests.get(
        "https://api.weatherbit.io/v2.0/forecast/airquality?city=" + city + "," + state + "&hours=24&key=" + weatherBitKey)
    formatted = result.json()
    return formatted["data"][0]["aqi"]

def update_status(phone, status, mydb, mycursor):
    sql = "UPDATE userdata SET status = ? WHERE phone = ?"
    val = (status, phone)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

if __name__ == '__main__':
    app.run()


