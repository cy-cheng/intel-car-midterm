#include <Arduino.h>
#include <SoftwareSerial.h>

#include <MFRC522.h>
#include <SPI.h>

// RFID variables
// 引入 SPI 程式庫與 MFRC522 程式庫
#define RST_PIN 49
#define SS_PIN 53
// 設定重設腳位與 SPI 介面裝置選擇腳位
MFRC522* mfrc522;

// Motor variables
// If PWMX, XIN1, XIN2 to t, t/2, t/2 ^ 1, then setSpeed(PWMX, t) will make the
// motor run forward at speed t.
#define PWMA 11  // Right
#define AIN2 3
#define AIN1 2
#define PWMB 12  // Left
#define BIN2 6
#define BIN1 5

// Motor variables
const int Avel = 100;
const int Bvel = 100;
const double adj[4] = {0, 20, 65, 35};

// IR variables
const int irRead[] = {32, 34, 36, 38, 40};
const int irLed[] = {0, 0, 0, 0, 0};
const double w[] = {15, 7, 0};
double weight[] = {15, 7, 0, -7, -15};
const int irNum = 5;

// BT variables

void setupRFID();
void setupMotor();
void setupIR();
void setupBT();

void loopRFID();
void loopMotor();
void loopIR();
void loopBT();

inline int status(int x) {
    return x > 0;
}

void setSpeed(int pos, int speed) {
    if (pos & 1) {
        analogWrite(pos, abs(speed));
        digitalWrite(AIN2, !status(speed));
        digitalWrite(AIN1, status(speed));
    } else {
        analogWrite(pos, abs(speed));
        digitalWrite(BIN2, !status(speed));
        digitalWrite(BIN1, status(speed));
    }
}

void setup() {
    Serial.begin(9600);
    // pinMode(LED_BUILTIN, OUTPUT);
    setupRFID();
    setupMotor();
    setupIR();

    // setupBT();
}

void loop() {
    // digitalWrite(LED_BUILTIN, HIGH);
    // loopRFID();
    // delay(500);
    // digitalWrite(LED_BUILTIN, LOW);
    // delay(500);
    // loopMotor();
    // loopIR();
    // loopBT();
}

void setupRFID() {
    Serial.println("RFID setup:");
    SPI.begin();
    mfrc522 = new MFRC522(SS_PIN, RST_PIN);
    // 請系統去要一塊記憶體空間，後面呼叫它的建構函式將(SS, RST)
    // 當成參數傳進去初始化。
    mfrc522->PCD_Init();
    /* 初始化 MFRC522 讀卡機 PCD_Init 模組。-> 表示：透過記憶體位置，找到mfrc522
     * 這物件，再翻其內容。*/
    Serial.println(F("Read UID on a MIFARE PICC:"));
}

void loopRFID() {
    if (!mfrc522->PICC_IsNewCardPresent())
        return;  // 是否感應到新的卡片？
    if (!mfrc522->PICC_ReadCardSerial())
        return;  // 是否成功讀取資料？
    Serial.println("RFID: ");
    mfrc522->PICC_DumpDetailsToSerial(&(mfrc522->uid));
    mfrc522->PICC_HaltA();       // 讓同一張卡片進入停止模式(只顯示一次)
    mfrc522->PCD_StopCrypto1();  // 停止 Crypto1
    // delay(500);
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

void loopMotor() {
    Serial.println("Motor:");
    setSpeed(PWMA, 100);
    setSpeed(PWMB, 100);
    delay(1000);
    setSpeed(PWMA, -100);
    setSpeed(PWMB, -100);
    delay(1000);
}

void Walking() {
    int suml = 2 * (1 - digitalRead(irRead[0])) + 1 - digitalRead(irRead[1]);
    int sumr = 1 - digitalRead(irRead[3]) + 2 * (1 - digitalRead(irRead[4]));
    setSpeed(PWMA, Avel);
    setSpeed(PWMB, Bvel);
    delay(1000);
}

void turnLeft() {
    setSpeed(PWMA, Avel * 0.5);
    setSpeed(PWMB, Bvel);
    delay(1000);
}

void setupIR() {
    Serial.println("IR setup:");
    for (int i = 0; i < irNum; i++)
        pinMode(irRead[i], INPUT), pinMode(irLed[i], OUTPUT);
}

void loopIR() {
    Serial.println("IR:");
    for (int i = 0; i < irNum; i++) {
        Serial.print(digitalRead(irRead[i]));
        Serial.print(" ");
    }
    Serial.println();
    delay(200);
}

void setupBT() {
    Serial.println("BT setup:");
    SoftwareSerial BT(8, 9);
    BT.begin(9600);
}
/*
void loopBT() {
    if (Serial.available()) {
        char c = Serial.read();
        BT.print(c);
    }
    if (BT.available()) {
        char c = BT.read();
        Serial.print(c);
    }
}
*/