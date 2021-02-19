#include<Wire.h> //communicate between different I2C devices
#include <RTC.h> //allows you to get a clock after setting the initial conditions
#include <LiquidCrystal.h>

static DS3231 RTC; //static so data is preserved
const int rs = 12, en = 11, d4 = 36, d5 = 34, d6 = 32, d7 = 30;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


void setup() {

Serial.begin(9600);  //defines baud rate
RTC.begin();
lcd.begin(16, 2);

}

void loop() {

Serial.print(RTC.getMonth());
Serial.print("-");
Serial.print(RTC.getDay());
Serial.print("-");
Serial.print(RTC.getYear());
Serial.print(" ");

Serial.print(RTC.getHours());
Serial.print(":");
Serial.print(RTC.getMinutes());
Serial.print(":");
Serial.print(RTC.getSeconds());
Serial.print("\n");

lcd.setCursor(0, 0);
lcd.print(RTC.getHours());
lcd.print(":");
lcd.print(RTC.getMinutes());
lcd.print(":");
lcd.print(RTC.getSeconds());

delay(1000);
}
