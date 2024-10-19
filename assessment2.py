import requests
import json
import sqlite3
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt

# API Configuration
API_KEY = 'def755d9dda5eafb2802baba0f41d1a0'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Convert temperature from Kelvin to Celsius or Fahrenheit
def convert_temperature(kelvin, unit='Celsius'):
    if unit == 'Celsius':
        return kelvin - 273.15
    elif unit == 'Fahrenheit':
        return (kelvin - 273.15) * 9/5 + 32
    else:
        return kelvin

# Retrieve weather data from the OpenWeatherMap API
def get_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve weather data for {city}. Error: {response.status_code}")
        return None

# Process the weather data (convert temperature, extract details)
def process_weather_data(data, unit='Celsius'):
    city = data['name']
    temp = convert_temperature(data['main']['temp'], unit)
    feels_like = convert_temperature(data['main']['feels_like'], unit)
    weather_main = data['weather'][0]['main']
    timestamp = data['dt']
    
    return {
        'city': city,
        'temp': temp,
        'feels_like': feels_like,
        'main': weather_main,
        'dt': timestamp
    }

# Setup the SQLite database to store weather data and daily summaries
def setup_database():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temp REAL,
            feels_like REAL,
            main TEXT,
            dt INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_summary (
            city TEXT,
            avg_temp REAL,
            max_temp REAL,
            min_temp REAL,
            dominant_weather TEXT,
            date TEXT
        )
    ''')
    
    conn.commit()
    return conn

# Store retrieved weather data in the database
def store_weather_data(db_conn, weather_data):
    cursor = db_conn.cursor()
    cursor.execute('''
        INSERT INTO weather (city, temp, feels_like, main, dt)
        VALUES (?, ?, ?, ?, ?)
    ''', (weather_data['city'], weather_data['temp'], weather_data['feels_like'], weather_data['main'], weather_data['dt']))
    db_conn.commit()

# Calculate daily weather summaries (average, min/max temp, dominant weather)
def calculate_daily_summary(db_conn, city):
    cursor = db_conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT temp, main FROM weather
        WHERE city = ? AND date(dt, 'unixepoch') = ?
    ''', (city, today))
    
    data = cursor.fetchall()
    
    if data:
        temps = [entry[0] for entry in data]
        conditions = [entry[1] for entry in data]
        
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        min_temp = min(temps)
        dominant_weather = max(set(conditions), key=conditions.count)
        
        cursor.execute('''
            INSERT INTO daily_summary (city, avg_temp, max_temp, min_temp, dominant_weather, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (city, avg_temp, max_temp, min_temp, dominant_weather, today))
        db_conn.commit()

# Check for alert threshold violations
def check_alerts(weather_data, temp_threshold=35):
    city = weather_data['city']
    temp = weather_data['temp']
    
    if temp > temp_threshold:
        print(f"ALERT: {city} temperature has exceeded the threshold! Current temperature: {temp}°C")
        # Add email notification here using smtplib or SendGrid

# Fetch, store, and process weather data at intervals
def fetch_and_store_weather_data(db_conn):
    for city in CITIES:
        weather_data = get_weather_data(city)
        if weather_data:
            processed_data = process_weather_data(weather_data)
            store_weather_data(db_conn, processed_data)
            check_alerts(processed_data)
            calculate_daily_summary(db_conn, city)

# Scheduler to retrieve data at a configurable interval (e.g., every 5 minutes)
def start_scheduler(db_conn):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: fetch_and_store_weather_data(db_conn), 'interval', minutes=5)
    scheduler.start()

# Visualize the daily summaries using Matplotlib
def visualize_daily_summaries(db_conn):
    cursor = db_conn.cursor()
    cursor.execute('SELECT city, avg_temp, date FROM daily_summary')
    data = cursor.fetchall()
    
    cities = {}
    for city, temp, date in data:
        if city not in cities:
            cities[city] = {'dates': [], 'temps': []}
        cities[city]['dates'].append(date)
        cities[city]['temps'].append(temp)
    
    for city, info in cities.items():
        plt.plot(info['dates'], info['temps'], label=city)
    
    plt.xlabel('Date')
    plt.ylabel('Avg Temperature (°C)')
    plt.title('Daily Avg Temperature by City')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    # Initialize the database
    db_conn = setup_database()
    
    # Start the scheduler to fetch data every 5 minutes
    start_scheduler(db_conn)
    
    # Keep the application running
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Stopping the scheduler.")
