import xml.etree.ElementTree as ET
import random
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Используйте бэкенд без GUI
import matplotlib.pyplot as plt
import re

# Класс PID-регулятора
class PID:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp  # Пропорциональный коэффициент
        self.ki = ki  # Интегральный коэффициент
        self.kd = kd  # Дифференциальный коэффициент
        self.setpoint = setpoint  # Целевая величина
        self.last_error = 0  # Последняя ошибка
        self.integral = 0  # Интеграл ошибки

    def update(self, measured_value):
        error = self.setpoint - measured_value  # Ошибка
        self.integral += error  # Интегрирование ошибки
        derivative = error - self.last_error  # Производная ошибки
        self.output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)  # Управляющий сигнал
        self.last_error = error  # Обновление последней ошибки
        return self.output

# Создание корневого элемента
robot = ET.Element("robot", name="quadcopter")

# Функция для добавления link
def add_link(name, geometry, material=None, sensor=None, mass=0, inertia=None, propeller_speed=None):
    link = ET.SubElement(robot, "link", name=name)

    # Установка физики
    if mass > 0:
        inertia_elem = ET.SubElement(link, "inertial")
        ET.SubElement(inertia_elem, "mass").text = str(mass)  # Масса в килограммах
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

    # Если это пропеллер, добавим скорость вращения
    if propeller_speed is not None:
        ET.SubElement(link, "propeller_speed").text = str(propeller_speed)

# Добавление всех links с физическими параметрами
add_link("base_link", 
          {"type": "mesh", "filename": "C:/Users/user/ardupilot/Tools/gazebo/models/quadcopter_X/quadcopter_X.stl"}, 
          mass=1.5)

propeller_geometry = {"type": "cylinder", "radius": "1.5", "length": "10"}
material_black = {"name": "black", "rgba": "0 0 0 1"}

# Переменные для изменения скорости вращения пропеллеров, скорости взлета и высоты взлета
propeller_speed_value = 1900  # об/мин
takeoff_speed_value = 3  # м/с
max_flight_height = 80  # м

for i in range(1, 5):
    add_link(f"propeller{i}", propeller_geometry, material_black, mass=0.2, inertia=[0.01]*6, propeller_speed=propeller_speed_value)

flight_controller_geometry = {"type": "box", "size": "10 10 2"}
material_blue = {"name": "blue", "rgba": "0 0 1 1"}
add_link("flight_controller", flight_controller_geometry, material_blue, mass=0.3)

# Добавление других компонентов
mpu6050_sensor = {"name": "mpu6050_sensor", "type": "IMU", "update_rate": 100}
add_link("mpu6050", {"type": "box", "size": "2 2 1"}, {"name": "red", "rgba": "1 0 0 1"}, mpu6050_sensor)

bmp180_sensor = {"name": "bmp180_sensor", "type": "Barometer", "update_rate": 50}
add_link("bmp180", {"type": "box", "size": "2 2 1"}, {"name": "green", "rgba": "0 1 0 1"}, bmp180_sensor)

gps_sensor = {"name": "gps_sensor", "type": "GPS", "update_rate": 1}
add_link("gps_module", {"type": "box", "size": "2 2 1"}, {"name": "yellow", "rgba": "1 1 0 1"}, gps_sensor)

add_link("bluetooth_module", {"type": "box", "size": "2 2 1"}, {"name": "purple", "rgba": "0.5 0 0.5 1"})

# Функция для добавления joint
def add_joint(name, parent, child, origin):
    joint = ET.SubElement(robot, "joint", name=name, type="fixed")
    ET.SubElement(joint, "parent", link=parent)
    ET.SubElement(joint, "child", link=child)
    ET.SubElement(joint, "origin", rpy="0 0 0", xyz=origin)

# Добавление всех joints
add_joint("base_to_propeller1", "base_link", "propeller1", "-25 0 2.5")
add_joint("base_to_propeller2", "base_link", "propeller2", "25 0 2.5")
add_joint("base_to_propeller3", "base_link", "propeller3", "0 -25 2.5")
add_joint("base_to_propeller4", "base_link", "propeller4", "0 25 2.5")
add_joint("base_to_flight_controller", "base_link", "flight_controller", "0 0 6")
add_joint("controller_to_mpu6050", "flight_controller", "mpu6050", "3 0 1")
add_joint("controller_to_bmp180", "flight_controller", "bmp180", "-3 0 1")
add_joint("controller_to_gps", "flight_controller", "gps_module", "0 3 1")
add_joint("controller_to_bluetooth", "flight_controller", "bluetooth_module", "0 -3 1")

# PID-регулирование для управления скоростью вращения пропеллеров и высотой
propeller_pid = PID(1.0, 0.1, 0.05, propeller_speed_value)
height_pid = PID(1.0, 0.1, 0.05, max_flight_height)

# Списки для хранения значений для графиков
propeller_speed_history = []
desired_propeller_speed_history = []
height_history = []
desired_height_history = []

# Симуляция регулирования
for _ in range(20):  # Симуляция 20 итераций
    # Симуляция значений от сенсоров
    current_propeller_speed = random.uniform(1800, 2300)  # случайная скорость пропеллеров
    current_height = random.uniform(60, 100)  # случайная высота

    # Обновляем PID-регуляторы
    new_propeller_speed = propeller_pid.update(current_propeller_speed)
    new_height = height_pid.update(current_height)

    # Сохраняем значения для графиков
    propeller_speed_history.append(current_propeller_speed)
    desired_propeller_speed_history.append(new_propeller_speed)
    height_history.append(current_height)
    desired_height_history.append(new_height)

    print(f"Current Propeller Speed: {current_propeller_speed:.2f}, New Desired Speed: {new_propeller_speed:.2f}")
    print(f"Current Height: {current_height:.2f}, New Desired Height: {new_height:.2f}")
    time.sleep(0.5)  # Задержка для имитации времени между измерениями

# Построение и сохранение графиков
plt.figure(figsize=(12, 6))

# График скорости пропеллеров
plt.subplot(2, 1, 1)
plt.plot(propeller_speed_history, label='Такущая скорость вращения', color='b')
plt.plot(desired_propeller_speed_history, label='Рекомендуемая скорость вращения', color='r', linestyle='--')
plt.title('Скорость вращения')
plt.xlabel('Время (s)')
plt.ylabel('Скорость (RPM)')
plt.legend()
plt.grid()

# График высоты
plt.subplot(2, 1, 2)
plt.plot(height_history, label='Текущая высота', color='g', linestyle='-.')
plt.plot(desired_height_history, label='Рекомендуемая высота', color='orange', linestyle='--')
plt.title('Высота')
plt.xlabel('Время (s)')
plt.ylabel('Высота (m)')
plt.legend()
plt.grid()

# Сохранение графиков в файл
plt.tight_layout()
plt.savefig('quadcopter_control_analysis.png')
plt.close()