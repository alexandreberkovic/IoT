#include "DHT.h"
#define DHTPIN 4 // GPIO19
#define DHTTYPE DHT22
#define LIGHT_SENSOR_PIN 2 // ESP32 pin GPIO2 

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  dht.begin(); // initialize the sensor
}

void loop() {
  // wait a few seconds between measurements.
  delay(1000);

  // read humidity
  float humi  = dht.readHumidity();
  // read temperature as Celsius
  float tempC = dht.readTemperature();
  // reads the input on analog pin (value between 0 and 4095)
  int analogValue = analogRead(LIGHT_SENSOR_PIN);

  // check if any reads failed
  if (isnan(humi) || isnan(tempC)) {
    Serial.println("Failed to read from DHT sensor!");
  } else if (isnan(analogValue)) {
    Serial.println("Failed to read from light sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humi);
    Serial.print("%");

    Serial.print("  |  "); 

    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.print("°C");

    Serial.print("  |  "); 

    Serial.print("Analog Value = ");
    Serial.print(analogValue);   // the raw analog reading
    
    // We'll have a few threshholds, qualitatively determined
    if (analogValue < 50) {
      Serial.println(" => Dark");
    } else if (analogValue < 800) {
      Serial.println(" => Dim");
    } else if (analogValue < 2000) {
      Serial.println(" => Light");
    } else if (analogValue < 3200) {
      Serial.println(" => Bright");
    } else {
      Serial.println(" => Very bright");
    }
  }
}
