/* Writes data from accelerometer and gyroscope to a file on an SD card
 * The file format is a csv with the following columns:
 * LSM9 bus (0-2), acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z
 * 
 * First row contains the Sample Rate for each accelerometer for both acceleration and gyroscope in the form:
 * Sample Rate Identifyer (-1), acceleration sample rate channel 1, acceleration sample rate channel 2, acceleration sample rate channel 3,
 ** gyroscope sample rate channel 1, gyroscope sample rate channel 2, gyroscope sample rate channel 3
 */

#include <Arduino_LSM9DS1.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// Put this as the CS pin
const int chipSelect = 53;

// File name to be written to
const char* filename = "restdata.csv";

// Function to change bus
void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

// Function to write to SD card
void writeSD(File datafile, char* datachar)
{
  if (datafile) {
    datafile.println(datachar);
    datafile.close();

    // Print to the Serial Monitor too
    Serial.println(datachar);
  }
}

void setup() {
  // Initialize
  Wire.begin();
  IMU.begin();
  // Prepare the Serial Monitor for output
  Serial.begin(9600);
  while (!Serial);

  // make sure the sd card is present
  if (!SD.begin(chipSelect)) {
    Serial.println("SD Card not present");
    // Halt operations
    while (1);
  }

  // Iterator for the accelerometers
  uint8_t channel;

  // Container for the sample rate data
  uint8_t sample_data_arr[6];
  char sampledata[250];
  
  // Check Accelerometer rates for all channels in Hz
  for (channel = 0; channel < 3; ++channel) {
    TCA9548A(channel); // Set the channel
    // Store the rate
    sample_data_arr[channel] = (uint8_t) IMU.accelerationSampleRate();
  }

  // Check Gyroscopic rates for all channels in Hz
  for (channel = 0; channel < 3; ++channel) {
    TCA9548A(channel + 3); // Set the channel
    // Store the rate
    sample_data_arr[channel + 3] = (uint8_t) IMU.gyroscopeSampleRate();
  }

  // Convert int array to chars
  sprintf(sampledata, "%i,%i,%i,%i,%i,%i,%i", -1, sample_data_arr[0], sample_data_arr[1], sample_data_arr[2],
          sample_data_arr[3], sample_data_arr[4], sample_data_arr[5]);

  // Write to the SD
  File datafile_init = SD.open(filename, FILE_WRITE); // Open the file
  writeSD(datafile_init, sampledata);
}

void loop() {
  // Initialize variables
  float ax, ay, az, gx, gy, gz;
  float acc_arr[9];
  float gyr_arr[9]; 
  char ax_c[11], ay_c[11], az_c[11],
       gx_c[11], gy_c[11], gz_c[11];

  
  // Get the acceleration & gyro values for each channel
  uint8_t channel;
  for (channel = 0; channel < 3; ++channel) {
    TCA9548A(channel); // Set the channel
    
    // Read the data
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);

    // Save the values to the acceleration array
    acc_arr[0 + (channel * 3)] = ax;
    acc_arr[1 + (channel * 3)] = ay;
    acc_arr[2 + (channel * 3)] = az;
    
    // Save the values to the gyroscope array
    gyr_arr[0 + (channel * 3)] = gx;
    gyr_arr[1 + (channel * 3)] = gy;
    gyr_arr[2 + (channel * 3)] = gz;

  }

  // Convert floats to char for each channel
  for (channel = 0; channel < 3; ++channel){
    dtostrf(acc_arr[0 + (channel * 3)] * 1000, 10, 5, ax_c); // in kG
    dtostrf(acc_arr[1 + (channel * 3)] * 1000, 10, 5, ay_c); // in kG
    dtostrf(acc_arr[2 + (channel * 3)] * 1000, 10, 5, az_c); // in kG
    dtostrf(gyr_arr[0 + (channel * 3)], 10, 5, gx_c); // in dps
    dtostrf(gyr_arr[1 + (channel * 3)], 10, 5, gy_c); // in dps
    dtostrf(gyr_arr[2 + (channel * 3)], 10, 5, gz_c); // in dps

    // Put into one datachar
    char datachar[100];
    sprintf(datachar, "%i,%s,%s,%s,%s,%s,%s", channel, ax_c, ay_c, az_c, gx_c, gy_c, gz_c);

    // Write to the SD
    File datafile = SD.open(filename, FILE_WRITE); // Open the file
    writeSD(datafile, datachar);
  }
}
