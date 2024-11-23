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