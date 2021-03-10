#include <Arduino_LSM9DS1.h>
#include <Wire.h>
#include <SD.h>
#include <SPI.h>
#include "RTClib.h"

// Constants //

// Put this as the CS pin
const int chipSelect = 53;
//RTC variables

RTC_DS3231 rtc;         //declare RTC
DateTime now;

 long start= millis();
 
// File name to be written to
const char* FILENAME = "test.txt";

// File object
File datafile;

// Counter
uint16_t n_run = 0;

// Max number of iterations
uint16_t n_max = 50;


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

 int return_code = rtc.begin();     //setup and check RTC
 
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

  // Get the sample rate
  uint8_t sr_a0, sr_a1, sr_a2,
          sr_g0, sr_g1, sr_g2,
          sr_m0, sr_m1, sr_m2;
          

  // Get for channel 0
  TCA9548A(0);
  sr_a0 = (uint8_t) IMU.accelerationSampleRate();
  sr_g0 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m0 = (uint8_t) IMU.magneticFieldSampleRate();
  Serial.print(sr_a0); Serial.print(" "); Serial.print(sr_g0); Serial.print(" "); Serial.print(sr_m0); Serial.print("\n");
  // Get for channel 1
  TCA9548A(1);
  sr_a1 = (uint8_t) IMU.accelerationSampleRate();
  sr_g1 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m1 = (uint8_t) IMU.magneticFieldSampleRate();
  Serial.print(sr_a1); Serial.print(" "); Serial.print(sr_g1); Serial.print(" "); Serial.print(sr_m1);  Serial.print("\n");
  // Get for channel 1
  // Get for channel 2
  TCA9548A(2);
  sr_a2 = (uint8_t) IMU.accelerationSampleRate();
  sr_g2 = (uint8_t) IMU.gyroscopeSampleRate();
  sr_m2 = (uint8_t) IMU.magneticFieldSampleRate();
  

 
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
  long x= millis();
  
  for (channel = 0; channel < 3; ++channel) {
    // Hold the values
    // Set to channel 0, 1, 2
    TCA9548A(channel);
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
   // while(!IMU.magneticFieldAvailable()) {}
   // IMU.readMagneticField(m1, m2, m3);
    long uno= millis();
    datafile.print("\n");
    datafile.print(channel);
    datafile.print(", ");
    datafile.print(ax * 1000); // in mG
    datafile.print(", ");
    datafile.print(ay * 1000); // in mG
    datafile.print(", ");
    datafile.print(az * 1000); // in mG
    datafile.print(", ");
    datafile.print(g1 * 10); // in d(dps)
    datafile.print(", ");
    datafile.print(g2 * 10); // in d(dps)
    datafile.print(", ");
    datafile.print(g3 * 10); // in d(dps)
    datafile.print(", "); 
    datafile.print(m1); // in microT
    datafile.print(", ");
    datafile.print(m2); // in microT
    datafile.print(", ");
    datafile.print(m3); // in microT
    datafile.print("\n"); datafile.print(millis()-uno); datafile.print("\n ");    //time for each accel to take data
      
  }

  datafile.print("\nTotal: "); datafile.print(millis()- start);     //time from beginning in milliseconds
  datafile.print(", ");
  datafile.print("Loop: "); datafile.print(millis()-x);           //time for each loop over 3 accelerometers to run
  datafile.print(", "); 
  datafile.print("Real time: ");                                  //real time
      now = rtc.now();
      datafile.print(now.hour(), DEC);
      datafile.print(':');
      if(now.minute() < 10)  datafile.print(0);
      datafile.print(now.minute(), DEC);
      datafile.print(':');
      if(now.second() < 10)  datafile.print(0);
      datafile.print(now.second(), DEC); 
      datafile.print("\n");
      //Serial.print("outside loop");
      //delay(1000);
      n_run = n_run + 1;
}
