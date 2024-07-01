
from flask import Flask, request, jsonify
import time
import requests
import ngrok

# Creating instance of the Flask object
server = Flask(__name__)

# Makeing request for IP 
def fetch_client_ip():
    response = requests.get("https://api.ipify.org?format=json")
    if response.status_code == 200:
        return response.json().get('ip', 'Unknown IP')
    else:
        return "Failed to fetch IP"

# Makeing request for geolocation
def fetch_geolocation(ip):
    response = requests.get(f"http://ip-api.com/json/{ip}?fields=lat,lon,city")
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch geolocation"}

def fetch_weather(lat, lon, api_key): 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
    
        # Extracting temperature data
        if 'main' in data and 'temp' in data['main']:
            temperature = data['main']['temp']
            location = data.get('name', 'Unknown location')
            return {"temperature": temperature, "location": location}
        else:
            return {"error": "Temperature data not found in the response."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data from the API: {e}"}
    except ValueError as e:
        return {"error": f"Error parsing JSON: {e}"}

# Mapping the URL root 
@server.route("/", methods=['GET'])
def home():
    data_set = {
        'Page': 'Home',
        'Message': 'Successfully loaded homepage',
        'Timestamp': time.time()
    }
    return jsonify(data_set)

@server.route("/user/api/", methods=['GET'])
def user_request():
    ip = fetch_client_ip()
    if ip == "Failed to fetch IP":
        return jsonify({"error": "Failed to fetch client IP"}), 500

    geolocation = fetch_geolocation(ip)
    if "error" in geolocation:
        return jsonify(geolocation), 500

    lat = geolocation.get('lat')
    lon = geolocation.get('lon')
    city = geolocation.get('city')
    api_key = "c2f6090886f86e8642692b5610783d58"
    weather_data = fetch_weather(lat, lon, api_key)
    
    return jsonify({"city": city, **weather_data})

@server.route("/api/hello", methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name', 'Guest')  # Default to 'Guest' if no name is provided
   
    ip = fetch_client_ip()
    if ip == "Failed to fetch IP":
        return jsonify({"error": "Failed to fetch client IP"}), 500

    geolocation = fetch_geolocation(ip)
    if "error" in geolocation:
        return jsonify(geolocation), 500

    lat = geolocation.get('lat')
    lon = geolocation.get('lon')
    city = geolocation.get('city')
    api_key = "c2f6090886f86e8642692b5610783d58"
    weather_data = fetch_weather(lat, lon, api_key)

    if "error" in weather_data:
        return jsonify(weather_data), 500

    temperature = weather_data['temperature']
    location = weather_data['location']
    greeting_message = f"Hello!,{visitor_name}The temperature is {temperature} Degree Celcius in {location}."

    return jsonify({
        "greeting": greeting_message,
        "client_ip": ip,
        "city": city,
        # "temperature": temperature,
        # "location": location
    })

if __name__ == '__main__':
    server.run(debug=True, port=8080)
