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



 * A file to test to see if specific Accelerometers are working properly. Altering
 * the channel value from 0 to 2 changes which SCL and SDA lines are being 
 * utilized.
 * 
 * This file also solves a current issue with the MultAccelData code. If that code
 * reads the acceleration values as 0 regardless of the true value, running
 * this code on each channel solves it. This is a temporary fix.
 */

#include <Arduino_LSM9DS1.h>
#include <Wire.h>

// Function to change bus
void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

void setup() {
  Wire.begin();
  IMU.begin();
  Serial.begin(9600);
  while (!Serial);
  
  // Set to channel 0, 3, or 6
  TCA9548A(2);
  
  Serial.println("Started");
  Serial.print("Acc sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
  Serial.println();
  Serial.println("Acc in G's");
  Serial.println("X\tY\tZ");
}

void loop() {
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);

    Serial.print(x);
    Serial.print('\t');
    Serial.print(y);
    Serial.print('\t');
    Serial.println(z);
  }
}
