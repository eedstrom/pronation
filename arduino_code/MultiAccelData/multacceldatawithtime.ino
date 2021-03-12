#include <Arduino_LSM9DS1.h>
#include <Wire.h>
#include <SD.h>
#include <SPI.h>
#include "RTClib.h"

// Constants //

// Put this as the CS pin
const int chipSelect = 53;

RTC_DS3231 rtc;         //declare RTC
DateTime now;

// File name to be written to
const char* FILENAME = "accel.txt";

// File object
File datafile;

// Counter
uint8_t n_run = 0;

// Number of iterations in between writes
uint8_t n_iter = 10;


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

  int return_code = rtc.begin();
  //check if RTC started correctly
  if(!return_code) {    
    Serial.println("RTC doesn't work.");
    while (1) {};
                    }

  
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
  Serial.print("File opened");

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
  datafile.println(sr_g2); // in Hz 
  datafile.print(",");
  datafile.print(sr_m0); // in Hz
  datafile.print(",");
  datafile.print(sr_m1); // in Hz
  datafile.print(",");
  datafile.println(sr_m2); // in Hz 
}

void loop() {
  // Check if we have run the course
  if (n_run >= n_iter) {
    // Close the file (save)
    datafile.close();

    // Inform user that data was saved - for testing only
    //  Serial.print("Write");

    // Reset the counter to 0
    n_run = 0;
    
    // Reopen the file
    datafile = SD.open(FILENAME, FILE_WRITE);
  }
  
  // Initialize storage variables
  Serial.print("\nStarting measurements");
  uint8_t channel;
  
  for (channel = 0; channel < 3; ++channel) {
    // Containers for the data
    float ax, ay, az;
    float g1, g2, g3;
    float m1, m2, m3;
    int t, dt;

    // Get the time where data is collected first
    t = millis();
    now = rtc.now();
    // Get the acceleration
    while(!IMU.accelerationAvailable()) {}
    IMU.readAcceleration(ax, ay, az);

    // Get the gyroscope
    while(!IMU.gyroscopeAvailable()) {}
    IMU.readGyroscope(g1, g2, g3);

    // Get the magnetic field
    while(!IMU.magneticFieldAvailable()) {}
    IMU.readMagneticField(m1, m2, m3);

    // Get the time taken to collect all data
    dt = millis() - t;
    
    // Write to a file
    datafile.print(channel);
    datafile.print(",");   
    datafile.print(t);
    datafile.print(",");
    datafile.print(dt);    
    datafile.print(",");
    datafile.print(now.hour(), DEC);
      datafile.print(':');
      if(now.minute() < 10)  datafile.print(0);
      datafile.print(now.minute(), DEC);
      datafile.print(':');
      if(now.second() < 10)  datafile.print(0);
      datafile.print(now.second(), DEC); 
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
  }
  
  // Increment iterator
  n_run = n_run + 1;
}
