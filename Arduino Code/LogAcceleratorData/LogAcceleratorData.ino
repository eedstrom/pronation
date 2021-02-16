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


// SD Card Data Logger
#include <Arduino_LSM9DS1.h>
#include <SPI.h>
#include <SD.h>

// Put this value as your CS pin
const int chipSelect = 53;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    while (1);
  }
  Serial.println("card initialized.");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
}

void loop() {
  // make an array for assembling the data to log:
  float x, y, z; // acceleration data
  char x_c[10], y_c[10], z_c[10]; // chars for acc data
  float g1, g2, g3; // gyroscope data
  char g1_c[10], g2_c[10], g3_c[10]; // chars for gyro data

  char datachar[200];

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z); // in Gs
    IMU.readGyroscope(g1, g2, g3); // in degrees-per-second
    // Multiply the floats by 1000
    dtostrf(x * 1000, 4, 5, x_c); // mG's
    dtostrf(y * 1000, 4, 5, y_c); // mG's
    dtostrf(z * 1000, 4, 5, z_c); // mG's
    dtostrf(g1 * 1000, 4, 5, g1_c); // mdps
    dtostrf(g2 * 1000, 4, 5, g2_c); // mdps
    dtostrf(g3 * 1000, 4, 5, g3_c); // mdps

    // Concat to one string for storage
    sprintf(datachar, "%s,%s,%s,%s,%s,%s", x_c, y_c, z_c, g1_c, g2_c, g3_c);

    // Open the file
    File datafile = SD.open("testfile.csv", FILE_WRITE);

    if (datafile) {
      datafile.println(datachar);
      datafile.close();

      // Print to the Serial Monitor too
      Serial.println(datachar);
    }
  }
}
