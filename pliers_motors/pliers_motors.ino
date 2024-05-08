#include "XL320.h"
#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>

Servo servo;

XL320 robot;

#include <SoftwareSerial.h>

void performAction(int);


SoftwareSerial mySerial(10,11); // (RX, TX)

char rgb[] = "rgbypcwo";
int ledColour = 0;

// 3 servoID to talk to
int servo_left = 1; // left
int servo_right = 2; // right
int servo_arm = 3; // arm

int switch_pin_left = 5;
int switch_pin_right = 6;

int servo_9g_pin = 9;

int operationToPerform = -1;

void receive_event(int byteCount) {
  while (Wire.available()) {
    int receivedData = Wire.read();
    Serial.println(receivedData);
    operationToPerform = receivedData;
    //erformAction(receivedData);
  }
}

void requestEvent() {
  Wire.write(operationToPerform != -1);
}

void setup() {
  //Serial
  Serial.begin(115200);

  //Servo xl320
  mySerial.begin(115200);
  robot.begin(mySerial);
  
  //Wire I2C
  Wire.begin(10);
  Wire.onReceive(receive_event);
  Wire.onRequest(requestEvent);

  //Servo 9g
  servo.attach(servo_9g_pin);

  //switch
  pinMode(switch_pin_left, INPUT);
  pinMode(switch_pin_right, INPUT);

  //
  robot.setJointSpeed(servo_right, 523);
  robot.setJointSpeed(servo_left, 523);
  robot.setJointSpeed(servo_arm, 300);
}

void loop() {
  /*if (Serial.available() > 0) {
    // Lire l'entier envoyé depuis le moniteur série
    int valeur = Serial.parseInt();
    performAction(valeur);
    // Afficher la valeur lue dans le moniteur série
    Serial.print("La valeur lue est : ");
    Serial.println(valeur);
  }*/
  Serial.println(operationToPerform);
  if (operationToPerform != -1) {
    performAction(operationToPerform);
    operationToPerform = -1;
  }
  delay(100);
}

//is right switch triggered
bool switch_right(){
  return digitalRead(switch_pin_right);
}

//is left switch trigered
bool switch_left(){
  return digitalRead(switch_pin_left);
}

//ARM SECTION

//pince Up
void up(){
  robot.moveJoint(servo_arm, 900);
  delay(2000);
}

//pince Down Small pot
void downSmall(){
  robot.moveJoint(servo_arm, 500);
  delay(2000);
}

//pince Down Big pot
void downBig(){
  robot.moveJoint(servo_arm, 540);
  delay(2000);
}

//pince Down for potting
void downPotting(){
  robot.moveJoint(servo_arm, 700);
  delay(1000);
}

//PINCE SECTION

//OPEN PART

// open the both pince
void open(){
  for(int i=0; i<10; i++){
  robot.moveJoint(servo_right, 223);
  delay(50);
  robot.moveJoint(servo_left, 800);
  delay(50);
  }
}

// open just the left
void openLeft(){
  robot.moveJoint(servo_left, 800);
  delay(1000);
}


// open just the right
void openRight(){
  robot.moveJoint(servo_right, 223);
  delay(1000);
}

//CLOSE PART

// close the pince Small pot
void closeSmall(){
  for(int i=0; i<10; i++){
  robot.moveJoint(servo_right, 553);
  delay(50);
  robot.moveJoint(servo_left, 470);
  delay(50);
  }
}

// close the pince Small pot left
void closeSmallLeft(){
  robot.moveJoint(servo_left, 470);
  delay(1000);
}

// close the pince Small pot right
void closeSmallRight(){
  robot.moveJoint(servo_right, 553);
  delay(1000);
}

// close the pince Big pot
void closeBig(){
  for(int i=0; i<10; i++){
  robot.moveJoint(servo_right, 473);
  delay(50);
  robot.moveJoint(servo_left, 550);
  delay(50);
  }
}

// close the pince Big pot left
void closeBigLeft(){
  robot.moveJoint(servo_left, 550);
  delay(1000);
}

// close the pince Big pot left
void closeBigRight(){
  robot.moveJoint(servo_right, 473);
  delay(1000);
}

//SECTION SERVO 9G

//9g_servo position back
void Servo_9g_back(){
  servo.write(40);
}

//9g_servo position Small pot
void Servo_9g_Small(){
  servo.write(160);
}

//9g_servo position Big pot
void Servo_9g_Big(){
  servo.write(100);
}

//SECTION BIG FUNCTIONS

void grabSmall(){
  Servo_9g_Small();
  if(switch_left())
    openRight();
  if(switch_right())
    openLeft();
  else
    open();
  downSmall();
  closeSmall();
  up();
  Servo_9g_Big();
}

void grabBig(){
  Servo_9g_Big();
  if(switch_left())
    openRight();
  if(switch_right())
    openLeft();
  else
    open();
  downBig();
  closeBig();
  up();
}

void Poting(){
  downPotting();
  open();
  up();
  grabBig();
}

void Release(){
  downBig();
  open();
  up();
  Servo_9g_Small();
}

void Search(){
  while(!switch_left() && !switch_right()){
    if(!switch_left()){
      closeSmallLeft();
      if(!switch_left())
        openLeft();
    }
    if(!switch_right()){
      closeSmallRight();
      if(!switch_right())
        openRight();
    }
  }
  //Send 1 to master to inform that two pot have been found
  Wire.beginTransmission(1);//change by master ID
  Wire.write(1);
  Wire.endTransmission();
}

void performAction(int action) {
  switch(action) {
    case 0:
      grabSmall();
      break;
    case 1:
      grabBig();
      break;
    case 2:
      Poting();
      break;
    case 3:
      Release();
      break;
    case 4:
      downSmall();
      break;
    case 5:
      downBig();
      break;
    case 6:
      downPotting();
      break;
    case 7:
      open();
      break;
    case 8:
      closeSmall();
      break;
    case 9:
      closeBig();
      break;
    case 10:
      Servo_9g_Small();
      break;
    case 11:
      Servo_9g_Big();
      break;
    case 12:
      Servo_9g_back();
      break;
    case 13:
      up();
      break;
    default:
      // Handle default case, if needed
      break;
  }
}
