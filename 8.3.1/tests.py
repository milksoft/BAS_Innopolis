# test_uav_control.py

import unittest
from pymavlink import mavutil
from unittest.mock import MagicMock, patch, call
from mission_planner import MissionPlanner
from uav_control import UAVControl
class TestUAVControl(unittest.TestCase):
    def setUp(self):
        # Создание mock-объекта для mavlink_connection
        self.patcher = patch('uav_control.mavutil.mavlink_connection')
        self.mock_mavlink_connection = self.patcher.start()
        self.mock_master = MagicMock()
        self.mock_mavlink_connection.return_value = self.mock_master
        self.mock_master.wait_heartbeat.return_value = True
        # Настройка mode_mapping
        self.mock_master.mode_mapping.return_value = {'GUIDED': 4, 'LAND': 9, 'RTL': 6}

        self.uav = UAVControl('udp:127.0.0.1:14550')

    def tearDown(self):
        # Остановка патчера
        self.patcher.stop()

    def test_connection(self):
        # Проверка установления соединения
        self.mock_mavlink_connection.assert_called_with('udp:127.0.0.1:14550')
        self.mock_master.wait_heartbeat.assert_called_once()

    def test_arm_disarm(self):
        # Проверка взведения и разоружения БПЛА
        self.uav.arm()
        self.mock_master.arducopter_arm.assert_called_once()
        self.mock_master.motors_armed_wait.assert_called_once()

        self.uav.disarm()
        self.mock_master.arducopter_disarm.assert_called_once()
        self.mock_master.motors_disarmed_wait.assert_called_once()

    def test_set_mode_valid(self):
        # Проверка установки корректного режима полёта
        self.uav.set_mode('GUIDED')
        expected_mode_id = self.mock_master.mode_mapping.return_value.get('GUIDED')
        self.mock_master.set_mode.assert_called_with(expected_mode_id)

    def test_set_mode_invalid(self):
        # Проверка реакции на установку некорректного режима
        with self.assertRaises(ValueError):
            self.uav.set_mode('INVALID_MODE')

    def test_takeoff_positive_altitude(self):
        # Проверка взлёта на положительную высоту
        # Настройка возврата координат
        position_msg = MagicMock()
        position_msg.get_type.return_value = 'GLOBAL_POSITION_INT'
        position_msg.lat = 550000000  # 55.0 градусов
        position_msg.lon = 370000000  # 37.0 градусов
        self.mock_master.recv_match.return_value = position_msg

        self.uav.takeoff(10)
        expected_mode_id = self.mock_master.mode_mapping.return_value.get('GUIDED')
        self.mock_master.set_mode.assert_called_with(expected_mode_id)
        self.mock_master.mav.command_long_send.assert_called_once()
        self.mock_master.recv_match.assert_called_with(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)

    def test_takeoff_negative_altitude(self):
        # Проверка реакции на отрицательную высоту
        with self.assertRaises(ValueError):
            self.uav.takeoff(-5)

    def test_goto(self):
        # Проверка команды полёта к заданной точке
        self.uav.goto(55.0, 37.0, 100.0)

        self.mock_master.mav.mission_count_send.assert_called_once()
        self.mock_master.mav.mission_item_send.assert_called_once()

        # Проверяем параметры вызова mission_item_send
        args, kwargs = self.mock_master.mav.mission_item_send.call_args

        # Проверяем, что используется правильный фрейм координат
        frame = args[3]
        self.assertEqual(frame, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT)

    def test_get_telemetry(self):
        # Проверка получения телеметрических данных
        attitude_msg = MagicMock()
        attitude_msg.get_type.return_value = 'ATTITUDE'
        attitude_msg.roll = 0.1
        attitude_msg.pitch = 0.2
        attitude_msg.yaw = 0.3

        self.mock_master.recv_match.return_value = attitude_msg

        telemetry = self.uav.get_telemetry()
        self.assertIsNotNone(telemetry)
        self.assertEqual(telemetry['roll'], 0.1)
        self.assertEqual(telemetry['pitch'], 0.2)
        self.assertEqual(telemetry['yaw'], 0.3)

    def test_wait_command_ack(self):
        # Проверка ожидания подтверждения команды
        ack_msg = MagicMock()
        ack_msg.command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
        ack_msg.result = mavutil.mavlink.MAV_RESULT_ACCEPTED

        self.mock_master.recv_match.return_value = ack_msg

        result = self.uav.wait_command_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)
        self.assertTrue(result)

    def test_wait_command_ack_timeout(self):
        # Проверка таймаута при ожидании подтверждения команды
        self.mock_master.recv_match.return_value = None

        result = self.uav.wait_command_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, timeout=1)
        self.assertFalse(result)

# test_mission_planner.py
class TestMissionPlanner(unittest.TestCase):
    def setUp(self):
        # Создание mock-объекта для UAVControl
        self.patcher = patch('mission_planner.UAVControl')
        self.mock_uav_control_class = self.patcher.start()
        self.mock_uav = MagicMock()
        self.mock_uav_control_class.return_value = self.mock_uav
        self.planner = MissionPlanner('udp:127.0.0.1:14550')

    def tearDown(self):
        # Остановка патчера
        self.patcher.stop()

    def test_execute_mission_success(self):
        # Тест успешного выполнения миссии
        waypoints = [
            (55.0, 37.0, 10.0),
            (55.0001, 37.0001, 20.0),
            (55.0002, 37.0002, 15.0)
        ]

        # Настройка side_effect для get_telemetry
        telemetry_data = iter([
            {'lat': 55.0, 'lon': 37.0, 'alt': 10.0},
            {'lat': 55.0001, 'lon': 37.0001, 'alt': 20.0},
            {'lat': 55.0002, 'lon': 37.0002, 'alt': 15.0}
        ])

        self.mock_uav.get_telemetry.side_effect = lambda: next(telemetry_data, None)

        self.planner.execute_mission(waypoints)

        self.mock_uav.arm.assert_called_once()
        self.mock_uav.set_mode.assert_any_call('GUIDED')
        self.mock_uav.takeoff.assert_called_once_with(waypoints[0][2])

        expected_calls = [call(wp[0], wp[1], wp[2]) for wp in waypoints]
        self.assertEqual(self.mock_uav.goto.call_count, len(waypoints))
        self.mock_uav.goto.assert_has_calls(expected_calls)

        self.mock_uav.set_mode.assert_any_call('RTL')
        self.mock_uav.disarm.assert_called_once()

    def test_execute_mission_failure(self):
        # Тест провала выполнения миссии из-за недостижения точки
        waypoints = [
            (55.0, 37.0, 10.0),
            (55.0001, 37.0001, 20.0)
        ]

        # Настройка get_telemetry для возвращения неизменных координат
        self.mock_uav.get_telemetry.return_value = {
            'lat': 55.0,
            'lon': 37.0,
            'alt': 10.0
        }

        with self.assertRaises(Exception) as context:
            self.planner.execute_mission(waypoints)

        self.assertIn('Не удалось достичь точки 1', str(context.exception))
        self.mock_uav.disarm.assert_called_once()


if __name__ == '__main__':
    unittest.main()