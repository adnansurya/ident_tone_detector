#include <Arduino.h>
#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif

#include <QMC5883LCompass.h>
#include <Firebase_ESP_Client.h>

// Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

/* 1. Define the WiFi credentials */
#define WIFI_SSID "MUH ASRIANTO"
#define WIFI_PASSWORD "As030793"

/* 2. Define the RTDB URL */
#define DATABASE_URL "azimuth-360-default-rtdb.asia-southeast1.firebasedatabase.app"


#define offlinePin D5
#define identPin D6
#define statusPin D7


QMC5883LCompass compass;

/* 3. Define the Firebase Data object */
FirebaseData fbdo;

/* 4, Define the FirebaseAuth data for authentication data */
FirebaseAuth auth;

/* Define the FirebaseConfig data for config data */
FirebaseConfig config;

bool pcConnected = false;
bool identOK = false;
bool lastIdent = false;

unsigned long timeoutSeconds = 10;
unsigned long lastIdentTime = 0;

int az, lastAz;


void setup() {

  Serial.begin(9600);
  compass.init();

  pinMode(LED_BUILTIN, OUTPUT);  // Atur LED bawaan sebagai output
  pinMode(offlinePin, OUTPUT);
  pinMode(identPin, OUTPUT);
  pinMode(statusPin, OUTPUT);

  digitalWrite(offlinePin, HIGH);
  digitalWrite(identPin, LOW);
  digitalWrite(statusPin, LOW);
  blinkOut(LED_BUILTIN, 1, 250);
  blinkOut(statusPin, 1, 250);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);


  Serial.print("Connecting to Wi-Fi");
  unsigned long ms = millis();
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);


  /* Assign the database URL(required) */
  config.database_url = DATABASE_URL;

  config.signer.test_mode = true;

  // Comment or pass false value when WiFi reconnection will control by your code or third party library e.g. WiFiManager
  Firebase.reconnectNetwork(true);

  // Since v4.4.x, BearSSL engine was used, the SSL buffer need to be set.
  // Large data transmission may require larger RX buffer, otherwise connection issue or data read time out can be occurred.
  fbdo.setBSSLBufferSize(4096 /* Rx buffer size in bytes from 512 - 16384 */, 1024 /* Tx buffer size in bytes from 512 - 16384 */);

  /* Initialize the library with the Firebase authen and config */
  Firebase.begin(&config, &auth);


  // Or use legacy authenticate method
  // Firebase.begin(DATABASE_URL, DATABASE_SECRET);
  blinkOut(statusPin, 3, 500);

  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {

  if (Serial.available() > 0) {
    String serialData = Serial.readStringUntil('\n');
    serialData.trim();
    Serial.print("Received Text: ");
    Serial.println(serialData);
    if (serialData.indexOf("ident") > -1) {
      Serial.println("Ident On");
      lastIdentTime = millis();
      identOK = true;
      blinkOut(identPin, 1, 50);
    }

    if (serialData.indexOf("ready") > -1) {
      digitalWrite(offlinePin, LOW);
      pcConnected = true;
    }
  }
  delay(100);


  // Read compass values
  compass.read();

  // Return Azimuth reading
  az = compass.getAzimuth();

  if(az < 0){
    az = abs(az);
  }else if(az > 0){
    az = 360 - az;
  }

  Serial.print("A: ");
  Serial.print(az);
  Serial.println();

  if (az != lastAz) {
    fbSetInt("/azimuth", az);
  }

  delay(50);

  if (identOK == true) {
    if (millis() - lastIdentTime >= timeoutSeconds * 1000) {
      Serial.println("Ident Off");
      identOK = false;
    }
  }

  if (lastIdent != identOK) {
    if (identOK) {      
      digitalWrite(statusPin, HIGH);
      if (pcConnected) {
        fbSetString("/ident", "ON");
      }

    } else {
      digitalWrite(statusPin, LOW);
      if (pcConnected) {
        fbSetString("/ident", "OFF");
      }
    }
  }

  lastIdent = identOK;
  lastAz = az;

  delay(100);
}


void fbSetString(String dir, String value) {
  if (Firebase.RTDB.setString(&fbdo, dir, value)) {
    Serial.println(dir + " has been set to " + value + " !");
    blinkOut(LED_BUILTIN, 1, 250);
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    Serial.println(fbdo.errorReason().c_str());
    blinkOut(offlinePin, 2, 500);
  }
}

void fbSetInt(String dir, int value) {
  if (Firebase.RTDB.setInt(&fbdo, dir, value)) {
    Serial.println(dir + " has been set to " + String(value) + " !");
    blinkOut(LED_BUILTIN, 1, 250);
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    Serial.println(fbdo.errorReason().c_str());
    blinkOut(offlinePin, 2, 500);
  }
}

void blinkOut(int ledpin, int freq, int delayms) {
  for (int i = 0; i < freq; i++) {
    digitalWrite(ledpin, HIGH);
    delay(delayms);
    digitalWrite(ledpin, LOW);
    delay(delayms);
  }
}
