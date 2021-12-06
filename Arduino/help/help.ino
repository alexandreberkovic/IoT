#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
//#include "secrets.h"
#include "DHT.h"

#define DHTPIN 4 // GPIO19
#define DHTTYPE DHT22
#define LED_BUILTIN 13
#define LIGHT_SENSOR_PIN 39 // ESP32 pin GPI39 
const int SAMPLES= 10;
RTC_DATA_ATTR int bootCount = 0;
//RTC_DATA_ATTR char name[15] = CLIENT;
StaticJsonDocument<500> doc;

DHT dht(DHTPIN, DHTTYPE);

//This is the secret file
const char* ssid = "Flat9";
const char* password = "Fiona1738!";
const char* serverName = "https://eu-west-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/esp32-room-mpvbz/service/IoTWebhook/incoming_webhook/webhook0";

// -- Project -------------------------------------------
#define CLIENT                  "Bedroom"        // Client ID for the ESP (or something descriptive "Front Garden")
#define TYPE                    "ESP32"               // Type of Sensor ("Hornbill ESP32" or "Higrow" or "ESP8266" etc.)  

// -- Other - Helpers ------------------------------------
#define uS_TO_S_FACTOR          1000000               // Conversion factor for micro seconds to seconds
#define TIME_TO_SLEEP           300                   // Time ESP32 will go to sleep (in seconds) 
#define TIME_TO_SNOOZE          5                     // Time ESP32 will go to sleep (in seconds) 
//

void setup() {
  // this connects to the wifi and sets up the board for connection with the DB
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.print("Connecting to ");
  Serial.print(ssid);
  Serial.print(" with password ");
  Serial.println(password);

  WiFi.begin(ssid, password);
//  while (WiFi.status() != WL_CONNECTED) {
//    delay(500);
//    Serial.println("Wifi connecting");
//  }
//  Serial.println("Wifi connected");
//  Serial.print("Connected to WiFi network with IP Address: ");
//  Serial.println(WiFi.localIP());
//  digitalWrite(LED_BUILTIN, LOW);
//  dht.begin(); // initialize the sensor
}

void POSTData()
{
      
//      if(WiFi.status()== WL_CONNECTED){
//      HTTPClient http;
//
//      http.begin(serverName);
//      http.addHeader("Content-Type", "application/json");

      String json;
      serializeJson(doc, json);

      Serial.println(json);
//      int httpResponseCode = http.POST(json);
//      Serial.println(httpResponseCode);
//      }
}

int senseLight(int readPin)
{
  int reading = 0;
  if(analogRead(readPin) >= 0)
  {
    reading = analogRead(readPin);
    for (int i = 0; i < SAMPLES; i++)
  {
    reading += analogRead(readPin);
    delay(500);
  }
  reading = reading/10;
  }
  else
  {
    Serial.println("Error light!");
  }
  doc["sensors"]["light"] = reading;
  Serial.println("light!");
  return reading;
}


void loop() {
  senseLight(LIGHT_SENSOR_PIN);
  delay(5000);
  serializeJsonPretty(doc, Serial);
}
