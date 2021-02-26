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


#include <Wire.h>
#include <SPI.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h> 
#include <RTC.h>
#include <LiquidCrystal.h>
#include "SdFat.h"

Adafruit_LSM9DS1 lsm = Adafruit_LSM9DS1();

#define LSM9DS1_SCK A5
#define LSM9DS1_MISO 12
#define LSM9DS1_MOSI A4
#define LSM9DS1_XGCS 6
#define LSM9DS1_MCS 5
#define SD_CS_PIN SS

static DS3231 RTC;
const int rs = 12, en = 11, d4 = 36, d5 = 34, d6 = 32, d7 = 30;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
SdFat SD;
File myFile;
char filename[ ] = "gyrortcdata.txt";

void setupSensor()
{
  // 1.) Set the accelerometer range
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_4G);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_8G);
  //lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_16G);
  
  // 2.) Set the magnetometer sensitivity
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_8GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_12GAUSS);
  //lsm.setupMag(lsm.LSM9DS1_MAGGAIN_16GAUSS);

  // 3.) Setup the gyroscope
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
  //lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_500DPS);
  //lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_2000DPS);
}


void setup() 
{
  Serial.begin(9600);

 RTC.begin();
 RTC.setHours(0);
 RTC.setMinutes(00);
 RTC.setSeconds(00);
  lcd.begin(16, 2);


  while (!Serial) {
    delay(1); // will pause Zero, etc until serial console opens
  }


  Serial.print("Initializing SD card reading software... ");
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD initialization failed!");
    delay(100);
    exit(0);
  }
    
  Serial.println("LSM9DS1 data read demo");
  
  // Try to initialise and warn if we couldn't detect the chip
  if (!lsm.begin())
  {
    Serial.println("Oops ... unable to initialize the LSM9DS1. Check your wiring!");
    while (1);
  }
  Serial.println("Found LSM9DS1 9DOF");

  // helper to just set the default scaling we want, see above!
  setupSensor();
}

void loop() 
{
   myFile = SD.open(filename, FILE_WRITE);
  if (myFile) {
    Serial.print("Writing to "); Serial.print(filename); Serial.println("...");    

 //int lines_to_write=100;
 //for (int file_line = 0; file_line < lines_to_write; file_line++)
 //{
  lsm.read();  
 
  sensors_event_t a, m, g, temp;

  lsm.getEvent(&a, &m, &g, &temp); 
  
  lcd.setCursor(0, 0);
  lcd.print(RTC.getHours());
  lcd.print(":");
  lcd.print(RTC.getMinutes());
  lcd.print(":");
  lcd.print(RTC.getSeconds());
  Serial.print("\n");
 
  lcd.print("\tX:"); lcd.print(a.acceleration.x); //Serial.print(" m/s^2");
  
  lcd.setCursor(0, 1);
  lcd.print("\tY:"); lcd.print(a.acceleration.y);    // Serial.print(" m/s^2 ");
  lcd.print("\tZ:"); lcd.print(a.acceleration.z);    // Serial.println(" m/s^2 ");

  
  myFile.print("X, Y, Z, t: "); myFile.print(g.gyro.x);
  myFile.print(" "); myFile.print(g.gyro.y); myFile.print(" "); myFile.print(g.gyro.z); myFile.print(" "); 
  myFile.print(RTC.getMinutes()); myFile.print(":"); myFile.print(RTC.getSeconds()); myFile.print("\n");
 

  Serial.print(RTC.getMinutes()); Serial.print(":"); Serial.print(RTC.getSeconds());
  Serial.print("\nGyro X: "); Serial.print(g.gyro.x);   Serial.print(" rad/s");
  Serial.print("\tY: "); Serial.print(g.gyro.y);      Serial.print(" rad/s");
  Serial.print("\tZ: "); Serial.print(g.gyro.z);      Serial.println(" rad/s");

  Serial.println();
  delay(1000);
  myFile.close();
  //}
  }
  
}
