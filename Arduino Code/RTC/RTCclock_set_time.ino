#include<Wire.h> //communicate between different I2C devices
#include <RTC.h> //allows you to get a clock after setting the initial conditions

static DS3231 RTC; //static so data is preserved
void setup() {

Serial.begin(9600);  //defines baud rate
RTC.begin();

RTC.setDay(5);
//RTC.setMonth(2);
RTC.setHours(15);
RTC.setMinutes(43);
RTC.setSeconds(00);
RTC.setYear(2021);
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

delay(1000);
}
