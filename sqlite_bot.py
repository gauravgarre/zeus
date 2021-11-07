import sqlite3
from twilio.rest import Client

def create_db():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    mycursor.execute('''CREATE TABLE IF NOT EXISTS userdata
                        (phone TEXT, status TEXT, location TEXT)''')

    mydb.commit()

    mycursor.execute("SELECT * FROM userdata")
    output = mycursor.fetchall()
    print(output)

def peek():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM userdata")

    output = mycursor.fetchall()
    print(output)

def peek_reminders():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM reminders")

    output = mycursor.fetchall()
    print(output)

def create_reminder_db():
    mydb = sqlite3.connect('userdata.db')
    mycursor = mydb.cursor()

    mycursor.execute('''CREATE TABLE IF NOT EXISTS reminders
                            (phone TEXT, location TEXT, options TEXT, hour TEXT, day TEXT, type TEXT)''')

    mydb.commit()

    mycursor.execute("SELECT * FROM reminders")
    output = mycursor.fetchall()
    print(output)

#create_db()
#create_reminder_db()

#peek()
#peek_reminders()
