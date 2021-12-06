#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
//#include "secrets.h"
#include "DHT.h"

#define DHTPIN 4 // GPIO19
#define DHTTYPE DHT22
//#define LED_BUILTIN 13
#define LIGHT_SENSOR_PIN 39 // ESP32 pin GPIO2
const int SAMPLES = 10;
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
//#define TIME_TO_SLEEP           300                   // Time ESP32 will go to sleep (in seconds) 
//#define TIME_TO_SNOOZE          5                     // Time ESP32 will go to sleep (in seconds) 
//

void setup() {
  // this connects to the wifi and sets up the board for connection with the DB
//  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
//  digitalWrite(LED_BUILTIN, HIGH);
  Serial.print("Connecting to ");
  Serial.print(ssid);
  Serial.print(" with password ");
  Serial.println(password);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Wifi connecting");
  }
  Serial.println("Wifi connected");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
//  digitalWrite(LED_BUILTIN, LOW);

  dht.begin(); // initialize the sensor
}


void POSTData()
{

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String json;
    serializeJson(doc, json);

    Serial.println(json);
    int httpResponseCode = http.POST(json);
    Serial.println(httpResponseCode);
  }
}

void getDevice()
{

  esp_sleep_wakeup_cause_t wakeup_reason;
  wakeup_reason = esp_sleep_get_wakeup_cause();

  uint64_t chipid = ESP.getEfuseMac(); //The chip ID is essentially its MAC address(length: 6 bytes).
  Serial.printf("***ESP32 Chip ID = %04X%08X\n", (uint16_t)(chipid >> 32), (uint32_t)chipid); //print High 2 bytes
  char buffer[200];
  sprintf(buffer, "%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);

  doc["device"]["IP"] = WiFi.localIP().toString();
  doc["device"]["RSSI"] = String(WiFi.RSSI());
  doc["device"]["type"] = TYPE;
  //    doc["device"]["name"] = name;
  doc["device"]["chipid"] = buffer;
  doc["device"]["bootCount"] = bootCount;
  doc["device"]["wakeup_reason"] = String(wakeup_reason);
  //doc["device"]["vbatt_raw"] = vbatt_raw;
  //    doc["device"]["vbatt"] = map(vbatt_raw, 0, 4096, 0, 4200);

}

float senseTemp()
{
  float reading = 0;
  if (dht.readTemperature() > 0)
  {
    reading = (float)dht.readTemperature();
  }
  else
  {
    Serial.println("Error temperature!");
  }
  doc["sensors"]["temperature"] = reading;
  return reading;
}

float senseHumid()
{
  float reading = 0;
  if (dht.readHumidity() > 0)
  {
    reading = (float)dht.readHumidity();
  }
  else
  {
    Serial.println("Error humidity!");
  }
  doc["sensors"]["humidity"] = reading;
  return reading;
}

int senseLight(int readPin)
{
  int reading = 0;
  if (analogRead(readPin) >= 0)
  {
    reading = analogRead(readPin);
    for (int i = 0; i < SAMPLES; i++)
    {
      reading += analogRead(readPin);
      delay(30000);
    }
    reading = reading / 10;
  }
  else
  {
    Serial.println("Error light!");
  }
  doc["sensors"]["light"] = reading;
  return reading;
}

void loop() {
  delay(300000);
  ++bootCount; // move this to setup()
//  turn the LED on (HIGH is the voltage level)
//  digitalWrite(LED_BUILTIN, HIGH);
  getDevice();
  senseTemp();
  senseHumid();
  int sense = senseLight(LIGHT_SENSOR_PIN);
  Serial.print(sense);
  Serial.println(analogRead(LIGHT_SENSOR_PIN));
//  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Posting...");
  POSTData();
  serializeJsonPretty(doc, Serial);
  Serial.println("\nDone.");
}

/*
  MongoDB Atlas Realm Function
  ----------------------------
  exports = function(payload){
    var atlas = context.services.get("mongodb-atlas");
    var coll = atlas.db("iot").collection("readings");
    try {
      if (payload.body)
      {
        //const ts = {ts:new Date()};
        //const ts_ej = EJSON.stringify(ts);
        body = EJSON.parse(payload.body.text());
        body['ts'] = new Date();
      }
      coll.insertOne(body);
      console.log(body);
    } catch (e) {
      console.log("Error inserting doc: " + e);
      return e.message();
    }
  };
  ----------------
*/
