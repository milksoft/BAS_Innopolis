from pymavlink import mavutil
import time

# Подключаемся к виртуальному полетному контроллеру
connection_string = 'udp:127.0.0.1:14552'
master = mavutil.mavlink_connection(connection_string)

# Ждем, пока не получим первый heartbeat
print("Подключение к полетному контроллеру...")
master.wait_heartbeat()
print("Подключено!")

# GPS данные (обновленные)
gps_data = {
    'lat': 53.059993,  # Замените на свою широту
    'lon': 63.206572,   # Замените на свою долготу
    'alt': 0,           # Замените на свою высоту
    'fix_type': 3       # 3 — трехмерная фиксация
}

# Функция для отправки GPS данных
def send_gps_data():
    master.mav.send(mavutil.mavlink.MAVLink_gps_raw_int_message(
        0,                     # Время с момента запуска (мс)
        gps_data['fix_type'],  # Тип фиксации
        int(gps_data['lat'] * 1e7),  # Широта
        int(gps_data['lon'] * 1e7),   # Долгота
        int(gps_data['alt'] * 1000),   # Высота (миллиметры)
        0,                      # Горизонтальная точность (мм)
        0,                      # Вертикальная точность (мм)
        0,                      # Количество видимых спутников
        0                       # Статус DGPS
    ))
    print(f"Отправлены данные GPS: {gps_data}")

# Функция для отправки команды взлета
def arm_and_takeoff(aTargetAltitude):
    print("Запускаем...")
    master.arducopter_arm()  # Разблокировка (армер)
    print("Дрон разблокирован (армер).")
    time.sleep(5)  # Ждем, пока дрон не разблокируется (армится)

    # Запускаем взлет
    master.mav.command_long_send(
        master.target_system,     # ID системы
        master.target_component,  # ID компонента
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # Команда взлета
        0,                         # Подтверждение
        0,                         # Не используется
        0,                         # Широта взлета (автоматически)
        0,                         # Долгота взлета (автоматически)
        aTargetAltitude,          # Целевая высота
        0, 0, 0, 0               # Не используется
    )
    print(f"Взлетаем на высоту {aTargetAltitude} метров.")

# Основная программа
if __name__ == "__main__":
    # Отправляем начальные GPS данные
    send_gps_data()
    arm_and_takeoff(10)  # Взлет на 10 метров
    print("Взлет завершён.")