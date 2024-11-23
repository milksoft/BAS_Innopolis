import numpy as np
import unittest
from drone_accelerometer import data_acs

class TestIntegrationDataAcs(unittest.TestCase):

    def test_integration_case_success(self):
        accel_data = [[2, 2, 2], [5, 5, 5], [8, 8, 8]]
        weight = 1200  # допустимая масса
        flight_time = 1600  # допустимое время полета
        control_distance = 800  # допустимая дальность управления

        result = data_acs(accel_data, weight, flight_time, control_distance)

        expected_acceleration = [2.0, 5.0, 8.0]
        expected_inclination_x = np.arctan2(2.0, np.sqrt(5.0 ** 2 + 8.0 ** 2)) * 180 / np.pi
        expected_inclination_y = np.arctan2(5.0, np.sqrt(2.0 ** 2 + 8.0 ** 2)) * 180 / np.pi

        # Проверяем результаты
        self.assertAlmostEqual(result["acceleration"][0], expected_acceleration[0])
        self.assertAlmostEqual(result["acceleration"][1], expected_acceleration[1])
        self.assertAlmostEqual(result["acceleration"][2], expected_acceleration[2])
        self.assertAlmostEqual(result["inclination"][0], expected_inclination_x, places=2)
        self.assertAlmostEqual(result["inclination"][1], expected_inclination_y, places=2)

    def test_exceed_payload(self):
        accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        weight = 1600  # превышение массы
        flight_time = 10  # допустимое время полета
        control_distance = 500  # допустимая дальность управления

        with self.assertRaises(ValueError) as context:
            data_acs(accel_data, weight, flight_time, control_distance)

        self.assertEqual(str(context.exception), "Превышена максимальная взлетная масса БЛА.")

    def test_exceed_flight_time(self):
        accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        weight = 1200  # допустимая масса
        flight_time = 4000  # превышение времени полета
        control_distance = 500  # допустимая дальность управления

        with self.assertRaises(ValueError) as context:
            data_acs(accel_data, weight, flight_time, control_distance)

        self.assertEqual(str(context.exception), "Превышено максимальное время полета.")

    def test_exceed_control_distance(self):
        accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        weight = 1200  # допустимая масса
        flight_time = 10  # допустимое время полета
        control_distance = 1500  # превышение дальности управления

        with self.assertRaises(ValueError) as context:
            data_acs(accel_data, weight, flight_time, control_distance)

        self.assertEqual(str(context.exception), "Превышена максимальная дальность управления.")

if __name__ == "__main__":
    unittest.main(verbosity=2)