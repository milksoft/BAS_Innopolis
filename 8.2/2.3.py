import time
def convert_to_decimal(degree_str, direction):
    """Преобразует строку с градусами в десятичный формат.""" 
    # Преобразуем строку в float
    degree_value = float(degree_str)
    degrees = int(degree_value // 100)
    minutes = degree_value % 100 
    decimal = degrees + (minutes / 60.0) 
    if direction in ['S', 'W']:
        decimal *= -1 
    return decimal
def data_gps(gps_data): 
    """Обработка данных с GPS.
Args:
gps_data: Строка данных в формате NMEA.

Returns:
Словарь с обработанными данными:
    • latitude: Широта (градусы).
    • longitude: Долгота (градусы).
    • altitude: Высота (метры).
    • speed: Скорость (м/с).
    • timestamp: Время (секунды). """
    try:
        # Разделение строки NMEA по запятым 
        data_parts = gps_data.split(",")
        # Проверка на формат GGA
        if data_parts[0] == "$GPGGA":
             # Обработка данных GGA 
             timestamp_str = data_parts[1]
             # Время фиксируется 
             latitude = convert_to_decimal(data_parts[2], data_parts[3]) 
             longitude = convert_to_decimal(data_parts[4], data_parts[5]) 
             altitude = float(data_parts[9])
             speed = None # Скорость не доступна в GGA

            # Форматирование даты для mktime
            # Текущая дата, чтобы использовать её вместе со временем 
             current_time = time.localtime()
             current_date = time.strftime("%Y,%m,%d", current_time).split(',')
             year, month, day = int(current_date[0]), int(current_date[1]), int(current_date[2])
             timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}", "%H%M%S.%f,%Y,%m,%d") 
             timestamp_seconds = time.mktime(timestamp)

             # Проверка на формат RMC для извлечения скорости
        elif data_parts[0] == "$GPRMC":
             timestamp_str = data_parts[1]
             latitude = convert_to_decimal(data_parts[3], data_parts[4]) 
             longitude = convert_to_decimal(data_parts[5], data_parts[6])
             speed = float(data_parts[7]) * 0.514444 # Преобразование узлов в м/с 
             altitude = None # Высота недоступна в RMC
             # Форматирование даты для mktime 
             current_time = time.localtime()
             current_date = time.strftime("%Y,%m,%d", current_time).split(',')
             year, month, day = int(current_date[0]), int(current_date[1]), int(current_date[2])

             # Преобразование времени
             timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}", "%H%M%S.%f,%Y,%m,%d")
             timestamp_seconds = time.mktime(timestamp)

        else:
             raise ValueError("Неизвестный формат NMEA")

        # Возвращение обработанных данных 
        return {
                "latitude": latitude, 
                "longitude": longitude,
                "altitude": altitude, 
                "speed": speed,
                "timestamp": timestamp_seconds
                }
    
    except Exception as e:
        print("Ошибка при обработке данных GPS:", e) 
        return None
    
    # Реализация алгоритма
gps_data_gga = "$GPGGA,123519.487,3754.587,N,14507.036,W,1,08,0.9,545.4,M,46.9,M,,*47" 
gps_data_rmc = "$GPRMC,123519.487,A,3754.587,N,14507.036,W,000.0,360.0,120419,,,D"

data_gps_gga = data_gps(gps_data_gga) 
data_gps_rmc = data_gps(gps_data_rmc)
for data_source, data_gps_obj in zip(["GGA", "RMC"], [data_gps_gga, data_gps_rmc]):
    if data_gps_obj:
        print(f"Обработанные данные из {data_source}:")
        print(f"Широта: {data_gps_obj['latitude']}") 
        print(f"Долгота: {data_gps_obj['longitude']}")
        print(f"Высота: {data_gps_obj['altitude']}") 
        print(f"Скорость: {data_gps_obj['speed']}")
        print(f"Время: {data_gps_obj['timestamp']}")
    else:
        print(f"Некорректные данные GPS из {data_source}.")


