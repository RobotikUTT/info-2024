

const int controlPin1=2;
const int controlPin2=4;
const int controlPin3=7;
const int controlPin4=8;
const int enable1=3;
const int enable2=5;
const int trig=9;
const int echo=10;
unsigned long temps;
// unsigned long tDepart=92000000;
// unsigned long tFin=98000000;
unsigned long long tDepart=1000000;
unsigned long long tFin=20000000;
float duree;
long duration;
int distance;

void setup() {
  Serial.begin(9600);
  pinMode(enable1,OUTPUT);
  pinMode(enable2,OUTPUT);
  pinMode(controlPin1,OUTPUT);
  pinMode(controlPin2,OUTPUT);
  pinMode(controlPin3,OUTPUT);
  pinMode(controlPin4,OUTPUT);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);

  digitalWrite(controlPin1,LOW);
  digitalWrite(controlPin2,HIGH);
  digitalWrite(controlPin3,HIGH);
  digitalWrite(controlPin4,LOW);
}

void loop() {
  temps=micros();
  if((tDepart<temps)&&(getDistance()>35)&&(tFin>temps)){
    avancer();
  }
  else{
    arret();
  }
  Serial.println(getDistance());
  delay(100);

}



void avancer(){

  analogWrite(enable1,80);  // gauche
  analogWrite(enable2,90); // droit
}
void arret(){
  analogWrite(enable1,0);
  analogWrite(enable2,0);
}

int getDistance() {
  // Clear the trigPin
  digitalWrite(trig, LOW);
  delayMicroseconds(2);

  // Send a pulse to trigger
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  // Measure the duration of the pulse
  duration = pulseIn(echo, HIGH);


  // Calculate distance in cm
  distance = duration * 0.034 / 2;

  // Wait before next measurement
  return(distance);
}