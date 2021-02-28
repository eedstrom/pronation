#include <LiquidCrystal.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_GPS.h>
#include "SdFat.h"

const int rs = 12, en = 11, d4 = 36, d5 = 34, d6 = 32, d7 = 30; //lcd setup
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
#define LCDWIDTH 16

#include "RTClib.h"   //real time clock setup
RTC_DS3231 rtc;
SdFat SD;
char daysOfTheWeek[7][4] = 
  {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};

const int microSD_CS_pin = 53;

// clock 
const int microSD_CLK_pin = 52;

// data out (DO or SO or MISO or...)
const int microSD_DO_pin = 50;

// data in (DI or SI or MOSI or...)
const int microSD_DI_pin = 51;

// instantiate a file object.
File myFile;


#define GPSECHO_GPS_query true   //GPS setup
#define GPSECHO_loop true
#define PMTK_SET_NMEA_UPDATE_5SEC "$PMTK220,10000*2F"
#define PMTK_SET_NMEA_UPDATE_1SEC "$PMTK220,5000*2F"
#define GPSSerial Serial2

Adafruit_GPS GPS(&GPSSerial);

#define GPSMAXLENGTH 120
#define GPSMINLENGTH 55

char* GPS_sentence;
String GPS_sentence_string;
String GPS_command;   //holds sentence from GPS read

const int GPRMC_hour_index1 = 7;
const int GPRMC_hour_index2 = GPRMC_hour_index1 + 2;

const int GPRMC_minutes_index1 = GPRMC_hour_index2;
const int GPRMC_minutes_index2 = GPRMC_minutes_index1 + 2;
      
const int GPRMC_seconds_index1 = GPRMC_minutes_index2;
const int GPRMC_seconds_index2 = GPRMC_seconds_index1 + 2;
      
const int GPRMC_milliseconds_index1 = GPRMC_seconds_index2 + 1;   // skip the decimal point
const int GPRMC_milliseconds_index2 = GPRMC_milliseconds_index1 + 3;
      
// const int GPRMC_AV_code_index1 = 19;
const int GPRMC_AV_code_index1 = GPRMC_hour_index1 +  11;
const int GPRMC_AV_code_index2 = GPRMC_AV_code_index1 + 1;
      
// const int GPRMC_latitude_1_index1 = 21;
const int GPRMC_latitude_1_index1 = GPRMC_AV_code_index1 + 2;
const int GPRMC_latitude_1_index2 = GPRMC_latitude_1_index1 + 4;
      
const int GPRMC_latitude_2_index1 = GPRMC_latitude_1_index2 + 1;   
const int GPRMC_latitude_2_index2 = GPRMC_latitude_2_index1 + 4;

// const int GPRMC_latitude_NS_index1 = 31;
const int GPRMC_latitude_NS_index1 = GPRMC_latitude_1_index1 + 10;
const int GPRMC_latitude_NS_index2 = GPRMC_latitude_NS_index1 + 1;

// const int GPRMC_longitude_1_index1 = 33;
const int GPRMC_longitude_1_index1 = GPRMC_latitude_NS_index1 + 2;
const int GPRMC_longitude_1_index2 = GPRMC_longitude_1_index1 + 5;    
      
const int GPRMC_longitude_2_index1 = GPRMC_longitude_1_index2 + 1;   
const int GPRMC_longitude_2_index2 = GPRMC_longitude_2_index1 + 4;
      
// const int GPRMC_longitude_EW_index1 = 44;
const int GPRMC_longitude_EW_index1 = GPRMC_longitude_1_index1 + 11;
const int GPRMC_longitude_EW_index2 = GPRMC_longitude_EW_index1 + 1;

const int GPGGA_hour_index1 = 7;
const int GPGGA_hour_index2 = GPGGA_hour_index1 + 2;

const int GPGGA_minutes_index1 = GPGGA_hour_index2;
const int GPGGA_minutes_index2 = GPGGA_minutes_index1 + 2;
      
const int GPGGA_seconds_index1 = GPGGA_minutes_index2;
const int GPGGA_seconds_index2 = GPGGA_seconds_index1 + 2;
      
const int GPGGA_milliseconds_index1 = GPGGA_seconds_index2 + 1;   // skip the decimal point
const int GPGGA_milliseconds_index2 = GPGGA_milliseconds_index1 + 3;
      
// const int GPGGA_latitude_1_index1 = 19;
const int GPGGA_latitude_1_index1 = GPGGA_hour_index1 + 11;
const int GPGGA_latitude_1_index2 = GPGGA_latitude_1_index1 + 4;
      
const int GPGGA_latitude_2_index1 = GPGGA_latitude_1_index2 + 1;   // skip the decimal point
const int GPGGA_latitude_2_index2 = GPGGA_latitude_2_index1 + 4;

// const int GPGGA_latitude_NS_index1 = 29;
const int GPGGA_latitude_NS_index1 = GPGGA_latitude_1_index1 + 10;
const int GPGGA_latitude_NS_index2 = GPGGA_latitude_NS_index1 + 1;

// const int GPGGA_longitude_1_index1 = 31;
const int GPGGA_longitude_1_index1 = GPGGA_latitude_NS_index1 + 2;
const int GPGGA_longitude_1_index2 = GPGGA_longitude_1_index1 + 5;    // 0 - 180 so we need an extra digit
      
const int GPGGA_longitude_2_index1 = GPGGA_longitude_1_index2 + 1;   // skip the decimal point
const int GPGGA_longitude_2_index2 = GPGGA_longitude_2_index1 + 4;
      
// const int GPGGA_longitude_EW_index1 = 42;
const int GPGGA_longitude_EW_index1 = GPGGA_longitude_1_index1 + 11;
const int GPGGA_longitude_EW_index2 = GPGGA_longitude_EW_index1 + 1;

// const int GPGGA_fix_quality_index1 = 44;
const int GPGGA_fix_quality_index1 = GPGGA_longitude_EW_index1 + 2;
const int GPGGA_fix_quality_index2 = GPGGA_fix_quality_index1 + 1;

// const int GPGGA_satellites_index1 = 46;
const int GPGGA_satellites_index1 = GPGGA_fix_quality_index1 + 2;
const int GPGGA_satellites_index2 = GPGGA_satellites_index1 + 2;

const int asterisk_backup = 5;
long GPS_char_reads = 0;
const long GPS_char_reads_maximum = 1000000;

String GPS_hour_string;
String GPS_minutes_string;
String GPS_seconds_string;
String GPS_milliseconds_string;
int GPS_hour;
int GPS_minutes;
int GPS_seconds;
int GPS_milliseconds;

String GPS_AV_code_string;
String GPS_latitude_1_string;
String GPS_latitude_2_string;
String GPS_latitude_NS_string;
int GPS_latitude_1;
int GPS_latitude_2;

// longitude data
String GPS_longitude_1_string;
String GPS_longitude_2_string;
String GPS_longitude_EW_string;
int GPS_longitude_1;
int GPS_longitude_2;
String GPS_speed_knots_string;
String GPS_direction_string;
float GPS_speed_knots;
float GPS_direction;

String GPS_date_string;

String GPS_fix_quality_string;
String GPS_satellites_string;
int GPS_fix_quality;
int GPS_satellites;

String GPS_altitude_string;
float GPS_altitude;
const long maximum_times_to_loop = 20;   //how many times to go through the data
long my_counter;

void setup() 
{
  Serial.begin(115200);

  //begin LCD
  my_counter = 0;
  lcd.begin(16, 2);
  delay(1000);

   //begin RTC
  if (! rtc.begin()) {
    
    delay(3000);  

    } else { }

    
  pinMode(microSD_CS_pin, OUTPUT);

  if (!SD.begin(microSD_CS_pin)) {
    Serial.println("microSD initialization failed");
    while (1);
    }

  //begin GPS
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_2HZ);           //how fast it reads data
  //GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1SEC);
    }


void loop() 
{
  // loop function is executed repeatedly after the setup function finishes.
    my_counter++;

    if(my_counter == 1)
      {
       myFile = SD.open("testigngng.txt", FILE_WRITE);
  
        delay(1000);   
      }

  if(my_counter > 100000000000)
     {

    // close the file:
    myFile.close();
    Serial.println("Just closed the microSD file.");

    // tumble into an infinite loop.
    Serial.println("All done, so about to enter a parking loop.");
    while(true){}
  
     }

    int GPS_return_code = GPS_query();

   if(GPS_return_code == 0)
     {
      myFile.print("GPS_hour,"); myFile.print(GPS_hour-6); myFile.print(","); 
      myFile.print("GPS_minutes,"); myFile.print(GPS_minutes); myFile.print(",");
      myFile.print("GPS_seconds,"); myFile.print(GPS_seconds); myFile.print(","); 
      myFile.print("GPS_milliseconds,"); myFile.println(GPS_milliseconds);
      myFile.print("\nSpeed (m/s) = "); Serial.print(GPS_speed_knots * 0.514444);
      myFile.print("     Direction (degrees) = "); myFile.println(GPS_direction);
     }
  }

int GPS_query()
  {

    GPS_char_reads = 0;
    GPS_sentence = GPS.lastNMEA();
    while (true) {
  
    while(GPS_char_reads <= GPS_char_reads_maximum) 
      {
        char single_GPS_char = GPS.read();
        if(single_GPS_char == '\0')
        {
        // Serial.println("\ncharacter was a null so bail out.");
        return -1;
        }

        if(GPSECHO_GPS_query) //Serial.print(single_GPS_char);
        GPS_char_reads++;

         if(GPS.newNMEAreceived()) break;
  
      }
      
      if (GPS_char_reads >= GPS_char_reads_maximum) 
      {
      Serial.println("Having trouble reading GPS navigation data. Try again later.");   
      return -1;        
      }

       GPS_sentence = GPS.lastNMEA();
       GPS_sentence_string = String(GPS_sentence);

       bool data_OK = GPS_sentence_string.charAt(0) == '$'; 
       data_OK = data_OK && (GPS_sentence_string.indexOf('$', 2) <  0);
       data_OK = data_OK && (GPS_sentence_string.indexOf('*', 0) >  0);

       GPS_command = GPS_sentence_string.substring(0, 6);
       GPS_command.trim();

       bool command_OK = GPS_command.equals("$GPRMC") || GPS_command.equals("$GPGGA");
       
        if (!command_OK) 
       {


      return -1;        
      }


if (data_OK && GPS_command.equals("$GPRMC"))
        {
      
        GPS_hour_string = GPS_sentence_string.substring(GPRMC_hour_index1, GPRMC_hour_index2);
        GPS_minutes_string = GPS_sentence_string.substring(GPRMC_minutes_index1, GPRMC_minutes_index2);
        GPS_seconds_string = GPS_sentence_string.substring(GPRMC_seconds_index1, GPRMC_seconds_index2);
        GPS_milliseconds_string = GPS_sentence_string.substring(GPRMC_milliseconds_index1, 
        GPRMC_milliseconds_index2);
        GPS_AV_code_string = GPS_sentence_string.substring(GPRMC_AV_code_index1, GPRMC_AV_code_index2);
    
        GPS_hour = GPS_hour_string.toInt();
        GPS_minutes = GPS_minutes_string.toInt();
        GPS_seconds = GPS_seconds_string.toInt();
        GPS_milliseconds = GPS_milliseconds_string.toInt();

        int comma_A_index = GPRMC_longitude_EW_index2;
        int comma_B_index = GPS_sentence_string.indexOf(",", comma_A_index + 1);
        int comma_C_index = GPS_sentence_string.indexOf(",", comma_B_index + 1);
    
        GPS_speed_knots_string = GPS_sentence_string.substring(comma_A_index + 1, comma_B_index); 
        GPS_direction_string = GPS_sentence_string.substring(comma_B_index + 1, comma_C_index); 
        
        GPS_speed_knots = GPS_speed_knots_string.toFloat();
        GPS_direction = GPS_direction_string.toFloat();


    if(GPSECHO_GPS_query)
          {
          Serial.print("\nTime (UTC) = "); Serial.print(GPS_hour-6); Serial.print(":");
          Serial.print(GPS_minutes); Serial.print(":");
          Serial.print(GPS_seconds); Serial.print(".");
          Serial.println(GPS_milliseconds);
          Serial.print("Speed (m/s) = "); Serial.println(GPS_speed_knots * 0.514444);
          Serial.print("Direction (degrees) = "); Serial.println(GPS_direction);
          Serial.print("\n");
          //Serial.print(micros());
          //lcd.print(GPS_hour-6); lcd.print(":");
          //lcd.print(GPS_minutes); lcd.print(":");
          //lcd.print(GPS_seconds); 
          
          }
      
      data_OK = GPS_AV_code_string == "A";
      int asterisk_should_be_here = GPS_sentence_string.length() - asterisk_backup; 
      data_OK = data_OK && (GPS_sentence_string.charAt(asterisk_should_be_here) == '*');
      data_OK = data_OK && (GPS_sentence_string.length() >= GPSMINLENGTH);

    

      return 0;
        }
    }}
