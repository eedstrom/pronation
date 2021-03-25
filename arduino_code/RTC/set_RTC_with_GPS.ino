/*************************************************************************************
  This program is set_RTC_with_GPS.ino

  Set a DS3231 real time clock connected to an Arduino Mega 2560 based on the GPS information 
  at our disposal. I am assuming that the Arduino is talking to an Adafruit DS3231 real
  time clock breakout board and an Adafruit "Ultimate GPS" breakout board. See 
  https://www.adafruit.com/product/746. 
  
  Note that the RTC won't be set until the GPS chip sees satellites. So this
  is best done outside! The GPS-based time will be UTC, not Central Time.

  UTC is approximately the same thing as Greenwich Mean Time, which is five hours 
  later than central daylight time, and six hours later than central standard time. 
  Once the RTC is set from GPS data that are reinforced by satellite data, the program 
  will stop setting the RTC. 
 
  This "sketch" is based in part on the Adafruit/Arduino GPS library example code
  in GPS_HardwareSerial_Parsing.ino, with subsequent modifications by George Gollin, 
  University of Illinois, 2018.

  I assume that the GPS board's PPS pin is connected to Arduino pin D43. The PPS (pulse-
  per-second) pin puts out a positive ~100 ms pulse just as the GPS clock rolls over to
  the next second, so I use this to obtain RTC syncronization with the GPS
  system that is (I hope) good to a millisecond or two. See comments in the body of the program.

  The method is to fetch the UTC time from the GPS, then add one second to it. I refer to
  this as the "bumped" time. I wait until the next time the GPS PPS pin lights up, then load
  the RTC module clock with the bumped time.

  See https://www.adafruit.com/products/3133, https://www.adafruit.com/products/1059, 
  https://www.adafruit.com/products/1272, and https://www.adafruit.com/products/746.
  
  You'll want to do Tools -> Serial Monitor, then set the baud rate to 9600.
  
  Also make sure that Tools -> Port is set to the Arduino's port.
  
  The Adafruit Ultimate GPS breakout board uses a MediaTek 3339 GPS chip set.
  The NMEA ("National Marine Electronics Association") command format includes a 
  two character checksum at the end; see http://www.hhhh.org/wiml/proj/nmeaxor.html 
  for a checksum calculator.

*************************************************************************************/

// Date and time functions using a DS3231 RTC connected via I2C and Wire lib
#include <Wire.h>
#include "RTClib.h"
#include <Adafruit_GPS.h>

// instantiate an rtc (real time clock) object:
RTC_DS3231 rtc;

// declare which Arduino pin sees the GPS PPS signal
int GPS_PPS_pin = 43;

// Which hardware serial port shall we use? Let's use the second. Why? Who knows?
#define GPSSerial Serial2

// declare variables which we'll use to store the value (0 or 1). 
int GPS_PPS_value, GPS_PPS_value_old;

// Connect the GPS to the hardware port
Adafruit_GPS GPS(&GPSSerial);

// define the synch-GPS-with-PPS command. NMEA is "National Marine Electronics 
// Association." 
#define PMTK_SET_SYNC_PPS_NMEA "$PMTK255,1*2D"

// command string to set GPS NMEA baud rate to 9,600:
#define PMTK_SET_NMEA_9600 "$PMTK251,9600*17"

// define a command to disable all NMEA outputs from the GPS except the date/time
#define PMTK_DATE_TIME_ONLY "$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0*29"
 
// define a command to disable ALL NMEA outputs from the GPS
#define PMTK_ALL_OFF "$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"
 
// define a command to enable all NMEA outputs from the GPS
#define PMTK_ALL_ON "$PMTK314,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1*29"
 
// See https://blogs.fsfe.org/t.kandler/2013/11/17/ for additional GPS definitions.

// we don't expect a valid GPS "sentence" to be longer than this...
#define GPSMAXLENGTH 120
char GPS_sentence[GPSMAXLENGTH];
int GPS_command_string_index;

// we'll also want to convert the GPS sentence character array to a string for convenience
String GPS_sentence_string;

// pointers into parts of a GPZDA GPS data sentence whose format is
//    $GPZDA,hhmmss.sss,dd,mm,yyyy,xx,xx*CS 
//              111111111122222222223
//    0123456789012345678901234567890             
// where CS is a two-character checksum. Identify this sentence by the presence of a Z.

const int GPZDA_hour_index1 = 7;
const int GPZDA_hour_index2 = GPZDA_hour_index1 + 2;

const int GPZDA_minutes_index1 = GPZDA_hour_index2;
const int GPZDA_minutes_index2 = GPZDA_minutes_index1 + 2;
      
const int GPZDA_seconds_index1 = GPZDA_minutes_index2;
const int GPZDA_seconds_index2 = GPZDA_seconds_index1 + 2;
      
const int GPZDA_milliseconds_index1 = GPZDA_seconds_index2 + 1;   // skip the decimal point
const int GPZDA_milliseconds_index2 = GPZDA_milliseconds_index1 + 3;
      
const int GPZDA_day_index1 = GPZDA_milliseconds_index2 + 1;  // skip the comma
const int GPZDA_day_index2 = GPZDA_day_index1 + 2;
      
const int GPZDA_month_index1 = GPZDA_day_index2 + 1;
const int GPZDA_month_index2 = GPZDA_month_index1 + 2;

const int GPZDA_year_index1 = GPZDA_month_index2 + 1;
const int GPZDA_year_index2 = GPZDA_year_index1 + 4;

// define some time variables.
unsigned long  time_ms_bumped_RTC_time_ready;

// system time from millis() at which the most recent GPS date/time
// sentence was first begun to be read
unsigned long t_GPS_read_start;

// system time from millis() at which the most recent GPS date/time
// sentence was completely parsed 
unsigned long t_GPS_read;

// system time from millis() at which the proposed bumped-by-1-second
// time is ready for downloading to the RTC
unsigned long t_bump_go; 
                
// system time from millis() at which the most recent 0 -> 1 
// transition on the GPS's PPS pin is detected
unsigned long t_GPS_PPS;  

// system time from millis() at which the RTC time load is done 
unsigned long t_RTC_update;

// keep track of whether or not we have set the RTC using satellite-informed GPS data
bool good_RTC_time_from_GPS_and_satellites;

// define some of the (self-explanatory) GPS data variables. Times/dates are UTC.
String GPS_hour_string;
String GPS_minutes_string;
String GPS_seconds_string;
String GPS_milliseconds_string;
int GPS_hour;
int GPS_minutes;
int GPS_seconds;
int GPS_milliseconds;

String GPS_day_string;
String GPS_month_string;
String GPS_year_string;
int GPS_day;
int GPS_month;
int GPS_year;

// RTC variables...
int RTC_hour;
int RTC_minutes;
int RTC_seconds;
int RTC_day;
int RTC_month;
int RTC_year;

// we will use the following to update the real time clock chip.
int RTC_hour_bumped;
int RTC_minutes_bumped;
int RTC_seconds_bumped;
int RTC_day_bumped;
int RTC_month_bumped;
int RTC_year_bumped;

// define a "DateTime" object:
DateTime now;

// limits for the timing data to be good:
const int t_RTC_update__t_GPS_PPS_min = -1;
const int t_GPS_PPS___t_bump_go_min = 200;
const int t_bump_go___t_GPS_read_min = -1;
const int t_RTC_update___t_GPS_read_min = 400;

const int t_RTC_update__t_GPS_PPS_max = 20;
const int t_GPS_PPS___t_bump_go_max = 800;
const int t_bump_go___t_GPS_read_max = 350;
const int t_RTC_update___t_GPS_read_max = 1000;

// more bookkeeping on clock setting... I will want to see several consecutive
// good reads/parses of GPS system time data to declare that all is good, and that
// we can wrap this up.
int consecutive_good_sets_so_far;
bool time_to_quit;
const int thats_enough = 5;

// the only kind of GPS sentence that can hold a Z, that I am allowing from the GPS,
// will carry date/time information.
bool sentence_has_a_Z;
  
// get the LCD display header file.
#include <LiquidCrystal.h>

// it's obvious what these are:
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", 
  "Thursday", "Friday", "Saturday"};

// times for the arrival of a new data sentence and the receipt of its last character
unsigned long t_new_sentence;
unsigned long t_end_of_sentence;

// a "function prototype" so I can put the actual function at the end of the file:
void bump_by_1_sec(void);

// initialize the LCD library by associating any needed LCD interface pins
// with the arduino pin numbers to which they are connected
const int rs = 12, en = 11, d4 = 36, d5 = 34, d6 = 32, d7 = 30;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// a counter
int i_am_so_bored;

/////////////////////////////////////////////////////////////////////////

void setup () {

  // fire up the serial monitor
  Serial.begin(115200);
  while(!Serial){};
  
  Serial.println("Let's set the DS3231 real time clock from the GPS after acquiring satellites.");

  // declare the GPS PPS pin to be an Arduino input 
  pinMode(GPS_PPS_pin, INPUT);

  // initialize a flag and some counters
  good_RTC_time_from_GPS_and_satellites = false;
  consecutive_good_sets_so_far = 0;
  i_am_so_bored = 0;

  // 9600 NMEA is the default communication and baud rate for Adafruit MTK 3339 chipset GPS 
  // units. NMEA is "National Marine Electronics Association." 
  // Note that this serial communication path is different from the one driving the serial 
  // monitor window on your laptop.
  GPS.begin(9600);

  // initialize a flag holding the GPS PPS pin status: this pin pulses positive as soon as 
  // the seconds value rolls to the next second.
  GPS_PPS_value_old = 0;
    
  // turn off most GPS outputs to reduce the rate of stuff coming at us.
  GPS.sendCommand(PMTK_DATE_TIME_ONLY);

  // Set the update rate to once per second. 
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); 

  // Send a synch-with-PPS command to the GPS in hopes of having a deterministic
  // relationship between the PPS line lighting up and the GPS reporting data to us. According
  // to the manufacturer, the GPS will start snding us a date/time data sentence about 170
  // milliseconds after the PPS line transitions fom 0 to 1. 
  GPS.sendCommand(PMTK_SET_SYNC_PPS_NMEA);
  
  // this keeps track of where in the string of characters of a GPS data sentence we are.
  GPS_command_string_index = 0;

  // more initialization
  sentence_has_a_Z = false;

  time_to_quit = false;

  // fire up the RTC.
  Serial.print("Fire up the RTC. return code is "); 
  int return_code = rtc.begin();
  Serial.println(rtc.begin());

  // problems?
  if(!return_code) {
    Serial.println("RTC wouldn't respond so bail out.");
    while (1) {};
  }

  // now try read back the RTC to check.       
  delay(500);
  
  now = rtc.now();
  Serial.print("Now read back the RTC to check during setup. ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  if(now.minute() < 10)   Serial.print(0);
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  if(now.second() < 10)   Serial.print(0);
  Serial.print(now.second(), DEC);

  Serial.print("   Date (dd/mm/yyyy): ");
  Serial.print(now.day(), DEC); Serial.print('/');
  if(int(now.month()) < 10) Serial.print("0");
  Serial.print(now.month(), DEC); Serial.print("/");
  Serial.println(now.year(), DEC);
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);

  // Print a message to the LCD.
  lcd.setCursor(0, 0);
  lcd.print("Now looking for ");
  lcd.setCursor(0, 1);
  lcd.print("GPS satellites  ");
}

/////////////////////////////////////////////////////////////////////////

void loop () {

  // ******************************************************************************
  /*

  First things first: check to see if we are we done setting the RTC. In order to 
  declare victory and exit, we'll need the following to happen. 

  Definitions:

    t_GPS_read    system time from millis() at which the most recent GPS date/time
                  sentence was completely parsed BEFORE the most recent PPS 0 -> 1 
                  transition was detected 
                      
    t_bump_go     system time from millis() at which the proposed bumped-by-1-second
                  time is ready for downloading to the RTC
    
    t_GPS_PPS     system time from millis() at which the most recent 0 -> 1 
                  transition on the GPS's PPS pin is detected

    t_RTC_update  system time from millis() at which the RTC time load is done 

  Typical timing for an event:   

    t_GPS_read    17,961    
    t_bump_go     17,971 (t_GPS_read +  10 ms)    
    t_GPS_PPS     18,597 (t_bump_go  + 626 ms)    
    t_RTC_update  18,598 (t_GPS_PPS  +   1 ms)

  Every once in a while we might miss the PPS 0 -> 1 transition, or the GPS might 
  not feed us a data sentence. So let's impose the following criteria.

  0 ms   <= t_RTC_update - t_GPS_PPS  <= 10 ms
  200 ms <= t_GPS_PPS - t_bump_go     <= 800 ms
  0 ms   <= t_bump_go - t_GPS_read    <= 50 ms
  400 ms <= t_RTC_update - t_GPS_read <= 1000 ms

  */

  if(time_to_quit) {

    // print a message to the serial monitor, but only once.
    if (i_am_so_bored == 0) Serial.print("\n\nTime to quit! We have set the RTC.");

    // Print a message to the LCD each pass through, updating the time.
    lcd.setCursor(0, 0);
    //         0123456789012345
    lcd.print("RTC is now set  ");

    // blank the LCD's second line 
    lcd.setCursor(0, 1);
    lcd.print("                ");

    // print the time
    lcd.setCursor(0, 1);
    now = rtc.now();
    
    if(now.hour() < 10)   lcd.print(0);
    lcd.print(now.hour(), DEC);
    
    lcd.print(':');
    if(now.minute() < 10)   lcd.print(0);
    lcd.print(now.minute());
    
    lcd.print(':');
    if(now.second() < 10)   lcd.print(0);
    lcd.print(now.second());

    delay(50);

    // increment a counter
    i_am_so_bored++;

    return;
  }

  // *******************************************************************************

  // now check to see if we just got a PPS 0 -> 1 transition, indicating that the
  // GPS clock has just ticked over to the next second.
  GPS_PPS_value = digitalRead(GPS_PPS_pin);
  
  // did we just get a 0 -> 1 transition?
  if (GPS_PPS_value == 1 && GPS_PPS_value_old == 0) {
    
    Serial.print("\nJust saw a PPS 0 -> 1 transition at time (ms) = ");
    t_GPS_PPS = millis();
    Serial.println(t_GPS_PPS);

    // load the previously established time values into the RTC now.
    if (good_RTC_time_from_GPS_and_satellites) {

      // now set the real time clock to the bumped-by-one-second value that we have 
      // already calculated. To set the RTC with an explicit date & time, for example 
      // January 21, 2014 at 3am you would call
      // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
    
      rtc.adjust(DateTime(int(RTC_year_bumped), int(RTC_month_bumped), int(RTC_day_bumped), int(RTC_hour_bumped), 
        int(RTC_minutes_bumped), int(RTC_seconds_bumped)));

      // take note of when we're back from setting the real time clock:
      t_RTC_update = millis();

      // Serial.print("Just returned from updating RTC at system t = "); Serial.println(t_RTC_update);

      Serial.print("Proposed new time fed to the RTC was ");
      Serial.print(RTC_hour_bumped, DEC); Serial.print(':');
      if(RTC_minutes_bumped < 10) Serial.print("0");
      Serial.print(RTC_minutes_bumped, DEC); Serial.print(':');
      if(RTC_seconds_bumped < 10) Serial.print("0");
      Serial.print(RTC_seconds_bumped, DEC); 
      Serial.print("   Date (dd/mm/yyyy): ");
      Serial.print(RTC_day_bumped, DEC); Serial.print('/');
      if(RTC_month_bumped < 10) Serial.print("0");
      Serial.print(RTC_month_bumped, DEC); Serial.print("/");
      Serial.println(RTC_year_bumped, DEC);  

      // now read back the RTC to check.       
      now = rtc.now();
      Serial.print("Now read back the RTC to check. ");
      Serial.print(now.hour(), DEC);
      Serial.print(':');
      if(now.minute() < 10)   Serial.print(0);
      Serial.print(now.minute(), DEC);
      Serial.print(':');
      if(now.second() < 10)   Serial.print(0);
      Serial.print(now.second(), DEC);

      Serial.print("   Date (dd/mm/yyyy): ");
      Serial.print(now.day(), DEC); Serial.print('/');
      if(int(now.month()) < 10) Serial.print("0");
      Serial.print(now.month(), DEC); Serial.print("/");
      Serial.println(now.year(), DEC);
      
      // now that we've used this GPS value, set the following flag to false:
      good_RTC_time_from_GPS_and_satellites = false;

      // Check that the times of various events is consistent with a good RTC setting
  
      bool ILikeIt = 
      int(t_RTC_update - t_GPS_PPS)  >= t_RTC_update__t_GPS_PPS_min   &&
      int(t_GPS_PPS - t_bump_go)     >= t_GPS_PPS___t_bump_go_min     &&
      int(t_bump_go - t_GPS_read)    >= t_bump_go___t_GPS_read_min    &&
      int(t_RTC_update - t_GPS_read) >= t_RTC_update___t_GPS_read_min &&
      int(t_RTC_update - t_GPS_PPS)  <= t_RTC_update__t_GPS_PPS_max   &&
      int(t_GPS_PPS - t_bump_go)     <= t_GPS_PPS___t_bump_go_max     &&
      int(t_bump_go - t_GPS_read)    <= t_bump_go___t_GPS_read_max    &&
      int(t_RTC_update - t_GPS_read) <= t_RTC_update___t_GPS_read_max ;
    
      if(ILikeIt) {
        consecutive_good_sets_so_far++;
      }else{
        consecutive_good_sets_so_far = 0;
      }
     
      time_to_quit = consecutive_good_sets_so_far >= thats_enough;

    }

  }

  GPS_PPS_value_old = GPS_PPS_value;

  // *******************************************************************************
  // read data from the GPS; do this one character per pass through function loop.
  // when synched to the PPS pin, the GPS sentence will start arriving about 170 ms
  // after the PPS line goes high, according to the manufacturer of the MTK3339 GPS
  // chipset. So we need to start by seeing if there's been a PPS 0 -> 1 transition.
  // *******************************************************************************

  char c;

  // is there anything new to be read?

  if(GPSSerial.available()) {

    // read the character
    c = GPS.read();

    // a "$" indicates the start of a new sentence.
    if (c == '$') {

      //reset the array index indicating where we put the characters as we build the GPS sentence.
      GPS_command_string_index = 0;
      t_new_sentence = millis();
      sentence_has_a_Z = false;

    }else{
  
    GPS_command_string_index++;

   }

    // build up the data sentence, one character at a time.
    GPS_sentence[GPS_command_string_index] = c;

    // are we reading a sentence from the GPS that carries date/time information? The
    // format is this: 
    //    $GPZDA,hhmmss.sss,dd,mm,yyyy,xx,xx*CS 
    // where CS is a checksum. Identify this kind of sentence by the presence of a Z.

    if (c == 'Z') {
      sentence_has_a_Z = true;
    }
    
    // a "*" indicates the end of the sentence, except for the two-digit checksum and the CR/LF.
    if (c == '*') {
      t_end_of_sentence = millis();
      t_GPS_read = t_end_of_sentence;
      // Serial.print("Beginning, end of reception of latest GPS sentence: "); Serial.print(t_new_sentence);
      // Serial.print(", "); Serial.println(t_end_of_sentence);

      // convert GPS data sentence from a character array to a string.
      GPS_sentence_string = String(GPS_sentence);

      // print the GPS sentence
      Serial.print("New GPS_sentence_string is "); 
      Serial.println(GPS_sentence_string.substring(0, GPS_command_string_index+1));

      // now parse the string if it corresponds to a date/time message.
      if (sentence_has_a_Z) {
        
        GPS_hour_string = GPS_sentence_string.substring(GPZDA_hour_index1, GPZDA_hour_index2);
        GPS_minutes_string = GPS_sentence_string.substring(GPZDA_minutes_index1, GPZDA_minutes_index2);
        GPS_seconds_string = GPS_sentence_string.substring(GPZDA_seconds_index1, GPZDA_seconds_index2);
        GPS_milliseconds_string = GPS_sentence_string.substring(GPZDA_milliseconds_index1, GPZDA_milliseconds_index2);
        GPS_day_string = GPS_sentence_string.substring(GPZDA_day_index1, GPZDA_day_index2);
        GPS_month_string = GPS_sentence_string.substring(GPZDA_month_index1, GPZDA_month_index2);
        GPS_year_string = GPS_sentence_string.substring(GPZDA_year_index1, GPZDA_year_index2);
  
        Serial.print("GPS time (UTC) in this sentence is " + GPS_hour_string + ":" + GPS_minutes_string + ":" + 
        GPS_seconds_string + "." + GPS_milliseconds_string);
        Serial.println("      dd/mm/yyyy = " + GPS_day_string + "/" + GPS_month_string + "/" + GPS_year_string);
  
        // now convert to integers
        GPS_hour = GPS_hour_string.toInt();
        GPS_minutes = GPS_minutes_string.toInt();
        GPS_seconds = GPS_seconds_string.toInt();
        GPS_milliseconds = GPS_milliseconds_string.toInt();
        GPS_day = GPS_day_string.toInt();
        GPS_month = GPS_month_string.toInt();
        GPS_year = GPS_year_string.toInt();
  
        // now set the RTC variables.
        RTC_hour = GPS_hour;
        RTC_minutes = GPS_minutes;
        RTC_seconds = GPS_seconds;
        RTC_day = GPS_day;
        RTC_month = GPS_month;
        RTC_year = GPS_year;
  
        // now try bumping everything by 1 second.
        bump_by_1_sec();
  
        t_bump_go = millis();
  
        // set a flag saying that we have a good proposed time to load into the RTC. We
        // will load this the next time we see a PPS 0 -> 1 transition.
        good_RTC_time_from_GPS_and_satellites = true;
        
      }
    }
  }  
}

/////////////////////////////////////////////////////////////////////////

void bump_by_1_sec(){

  // bump the RTC clock time by 1 second relative to the GPS value reported 
  // a few hundred milliseconds ago. I am using global variables for the ease
  // of doing this. Note that we're going to need to handle roll-overs from 59 
  // seconds to 0, and so forth.

    bool bump_flag;
    int place_holder;

    bool debug_echo = false;

    RTC_seconds_bumped = RTC_seconds + 1;

    // use "place_holder" this way so the timings through the two branches of the if blocks 
    // are the same
    place_holder = RTC_seconds + 1;
    
    if(int(RTC_seconds_bumped) >= 60) {
      bump_flag = true;
      RTC_seconds_bumped = 0;
      }else{
      bump_flag = false;
      RTC_seconds_bumped = place_holder;
      }
      
    place_holder = RTC_minutes + 1;
    
    // do we also need to bump the minutes?  
    if (bump_flag) {
      RTC_minutes_bumped = place_holder;
      }else{
      RTC_minutes_bumped = RTC_minutes;
      }

    // again, do this to equalize the time through the two branches of the if block
    place_holder = RTC_minutes_bumped;
    
    if(int(RTC_minutes_bumped) >= 60) {
      bump_flag = true;
      RTC_minutes_bumped = 0;
      }else{
      bump_flag = false;
      RTC_minutes_bumped = place_holder;
      }

    place_holder = RTC_hour + 1;
    
    // do we also need to bump the hours?  
    if (bump_flag) {
      RTC_hour_bumped = place_holder;
      }else{
      RTC_hour_bumped = RTC_hour;
      }

    place_holder = RTC_hour;

    if(int(RTC_hour_bumped) >= 24) {
      bump_flag = true;
      RTC_hour_bumped = 0;
      }else{
      bump_flag = false;
      RTC_hour_bumped = place_holder;
      }

    place_holder = RTC_day + 1;
    
    // do we also need to bump the days?  
    if (bump_flag) {
      RTC_day_bumped = place_holder;
      }else{
      RTC_day_bumped = RTC_day;
      }

    // do we need to bump the month too? Note the stuff I do to make both paths
    // through the if blocks take the same amount of execution time.
    
    int nobody_home;
    int days_in_month = 31;

    // 30 days hath September, April, June, and November...
    if (int(RTC_month) == 9 || int(RTC_month) == 4 || int(RTC_month) == 6 || int(RTC_month) == 11) {
      days_in_month = 30;
    }else{
      nobody_home = 99;
    }
      
    // ...all the rest have 31, except February...
    if (int(RTC_month) == 2 && (int(RTC_year) % 4)) {
      days_in_month = 28;
    }else{
      nobody_home = 99;
    }
    
    // ...leap year!
    if (int(RTC_month) == 2 && !(int(RTC_year) % 4)) {
      days_in_month = 29;
    }else{
      nobody_home = 99;
    }

    place_holder = RTC_day_bumped;
    
    if(int(RTC_day_bumped) > days_in_month) {
      bump_flag = true;
      RTC_day_bumped = 1;
      }else{
      bump_flag = false;
      RTC_day_bumped = place_holder;
      }

    if (bump_flag) {
      RTC_month_bumped = RTC_month + 1;
      }else{
      RTC_month_bumped = RTC_month;
      }

    place_holder = RTC_month_bumped;
              
    //... and also bump the year?
    
    if(int(RTC_month_bumped) > 12) {
      bump_flag = true;
      RTC_month_bumped = 1;
      }else{
      bump_flag = false;
      RTC_month_bumped = place_holder;
      }

    if (bump_flag) {
      RTC_year_bumped = RTC_year + 1;
      }else{
      RTC_year_bumped = RTC_year;
      }

    // keep track of when we have the proposed RTC time value ready for loading
    time_ms_bumped_RTC_time_ready = millis();

    if (debug_echo) {
      // now print the newly bumped time:
      Serial.print("Now have a proposed (1 second bumped) time ready at (ms) ");
      Serial.println(time_ms_bumped_RTC_time_ready, DEC);       
      Serial.print("Proposed (1 second bumped) time: ");
      Serial.print(RTC_hour_bumped, DEC); Serial.print(':');
      if(RTC_minutes_bumped < 10) Serial.print("0");
      Serial.print(RTC_minutes_bumped, DEC); Serial.print(':');
      if(RTC_seconds_bumped < 10) Serial.print("0");
      Serial.print(RTC_seconds_bumped, DEC); 
      Serial.print("   Date (dd/mm/yyyy): ");
      Serial.print(RTC_day_bumped, DEC); Serial.print('/');
      if(RTC_month_bumped < 10) Serial.print("0");
      Serial.print(RTC_month_bumped, DEC); Serial.print("/");
      Serial.println(RTC_year_bumped, DEC);
    }
  
}    

/////////////////////////////////////////////////////////////////////////

// also at the end reset the GPS to the usual configuration.

////////////////// That's it! ////////////////////////
