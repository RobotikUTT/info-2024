#include "XL320.h"
#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>

#define LEFT 0
#define RIGHT 1
#define ARM 2
#define uint unsigned int

Servo servo;

XL320 robot;

#include <SoftwareSerial.h>

void performAction(int);


SoftwareSerial mySerial(10,11); // (RX, TX)

char rgb[] = "rgbypcwo";
int ledColour = 0;

int servos[2][3] = {
  {1, 2, 3},
  {4, 5, 6},
  {7, 8, 9},
};

bool pliersFull[3][2] = {
  {false, false},
  {false, false},
  {false, false},
};

int switchPins[2][2] = {
  {5, 6},
  {7, 8},
  {9, 10},
};

// int servo_9g_pin = 9;

struct Operation {
  uint command;
  uint arm;
};

Operation operationToPerform {-1, 0};

const int startSwitch = ;

void receive_event(int byteCount) {
  if (Wire.available() != 2) {
    Serial.println("Error, found an anormal number of elements transmitted");
  }
  uint command = Wire.read();
  uint arm = Wire.read();
  operationToPerform.command = command;
  operationToPerform.arm = arm;
}

void requestEvent() {
  Wire.write(operationToPerform.command != -1);
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
  // servo.attach(servo_9g_pin);

  //switch
  pinMode(switchPins[0][0], INPUT);
  pinMode(switchPins[0][0], INPUT);
  pinMode(switchPins[1][0], INPUT);
  pinMode(switchPins[1][0], INPUT);

  for (uint arm = 0; arm < 3 arm++) {
    robot.setJointSpeed(servos[arm][RIGHT], 523);
    robot.setJointSpeed(servos[arm][LEFT], 523);
    robot.setJointSpeed(servos[arm][ARM], 300);
  }

  pinMode(startSwitch, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    // Lire l'entier envoyé depuis le moniteur série
    int valeur = Serial.parseInt();
    // Afficher la valeur lue dans le moniteur série
    Serial.print("La valeur lue est : ");
    Serial.println(valeur);
    performAction(valeur, 0);
  }
  //Serial.println(operationToPerform.command);
  if (operationToPerform.command != -1) {
    performAction(operationToPerform.command, operationToPerform.arm);
    operationToPerform.command = -1;
  }
  delay(100);
}

//is right switch triggered
bool switch_pressed(uint arm, uint plier){
  return digitalRead(switchPins[arm][plier]);
}

//ARM SECTION

//pince Up
void up(uint arm) {
  robot.moveJoint(servos[arm][ARM], 900);
  delay(2000);
}

//pince Down Small pot
void downSmall(uint arm){
  robot.moveJoint(servos[arm][ARM], 500);
  delay(2000);
}

//pince Down Big pot
void downBig(uint arm){
  robot.moveJoint(servos[arm][ARM], 540);
  delay(2000);
}

//pince Down for potting
void downPotting(uint arm){
  robot.moveJoint(servos[arm][ARM], 700);
  delay(1000);
}

//PINCE SECTION

//OPEN PART

// open the both pince
void openBoth(uint arm){
  for(int i=0; i<10; i++){
    robot.moveJoint(servos[arm][RIGHT], 223);
    delay(50);
    robot.moveJoint(servos[arm][LEFT], 800);
    delay(50);
  }
}

void openSingle(uint arm, uint servo) {
  robot.moveJoint(servos[arm][servo], servo == LEFT ? 800 : 223);
  delay(1000);
}

//CLOSE PART

// close the pince Small pot
void closeSmallBoth(uint arm){
  for(int i=0; i<10; i++){
    robot.moveJoint(servos[arm][RIGHT], 553);
    delay(50);
    robot.moveJoint(servos[arm][LEFT], 470);
    delay(50);
  }
}

void closeSmallSingle(uint arm, uint servo) {
  robot.moveJoint(servos[arm][servo], servo == LEFT ? 470 : 553);
  delay(1000);
}

// close the pince Big pot
void closeBigBoth(uint arm) {
  for(int i=0; i<10; i++){
    robot.moveJoint(servos[arm][RIGHT], 473);
    delay(50);
    robot.moveJoint(servos[arm][LEFT], 550);
    delay(50);
  }
}

void closeBigSingle(uint arm, uint servo) {
  robot.moveJoint(servos[arm][servo], servo == LEFT ? 550 : 473);
  delay(1000);
}

//SECTION SERVO 9G

//9g_servo position back
// void Servo_9g_back(){
  // servo.write(40);
// }

//9g_servo position Small pot
// void Servo_9g_Small(){
  // servo.write(160);
// }

//9g_servo position Big pot
// void Servo_9g_Big(){
//   servo.write(100);
// }

//SECTION BIG FUNCTIONS

void Poting(uint arm){
  downPotting(arm);
  openBoth(arm);
  up(arm);
}

void OpenUnfullPliers(uint arm) {
  if (!pliersFull[arm][LEFT] && !pliersFull[arm][RIGHT]) {
    openBoth(arm);
  } else if (!pliersFull[arm][LEFT]) {
    openSingle(arm, LEFT);
  } else if (!pliersFull[arm][RIGHT]) {
    openSingle(arm, RIGHT);
  }
}

void ReleaseOnGround(uint arm){
  Serial.println("Releasing on ground");
  downBig(arm);
  openBoth(arm);
  up(arm);
  pliersFull[arm][LEFT] = false;
  pliersFull[arm][RIGHT] = false;
  // Servo_9g_Small();
}

void ReleaseOnGarden(uint arm) {
  downSmall(arm);
  openBoth(arm);
  up(arm);
  pliersFull[arm][LEFT] = false;
  pliersFull[arm][RIGHT] = false;
}

void ArmDown(uint arm) {
  downBig(arm);
}

void GrabPot(uint arm) {
  closeBigBoth(arm);
  up(arm);
  pliersFull[arm][LEFT] = switch_pressed(arm, LEFT);
  pliersFull[arm][RIGHT] = switch_pressed(arm, RIGHT);
}

void GrabPlant(uint arm) {
  closeSmallBoth(arm);
}

/*void Search(){
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
}*/

void performAction(uint action, uint arm) {
  switch(action) {
    case 0:
      GrabPlant(arm);
      break;
    case 1:
      GrabPot(arm);
      break;
    case 2:
      Poting(arm);
      break;
    case 3:
      ReleaseOnGround(arm);
      break;
    case 4:
      ReleaseOnGarden(arm);
      break;
    case 5:
      OpenUnfullPliers(arm);
      break;
    case 6:
      ArmDown(arm);
      break;
    //case 7:
    //  Search(arm);
    default:
      // Handle default case, if needed
      break;
  }
}
