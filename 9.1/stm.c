
int main(void)
{
/* USER CODE BEGIN 2 */
while (1)
{
  HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
  HAL_Delay(500);
}
/* USER CODE END 2 */
}


