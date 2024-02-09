
// ========================================
// Dynamixel XL-320 Arduino library example
// ========================================

// Read more:
// https://github.com/hackerspace-adelaide/XL320

#include "XL320.h"

// Name your robot!
XL320 robot;
// If you want to use Software Serial, uncomment this line
#include <SoftwareSerial.h>

// Set the SoftwareSerial RX & TX pins
SoftwareSerial mySerial(19, 18); // (RX, TX)

// Set some variables for incrementing position & LED colour
char rgb[] = "rgbypcwo";
int servoPosition = 0;
int ledColour = 0;

// 3 servoID to talk to
int servoID1 = 1; // right
int servoID2 = 2; // left
int servoID3 = 3; // arm


void setup() {

  // Talking standard serial, so connect servo data line to Digital TX 1
  // Comment out this line to talk software serial
  Serial.begin(115200);

  // Setup Software Serial
  //mySerial.begin(115200);

  // Initialise your robot
  robot.begin(Serial); // Hand in the serial object you're using
  
  // I like fast moving servos, so set the joint speed to max!
  robot.setJointSpeed(servoID1, 500);
  robot.setJointSpeed(servoID2, 1023);
  robot.setJointSpeed(servoID3, 1023);
  

}

void loop() {


// Function onReceive





close(servoID1,100);
open(servoID1,0);

}

/*################################################
 Reception of 16 bits from the rasberry Pi (ex : 100 11001)

*/
/*
 1: close arm (ID servo , angle)
 2: open arm (ID servo , angle)
 3: move up (ID servo , angle)
 4: move down (ID servo , angle)

*/
void readInstruction(uint8_t command){
  int functionChoosen = (command >> 5);
  int angle = (command & 0b11111);
  switch(functionChoosen){
    case 1:
      close(servoID, angle);
      break;
    case 2:
      open(servoID, angle);
      break;
    case 3:
      
      break;
    case 4:
      
      break;
    case 5:
      
      break;
    case 6:
      
      break;
    case 7:
      
      break;
    case 8:
      
      break;
    case 9:
      
      break;
    case 10:
      
      break;
    case 11:
      
      break;
    case 12:
      
      break;
    default:
      Serial.println("Default");
  }
}

void down(int servoID, int angle ){

}
void midle(int servoID, int angle){

}
void up(int servoID, int angle){

}

int angleToPosition(int angle) {
  // Proporsional conversion from 0 to 300° to (0,1023)
  return map(angle, 0, 300, 0, 1023);

}
// open a servo from an angle
void open(int servoID, int angle){
  robot.moveJoint(servoID, angleToPosition(angle)); // set 0 to open position 
  delay(2500); // Set a delay to account for the receive delay period
  robot.LED(servoID1, &rgb[4] );
  delay(100);
}
 // close a servo from an angle
 void close(int servoID, int angle){
  robot.moveJoint(servoID, angleToPosition(angle)); // close position 
  delay(2500); // Set a delay to account for the receive delay period
  robot.LED(servoID1, &rgb[0] );
  delay(100);
 }