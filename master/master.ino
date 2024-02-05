#include <Wire.h>

#define DEV_ENV true
#if DEV_ENV
  #define PRINT(x) Serial.print(x)
  #define PRINTLN(x) Serial.println(x)
#else
  #define PRINT(x)
  #define PRINTLN(x)
#endif

#define I2C_MOVING_ID 1
#define I2C_ULTRASOUND_SENSOR_ID 2

#define START_PIN             2

#define CHANGE_STRATEGY_PIN   3
#define STRATEGY_ID_BIT_1_PIN 0
#define STRATEGY_ID_BIT_2_PIN 0
#define STRATEGY_ID_BIT_4_PIN 0

#define NUMBER_OF_STRATEGIES 2

#define RADIUS_ROBOT 0.15

#define BUILTIN_LED_PIN 13

int distances[12];
const uint8_t sonarIds[12] {7, 8, 2, 6, 5, 4, 1, 1, 0, 11, 10, 9};

String inputString = "";
long startTime_;

// Homologation
const float strategy0[] = {
  0.235, 1.14, PI/2,
  6,
  0.235, 2.65,
  0.235, 2.35,
  -PI, -1,
  0.235, -2,
  2.35, -3,
  0.235, 1.14,
};

const float strategy1[] = {
  1.765, 1.14, PI/2,
  6,
  1.765, 2.65,
  1.765, 2.35,
  PI, -1,
  1.765, -2,
  2.35, -3,
  1.765, 1.14,
};

int strategyId = 0;
// A pointer to the array (aka an array)
float* strategy = 0;
int strategyStep = -1;

bool gameStarted = false;
float strategyFinished = false;

// Angle that stores the direction we are moving to
float currentMovingDirection = 0;

float xRequest, yRequest, angleRequest;

float position[2];
float angle;

void setup() {
  #if DEV_ENV
    Serial.begin(9600);  // Démarrage port série
    Serial.setTimeout(1);  // Délai d'attente port série 1ms
    while (!Serial);
  #endif

  PRINTLN("Starting");

  Wire.begin();

  pinMode(CHANGE_STRATEGY_PIN, INPUT_PULLUP);

  pinMode(START_PIN, INPUT_PULLUP);

  pinMode(BUILTIN_LED_PIN, OUTPUT);

  StopMoving();
  
  PRINTLN("Initialised");
}

void loop() {
  if (!gameStarted) {
    CheckStrategyButton();
    CheckStartGameButton();
    delay(100);
  } else if (!strategyFinished) {
    if (millis() - startTime_ > 95000) {
      StopMoving();
      strategyFinished = true;
    }
    RunStrategy();
    CheckRobotsAround();
  } else {
    CheckRobotsAround();
  }
}

void CheckStrategyButton() {
  if (!digitalRead(CHANGE_STRATEGY_PIN)) {
    strategyId = (strategyId + 1) % NUMBER_OF_STRATEGIES;
    // Wait until the button is released
    while (!digitalRead(CHANGE_STRATEGY_PIN));
    for (int i = 0; i < strategyId + 1; i++) {
      digitalWrite(BUILTIN_LED_PIN, HIGH);
      delay(500);
      digitalWrite(BUILTIN_LED_PIN, LOW);
      delay(500);
    }
  }
}

void CheckStartGameButton() {
  if (digitalRead(START_PIN)) {
    gameStarted = true;
    startTime_ = millis();
    switch(strategyId) {
      case 0:
        strategy = strategy0;
        break;
      case 1:
        strategy = strategy1;
        break;
      default:
        // The strategy does not exist ! To avoid any strange thing with memory, it is better to just do nothing. And hope this case never happens >.<
        strategyFinished = true;
        return;
    }
    position[0] = strategy[0];
    position[1] = strategy[1];
    angle = strategy[2];
    delay(1000);
  }
}

void CheckRobotsAround() {
  bool canContinueMoving = false;
  bool hasStopped = false;
  while (!canContinueMoving) {
    canContinueMoving = true;
    FetchDistances();
    // float array of length 2
    float* targetPosition = GetTarget();
    // If we are rotating, there should not be any problem with collisions
    if (targetPosition[1] < 0) {
      return;
    }
    float relativeTargetPosition[2] = {targetPosition[0] - position[0], targetPosition[1] - position[1]};
    relativeTargetPosition[0] -= position[0];
    relativeTargetPosition[1] -= position[1];
    bool forward = (targetPosition[0] - position[0]) * cos(angle) > 0.01 || (targetPosition[1] - position[1]) * sin(angle) > 0.01;
    for (int j = 0; j < 12; j++) {
      int i = sonarIds[j];
      if (distances[j] > 300 || distances[j] < 10) {
        continue;
      }
      float xMoved, yMoved, angleMoved;
      FetchDistanceMoved(xMoved, yMoved, angleMoved);
      // If we are already backing up, we continue
      /*if (hasStopped && abs(xMoved - xRequest) > 0.001 && abs(yMoved - yRequest) > 0.001) {
        canContinueMoving = false;
        continue;
      }*/
      float obstacleAngle = i * PI/6 + angle;
      float movingAngle;
      if (xMoved == 0) {
        // y should never equal 0 at the same time as x. If it does, well, it should not (and it should not break things either anyway)
        if (yMoved > 0) {
          movingAngle = PI / 2;
        } else {
          movingAngle = -PI / 2;
        }
      } else {
        movingAngle = atan(yMoved / xMoved);
        if (xMoved < 0) {
          movingAngle += PI;
        }
      }
      float obstacleAngleRelativeToDirection = fmod(fmod(obstacleAngle, 2*PI) - fmod(angle, 2*PI), 2*PI);
      // The obstacle is in the back
      if (obstacleAngleRelativeToDirection > PI/2 && obstacleAngleRelativeToDirection < 3*PI/2) {
        continue;
      }
      float obstacleX = position[0] + xMoved + cos(obstacleAngle) * distances[j] / 1000;
      float obstacleY = position[0] + yMoved + sin(obstacleAngle) * distances[j] / 1000;
      if (obstacleX <= 0.05 || obstacleX >= 1.95 || obstacleY <= 0.05 || obstacleY >= 2.95) {
        continue;
      }
      hasStopped = true;
      canContinueMoving = false;
      StopMoving();
    }
  }
  // If we stopped, we need to start moving again
  if (hasStopped) {
    delay(500);
    float* target = GetTarget();
    // If this is a rotation
    if (target[1] < 0) {
      float xMoved, yMoved, angleMoved;
      FetchDistanceMoved(xMoved, yMoved, angleMoved);
      Rotation(position[0] + xMoved, position[1] + yMoved, target[0]);
    } else if (target[0] != position[0] || target[1] != position[1]) {
      Move(target[0], target[1]);
    }
  }
}


void RunStrategy() {
  // float array of length 2
  float* target = GetTarget();
  float xMoved, yMoved, angleMoved;
  FetchDistanceMoved(xMoved, yMoved, angleMoved);
  if (strategyStep == -1
     || target[1] <= -2
     || (target[1] != -1 && abs(position[0] + xMoved - target[0]) < 0.005 && abs(position[1] + yMoved - target[1]) < 0.005)
     || target[1] == -1 && (fmod(fmod(angleMoved, 2*PI) - fmod(angleRequest, 2*PI), 2*PI) < 0.05 || fmod(fmod(angleMoved, 2*PI) - fmod(angleRequest, 2*PI), 2*PI) > 2*PI-0.05)) {
    strategyStep++;
    delay(500);
    PRINT("Starting step ");
    PRINT(strategyStep);
    PRINT("/");
    PRINTLN(strategy[3]-1);
    // If we reached the end of the strategy, we leave
    if (strategyStep >= strategy[3]) {
      strategyFinished = true;
      PRINTLN("STRATEGY finished !!");
      return;
    }
    target = GetTarget();
    // If this is a rotation
    if (target[1] == -1) {
      float xMoved, yMoved, angleMoved;
      FetchDistanceMoved(xMoved, yMoved, angleMoved);
      Rotation(position[0]+xMoved, position[1]+yMoved, target[0]);
      delay(3000);
    } else if (target[1] == -2) {
      StopMoving();
      position[0] = target[0];
    } else if (target[1] == -3) {
      StopMoving();
      position[1] = target[0];
    } else if (target[0] != position[0] || target[1] != position[1]) {
      Move(target[0], target[1]);
    }
    Serial.print("donc on affiche la position : ");
    Serial.print(position[0]);
    Serial.print(" ");
    Serial.println(position[1]);
  } else if (abs(xMoved - xRequest) < 0.001 && abs(yMoved - yRequest) < 0.001 && abs(angleMoved - angleRequest) < 0.001) {
    // If we enter in this condition, movement should always be a straight path, and never a rotation
    // It should never be called, but it should detect when the robot hasn't moved enough, and tell him to move more
    Move(target[0], target[1]);
  }
}

// Returns the position of the current target in the strategy
float* GetTarget() {
  // We return a pointer to the right value of the array
  return strategy + (4 + strategyStep * 2);
}

void TestEachDirection() {
  float angle = 0;
  float x, y;
  float xMoved = 9999, yMoved = 9999;
  while (angle < 2 * PI) {
    PRINT("Testing angle ");
    PRINT(angle * 180 / PI);
    PRINTLN("°");
    x = cos(angle) * 0.5;
    y = sin(angle) * 0.5;
    Move(x, y);
    while (xMoved != x || yMoved != y) {
      FetchDistanceMoved(xMoved, yMoved);
    }
    Move(-x, -y);
    while (xMoved != -x || yMoved != -y) {
      FetchDistanceMoved(xMoved, yMoved);
    }
    angle += 0.5;
  }
}

/** WHEELS COMMUNICATION **/

void Move(float x, float y) {
  float xMoved, yMoved, angleMoved;
  FetchDistanceMoved(xMoved, yMoved, angleMoved);
  PRINT("distance Moved x : ");
  PRINTLN(xMoved);
  position[0] += xMoved;
  position[1] += yMoved;
  angle += angleMoved;
  xRequest = x - position[0];
  yRequest = y - position[1];
  if (xRequest == 0 && yRequest == 0) {
    return;
  }
  // Changing the base
  // We need to inverse the direction of the y axis so that the coordinate system is turning in the trigonometric sens
  float xRequestRotated = cos(-angle+PI/2) * xRequest - sin(-angle+PI/2) * yRequest;
  float yRequestRotated = -(sin(-angle+PI/2) * xRequest + cos(-angle+PI/2) * yRequest);
  Wire.beginTransmission(I2C_MOVING_ID);
  Wire.write(1);
  writeFloatToWire(xRequestRotated);
  writeFloatToWire(yRequestRotated);
  Wire.write(100);
  Wire.endTransmission();
  angleRequest = 0;
  PRINT("Consigne 1 envoyée : Move ");
  PRINT(xRequestRotated);
  PRINT(" ");
  PRINTLN(yRequestRotated);
}

void Rotation(float xCentre, float yCentre, float angle_) {
  float xMoved, yMoved, angleMoved;
  FetchDistanceMoved(xMoved, yMoved, angleMoved);
  position[0] += xMoved;
  position[1] += yMoved;
  angle += angleMoved;
  Wire.beginTransmission(I2C_MOVING_ID);
  Wire.write(2);
  writeFloatToWire(xCentre - position[0]);
  writeFloatToWire(yCentre - position[1]);
  writeFloatToWire(angle_);
  Wire.write(100);
  Wire.endTransmission();
  xRequest = xCentre - position[0];
  yRequest = yCentre - position[1];
  angleRequest = angle_;
  PRINTLN("Consigne 2 envoyée : Rotation");
}

void StopMoving() {
  float xMoved, yMoved, angleMoved;
  FetchDistanceMoved(xMoved, yMoved, angleMoved);
  PRINT("distance Moved x : ");
  PRINTLN(xMoved);
  position[0] += xMoved;
  position[1] += yMoved;
  angle += angleMoved;
  Wire.beginTransmission(I2C_MOVING_ID);
  Wire.write(0);
  Wire.endTransmission();
  //delay(1000);
  PRINTLN("Consigne 3 envoyée : Arret");
}

void FetchDistanceMoved(float &x, float &y) {
  Wire.requestFrom(I2C_MOVING_ID, 12);
  float xInMotorsBase = readFloatFromWire();
  float yInMotorsBase = readFloatFromWire();
  x = cos(-angle+PI/2) * xInMotorsBase - sin(-angle+PI/2) * yInMotorsBase;
  y = -sin(-angle+PI/2) * xInMotorsBase - cos(-angle+PI/2) * yInMotorsBase;
  readFloatFromWire();
}

void FetchDistanceMoved(float &x, float &y, float &pAngle) {
  Wire.requestFrom(I2C_MOVING_ID, 12);
  float xInMotorsBase = readFloatFromWire();
  float yInMotorsBase = readFloatFromWire();
  x = cos(-angle+PI/2) * xInMotorsBase - sin(-angle+PI/2) * yInMotorsBase;
  y = -sin(-angle+PI/2) * xInMotorsBase - cos(-angle+PI/2) * yInMotorsBase;
  pAngle = readFloatFromWire();
}

/** ULTRASOUND SENSORS COMMUNICATION **/

void FetchDistances() {
  Wire.requestFrom(I2C_ULTRASOUND_SENSOR_ID, 24);
  for (int i = 0; i < 12; i++) {
    distances[i] = (Wire.read() << 8) | Wire.read();
    //Serial.print(distances[i]);
  }
  //Serial.println();
}

/** UTILITY FUNCTION TO READ/WRITE FROM/TO Wire **/

void writeFloatToWire(float value) {
  uint32_t bits = *((uint32_t*) &value);
  Wire.write((bits >> 24) & 0xff);
  Wire.write((bits >> 16) & 0xff);
  Wire.write((bits >> 8) & 0xff);
  Wire.write(bits & 0xff);
}

float readFloatFromWire() {
  uint32_t bits = ((uint32_t) Wire.read() << 24) |
                  ((uint32_t) Wire.read() << 16) |
                  ((uint32_t) Wire.read() << 8) |
                  (uint32_t) Wire.read();
  return *((float*) &bits);
}

