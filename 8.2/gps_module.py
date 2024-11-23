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
    try:
# Разделение строки NMEA по запятым 
        data_parts = gps_data.split(",")

# Проверка на формат GGA
        if data_parts[0] == "$GPGGA":
            timestamp_str = data_parts[1] # Время фиксируется 
            latitude = convert_to_decimal(data_parts[2], data_parts[3])
            longitude = convert_to_decimal(data_parts[4], data_parts[5]) 
            altitude = float(data_parts[9])
            speed = None # Скорость не доступна в GGA
            
            # Форматирование даты для mktime 
            current_time = time.localtime()
            year, month, day = current_time.tm_year, current_time.tm_mon, current_time.tm_mday 
            timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}","%H%M%S.%f,%Y,%m,%d")
            timestamp_seconds = time.mktime(timestamp)
        elif data_parts[0] == "$GPRMC": 
            timestamp_str = data_parts[1]
            latitude = convert_to_decimal(data_parts[3], data_parts[4]) 
            longitude = convert_to_decimal(data_parts[5], data_parts[6])
            speed = float(data_parts[7]) * 0.514444 # Преобразуем узлы в м/с
            altitude = None # Высота недоступна в RMC

            # Форматирование даты для mktime
            current_time = time.localtime()
            year, month, day = current_time.tm_year, current_time.tm_mon, current_time.tm_mday
            timestamp = time.strptime(f"{timestamp_str},{year},{month},{day}",
            "%H%M%S.%f,%Y,%m,%d")
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
        
        
        