/******************************************************************************
Force_Sensitive_Resistor_Example.ino
Example sketch for SparkFun's force sensitive resistors
  (https://www.sparkfun.com/products/9375)
Jim Lindblom @ SparkFun Electronics
April 28, 2016

Create a voltage divider circuit combining an FSR with a 3.3k resistor.
- The resistor should connect from A0 to GND.
- The FSR should connect from A0 to 3.3V
As the resistance of the FSR decreases (meaning an increase in pressure), the
voltage at A0 should increase.

Development environment specifics:
Arduino 1.6.7
******************************************************************************/
const int FSR_PIN0 = A0; // Pin connected to FSR/resistor divider
const int FSR_PIN1 = A1; // Pin connected to FSR/resistor divider
const int FSR_PIN2 = A2; // Pin connected to FSR/resistor divider
const int FSR_PIN3 = A3; // Pin connected to FSR/resistor divider

// Measure the voltage at 5V and resistance of your 10k resistor, and enter
// their value's below:
const float VCC = 4.67; // Measured voltage of Arduino 5V line
const float R_DIV = 9950.0; // Measured resistance of 10k resistor

void setup() 
{
  Serial.begin(9600);
  pinMode(FSR_PIN0, INPUT);
}

void loop() 
{
  int fsrADC = analogRead(FSR_PIN0);
  // If the FSR has no pressure, the resistance will be
  // near infinite. So the voltage should be near 0.
  if (fsrADC != 0) // If the analog reading is non-zero
  {
    // Use ADC reading to calculate voltage:
    float fsrV = fsrADC * VCC / 1023.0;
    // Use voltage and static resistor value to 
    // calculate FSR resistance:
    float fsrR = R_DIV * (VCC / fsrV - 1.0);
    Serial.println("Resistance: " + String(fsrR) + " ohms");
    // Guesstimate force based on slopes in figure 3 of
    // FSR datasheet:
    float force;
    float fsrG = 1.0 / fsrR; // Calculate conductance
    // Break parabolic curve down into two linear slopes:
    if (fsrR <= 600) 
      force = (fsrG - 0.00075) / 0.00000032639;
    else
      force =  fsrG / 0.000000642857;
    Serial.println("Force: " + String(force) + " g");
    Serial.println();

    delay(500);
  }
  else
  {
    // No pressure detected
  }
}
