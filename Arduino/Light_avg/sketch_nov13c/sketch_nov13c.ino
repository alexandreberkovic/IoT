#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
//#include "secrets.h"
#include "DHT.h"

#define LIGHT_SENSOR_PIN 2 // ESP32 pin GPIO2 
const int SAMPLES= 10;
RTC_DATA_ATTR int bootCount = 0;
//RTC_DATA_ATTR char name[15] = CLIENT;
StaticJsonDocument<500> doc;

void setup() {
  Serial.begin(115200);
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
