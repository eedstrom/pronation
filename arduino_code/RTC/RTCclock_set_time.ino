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
