##STM.C
Реализация для STM32 с FreeRTOS
Инструменты
STM32F103C8T6 (Blue Pill), STM32CubeIDE, FreeRTOS
Шаги разработки
    1. Создание нового проекта в STM32CubeIDE.
    2. Настройка тактирования и выводов для светодиодов.
    3. Включение поддержки FreeRTOS через CubeMX.
    4. Создание двух задач с разными приоритетами и периодами.
    5. Код:
void StartTask1(void *argument)
{
   while(TRUE) 
   {
      HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); // Светодиод 1
      vTaskDelay(500 / portTICK_PERIOD_MS);
   }
}

void StartTask2(void *argument) 
{
  while(TRUE)  
  {
      HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_14); // Светодиод 2
      vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

    1. Компиляция и прошивка проекта на плату.
    2. Отладка и проверка работы.


Реализация для ESP32 с ESP-IDF (FreeRTOS)
Инструменты
ESP32 DevKitC, Visual Studio Code с расширением ESP-IDF, FreeRTOS в ESP-IDF
Шаги разработки
    1. Установка ESP-IDF и настройка среды.
    2. Создание нового проекта на основе шаблона.
    3. Настройка выводов для светодиодов.
    4. Создание двух задач с разными приоритетами и периодами.
    


    1. Компиляция и прошивка проекта на плату.
    2. Отладка и проверка работы.
…