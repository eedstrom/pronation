#include <Wire.h>
#include "Kalman.h" // Source: https://github.com/TKJElectronics/KalmanFilter
#include <Arduino_LSM9DS1.h>
#include <SD.h>
#include <SPI.h>

#define RESTRICT_PITCH // Comment out to restrict roll to ±90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf

const int chipSelect = 53;      // Put this as the CS pin
const char* FILENAME = "accelkal.csv";      // File name to be written to

Kalman kalmanX; // Create the Kalman instances
Kalman kalmanY;

File datafile;      // File object

uint8_t n_run = 0;      //counter
uint8_t n_iter = 100;     //number of iterations between writes

/* IMU Data */
float accX, accY, accZ;
float gyroX, gyroY, gyroZ;

float gyroXangle, gyroYangle; // Angle calculate using the gyro only
float compAngleX, compAngleY; // Calculated angle using a complementary filter
float kalAngleX, kalAngleY; // Calculated angle using a Kalman filter

uint32_t timer;

uint8_t channel;
//float ax, ay, az;
//float g1, g2, g3;
float m1, m2, m3;
float m[9] = { 0, 0, 0, 0, 0, 0 ,0, 0, 0 };
uint32_t t, dti;

void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}


void setup() {                                             

                                                 // Initialize for each channel
 for (channel = 0; channel < 3; ++channel) {
                                                 // Set to channel 0, 1, 2
       TCA9548A(channel);
       
       Wire.begin();
       IMU.begin();
       }
          
    Serial.begin(9600);                              
    while (!Serial); 
    
    if (!SD.begin(chipSelect)) {
    Serial.println("SD Card not present or wiring issue");
    // Halt operations
    while (1);  }
                                
    datafile = SD.open(FILENAME, FILE_WRITE);       // Open the file
                                    
    uint8_t sr_a0, sr_a1, sr_a2,
            sr_g0, sr_g1, sr_g2,
            sr_m0, sr_m1, sr_m2;

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

 /* Serial.print(-1);
  Serial.print(",");
  Serial.print(sr_a0); // in Hz
  Serial.print(",");
  Serial.print(sr_a1); // in Hz
  Serial.print(",");
  Serial.print(sr_a2); // in Hz
  Serial.print(",");
  Serial.print(sr_g0); // in Hz
  Serial.print(",");
  Serial.print(sr_g1); // in Hz
  Serial.print(",");
  Serial.print(sr_g2); // in Hz
  Serial.print(",");
  Serial.print(sr_m0); // in Hz
  Serial.print(",");
  Serial.print(sr_m1); // in Hz
  Serial.print(",");
  Serial.println(sr_m2); // in Hz */
//delete if dont want printed to serial, here for debugging rn

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
}

void loop() {                              // has completed loop??
    if (n_run >= n_iter) {
                                          // Close the file (save)
       datafile.close();                     // Reset the counter to 0
       n_run = 0;                                                 
       datafile = SD.open(FILENAME, FILE_WRITE);   // Reopen the file
      }                                       
  
  for (channel = 0; channel < 3; ++channel) {
                                                  // Change channel
    TCA9548A(channel);
    t = millis();
   // Serial.println("\n\nStart: ");
                                             // Get the acceleration
    while(!IMU.accelerationAvailable()) {}
    IMU.readAcceleration(accX, accY, accZ);
                                             // Get the gyroscope
    while(!IMU.gyroscopeAvailable()) {}
    IMU.readGyroscope(gyroX, gyroY, gyroZ);
                                              //get magnetometer
    if(IMU.magneticFieldAvailable()) {
      IMU.readMagneticField(m1, m2, m3);
      m[3 * channel + 0] = m1;
      m[3 * channel + 1] = m2;
      m[3 * channel + 2] = m3;
    }

   //dti = millis() - t;
float dt = (float)(micros() - timer) / 1000000; // Calculate delta time
  timer = micros();

  // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
  // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
  // It is then converted from radians to degrees
#ifdef RESTRICT_PITCH // Eq. 25 and 26
  float roll  = atan2(accY, accZ) * RAD_TO_DEG;
  float pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
#else // Eq. 28 and 29
  float roll  = atan(accY / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
  float pitch = atan2(-accX, accZ) * RAD_TO_DEG;
#endif

//  float gyroXrate = gyroX / 131.0; // Convert to deg/s
//  float gyroYrate = gyroY / 131.0; // Convert to deg/s

    float gyroXrate = gyroX; // already in deg/s
    float gyroYrate = gyroY; // already in deg/s

#ifdef RESTRICT_PITCH
  // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
  if ((roll < -90 && kalAngleX > 90) || (roll > 90 && kalAngleX < -90)) {
    kalmanX.setAngle(roll);
    compAngleX = roll;
    kalAngleX = roll;
    gyroXangle = roll;
  } else
    kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleX) > 90)
    gyroYrate = -gyroYrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt);
#else
  // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
  if ((pitch < -90 && kalAngleY > 90) || (pitch > 90 && kalAngleY < -90)) {
    kalmanY.setAngle(pitch);
    compAngleY = pitch;
    kalAngleY = pitch;
    gyroYangle = pitch;
  } else
    kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleY) > 90)
    gyroXrate = -gyroXrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter
#endif

  gyroXangle += gyroXrate * dt; // Calculate gyro angle without any filter
  gyroYangle += gyroYrate * dt;
  //gyroXangle += kalmanX.getRate() * dt; // Calculate gyro angle using the unbiased rate
  //gyroYangle += kalmanY.getRate() * dt;

  compAngleX = 0.93 * (compAngleX + gyroXrate * dt) + 0.07 * roll; // Calculate the angle using a Complimentary filter
  compAngleY = 0.93 * (compAngleY + gyroYrate * dt) + 0.07 * pitch;

  // Reset the gyro angle when it has drifted too much
  if (gyroXangle < -180 || gyroXangle > 180)
    gyroXangle = kalAngleX;
  if (gyroYangle < -180 || gyroYangle > 180)
    gyroYangle = kalAngleY;

//end of calculations and now printing/displaying data
                                                          
                                                          //Print raw data
   /*Serial.println("Raw data");
   Serial.print(accX); Serial.print("\t");               // Converted into g's
   Serial.print(accY); Serial.print("\t");
   Serial.print(accZ); Serial.print("\t");
   Serial.print(gyroX); Serial.print("\t");
   Serial.print(gyroY); Serial.print("\t");
   Serial.println(gyroZ);
                                                        //Print roll and yaw
    Serial.println("Corrected data");
    Serial.print(roll); Serial.print("\t");
    Serial.print(gyroXangle); Serial.print("\t");
    Serial.print(compAngleX); Serial.print("\t");
    Serial.print(kalAngleX); Serial.print("\t");
    Serial.print(pitch); Serial.print("\t");
    Serial.print(gyroYangle); Serial.print("\t");
    Serial.print(compAngleY); Serial.print("\t");
    Serial.println(kalAngleY); 
    Serial.println("Time at end of loop: "); Serial.print(millis()-t); */
    //delay(1000);
    
    datafile.print(channel);
    datafile.print(",");   
    datafile.print(t);
    datafile.print(",");
    datafile.print(millis()-t);               //adjust this time to be either over loop or whole iteration
    datafile.print(",");
    //raw data
    datafile.print(accX * 1000); // in mG
    datafile.print(",");
    datafile.print(accY * 1000); // in mG
    datafile.print(",");
    datafile.print(accZ * 1000); // in mG
    datafile.print(",");
    datafile.print(gyroX * 10); // in d(dps)
    datafile.print(",");
    datafile.print(gyroY * 10); // in d(dps)
    datafile.print(",");
    datafile.print(gyroZ * 10); // in d(dps)
    datafile.print(","); 
    datafile.print(m[3 * channel + 0]); // in microT
    datafile.print(",");
    datafile.print(m[3 * channel + 1]); // in microT
    datafile.print(",");
    datafile.print(m[3 * channel + 2]); // in microT
    datafile.print(",");                  //filtered data
    // datafile.print(roll); 
    // datafile.print(",");
    // datafile.print(gyroXangle); 
    // datafile.print(",");
    datafile.print(compAngleX);
    datafile.print(",");
    datafile.print(kalAngleX); 
    datafile.print(",");
    // datafile.print(pitch); 
    // datafile.print(",");
    // datafile.print(gyroYangle); 
    // datafile.print(",");
    datafile.print(compAngleY); 
    datafile.print(",");
    datafile.println(kalAngleY); 

  }
  n_run = n_run + 1;
  //delay(5000);
 // Serial.println("\nDELAY AFTER READING 3");
}
