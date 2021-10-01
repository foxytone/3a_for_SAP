import os
import unittest
from datetime import datetime
from typing import Tuple, List

import requests
from requests import Response

KEY = os.environ.get('WEATHER_API_KEY')


class Weather:
    city: str
    lat: float
    lon: float
    timezone: int


    def __init__(self, city: str = 'Dmitrov'):
        self.city = city
        self._set_lon_lat_timezone()


    def _get_day_date(self, timestamp: int) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%A, %B %d, %Y")


    def min_degrees_and_day(self) -> Tuple[str, str]:
        """Returns (delta, day)"""
        response = self._forecast()
        night_indexes = [0] + self._get_night_indexes(response)

        delta, timestamp = self._calculate_delta_temp_and_day(response, night_indexes)

        delta = str(delta) + '℃'
        day = self._get_day_date(timestamp)

        return delta, day


    def _calculate_delta_temp_and_day(self, response: Response, night_indexes: list) -> Tuple[int, int]:
        """Returns (delta, timestamp)"""
        delta = 100500
        timestamp = 0

        # Yes, 2 cycles but still N complexity
        for i in range(0, len(night_indexes) - 1):
            for j in range(night_indexes[i], night_indexes[i + 1]):
                buff_delta = response.json()['list'][j]['main']['feels_like'] - \
                             response.json()['list'][night_indexes[i + 1]]['main']['temp_min']
                if abs(buff_delta) < delta:
                    delta = buff_delta
                    timestamp = response.json()['list'][j]['dt']
        return delta, timestamp


    def _get_night_indexes(self, response: Response) -> List[int]:
        days_edge = []
        for i in range(0, len(response.json()['list'])):
            if (response.json()['list'][i]['dt'] + self.timezone) % 86400 == 0:
                days_edge.append(i)
        return days_edge


    def _set_lon_lat_timezone(self) -> None:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={KEY}'
        response = requests.get(url)
        self.lat = response.json()['coord']['lat']
        self.lon = response.json()['coord']['lon']
        self.timezone = response.json()['timezone']


    def _one_call(self) -> Response:
        url = f'https://api.openweathermap.org/data/2.5/onecall?lat={self.lat}&lon={self.lon}&exclude=hourly,minutely&appid={KEY}'
        return requests.get(url)


    def _forecast(self) -> Response:
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={KEY}'
        return requests.get(url)


    def _sunrise_sunset_time(self) -> Tuple[List[int], List[int]]:
        """Returns (sunset, sunrise)"""
        response = self._one_call()
        sunset = []
        sunrise = []
        for day in range(0, 5):
            sunrise.append(response.json()['daily'][day]['sunrise'])
            sunset.append(response.json()['daily'][day]['sunset'])

        assert len(sunrise) == len(sunset), 'different sunset sunrise lengths, something went wrong'

        return sunrise, sunset


    def max_daylight_and_day(self) -> Tuple[str, str]:
        """Returns (daylight_duration, day)"""
        sunrise, sunset = self._sunrise_sunset_time()
        delta = 0
        # time mark, after we can figure a day
        sunrise_time = 0

        for i in range(0, len(sunset)):
            calculated_delta = sunset[i] - sunrise[i]

            if calculated_delta > delta:
                delta = calculated_delta
                sunrise_time = sunrise[i]

        day = self._get_day_date(sunrise_time)
        daylight_duration = datetime.fromtimestamp(delta).strftime('%H:%M:%S')

        return daylight_duration, day


if __name__ == '__main__':
    weather = Weather()
    daylight, day_with_longest_daylight = weather.max_daylight_and_day()
    print(f'Maximum daylight is {daylight} at day {day_with_longest_daylight}')

    min_delta_temp, day_with_min_delta_temp = weather.min_degrees_and_day()
    print(
        f'Minimum temperature differense between feels-like and night is {min_delta_temp} at day {day_with_min_delta_temp}')
