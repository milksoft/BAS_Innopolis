import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Используйте бэкенд без GUI
import matplotlib.pyplot as plt
import re

# Функция для чтения данных из файла
def read_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read().strip()
    return data

# Укажите путь к вашему файлу analyze.txt
file_path = 'analyze.txt'

# Чтение данных из файла
data = read_data(file_path)

# Разделение данных на строки
lines = data.split('\n')

# Списки для каждого типа данных
imu_list = []
barometer_list = []
gps_list = []

# Обработка строк данных
for line in lines:
    if "IMU Data" in line:
        imu_data = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        if len(imu_data) >= 7:
            imu_list.append([float(imu_data[i]) for i in range(6)] + [float(imu_data[6])])
    elif "Barometer Data" in line:
        barometer_data = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        if len(barometer_data) == 2:
            barometer_list.append([float(i) for i in barometer_data])
    elif "GPS Data" in line:
        gps_data = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        gps_list.append([float(i) for i in gps_data])  # Собираем данные GPS

# Создание DataFrame из собранных данных
imu_df = pd.DataFrame(imu_list, columns=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'temperature'])
barometer_df = pd.DataFrame(barometer_list, columns=['pressure', 'temp'])
gps_df = pd.DataFrame(gps_list, columns=['latitude', 'longitude', 'altitude'])

# Функция анализа и сохранения IMU данных
def analyze_imu_data(df):
    plt.figure(figsize=(14, 4))
    
    plt.subplot(1, 3, 1)
    plt.plot(df['acc_x'], label='Acceleration X')
    plt.plot(df['acc_y'], label='Acceleration Y')
    plt.plot(df['acc_z'], label='Acceleration Z')
    plt.title('IMU Acceleration')
    plt.xlabel('Sample Number')
    plt.ylabel('Acceleration (m/s²)')
    plt.legend()
    plt.grid()
    
    plt.subplot(1, 3, 2)
    plt.plot(df['gyro_x'], label='Gyro X', color='r')
    plt.plot(df['gyro_y'], label='Gyro Y', color='g')
    plt.plot(df['gyro_z'], label='Gyro Z', color='b')
    plt.title('IMU Gyroscope')
    plt.xlabel('Sample Number')
    plt.ylabel('Gyroscope (°/s)')
    plt.legend()
    plt.grid()
    
    plt.subplot(1, 3, 3)
    plt.plot(df['temperature'], label='Temperature', color='purple')
    plt.title('IMU Temperature')
    plt.xlabel('Sample Number')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('imu_data_analysis.png')  # Сохранить график в файл
    plt.close()  # Закрыть текущую фигуру, чтобы освободить память

# Функция анализа и сохранения данных барометра
def analyze_barometer_data(df):
    plt.figure(figsize=(7, 4))
    
    plt.plot(df['pressure'], label='Pressure', color='blue')
    plt.plot(df['temp'], label='Temperature', color='red')
    plt.title('Barometer Data')
    plt.xlabel('Sample Number')
    plt.ylabel('Pressure (hPa) / Temperature (°C)')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('barometer_data_analysis.png')  # Сохранить график в файл
    plt.close()  # Закрыть текущую фигуру

# Функция анализа и сохранения GPS данных
def analyze_gps_data(df):
    plt.figure(figsize=(7, 4))
    
    plt.plot(df['latitude'], label='Latitude', color='green')
    plt.plot(df['longitude'], label='Longitude', color='orange')
    plt.plot(df['altitude'], label='Altitude', color='purple')
    plt.title('GPS Data')
    plt.xlabel('Sample Number')
    plt.ylabel('GPS Coordinates / Altitude')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('gps_data_analysis.png')  # Сохранить график в файл
    plt.close()  # Закрыть текущую фигуру

# Выполнение анализа данных
try:
    analyze_imu_data(imu_df)
    analyze_barometer_data(barometer_df)
    analyze_gps_data(gps_df)
except Exception as e:
    print(f"An error occurred during analysis: {e}")