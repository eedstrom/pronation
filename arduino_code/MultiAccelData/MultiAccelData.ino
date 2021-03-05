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
 * LSM9 bus (0-2), acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z,
 *                 magnetic_field_x, magnetic_field_y, magnetic_field_z
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

// Constants //

// Put this as the CS pin
const int chipSelect = 53;

// File name to be written to
const char* FILENAME = "noprint.csv";

// File object
File datafile;

// Counter
uint16_t n_run = 0;

// Max number of iterations
uint16_t n_max = 1000;


// Helper Functions //

// Function to change bus
void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

//// Function to calculate pitch
//float calcPitch(float ax, float ay, float az)
//{
//  return atan2(ax, sqrt(ay * ay) + (az * az)) * 180.0 / M_PI;
//}
//
//// Function to calculate roll
//float calcRoll(float ax, float ay, float az)
//{
//  return atan2(ay, sqrt(ax * ax) + (az * az)) * 180.0 / M_PI;
//}

// Arduino Functions //

void setup() {
  // Initialize for each channel
  for (uint8_t channel = 0; channel < 3; ++channel) {
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

  // Write to the file
  datafile.print(millis());
  datafile.print(",");
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
  datafile.println(sr_m2); // in Hz

  
  // Print sample rate info
//  Serial.print(-1);
//  Serial.print('\t');
//  Serial.print(sr_a0); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_a1); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_a2); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_g0); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_g1); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_g2); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_m0); // in Hz
//  Serial.print('\t');
//  Serial.print(sr_m1); // in Hz
//  Serial.print('\t');
//  Serial.println(sr_m2); // in Hz
}

void loop() {
  // Check if we have run the course
  if (n_run >= n_max) {
    datafile.close();
    Serial.print("Done");
    while(1);  
  }
  
  // Initialize storage variables
  uint8_t channel;
  
  for (channel = 0; channel < 3; ++channel) {
    // Hold the values
    float ax, ay, az;
    float g1, g2, g3;
    float m1, m2, m3;

    // Get the acceleration
    while(!IMU.accelerationAvailable()) {}
    IMU.readAcceleration(ax, ay, az);

    // Get the gyroscope
    while(!IMU.gyroscopeAvailable()) {}
    IMU.readGyroscope(g1, g2, g3);

    // Get the magnetic field
    while(!IMU.magneticFieldAvailable()) {}
    IMU.readMagneticField(m1, m2, m3);
    
    // Write to a file   
    datafile.print(millis());
    datafile.print(",");
    datafile.print(channel);
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
    datafile.print(m1); // in microT
    datafile.print(",");
    datafile.print(m2); // in microT
    datafile.print(",");
    datafile.println(m3); // in microT

    // Print acceleration and gyro info
//    Serial.print(channel);
//    Serial.print("\t");
//    Serial.print(ax);
//    Serial.print('\t');
//    Serial.print(ay);
//    Serial.print('\t');
//    Serial.print(az);
//    Serial.print("\t");
//    Serial.print(g1);
//    Serial.print('\t');
//    Serial.print(g2);
//    Serial.print('\t');
//    Serial.print(g3);
//    Serial.print('\t');
//    Serial.print(m1);
//    Serial.print('\t');
//    Serial.print(m2);
//    Serial.print('\t');
//    Serial.println(m3);
  }
  
  // Increment iterator
  n_run = n_run + 1;
}
