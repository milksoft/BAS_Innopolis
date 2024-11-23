import numpy as np
import pytest
from drone_accelerometer import data_acs

# Константы для теста
MAX_PAYLOAD = 1500  

def test_data_processing():
    accel_data = [[2, 2, 2], [5, 5, 5], [8, 8, 8]]
    weight = 1200  
    flight_time = 1600  
    control_distance = 800  

    result = data_acs(accel_data, weight, flight_time, control_distance)

    assert np.isclose(result['acceleration'][0], 2.0, atol=1e-2)
    assert np.isclose(result['acceleration'][1], 5.0, atol=1e-2)
    assert np.isclose(result['acceleration'][2], 8.0, atol=1e-2)
    assert np.isclose(result['inclination'][0], 11.969, atol=1e-2)
    assert np.isclose(result['inclination'][1], 31.230, atol=1e-2)

def test_exceed_payload():
    accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    weight = 1600  # Превышение максимальной массы
    flight_time = 10
    control_distance = 500

    with pytest.raises(ValueError, match="Превышена максимальная взлетная масса БЛА."):
        data_acs(accel_data, weight, flight_time, control_distance)

def test_exceed_flight_time():
    accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    weight = 1200  
    flight_time = 4000  # Превышение максимального времени полета
    control_distance = 500  

    with pytest.raises(ValueError, match="Превышено максимальное время полета."):
        data_acs(accel_data, weight, flight_time, control_distance)

def test_exceed_control_distance():
    accel_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    weight = 1200  
    flight_time = 10  
    control_distance = 1500  # Превышение максимальной дальности управления

    with pytest.raises(ValueError, match="Превышена максимальная дальность управления."):
        data_acs(accel_data, weight, flight_time, control_distance)

if __name__ == "__main__":
    pytest.main()