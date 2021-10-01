from main import Weather
import unittest
from main import KEY
from datetime import datetime


class WeatherTest(unittest.TestCase):

    def test_key_exists(self):
        self.assertNotEqual(KEY, None, 'key does not exists')


    def test_init_with_default_city(self):
        weather = Weather()
        self.assertEqual(weather.city, 'Dmitrov')


    def test_correct_lan_lot_timezone(self):
        weather = Weather()
        self.assertAlmostEqual(weather.lat, 56.35, delta=0.1)
        self.assertAlmostEqual(weather.lon, 37.5167, delta=0.1)
        self.assertEqual(weather.timezone, 10800)


    def test_sunset_sunrise_len(self):
        weather = Weather()
        sunrise, sunset = weather._sunrise_sunset_time()
        self.assertEqual(len(sunset), 5)


    def test_daylight_and_day(self):
        weather = Weather()
        daylight_duration, day = weather.max_daylight_and_day()
        self.assertNotEqual(day, datetime.fromtimestamp(0).strftime("%A, %B %d %Y"))


    def test_calculate_nights_count(self):
        weather = Weather()
        response = weather._forecast()
        indexes = weather._get_night_indexes(response)
        self.assertEqual(len(indexes), 5)


if __name__ == '__main__':
    unittest.main()
