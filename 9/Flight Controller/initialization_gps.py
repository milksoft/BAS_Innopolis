from pymavlink import mavutil
import time

# Подключаемся к виртуальному полетному контроллеру
# Необходимо заменить 'tcp:127.0.0.1:14552' на свой адрес и порт
connection_string = 'tcp:127.0.0.1:14552'
master = mavutil.mavlink_connection(connection_string)

# Ожидание первого heartbeat
master.wait_heartbeat()
print("Подключено к полетному контроллеру")

# Инициализация GPS
# Необходимо убедиться, что виртуальный контроллер поддерживает включение GPS
# Отправляются GPS данные
gps_data = {
    'lat': 53.059993,  # Необходимо заменить на свою широту
    'lon': 63.206572,   # Необходимо заменить на свою долготу
    'alt': 0,      # Необходимо заменить на свою высоту
    'fix_type': 3      # 3 — трехмерная фиксация
}

# Отправка GPS данных в контроллер
def send_gps_data():
    master.mav.send(mavutil.mavlink.MAVLink_gps_raw_int_message(
        0,               # Time since boot (ms)
        gps_data['fix_type'],  # Fix type
        int(gps_data['lat'] * 1e7),  # Latitude
        int(gps_data['lon'] * 1e7),   # Longitude
        int(gps_data['alt'] * 1000),   # Altitude (millimeters)
        0,               # GPS horizontal accuracy (mm)
        0,               # GPS vertical accuracy (mm)
        0,               # GPS satellites visible
        0                # DGPS status
    ))

# Основной цикл
try:
    while True:
        send_gps_data()
        print(f"Отправлены данные GPS: {gps_data}")
        time.sleep(1)  # Отправляем данные каждые 1 секунду
except KeyboardInterrupt:
    print("Остановка...")
finally:
    master.close()