# 🌦 Weather App (Python CLI)

A simple *Weather App* built with Python that fetches live weather data using the *OpenWeatherMap API*.  
It provides temperature, humidity, wind speed, sunrise/sunset times, and condition description for any city.

---

## ✨ Features
- 🌍 Get current weather by city name  
- 🌡 Shows temperature, feels-like, humidity, wind speed  
- 🌅 Sunrise and sunset times (local time)  
- ⚡ Supports Celsius (metric) and Fahrenheit (imperial)  
- 💾 Lightweight, runs in terminal, no external dependencies except requests

---

## 🛠 Requirements
- Python *3.7+*  
- requests library  

Install dependency:
bash
pip install requests


---

## 🚀 How to Run

### 1. Clone the repo
bash
git clone https://github.com/zaidkhan-automation/python-automation-projects.git
cd python-automation-projects/WeatherApp


### 2. Run the script
Interactive mode:
bash
python weather_app.py


It will ask:

Enter city name (e.g. Delhi, London):
Enter your OpenWeatherMap API key:


### 3. Quick run (no prompts)
bash
python weather_app.py -c "Kanpur" -k YOUR_API_KEY


### 4. Using environment variable (recommended)
Save your API key:
powershell
setx OWM_API_KEY "YOUR_API_KEY"

Then run:
bash
python weather_app.py -c "Kanpur"


---

## 🖼 Example Output

Weather for: Kanpur, IN
Condition : Haze
Temperature: 34.2 °C (feels like 36.0 °C)
Humidity  : 45%
Wind speed: 3.6 m/s
Sunrise   : 2025-09-05 05:45:12
Sunset    : 2025-09-05 18:21:33


---

## 🔮 Future Improvements
- 5-day forecast support  
- Save recent searches  
- GUI version with Tkinter  
- Auto-detect location  

---

## 📜 License
MIT License — free to use, share, and modify.