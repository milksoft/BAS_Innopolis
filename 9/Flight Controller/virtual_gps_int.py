from pymavlink import mavutil
import time

# Подключаемся к виртуальному полетному контроллеру
connection_string = 'udp:127.0.0.1:14552'
master = mavutil.mavlink_connection(connection_string)

# Ожидаем получения первого heartbeat
print("Подключение к полетному контроллеру...")
master.wait_heartbeat()
print("Подключено!")

# Описание GPS данных с заданными координатами
gps_data = {
    'lat': 53.059993,  # Широта
    'lon': 63.206572,  # Долгота
    'alt': 0,           # Высота в метрах
    'fix_type': 3       # 3 — трехмерная фиксация
}

# Функция для отправки GPS данных
def send_gps_data():
    # Отправка данных GPS в формате MAVLink
    master.mav.send(mavutil.mavlink.MAVLink_gps_raw_int_message(
        0,                             # Время с момента запуска (мс)
        gps_data['fix_type'],         # Тип фиксации
        int(gps_data['lat'] * 1e7),   # Широта
        int(gps_data['lon'] * 1e7),   # Долгота
        int(gps_data['alt'] * 1000),  # Высота (миллиметры)
        0,                             # Горизонтальная точность (мм)
        0,                             # Вертикальная точность (мм)
        0,                             # Количество видимых спутников
        0                              # Статус DGPS
    ))
    print(f"Отправлены данные GPS: {gps_data}")

# Основной цикл отправки данных GPS
try:
    while True:
        send_gps_data()  # Отправляем GPS данные
        time.sleep(1)    # Отправляем данные каждые 1 секунду
except KeyboardInterrupt:
    print("Остановка интеграции GPS...")
finally:
    master.close()