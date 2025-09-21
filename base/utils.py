import requests
from django.conf import settings as django_settings


def get_weather_condition(house, forecast_hours=0):
    address = f'{house.city}, {house.country}'
    if forecast_hours == 0:
        weather_response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": django_settings.WEATHER_API_KEY, "q": address}
        )
        weather_data = weather_response.json()
        return weather_data["current"]["condition"]["text"]
    if forecast_hours > 0:
        weather_response = requests.get(
            "https://api.weatherapi.com/v1/forecast.json",
            params={"key": django_settings.WEATHER_API_KEY, "q": address, "days": 1, "aqi": "no", "alerts": "no"}
        )
        weather_data = weather_response.json()
        return weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
    else:
        from datetime import date, timedelta

        yesterday = date.today() - timedelta(days=1)
        formatted = yesterday.strftime("%Y-%m-%d")
        weather_response = requests.get(
            "https://api.weatherapi.com/v1/history.json",
            params={"key": django_settings.WEATHER_API_KEY, "q": address, "dt": formatted}
        )
        weather_data = weather_response.json()
        return weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
