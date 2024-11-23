import unittest
import xml.etree.ElementTree as ET
import random
import time
import threading
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция для добавления link
def add_link(robot, name, geometry, material=None, sensor=None, mass=0, inertia=None, propeller_speed=None):
    link = ET.SubElement(robot, "link", name=name)
    
    # Установка физики
    if mass > 0:
        inertia_elem = ET.SubElement(link, "inertial")
        ET.SubElement(inertia_elem, "mass").text = str(mass)
        if inertia:
            inertia_elem = ET.SubElement(inertia_elem, "inertia")
            ET.SubElement(inertia_elem, "ixx").text = str(inertia[0])
            ET.SubElement(inertia_elem, "ixy").text = str(inertia[1])
            ET.SubElement(inertia_elem, "ixz").text = str(inertia[2])
            ET.SubElement(inertia_elem, "iyy").text = str(inertia[3])
            ET.SubElement(inertia_elem, "iyz").text = str(inertia[4])
            ET.SubElement(inertia_elem, "izz").text = str(inertia[5])
    
    visual = ET.SubElement(link, "visual")
    geom = ET.SubElement(visual, "geometry")
    
    # Определение типа геометрии
    if geometry["type"] == "mesh":
        ET.SubElement(geom, "mesh", filename=geometry["filename"])
    elif geometry["type"] == "box":
        ET.SubElement(geom, "box", size=geometry["size"])
    elif geometry["type"] == "cylinder":
        ET.SubElement(geom, "cylinder", radius=geometry["radius"], length=geometry["length"])
    
    if material:
        mat = ET.SubElement(visual, "material", name=material["name"])
        ET.SubElement(mat, "color", rgba=material["rgba"])
    
    if propeller_speed is not None:
        ET.SubElement(link, "propeller_speed").text = str(propeller_speed)

    # Добавляем информацию о сенсорах
    if sensor:
        sensor_elem = ET.SubElement(link, "sensor", type=sensor["type"], name=sensor["name"])
        ET.SubElement(sensor_elem, "update_rate").text = str(sensor["update_rate"])

# Функция для мониторинга сенсоров
def monitor_sensors(num_measurements=0):
    measurements = 0
    while num_measurements == 0 or measurements < num_measurements:
        # Генерируем случайные данные для сенсоров
        imu_data = {
            "acceleration": (random.uniform(-9.81, 9.81), random.uniform(-9.81, 9.81), random.uniform(-9.81, 9.81)),
            "gyro": (random.uniform(-250, 250), random.uniform(-250, 250), random.uniform(-250, 250)),
            "temperature": random.uniform(-10, 50)
        }
        logging.info("IMU Data: %s", imu_data)

        barometer_data = {
            "pressure": random.uniform(950, 1050),
            "temperature": random.uniform(-10, 50)
        }
        logging.info("Barometer Data: %s", barometer_data)

        gps_data = {
            "latitude": random.uniform(37.0, 38.0),
            "longitude": random.uniform(-123.0, -122.0),
            "altitude": random.uniform(0, 100)
        }
        logging.info("GPS Data: %s", gps_data)

        measurements += 1
        time.sleep(2)  # Пауза между измерениями

class TestQuadcopterModel(unittest.TestCase):

    def setUp(self):
        """Создание тестового элемента robot перед каждым тестом."""
        self.robot = ET.Element("robot", name="quadcopter")

    def test_add_link(self):
        """Тестирование добавления link."""
        add_link(self.robot, "base_link", {"type": "box", "size": "1 1 1"}, mass=1.0)
        self.assertEqual(len(self.robot.findall("link")), 1)  # Убедимся, что link добавлен

        link = self.robot.find("link[@name='base_link']")
        self.assertIsNotNone(link)  # Убедимся, что link существует
        mass = link.find("inertial/mass")
        self.assertEqual(mass.text, "1.0")  # Убедимся, что масса установлена правильно

    def test_add_sensor(self):
        """Тестирование добавления сенсора."""
        sensor = {"name": "mpu6050_sensor", "type": "IMU", "update_rate": 100}
        add_link(self.robot, "mpu6050", {"type": "box", "size": "2 2 1"}, sensor=sensor)

        sensor_elem = self.robot.find("link[@name='mpu6050']/sensor")
        self.assertIsNotNone(sensor_elem)  # Убедимся, что сенсор добавлен
        self.assertEqual(sensor_elem.get("name"), "mpu6050_sensor")  # Проверка имени сенсора
        self.assertEqual(int(sensor_elem.find("update_rate").text), 100)  # Проверка частоты обновления

    def test_monitor_sensors(self):
        """Тестирование функции мониторинга сенсоров."""
        num_measurements = 5
        with self.assertLogs(level='INFO') as log:
            monitor_sensors(num_measurements)
            self.assertEqual(len(log.output), num_measurements * 3)  # 3 сообщения: IMU, Barometer и GPS

    def test_monitor_sensors_no_limit(self):
        """Тестирование функции мониторинга без ограничения (возможно, с использованием таймаута)."""
        def monitor_in_background():
            monitor_sensors(0)  # Бесконечный мониторинг

        monitor_thread = threading.Thread(target=monitor_in_background)
        monitor_thread.start()
        time.sleep(2)  # Ждем некоторое время
        monitor_thread.join(timeout=0.5)  # Остановка потока

if __name__ == '__main__':
    unittest.main()