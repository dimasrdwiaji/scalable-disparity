import requests

api_endpoint = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
    "latitude": "-6.20",
    "longitude": "106.82",
    "current": "pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi",
}
resp = requests.get(api_endpoint, params=params).json()
print("Open-Meteo response:")
print("Time:", resp.get("current", {}).get("time"))
print("PM2.5:", resp.get("current", {}).get("pm2_5"))
print("US AQI:", resp.get("current", {}).get("us_aqi"))
print("European AQI:", resp.get("current", {}).get("european_aqi"))
