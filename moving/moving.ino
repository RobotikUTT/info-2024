#include <SoftwareSerial.h>
#include <Wire.h>

#define DEV_ENV true  // Wheather this is production or development environment. In production environment, nothing will be printed out to the console

//-------------------------------------------------------------------
////////////////////////   Pin CNC shield     ///////////////////////
//-------------------------------------------------------------------

// Steppers Controller 
#define xStepPin         2  //PD2 -> set PORTD |= 0b00000100 ou 0x04   turn off PORTE &= 0b11111011 ou 0xFB
#define yStepPin         3  //PD3 -> set PORTD |= 0b00001000 ou 0x08   eteindre PORTE &= 0b11110111 ou 0xF7
#define zStepPin         4  //PD4 -> set PORTD |= 0b00010000 ou 0x10   eteindre PORTG &= 0b11101111 ou 0xEF
#define aStepPin         12 
#define xDirPin          5  //PD5 -> set PORTD |= 0b00100000 ou 0x20   eteindre PORTE &= 0b11011111 ou 0xDF
#define yDirPin          6  //PD6 -> set PORTD |= 0b01000000 ou 0x40   eteindre PORTH &= 0b10111111 ou 0xBF
#define zDirPin          7  //PD7 -> set PORTD |= 0b10000000 ou 0x80   eteindre PORTH &= 0b01111111 ou 0x7F
#define aDirPin          13
#define enablePin        8

// Mesure tension
#define tensionBatteriePin    A7       //Analogique 7
#define facteurTension        0.01659  //Pont diviseur de tension + lecture sur 10 bits.
#define seuilAlerteTension    11       //Volts
#define seuilCritiqueTension  10       //Volts

// Step and Direction (doc : Mega Pinout - how to use PORTX)
#define STEP_HIGH_X       PORTE |= _BV(PE4)   // Activation Pin Pas X
#define STEP_LOW_X        PORTE &= ~_BV(PE4)  // Désactivation Pin Pas X
#define STEP_HIGH_Y       PORTE |= _BV(PE5)   // Activation Pin Pas Y
#define STEP_LOW_Y        PORTE &= ~_BV(PE5)  // Désactivation Pin Pas Y
#define STEP_HIGH_Z       PORTG |= _BV(PG5)   // Activation Pin Pas Z
#define STEP_LOW_Z        PORTG &= ~_BV(PG5)  // Désactivation Pin Pas Z
#define STEP_HIGH_A       PORTB |= _BV(PB6)
#define STEP_LOW_A        PORTB &= ~_BV(PB6)
#define ANTI_CLOCKWISE_X  PORTE |= _BV(PE3)
#define CLOCKWISE_X       PORTE &= ~_BV(PE3)
#define ANTI_CLOCKWISE_Y  PORTH |= _BV(PH3)
#define CLOCKWISE_Y       PORTH &= ~_BV(PH3)
#define ANTI_CLOCKWISE_Z  PORTH |= _BV(PH4)
#define CLOCKWISE_Z       PORTH &= ~_BV(PH4)
#define ANTI_CLOCKWISE_A  PORTB |= _BV(PB7)
#define CLOCKWISE_A       PORTB &= ~_BV(PB7)

// Types of moves. Either NOT_MOVING, TRANSLATION or ROTATION
#define NOT_MOVING   0
#define TRANSLATION  1
#define ROTATION     2


//-------------------------------------------------------------------
///////////////////////////  Constantes  ////////////////////////////
//-------------------------------------------------------------------

// Conversion
#define stepByMeter    4680     //facteur experimental = 1.03 ; demi-pas alors que la valeur a été trouvée pour des quarts de pas
const float rRobot = 0.119;     //0.1265 théoriquement

// Determined
const PROGMEM long dtMaxSpeed = 1000;           // Microsecondes entre 2 pas à la vitesse maximale
const PROGMEM long acc = 2.5 * pow(10, 8);      // µs² / pas (inverse de l'acceleration)
const PROGMEM long dec = 2.5 * pow(10, 8);      // µs² / pas (inverse de la deceleration)
//const PROGMEM long tempsAcc = 1.0 * pow(10, 6); // Temps d'accélération en µs
//const PROGMEM long tempsDec = 1.0 * pow(10, 6); // Temps de décélération en µs

// Calculed
unsigned long tempsAcc = acc / dtMaxSpeed; // Temps d'accélération en µs
unsigned long tempsDec = dec / dtMaxSpeed; // Temps de décélération en µs
unsigned int  nbEtapesAcc = tempsAcc / (2 * dtMaxSpeed); // Nombres de pas parcourus pendant l'accelération (intégrale de la vitesse)
unsigned int  nbEtapesDec = tempsDec / (2 * dtMaxSpeed); // Nombres de pas parcourus pendant la décélération (intégrale de la vitesse)
//const PROGMEM unsigned int  nbEtapesAcc = 0; // Nombres de pas parcourus pendant l'accelération (intégrale de la vitesse)
//const PROGMEM unsigned int  nbEtapesDec = 0; // Nombres de pas parcourus pendant la décélération (intégrale de la vitesse)
float dtMaxAcc = 1. / sqrt(2. / (tempsAcc * dtMaxSpeed)); // Plus grand intervalle de temps entre deux pas à l'accélération
float dtMaxDec = 1. / sqrt(2. / (tempsDec * dtMaxSpeed)); // Plus grand intervalle de temps entre deux pas à la décélération

//-------------------------------------------------------------------
//////////////////////  Variables Déplacement  //////////////////////
//-------------------------------------------------------------------

// Consignes
float xCenter = 0;
float yCenter = 0;
float angleConsigne = 0;
int dtSpeed = dtMaxSpeed;

// Rotational Direction
bool dirX = false;             //
bool dirY = false;             // sens trigo robot : true, sens horraire robot : false
bool dirZ = false;             //
bool dirA = false;             //

// Motor Relative Speed
float ratioVitX = 1;
float ratioVitY = 1;
float ratioVitZ = 1;

// Step left and done for each Motor
volatile unsigned long stepDoneX = 0;
volatile unsigned long stepDoneY = 0;
volatile unsigned long stepDoneZ = 0;
volatile unsigned long stepDoneA = 0;
volatile unsigned long stepLeftX = 0;
volatile unsigned long stepLeftY = 0;
volatile unsigned long stepLeftZ = 0;
volatile unsigned long stepLeftA = 0;

// Control Boolean
volatile bool isMoving = false;   // Le robot est en mouvement
volatile bool isAcc = false;      // Le robot est en phase d'accélération
volatile bool isDec = false;      // Le robot est en phase de décélération
bool lastMove = false;            // false = Translation, true = Rotation

// Stages
volatile unsigned long trajectStage = 0;
volatile unsigned long t = 0;               // Temps actuel
volatile unsigned long prevT = 0;           // Stockage du temps en microseconde auquel s'est passé la dernière étape
volatile unsigned int newDt = 5000;         // Intervalle de temps en microseconde avant la prochaine étape
volatile unsigned long s;                   // Nombres d'étapes restantes
unsigned long nbTotalStages;                // Nombres total d'étapes à réaliser

//-------------------------------------------------------------------
/////////////////////     Autres Variables     //////////////////////
//-------------------------------------------------------------------

// Battery
bool batterieAlerte = false;
bool batterieCritique = false;
const unsigned int delaiCheckBatterie = 5000; //milisecondes
unsigned long prevCheckBatterie;
int onSeBallade = 0;
int moveType = NOT_MOVING;

//-------------------------------------------------------------------
///////////////////////    Initialisation    ////////////////////////
//-------------------------------------------------------------------

void setup() {
  pinMode(xStepPin, OUTPUT);  // Pin pas moteur x en mode OUTPUT
  pinMode(yStepPin, OUTPUT);  // Pin pas moteur y en mode OUTPUT
  pinMode(zStepPin, OUTPUT);  // Pin pas moteur z en mode OUTPUT
  pinMode(aStepPin, OUTPUT);  // Pin pas moteur a en mode OUTPUT
  pinMode(xDirPin, OUTPUT);   // Pin dir moteur x en mode OUTPUT
  pinMode(yDirPin, OUTPUT);   // Pin dir moteur y en mode OUTPUT
  pinMode(zDirPin, OUTPUT);   // Pin dir moteur z en mode OUTPUT
  pinMode(aDirPin, OUTPUT);   // Pin dir moteur a en mode OUTPUT
  pinMode(enablePin, OUTPUT); // Pin alimentation moteurs en mode OUTPUT
  
  //#if DEV_ENV
    Serial.begin(9600);   // Démarrage port série
    Serial.setTimeout(1);   // Délai d'attente port série 1ms
  //#endif

  AlimMoteurs(true);         // On éteint les moteurs (par sécurité)

  Wire.begin(1);
  Wire.onReceive(onReceive);
  Wire.onRequest(getRelativePositionFromStart);
  #if DEV_ENV
    Serial.println("Initialized !");
  #endif
}

//-------------------------------------------------------------------
///////////////////////////     Loop      ///////////////////////////
//-------------------------------------------------------------------

void loop() {
  if (isMoving) {       // Si on est en mouvement
    MoveForward();        // On passe à l'étape d'après (si le temps necessaire s'est écoulé)
  }
}

void testEngines() {
  Start();
  long lastTime = 0;
  long t;
  while (true) {
    t = micros();
    if (t - lastTime > dtMaxSpeed) {
      lastTime = t;
      MotorStepX();
      MotorStepY();
      MotorStepZ();
    }
  }
}

//-------------------------------------------------------------------
//////////////////////////   Functions    ///////////////////////////
//-------------------------------------------------------------------

void Start() { // Lancement du mouvement
  InitVariablesMvmt();
  AlimMoteurs(true);
}

void InitVariablesMvmt() { // Initialisation des variables
  isMoving = true;
  isAcc = true;
  isDec = false;
  trajectStage = 0;
  stagesLeft = nbTotalStages - trajectStage;
  stepDoneX = 0;
  stepDoneY = 0;
  stepDoneZ = 0;
  prevT = 0;
}

void StepCalculRotation(float xCenter, float yCenter, float angle) {
  if (sqrt(sq(xCenter) + sq(yCenter)) == rRobot) yCenter += 0.001;
  float distXX = rRobot * cos(-PI / 6) - xCenter;
  float distYX = rRobot * sin(-PI / 6) - yCenter;
  float distXY = rRobot * cos(-5 * PI / 6) - xCenter;
  float distYY = rRobot * sin(-5 * PI / 6) - yCenter;
  float distXZ = rRobot * cos(PI / 2) - xCenter;
  float distYZ = rRobot * sin(PI / 2) - yCenter;
  float angleX = arctan(distXX, distYX) + PI / 2;
  float angleY = arctan(distXY, distYY) + PI / 2;
  float angleZ = arctan(distXZ, distYZ) + PI / 2;
  float angleA = 
  float distToDoX = angle * sqrt(sq(distXX) + sq(distYX)); // longueur d'arc de rayon centre-point de contact
  float distToDoY = angle * sqrt(sq(distXY) + sq(distYY));
  float distToDoZ = angle * sqrt(sq(distXZ) + sq(distYZ));
  lastMove = true;
  long MotorStepX = (float) distToDoX * stepByMeter * cos(angleX + (2. / 3) * PI);     //
  long MotorStepY = (float) distToDoY * stepByMeter * cos(angleY - (2. / 3) * PI );    // Calcul des distances à parcourir
  long MotorStepZ = (float) distToDoZ * stepByMeter * cos(angleZ);                     //
  MouvementSynchrone(MotorStepX, MotorStepY, MotorStepZ);
}

void StepCalculTranslation(float x, float y) { // Calcul des pas à faire sur chaque moteurs
  float angle = arctan(x, y);
  float totalDistanceStep = sqrt(sq(x) + sq(y)) * stepByMeter;
  long MotorStepX = (float) totalDistanceStep * cos(borner(angle + (2. / 3) * PI));     //
  long MotorStepY = (float) totalDistanceStep * cos(borner(angle - (2. / 3) * PI ));    // Calcul des distances à parcourir
  long MotorStepZ = (float) totalDistanceStep * cos(borner(angle));                     //
  lastMove = false;
  MouvementSynchrone(MotorStepX, MotorStepY, MotorStepZ);
}

void MouvementSynchrone(long x, long y, long z) {
  MotorsDirection((x >= 0) ? sensX = 1 : sensX = 0, (y >= 0) ? sensY = 1 : sensY = 0, (z >= 0) ? sensZ = 1 : sensZ = 0);
  stepLeftX = abs(x);
  stepLeftY = abs(y);
  stepLeftZ = abs(z);
  nbTotalStages = max(max(stepLeftX, stepLeftY), stepLeftZ);                   //
  ratioVitX = (float) stepLeftX / nbTotalStages;                                     // Calcul et Stockage du vecteur
  ratioVitY = (float) stepLeftY / nbTotalStages;                                     //  directionnel souhaité
  ratioVitZ = (float) stepLeftZ / nbTotalStages;                                     //
  tempsAcc = acc / dtSpeed;
  tempsDec = dec / dtSpeed;
  dtMaxAcc = 1. / sqrt(2. / (tempsAcc * dtSpeed));
  dtMaxDec = 1. / sqrt(2. / (tempsDec * dtSpeed));
  nbEtapesAcc = tempsAcc / (2 * dtSpeed); // Nombres de pas parcourus pendant l'accelération (intégrale de la vitesse)
  nbEtapesDec = tempsDec / (2 * dtSpeed); // Nombres de pas parcourus pendant la décélération (intégrale de la vitesse)
  if ((nbEtapesAcc + nbEtapesDec) > nbTotalStages) {
    float total = nbEtapesAcc + nbEtapesDec;
    nbEtapesAcc = nbEtapesAcc / total * nbTotalStages;
    nbEtapesDec = nbEtapesDec / total * nbTotalStages;
  }
}

void MoveForward() { // Passe à la prochaine étape du mouvement si l'intervalle de temps est respecté
  t = micros();
  if (isAcc) { // Passage a la prochaine étape pendant l'accélération
    if (t - prevT >= newDt) {
      Move();
      prevT = t;
      ActualisertrajectStag();
      newDt = dtMaxAcc / Sqrt(trajectStage);
      if (trajectStage >= nbEtapesAcc) { //Fin de l'acc
        isAcc = false;
      }
      if (s <= nbEtapesDec) {
        isDec = true;
        isAcc = false;
      }
    }
  } else if (isDec) {
    if (t - prevT >= newDt) {
      Move();
      prevT = t;
      ActualisertrajectStag();
      newDt = dtMaxDec / Sqrt(s);
      if (s <= 0) {
        isMoving = false;
      }
    }
  } else {
    if (t - prevT >= dtSpeed) {
      Move();
      prevT = t;
      ActualisertrajectStag();
      if (s <= nbEtapesDec) isDec = true; //Debut décélération
    }
  }
}

void ActualisetrajectStage() {
  trajectStage++;
  s = nbTotalStages - trajectStage;
}

void Move() { // Commande des moteurs
  if (s >= 0) {     // >= 0 pour ne pas perdre les derniers pas
    if (ratioVitX * trajectStage >= stepDoneX) {
      MotorStepX();
      stepDoneX++;
    }
    if (ratioVitY * trajectStage >= stepDoneY) {
      MotorStepY();
      stepDoneY++;
    }
    if (ratioVitZ * trajectStage >= stepDoneZ) {
      MotorStepZ();
      stepDoneZ++;
    }
  }
}

//-------------------------------------------------------------------
/////////////////////////  Math Functions  //////////////////////////
//-------------------------------------------------------------------

double arctan(float x, float y) {
  if (abs(x) < 0.001) {
    return (y / abs(y)) * PI / 2;
  } else if (x > 0) {
    return atan(y / x);
  } else {
    return borner(atan(y / x) + PI);
  }
}

float borner(float angle) {                   //
  if (angle > PI) {                           //
    return angle - 2. * PI;                   //
  } else if (angle <= PI) {                   // On remet l'angle entre -180 et 180
    return angle + 2. * PI;                   //
  }                                           //
}                                             //

uint16_t Sqrt(uint16_t input) { // Fonction de calcul de racine plus rapide trouvée sur https://gist.github.com/devgru/5006529
  uint16_t result = 0;
  uint16_t one = 1u << 14;
  while (one > input) one /= 4;
  while (one != 0) {
    if (input >= result + one) {
      result += one;
      input -= result;
      result += one;
    }
    result /= 2;
    one /= 4;
  }
  return result;
}

//-------------------------------------------------------------------
////////////////////////  Motor Functions  //////////////////////////
//-------------------------------------------------------------------

void AlimMoteurs(bool power) { // Alimentation ou coupure du courant des moteurs
  digitalWrite(enablePin, !power);
}

void MotorsDirection(bool X, bool Y, bool Z) {
  X ? ANTI_CLOCKWISE_X : CLOCKWISE_X    ; // direction choice
  Y ? ANTI_CLOCKWISE_Y : CLOCKWISE_Y    ; 
  Z ? ANTI_CLOCKWISE_Z : CLOCKWISE_Z    ; 
}

void MotorStepX() {
  STEP_HIGH_X;                 //set pin to HIGH
  STEP_LOW_X;                  //set pin to LOW
}

void MotorStepY() {
  STEP_HIGH_Y;                 //set pin to HIGH
  STEP_LOW_Y;                  //set pin to LOW
}

void MotorStepZ() {
  STEP_HIGH_Z;                 //set pin to HIGH
  STEP_LOW_Z;                  //set pin to LOW
}

void MotorStepA() {
  STEP_HIGH_A;                 //set pin to HIGH
  STEP_LOW_A;                  //set pin to LOW
}

/** CALLBACKS FROM WIRE **/

/*
This function is called automatically when we receive something from the master throught the Wire.
*/
void onReceive() {
  #if DEV_ENV
    Serial.print("Reception consigne : ");
  #endif
  char command = Wire.read();
  #if DEV_ENV
    Serial.print(command, DEC);
  #endif
  int speedPercentage;
  switch (command) {
    case 0 : // Arret d'urgence
      #if DEV_ENV
        Serial.println(" : Arret");
      #endif
      isMoving = false;
      moveType = NOT_MOVING;
      AlimMoteurs(false);
      break;
    case 1 :  // Translation X,Y
      xCenter = readFloatFromWire();
      yCenter = readFloatFromWire();
      speedPercentage = Wire.read();
      dtSpeed = dtMaxSpeed * speedPercentage / 100.;
      #if DEV_ENV
        Serial.print(" : Translation de coordonnees (");
        Serial.print(xCenter);
        Serial.print(", ");
        Serial.print(yCenter);
        Serial.print(") avec une vitesse de ");
        Serial.print(speedPercentage);
        Serial.println("%");
      #endif
      dtSpeed = min(dtSpeed, dtMaxSpeed);
      moveType = TRANSLATION;
      StepCalculTranslation(-xCenter, -yCenter);
      angleConsigne = 0;
      Start();
      break;
    case 2 :  // Rotation : Centre X,Y et angle
      xCenter = readFloatFromWire();
      yCenter = readFloatFromWire();
      angleConsigne = readFloatFromWire();
      speedPercentage = Wire.read();
      dtSpeed = dtMaxSpeed * speedPercentage / 100.;
      dtSpeed = min(dtSpeed, dtMaxSpeed);
      #if DEV
        Serial.print("Rotation : centre = (");
        Serial.print(xCenter);
        Serial.print(", ");
        Serial.print(yCenter);
        Serial.print(") ; angle = ");
        Serial.println(angleConsigne);
      #endif
      moveType = ROTATION;
      StepCalculRotation(xCenter, yCenter, angleConsigne);
      Start();
      break;
  }
}

/*
This function is called automatically when we receive something from the master throught the Wire.
It sends 3 floats : the x, y, and theta
*/
void getRelativePositionFromStart() {
  float ratioStepsDone = 1 - (float) s / nbTotalStages;
  if (moveType == TRANSLATION) {
    writeFloatToWire(xCenter * ratioStepsDone);
    writeFloatToWire(yCenter * ratioStepsDone);
    writeFloatToWire(0);
  } else if (moveType == ROTATION) {
    float angle = ratioStepsDone * angleConsigne;
    writeFloatToWire(cos(angle) + xCenter);
    writeFloatToWire(sin(angle) + yCenter);
    writeFloatToWire(angle);
  } else {
    writeFloatToWire(0);
    writeFloatToWire(0);
    writeFloatToWire(0);
  }
}

//-------------------------------------------------------------------
/////////////////////////  Wire Functions  //////////////////////////
//-------------------------------------------------------------------

float readFloatFromWire() {
  uint32_t bits = ((uint32_t) Wire.read() << 24) |
                  ((uint32_t) Wire.read() << 16) |
                  ((uint32_t) Wire.read() << 8) |
                  (uint32_t) Wire.read();
  return *((float*) &bits);
}

void writeFloatToWire(float value) {
  uint32_t bits = *((uint32_t*) &value);
  Wire.write((bits >> 24) & 0xff);
  Wire.write((bits >> 16) & 0xff);
  Wire.write((bits >> 8) & 0xff);
  Wire.write(bits & 0xff);
}
