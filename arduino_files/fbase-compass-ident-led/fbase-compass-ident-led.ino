#include <Arduino.h>
#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif

#include <Firebase_ESP_Client.h>

// Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

/* 1. Define the WiFi credentials */
#define WIFI_SSID "MIKRO"
#define WIFI_PASSWORD "1DEAlist"

/* 2. Define the RTDB URL */
#define DATABASE_URL "pendeteksi01.firebaseio.com"  //<databaseName>.firebaseio.com or <databaseName>.<region>.firebasedatabase.app

/* 3. Define the Firebase Data object */
FirebaseData fbdo;

/* 4, Define the FirebaseAuth data for authentication data */
FirebaseAuth auth;

/* Define the FirebaseConfig data for config data */
FirebaseConfig config;

bool identOK = false;
bool lastIdent = false;

unsigned long timeoutSeconds = 10;
unsigned long lastIdentTime = 0;


void setup() {

  Serial.begin(9600);

  pinMode(LED_BUILTIN, OUTPUT);  // Atur LED bawaan sebagai output
  blinkOut(LED_BUILTIN, 1, 250);
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
  blinkOut(LED_BUILTIN, 3, 500);

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
    }
  }
  delay(100);

  if (identOK == true) {
    if (millis() - lastIdentTime >= timeoutSeconds * 1000) {
      Serial.println("Ident Off");
      identOK = false;
    }
  }

  if (lastIdent != identOK) {
    if (identOK) {
      digitalWrite(LED_BUILTIN, LOW);
      fbSetString("/ident/available", "ON");
    } else {
      digitalWrite(LED_BUILTIN, HIGH);
      fbSetString("/ident/available", "OFF");
    }
    // Serial.printf("Set bool... %s\n", Firebase.RTDB.setBool(&fbdo, "/ident/available", identOK) ? "ok" : fbdo.errorReason().c_str());
  } 

  lastIdent = identOK;


  delay(100);
}


void fbSetString(String dir, String value) {
  if (Firebase.RTDB.setString(&fbdo, dir, value)) {
    Serial.println(dir + " has been set to " + value + " !");
  } else {
    Serial.println(fbdo.errorReason().c_str());
  }
}

void blinkOut(int ledpin, int freq, int delayms){
  for(int i=0; i<freq; i++){
    digitalWrite(ledpin, HIGH);
    delay(delayms);
    digitalWrite(ledpin, LOW);
    delay(delayms);
  }
}
