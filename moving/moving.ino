#include <SoftwareSerial.h>
#include <Wire.h>

#define DEV_ENV true  // Wheather this is production or development environment. In production environment, nothing will be printed out to the console

//-------------------------------------------------------------------
////////////////////////   Pin CNC shield     ///////////////////////
//-------------------------------------------------------------------

// Controlleurs Pas a Pas
#define xDirPin           2  //PD2 -> set PORTD |= 0b00000100 ou 0x04   eteindre PORTE &= 0b11111011 ou 0xFB
#define yDirPin           3  //PD3 -> set PORTD |= 0b00001000 ou 0x08   eteindre PORTE &= 0b11110111 ou 0xF7
#define zDirPin           4  //PD4 -> set PORTD |= 0b00010000 ou 0x10   eteindre PORTG &= 0b11101111 ou 0xEF
#define xStepPin          5  //PD5 -> set PORTD |= 0b00100000 ou 0x20   eteindre PORTE &= 0b11011111 ou 0xDF
#define yStepPin          6  //PD6 -> set PORTD |= 0b01000000 ou 0x40   eteindre PORTH &= 0b10111111 ou 0xBF
#define zStepPin          7  //PD7 -> set PORTD |= 0b10000000 ou 0x80   eteindre PORTH &= 0b01111111 ou 0x7F
#define enablePin         8

// Mesure tension
#define tensionBatteriePin    A7       //Analogique 7
#define facteurTension        0.01659  //Pont diviseur de tension + lecture sur 10 bits.
#define seuilAlerteTension    11       //Volts
#define seuilCritiqueTension  10       //Volts

#define STEP_HIGH_X       PORTE |= _BV(PE4)   // Activation Pin Pas X
#define STEP_LOW_X        PORTE &= ~_BV(PE4)  // Désactivation Pin Pas X
#define STEP_HIGH_Y       PORTE |= _BV(PE5)   // Activation Pin Pas Z
#define STEP_LOW_Y        PORTE &= ~_BV(PE5)  // Désactivation Pin Pas Y
#define STEP_HIGH_Z       PORTG |= _BV(PG5)   // Activation Pin Pas Z
#define STEP_LOW_Z        PORTG &= ~_BV(PG5)  // Désactivation Pin Pas Z
#define SENS_TRIGO_X      PORTE |= _BV(PE3)
#define SENS_HORRAIRE_X   PORTE &= ~_BV(PE3)
#define SENS_TRIGO_Y      PORTH |= _BV(PH3)
#define SENS_HORRAIRE_Y   PORTH &= ~_BV(PH3)
#define SENS_TRIGO_Z      PORTH |= _BV(PH4)
#define SENS_HORRAIRE_Z   PORTH &= ~_BV(PH4)

// Types of moves. Either NOT_MOVING, TRANSLATION or ROTATION
#define NOT_MOVING   0
#define TRANSLATION  1
#define ROTATION     2


//-------------------------------------------------------------------
///////////////////////////  Constantes  ////////////////////////////
//-------------------------------------------------------------------

// conversion pas par tour et par radians.
#define pasParMetre    4680 //facteur experimental = 1.03 ; demi-pas alors que la valeur a été trouvée pour des quarts de pas
const float rRobot = 0.119; //0.1265 théoriquement

//Determinées
const PROGMEM long dtMaxSpeed = 1000; // Microsecondes entre 2 pas à la vitesse maximale
const PROGMEM long acc = 2.5 * pow(10, 8); // µs² / pas (inverse de l'acceleration)
const PROGMEM long dec = 2.5 * pow(10, 8); // µs² / pas (inverse de la deceleration)
//const PROGMEM long tempsAcc = 1.0 * pow(10, 6); // Temps d'accélération en µs
//const PROGMEM long tempsDec = 1.0 * pow(10, 6); // Temps de décélération en µs

//Calculées
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
float xCentre = 0;
float yCentre = 0;
float angleConsigne = 0;
int dtSpeed = dtMaxSpeed;
//Sens de rotation
bool sensX = false;             //
bool sensY = false;             // sens trigo robot : true, sens horraire robot : false
bool sensZ = false;             //

// Vitesse Relative des moteurs
float ratioVitX = 1;
float ratioVitY = 1;
float ratioVitZ = 1;

// Nombre de pas déja faits et restants sur chaque moteur
volatile unsigned long pasFaitsX = 0;
volatile unsigned long pasFaitsY = 0;
volatile unsigned long pasFaitsZ = 0;
volatile unsigned long pasRestantsX = 0;
volatile unsigned long pasRestantsY = 0;
volatile unsigned long pasRestantsZ = 0;

//booleen de controle
volatile bool enMvmt = false;    // Le robot est en mouvement
volatile bool enAcc = false;     // Le robot est en phase d'accélération
volatile bool enDec = false;     // Le robot est en phase de décélération
bool lastMove = false; // false = Translation, true = Rotation

// Etapes
volatile unsigned long etapeTrajet = 0;
volatile unsigned long t = 0; // Temps actuel
volatile unsigned long prevT = 0;                // Stockage du temps en microseconde auquel s'est passé la dernière étape
volatile unsigned int newDt = 5000;     // Intervalle de temps en microseconde avant la prochaine étape
volatile unsigned long etapesRestantes;          // Nombres d'étapes restantes
unsigned long nbTotalEtapes;            // Nombres total d'étapes à réaliser

//-------------------------------------------------------------------
/////////////////////     Autres Variables     //////////////////////
//-------------------------------------------------------------------

//Batterie
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
  pinMode(xDirPin, OUTPUT);   // Pin dir moteur x en mode OUTPUT
  pinMode(yDirPin, OUTPUT);   // Pin dir moteur y en mode OUTPUT
  pinMode(zDirPin, OUTPUT);   // Pin dir moteur z en mode OUTPUT
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
  if (enMvmt) {       // Si on est en mouvement
    Avancer();        // On passe à l'étape d'après (si le temps necessaire s'est écoulé)
  }
}

void testEngines() {
  Demarrer();
  long lastTime = 0;
  long t;
  while (true) {
    t = micros();
    if (t - lastTime > dtMaxSpeed) {
      lastTime = t;
      PasMoteurX();
      PasMoteurY();
      PasMoteurZ();
    }
  }
}

//-------------------------------------------------------------------
//////////////////////////   Fonctions    ///////////////////////////
//-------------------------------------------------------------------

void Demarrer() { // Lancement du mouvement
  InitVariablesMvmt();
  AlimMoteurs(true);
}

void InitVariablesMvmt() { // Initialisation des variables
  enMvmt = true;
  enAcc = true;
  enDec = false;
  etapeTrajet = 0;
  etapesRestantes = nbTotalEtapes - etapeTrajet;
  pasFaitsX = 0;
  pasFaitsY = 0;
  pasFaitsZ = 0;
  prevT = 0;
}

void CalculPasRotation(float xCentre, float yCentre, float angle) {
  if (sqrt(sq(xCentre) + sq(yCentre)) == rRobot) yCentre += 0.001;
  float distXX = rRobot * cos(-PI / 6) - xCentre;
  float distYX = rRobot * sin(-PI / 6) - yCentre;
  float distXY = rRobot * cos(-5 * PI / 6) - xCentre;
  float distYY = rRobot * sin(-5 * PI / 6) - yCentre;
  float distXZ = rRobot * cos(PI / 2) - xCentre;
  float distYZ = rRobot * sin(PI / 2) - yCentre;
  float angleX = arctan(distXX, distYX) + PI / 2;
  float angleY = arctan(distXY, distYY) + PI / 2;
  float angleZ = arctan(distXZ, distYZ) + PI / 2;
  float distAFaireX = angle * sqrt(sq(distXX) + sq(distYX)); // longueur d'arc de rayon centre-point de contact
  float distAFaireY = angle * sqrt(sq(distXY) + sq(distYY));
  float distAFaireZ = angle * sqrt(sq(distXZ) + sq(distYZ));
  lastMove = true;
  long pasMoteurX = (float) distAFaireX * pasParMetre * cos(angleX + (2. / 3) * PI);     //
  long pasMoteurY = (float) distAFaireY * pasParMetre * cos(angleY - (2. / 3) * PI );    // Calcul des distances à parcourir
  long pasMoteurZ = (float) distAFaireZ * pasParMetre * cos(angleZ);                     //
  MouvementSynchrone(pasMoteurX, pasMoteurY, pasMoteurZ);
}

void CalculPasTranslation(float x, float y) { // Calcul des pas à faire sur chaque moteurs
  float angle = arctan(x, y);
  float distanceTotalePas = sqrt(sq(x) + sq(y)) * pasParMetre;
  long pasMoteurX = (float) distanceTotalePas * cos(borner(angle + (2. / 3) * PI));     //
  long pasMoteurY = (float) distanceTotalePas * cos(borner(angle - (2. / 3) * PI ));    // Calcul des distances à parcourir
  long pasMoteurZ = (float) distanceTotalePas * cos(borner(angle));                     //
  lastMove = false;
  MouvementSynchrone(pasMoteurX, pasMoteurY, pasMoteurZ);
}

void MouvementSynchrone(long x, long y, long z) {
  SensMoteurs((x >= 0) ? sensX = 1 : sensX = 0, (y >= 0) ? sensY = 1 : sensY = 0, (z >= 0) ? sensZ = 1 : sensZ = 0);
  pasRestantsX = abs(x);
  pasRestantsY = abs(y);
  pasRestantsZ = abs(z);
  nbTotalEtapes = max(max(pasRestantsX, pasRestantsY), pasRestantsZ);                   //
  ratioVitX = (float) pasRestantsX / nbTotalEtapes;                                     // Calcul et Stockage du vecteur
  ratioVitY = (float) pasRestantsY / nbTotalEtapes;                                     //  directionnel souhaité
  ratioVitZ = (float) pasRestantsZ / nbTotalEtapes;                                     //
  tempsAcc = acc / dtSpeed;
  tempsDec = dec / dtSpeed;
  dtMaxAcc = 1. / sqrt(2. / (tempsAcc * dtSpeed));
  dtMaxDec = 1. / sqrt(2. / (tempsDec * dtSpeed));
  nbEtapesAcc = tempsAcc / (2 * dtSpeed); // Nombres de pas parcourus pendant l'accelération (intégrale de la vitesse)
  nbEtapesDec = tempsDec / (2 * dtSpeed); // Nombres de pas parcourus pendant la décélération (intégrale de la vitesse)
  if ((nbEtapesAcc + nbEtapesDec) > nbTotalEtapes) {
    float total = nbEtapesAcc + nbEtapesDec;
    nbEtapesAcc = nbEtapesAcc / total * nbTotalEtapes;
    nbEtapesDec = nbEtapesDec / total * nbTotalEtapes;
  }
}

void Avancer() { // Passe à la prochaine étape du mouvement si l'intervalle de temps est respecté
  t = micros();
  if (enAcc) { // Passage a la prochaine étape pendant l'accélération
    if (t - prevT >= newDt) {
      Move();
      prevT = t;
      ActualiserEtapeTrajet();
      newDt = dtMaxAcc / Sqrt(etapeTrajet);
      if (etapeTrajet >= nbEtapesAcc) { //Fin de l'acc
        enAcc = false;
      }
      if (etapesRestantes <= nbEtapesDec) {
        enDec = true;
        enAcc = false;
      }
    }
  } else if (enDec) {
    if (t - prevT >= newDt) {
      Move();
      prevT = t;
      ActualiserEtapeTrajet();
      newDt = dtMaxDec / Sqrt(etapesRestantes);
      if (etapesRestantes <= 0) {
        enMvmt = false;
      }
    }
  } else {
    if (t - prevT >= dtSpeed) {
      Move();
      prevT = t;
      ActualiserEtapeTrajet();
      if (etapesRestantes <= nbEtapesDec) enDec = true; //Debut décélération
    }
  }
}

void ActualiserEtapeTrajet() {
  etapeTrajet++;
  etapesRestantes = nbTotalEtapes - etapeTrajet;
}

void Move() { // Commande des moteurs
  if (etapesRestantes >= 0) {     // >= 0 pour ne pas perdre les derniers pas
    if (ratioVitX * etapeTrajet >= pasFaitsX) {
      PasMoteurX();
      pasFaitsX++;
    }
    if (ratioVitY * etapeTrajet >= pasFaitsY) {
      PasMoteurY();
      pasFaitsY++;
    }
    if (ratioVitZ * etapeTrajet >= pasFaitsZ) {
      PasMoteurZ();
      pasFaitsZ++;
    }
  }
}

//-------------------------------------------------------------------
//////////////////  Fonctions Math  ////////////////////
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

uint16_t Sqrt(uint16_t input) {// Fonction de calcul de racine plus rapide trouvée sur https://gist.github.com/devgru/5006529
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
//////////////////  Fonctions Physiques Moteurs  ////////////////////
//-------------------------------------------------------------------

void AlimMoteurs(bool power) { // Alimentation ou coupure du courant des moteurs
  digitalWrite(enablePin, !power);
}

void SensMoteurs(bool X, bool Y, bool Z) {
  X ? SENS_TRIGO_X : SENS_HORRAIRE_X; //choix du sens
  Y ? SENS_TRIGO_Y : SENS_HORRAIRE_Y; //choix du sens
  Z ? SENS_TRIGO_Z : SENS_HORRAIRE_Z; //choix du sens
}

void PasMoteurX() {
  STEP_HIGH_X;                 //set la pin sur HIGH
  STEP_LOW_X;                  //set la pin sur LOW
}

void PasMoteurY() {
  STEP_HIGH_Y;                 //set la pin sur HIGH
  STEP_LOW_Y;                  //set la pin sur LOW
}

void PasMoteurZ() {
  STEP_HIGH_Z;                 //set la pin sur HIGH
  STEP_LOW_Z;                  //set la pin sur LOW
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
      enMvmt = false;
      moveType = NOT_MOVING;
      AlimMoteurs(false);
      break;
    case 1 :  // Translation X,Y
      xCentre = readFloatFromWire();
      yCentre = readFloatFromWire();
      speedPercentage = Wire.read();
      dtSpeed = dtMaxSpeed * speedPercentage / 100.;
      #if DEV_ENV
        Serial.print(" : Translation de coordonnees (");
        Serial.print(xCentre);
        Serial.print(", ");
        Serial.print(yCentre);
        Serial.print(") avec une vitesse de ");
        Serial.print(speedPercentage);
        Serial.println("%");
      #endif
      dtSpeed = min(dtSpeed, dtMaxSpeed);
      moveType = TRANSLATION;
      CalculPasTranslation(-xCentre, -yCentre);
      angleConsigne = 0;
      Demarrer();
      break;
    case 2 :  // Rotation : Centre X,Y et angle
      xCentre = readFloatFromWire();
      yCentre = readFloatFromWire();
      angleConsigne = readFloatFromWire();
      speedPercentage = Wire.read();
      dtSpeed = dtMaxSpeed * speedPercentage / 100.;
      dtSpeed = min(dtSpeed, dtMaxSpeed);
      #if DEV
        Serial.print("Rotation : centre = (");
        Serial.print(xCentre);
        Serial.print(", ");
        Serial.print(yCentre);
        Serial.print(") ; angle = ");
        Serial.println(angleConsigne);
      #endif
      moveType = ROTATION;
      CalculPasRotation(xCentre, yCentre, angleConsigne);
      Demarrer();
      break;
  }
}

/*
This function is called automatically when we receive something from the master throught the Wire.
It sends 3 floats : the x, y, and 
*/
void getRelativePositionFromStart() {
  float ratioStepsDone = 1 - (float) etapesRestantes / nbTotalEtapes;
  if (moveType == TRANSLATION) {
    writeFloatToWire(xCentre * ratioStepsDone);
    writeFloatToWire(yCentre * ratioStepsDone);
    writeFloatToWire(0);
  } else if (moveType == ROTATION) {
    float angle = ratioStepsDone * angleConsigne;
    writeFloatToWire(cos(angle) + xCentre);
    writeFloatToWire(sin(angle) + yCentre);
    writeFloatToWire(angle);
  } else {
    writeFloatToWire(0);
    writeFloatToWire(0);
    writeFloatToWire(0);
  }
}

/** UTILITY FUNCTIONS TO READ/WRITE FROM/TO THE Wire **/

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
