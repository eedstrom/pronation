/* Pronation Program
Copyright (C) 2021 Dominic Culotta, Eric Edstrom, Jae Young Lee, Teagan Mathur, Brian Petro, Wilma Rishko, Ruizhi Wang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.*/


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
