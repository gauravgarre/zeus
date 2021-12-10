# Zeus

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#inspiration">Inspiration</a>
    </li>
    <li>
      <a href="#about">About</a>
    </li>
    <li><a href="#how-its-built">How It's Built</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Inspiration
According to the World Health Organization, 4.2 million deaths every year occur due to outdoor air pollution. Exposure to air pollution can result in significant health problems such as decreased lung function, aggravated asthma, and increased respiratory symptoms.

Additionally, UV radiation exposure is a risk factor for skin cancer, cataracts, and other ill-ness. The incidence of skin cancer, including melanoma, has increased due to excess exposure to UV radiation. To alert individuals of both air quality and UV index outdoors, along with several other weather conditions, we created Zeus the weather bot.

## About
Zeus alerts individuals via call or text about weather conditions. After the user messages the number with ‘start’ and enters their location, they have 3 options for interacting with Zeus. The first option allows them to receive current weather condition data which includes temperature, the chance of precipitation, cloud coverage, wind speed, UV index, visibility, humidity, and air quality.

The second option allows them to receive daily reminders - at a time of their choosing - of any selection of the weather conditions outlined above. A user might, for example, decide to receive a UV index reminder every morning to determine how much sunlight exposure is safe.

The third option allows users to set up alerts that will continue for the following 24 hours. These alerts will notify users of certain weather conditions, such as when the air quality increases to possibly hazardous levels. A user may set up an alert for the UV index on a day they go outside in order to warn them from experiencing UV radiation.

The user is always able to access the help menu with the command “help me”. From here, the user can access the menu, delete their reminders, and change their location. The service is currently functional for the entire U.S. subcontinent.

## How It's Built
We developed the backend for the chatbot using Twilio API and Python Flask to deliver automated SMS messages and phone calls. The Twilio API uses a webhook to redirect SMS messages to the Flask backend which houses Zeus’s implementation. This Flask backend is hosted on an AWS EC2 instance. After the user initially messages the Zeus phone number, they are prompted to enter their location. This phone number and location data is then sent to our Google Cloud Firestore database.

When the user requests for weather data pertaining to their current location, our Flask backend calls the WeatherBit API using the stored location data. When the user wants to create a reminder or alert, the Flask backend creates and stores reminder objects in an SQLite database. This database is accessed by the reminder system which ensures that reminders and alerts are being sent out periodically as necessary.

## Usage
To access the bot, text START to +1 (801) 337-0504. (Live functionality is not available at the moment).

Demo: https://youtu.be/0I3cJMA7YH4

## Contact
Devpost: https://devpost.com/software/weather-bot-fbvh0r

Project link: https://github.com/gauravgarre/zeus
