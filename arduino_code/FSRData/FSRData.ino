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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


   Writes data from accelerometer and gyroscope to a file on an SD card
 * The file format is a csv with the following columns:
 * FSR (0-3), time_taken, uncertainty_in_time, conductance
 * 
 * First row contains the Sample Rate for each accelerometer for both acceleration and gyroscope in the form:
 * Sample Rate Identifyer (-1), acceleration sample rate channel 0, acceleration sample rate channel 1, acceleration sample rate channel 2,
 ** gyroscope sample rate channel 0, gyroscope sample rate channel 1, gyroscope sample rate channel 2,
 ** magnetic field sample rate channel 0, magnetic field sample rate channel 1, magnetic field sample rate channel 2
 */

#include <Arduino_LSM9DS1.h>
#include <Wire.h>
#include <SD.h>
#include <SPI.h>
#include <LiquidCrystal.h>
#include <Keypad.h>
#include "RTClib.h"

// Constants //

// Put this as the CS pin
const int chipSelect = 53;

// Declare RTC
RTC_DS3231 rtc;         
DateTime now;

// File name to be written to
const char* FILENAME = "rest.csv";

// File object
File datafile;

// Counter
uint8_t n_run = 0;

// Number of iterations in between writes
uint8_t n_iter = 100;

// Variables //
uint8_t channel;
float ax, ay, az;
float g1, g2, g3;
float m1, m2, m3;
float m[9] = { 0, 0, 0, 0, 0, 0 ,0, 0, 0 };
uint32_t t, dt;
int fsr_idx[4] = { 3, 4, 5, 6 };

#define number_of_FSRs 4 // ADC channels used are 0 - 3, living in pins A0 - A3.
#define R_series 10000 // series resistor in the circuit
int FSR_pin[number_of_FSRs] = {A0, A1, A2, A3};
#define ADC_V_ref 5.0 // ADC reference voltage
#define ADC_max 1023 // ADC max value

char key;
boolean keyPressed = false;
boolean flag = true;
const int ROW_NUM = 4; //four rows
const int COLUMN_NUM = 3; //three columns
byte pin_rows[ROW_NUM] = {31, 33, 35, 37}; //connect to the row pinouts of the keypad
byte pin_column[COLUMN_NUM] = {2, 3, 18}; //connect to the column pinouts of the keypad
char keys[ROW_NUM][COLUMN_NUM] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};
Keypad keypad = Keypad( makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM );

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 12, en = 11, d4 = 36, d5 = 34, d6 = 32, d7 = 30;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Helper Functions //

// Function to change bus
void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

// Arduino Functions //

void setup() {
  
  // Set up and check RTC
  int return_code = rtc.begin();
  
  if(!return_code) {
    Serial.println("RTC doesn't work.");
    while (1) {};
  }

  // LED lights to arduino pins 4, 5, 6
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  
  // Set up the LCD's number of columns and rows
  lcd.begin(16, 2);
  
  // Initialize for each channel
  for (channel = 0; channel < 3; ++channel) {
    // Set to channel 0, 1, 2
    TCA9548A(channel);

    // Initialize
    Wire.begin();
    IMU.begin();
  }
  
  // For printing
    Serial.begin(9600);
    while (!Serial);

  // Make sure the sd card is present
  if (!SD.begin(chipSelect)) {
    Serial.println("SD Card not present or wiring issue");
    // Halt operations
    while (1);
  }

  // Open the file
  datafile = SD.open(FILENAME, FILE_WRITE);

  // Get the sample rate
  uint8_t sr_a0, sr_a1, sr_a2,
          sr_g0, sr_g1, sr_g2,
          sr_m0, sr_m1, sr_m2;
          

  // Get for channel 0
  TCA9548A(0);
  sr_a0 = (uint8_t) IMU.accelerationSampleRate();
  sr_g0 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m0 = (uint8_t) IMU.magneticFieldSampleRate();

  // Get for channel 1
  TCA9548A(1);
  sr_a1 = (uint8_t) IMU.accelerationSampleRate();
  sr_g1 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m1 = (uint8_t) IMU.magneticFieldSampleRate();

  // Get for channel 2
  TCA9548A(2);
  sr_a2 = (uint8_t) IMU.accelerationSampleRate();
  sr_g2 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m2 = (uint8_t) IMU.magneticFieldSampleRate();

  // Test if LED is blinking
  digitalWrite(4, HIGH);      
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  delay(2000);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
  digitalWrite(6, LOW);

  // Write to the file
  datafile.print(-1);
  datafile.print(",");
  datafile.print(sr_a0); // in Hz
  datafile.print(",");
  datafile.print(sr_a1); // in Hz
  datafile.print(",");
  datafile.print(sr_a2); // in Hz
  datafile.print(",");
  datafile.print(sr_g0); // in Hz
  datafile.print(",");
  datafile.print(sr_g1); // in Hz
  datafile.print(",");
  datafile.print(sr_g2); // in Hz
  datafile.print(",");
  datafile.print(sr_m0); // in Hz
  datafile.print(",");
  datafile.print(sr_m1); // in Hz
  datafile.print(",");
  datafile.print(sr_m2); // in Hz
  datafile.print(",");
  now = rtc.now();
  datafile.print(now.hour()-6, DEC);      //subtract 6 to get central time, or get UTC w/out it
  datafile.print(':');
  if(now.minute() < 10)  datafile.print(0);
  datafile.print(now.minute(), DEC);
  datafile.print(':');
  if(now.second() < 10)  datafile.print(0);
  datafile.println(now.second(), DEC);

  lcd.setCursor(0, 0);
  lcd.print("* key to start");
}

void loop() {
  now = rtc.now();
  
  // Stop grabbing data if the flag is up (# key pressed)
  // Also turn off LEDs
  if (!flag) {
    digitalWrite(4, LOW);      
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);    
    exit(0);
  }

  // Start grabbing data after * key is pressed
  while (keyPressed == false) {
    key = keypad.getKey();
    
    if (key == '*') {
      keyPressed = true;

      lcd.clear();
      lcd.print("Grabbing data...");
      lcd.setCursor(0, 1);
      lcd.print("# key to stop");
      
      break;
    }
  }
  
  // Check if we have run the course
  if (n_run >= n_iter) {
    // Close the file (save)
    datafile.close();

    // Reset the counter to 0
    n_run = 0;
    
    // Reopen the file
    datafile = SD.open(FILENAME, FILE_WRITE);
  }

  /*
  // Read for each channel
  for (channel = 0; channel < 3; ++channel) {
    // Change channel
    TCA9548A(channel);

    // Blinking the 3 LEDs every second
    if (now.second() % 2 == 0) {
      digitalWrite(4, HIGH);      
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
    } else {
      digitalWrite(4, LOW);      
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
    }

    //digitalWrite(4, (millis() / 1000) % 2);

    // Get the time where data is collected first
    t = millis();
    
    // Get the acceleration
    while(!IMU.accelerationAvailable()) {}
    IMU.readAcceleration(ax, ay, az);

    // Get the gyroscope
    while(!IMU.gyroscopeAvailable()) {}
    IMU.readGyroscope(g1, g2, g3);

    // Get the magnetic field if possible
    // Otherwise writes the previous values from the same line
    if(IMU.magneticFieldAvailable()) {
      IMU.readMagneticField(m1, m2, m3);
      m[3 * channel + 0] = m1;
      m[3 * channel + 1] = m2;
      m[3 * channel + 2] = m3;
    }
    
    // Get the time taken to collect all data
    dt = millis() - t;
    
    // Write to a file
    datafile.print(channel);
    datafile.print(",");   
    datafile.print(t);
    datafile.print(",");
    datafile.print(dt);    
    datafile.print(",");
    datafile.print(ax * 1000); // in mG
    datafile.print(",");
    datafile.print(ay * 1000); // in mG
    datafile.print(",");
    datafile.print(az * 1000); // in mG
    datafile.print(",");
    datafile.print(g1 * 10); // in d(dps)
    datafile.print(",");
    datafile.print(g2 * 10); // in d(dps)
    datafile.print(",");
    datafile.print(g3 * 10); // in d(dps)
    datafile.print(","); 
    datafile.print(m[3 * channel + 0]); // in microT
    datafile.print(",");
    datafile.print(m[3 * channel + 1]); // in microT
    datafile.print(",");
    datafile.println(m[3 * channel + 2]); // in microT
  }
  */

  // Read for each FSR
  for(int i = 0; i < number_of_FSRs; i++)
  {
    // Get the time where data is collected first
    t = millis();
    
    int ADC_value = analogRead(FSR_pin[i]);

    float voltage = ADC_V_ref * float(ADC_value) / (ADC_max + 1);

    double FSR_resistance;
    double FSR_conductance;

    // see Gollin's notebook, p. 16 for the calculation.
    if(ADC_value > 0)
    {
      FSR_resistance = (ADC_V_ref / voltage - 1.0) * R_series;
      FSR_conductance = 1.0 / FSR_resistance;
    } else {
      // a billion ohms
      FSR_resistance = 1.e9;
      FSR_conductance = 0.;
    }

    // Get the time taken to collect all data
    dt = millis() - t;
    
    // Write to a file
    datafile.print(i); // Current FSR, e.g. FSR0 = 0
    datafile.print(",");
    datafile.print(t);
    datafile.print(",");
    datafile.print(dt);    
    datafile.print(",");
    datafile.println(1.e6 * FSR_conductance, 6); // in micro-mhos
  }

  // Stop collecting data if # key is pressed
  key = keypad.getKey();
  if (key == '#') {
    lcd.clear();
    lcd.print("Stopping...");
    flag = false;
  }
  
  // Increment iterator
  n_run = n_run + 1;
}
