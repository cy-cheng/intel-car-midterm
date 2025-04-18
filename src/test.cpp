// Arduino
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include <MFRC522.h>

// C
#include <stdlib.h>

// RFID variable
#define RST_PIN 49
#define SS_PIN 53
MFRC522 *mfrc522;

// Motor variable
#define PWMB 13 // Left
#define BIN1 5 
#define BIN2 6 
#define PWMA 12 // Right
#define AIN1 2 
#define AIN2 3 

// Car controlling
static int strflg = 0;
static int suml = 0, sumr = 0;

const double Avel = 250; 
const double Bvel = 250; 
const double adj[4] = {0, -60, -160, -120};
const double slow = 0.6;
const double backSlow = 0.5;

// Eyes
const int irRead[] = {32, 34, 36, 38, 40};
const int irLed[] = {0, 0, 0, 0, 0};
const int irNum = 5;

// BT variables
SoftwareSerial BT(11, 10);

// Queue
#define MAXN 300
static char Queue[MAXN];
static int str = 0, end = 0;

// Functions declaration
void setupRFID();
void setupMotor();
void setupIR();
void setupBT();

void loopRFID();
void loopBT();
void loopWalking();

inline void waitToStart();
inline void carControl(char);
inline void dynamicTurningRight();
inline void dynamicTurningLeft();
inline void goStraight();
inline void stopWalking();
inline void fixedTurningBack();

inline bool status(int x) { return x >= 0; }

inline void setSpeed(int pos, int speed) {
    analogWrite(pos, abs(speed));
    if (pos == PWMA) {
        digitalWrite(AIN1, status(speed));
        digitalWrite(AIN2, !status(speed));
    } else {
        digitalWrite(BIN1, status(speed));
        digitalWrite(BIN2, !status(speed));
    }
}

void setup() {
    Serial.begin(9600);
    setupRFID();
    setupMotor();
    setupIR();
    setupBT();
}

inline int updl() { return 2 * (digitalRead(irRead[0])) + digitalRead(irRead[1]); }
inline int updr() { return digitalRead(irRead[3]) + 2 * (digitalRead(irRead[4])); }

void loop() {
    // waitToStart();
    loopWalking();
    loopRFID();
    loopBT();
}

inline void waitToStart() {
    if (strflg) return;
    while(true) {
        if (BT.available()) {
            char c = BT.read();
            strflg = 1;
            goStraight();
            break;
        }
    }
}

void loopWalking() {
    suml = updl();
    sumr = updr();
    setSpeed(PWMA, (Avel + adj[sumr]) * slow); // R
    setSpeed(PWMB, (Bvel + adj[suml]) * slow); // L
    if (suml == 3 && sumr == 3 && digitalRead(irRead[2]) == 1) {
        if (str < end) {
            carControl(Queue[str]);
            // if (Queue[str] == 'x') break;
            str++;
        } else {
            carControl('b');
            BT.println('t');
        }
    }
}

inline void dynamicTurningRight() {
    while (suml == 3 || sumr == 3) {
        suml = updl(), sumr = updr();
        setSpeed(PWMA, Avel * 0.0);
        setSpeed(PWMB, Bvel * slow);
    }
}

inline void dynamicTurningLeft() {
    while (suml == 3 || sumr == 3) {
        suml = updl(), sumr = updr();
        setSpeed(PWMA, Avel * slow);
        setSpeed(PWMB, Bvel * 0.0);
    }
}

inline void goStraight() {
    suml = updl(), sumr = updr();
    while (suml == 3 || sumr == 3) {
        suml = updl(), sumr = updr();
        setSpeed(PWMA, Avel * slow);
        setSpeed(PWMB, Bvel * slow);
    }
}

inline void stopWalking() {
    setSpeed(PWMA, 0);
    setSpeed(PWMB, 0);
    strflg = 0;
}

inline void fixedTurningBack() {
    suml = updl();
    sumr = updr();
    while (!digitalRead(irRead[4]) || digitalRead(irRead[0]) || digitalRead(irRead[1]) || digitalRead(irRead[2]) || digitalRead(irRead[3])) {
        setSpeed(PWMA, Avel * -backSlow);
        setSpeed(PWMB, Bvel * backSlow * 0.85);
        suml = updl(), sumr = updr();
    }
    // while (true) {
    //     setSpeed(PWMA, 0);
    //     setSpeed(PWMB, 0);
    // }
    // setSpeed(PWMA, Avel * slow); 
    // setSpeed(PWMB, Bvel * slow); 
    setSpeed(PWMA, Avel * 0); 
    setSpeed(PWMB, Bvel * 0); 
}

inline void carControl(char cmd) {
    switch(cmd) {
        case 'f':
            goStraight();
            break;
        case 'b':
            fixedTurningBack();
            break;
        case 'r':
            dynamicTurningRight();
            break;
        case 'l':
            dynamicTurningLeft();
            break;
        case 'x':
            stopWalking();
            break;
    }
}

void setupRFID() {
    Serial.println("RFID setup:");
    SPI.begin();
    mfrc522 = new MFRC522(SS_PIN, RST_PIN);
    mfrc522->PCD_Init();
    Serial.println(F("Read UID on a MIFARE PICC:"));
}

void loopRFID() {
    mfrc522->PCD_Init();
    
    if (!mfrc522->PICC_IsNewCardPresent()) return;
    if (!mfrc522->PICC_ReadCardSerial()) return;

    // Serial.println(F("**Card Detected:**"));
    // BT.println(F("**Card Detected:**"));
    
    // Serial.print("ID: ");
    // BT.print("ID: ");
    
    for (byte i = 0; i < mfrc522->uid.size; i++) {
        char buffer[3];
        sprintf(buffer, "%02X", mfrc522->uid.uidByte[i]);
        // Serial.print(buffer);
        BT.print(buffer);
        // if (i < mfrc522->uid.size - 1) {
            // Serial.print(":");
            // BT.print(":");
        // }
    }
    // Serial.println();
    BT.println();
    BT.flush();
   
    mfrc522->PICC_HaltA();
    mfrc522->PCD_StopCrypto1();
}

void setupMotor() {
    Serial.println("Motor setup:");
    pinMode(PWMA, OUTPUT);
    pinMode(AIN1, OUTPUT);
    pinMode(AIN2, OUTPUT);
    pinMode(PWMB, OUTPUT);
    pinMode(BIN1, OUTPUT);
    pinMode(BIN2, OUTPUT);
}

void setupIR() {
    Serial.println("IR setup:");
    for (int i = 0; i < irNum; i++) {
        pinMode(irRead[i], INPUT);
    }
}

void setupBT() {
    Serial.println("BT setup:");
    BT.begin(9600);
}

void loopBT() {
    if (Serial.available()) {
        char c = Serial.read();
        Serial.print(c);
        BT.println(c);
    }
    while (BT.available()) {
        char c = BT.read();
        Queue[end++] = c;
        // BT.println('r');
        Serial.print(c);
    }
}