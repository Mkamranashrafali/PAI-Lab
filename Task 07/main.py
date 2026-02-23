from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

base = "https://api.open-meteo.com/v1/forecast"

@app.get("/")
def home():
    return jsonify({
        "name": "weather backend",
        "routes": ["/weather", "/weather/city", "/health"]
    })

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.get("/weather")
def weather():
    lat = request.args.get("lat", "31.5204")
    lon = request.args.get("lon", "74.3587")

    url = base + "?latitude=" + lat + "&longitude=" + lon + "&current_weather=true"
    r = requests.get(url)
    data = r.json()

    cur = data.get("current_weather", {})

    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "temperature": cur.get("temperature"),
        "windspeed": cur.get("windspeed"),
        "time": cur.get("time")
    })

@app.get("/weather/city")
def weather_city():
    city = request.args.get("name", "Lahore")

    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search?name=" + city)
    gdata = geo.json()

    if "results" not in gdata:
        return jsonify({"city": city, "found": False})

    first = gdata["results"][0]
    lat = str(first.get("latitude"))
    lon = str(first.get("longitude"))

    url = base + "?latitude=" + lat + "&longitude=" + lon + "&current_weather=true"
    r = requests.get(url)
    w = r.json().get("current_weather", {})

    return jsonify({
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "temperature": w.get("temperature"),
        "windspeed": w.get("windspeed"),
        "time": w.get("time")
    })

if __name__ == "__main__":
    app.run(debug=True)