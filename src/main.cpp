#include <Arduino.h>
#include <DHT.h>

#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <Encoder.h>

void displayInfo(String message);
void updateDisplay(float currentTemp);
float readTemperature();
void updateRelay(float temperature);
void handleEncoder();
void toggleMode();

#define DHTTYPE DHT22
#define DHTPIN 16

#define RELAY_PIN 5

#define TFT_CS    14
#define TFT_RST   17
#define TFT_DC    4
#define TFT_MOSI  23
#define TFT_SCLK  18
#define TFT_MISO  19

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

#define ENCODER_CLK 25
#define ENCODER_DT  26
#define ENCODER_SW  27

Encoder *myEnc = nullptr;
const int SW_PIN = ENCODER_SW;

float LOWER_THRESHOLD = 20.0;
float UPPER_THRESHOLD = 25.0;

bool relayState = false;
bool swPressed = false;
unsigned long lastSwPress = 0;

enum Mode { VIEW, SET_LOWER, SET_UPPER };
Mode currentMode = VIEW;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);

  static Encoder encoder(ENCODER_CLK, ENCODER_DT);
  myEnc = &encoder;

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  displayInfo("Initializing...");

  dht.begin();

  pinMode(SW_PIN, INPUT_PULLUP);

  delay(2000);
}

void loop() {
  static unsigned long lastUpdate = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastUpdate >= 1000) {
    lastUpdate = currentMillis;
    float temperature = readTemperature();

    updateRelay(temperature);

    updateDisplay(temperature);
  }

  handleEncoder();
}

float readTemperature() {
  float temperature = 0.0;

  temperature = dht.readTemperature();
  if (isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    temperature = 0.0;
  }

  return temperature;
}

void updateRelay(float temperature) {
  if (temperature < LOWER_THRESHOLD && !relayState) {
    digitalWrite(RELAY_PIN, HIGH);
    relayState = true;
    Serial.println("Relay Activated.");
  }
  else if (temperature >= UPPER_THRESHOLD && relayState) {
    digitalWrite(RELAY_PIN, LOW);
    relayState = false;
    Serial.println("Relay Deactivated.");
  }
}

void displayInfo(String message) {
  tft.fillScreen(ILI9341_BLACK);
  tft.setCursor(10, 10);
  tft.println(message);
}

void updateDisplay(float currentTemp) {
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);

  tft.setCursor(10, 10);
  tft.print("Mode: ");
  switch (currentMode) {
    case VIEW:
      tft.println("VIEW");
      break;
    case SET_LOWER:
      tft.println("SET LOWER");
      break;
    case SET_UPPER:
      tft.println("SET UPPER");
      break;
  }

  tft.setCursor(10, 40);
  tft.print("Room Temp: ");
  tft.print(currentTemp, 1);
  tft.println(" C");

  tft.setCursor(10, 70);
  tft.print("Lower Set: ");
  tft.print(LOWER_THRESHOLD, 1);
  tft.println(" C");

  tft.setCursor(10, 100);
  tft.print("Upper Set: ");
  tft.print(UPPER_THRESHOLD, 1);
  tft.println(" C");

  if (currentMode == SET_LOWER || currentMode == SET_UPPER) {
    tft.setCursor(10, 130);
    tft.print("Rotate to adjust, Press to confirm.");
  }
}

void handleEncoder() {
  static long lastPosition = 0;
  long newPosition = myEnc->read() / 4;

  if (newPosition != lastPosition) {
    long delta = newPosition - lastPosition;
    lastPosition = newPosition;

    if (currentMode == SET_LOWER) {
      LOWER_THRESHOLD += delta * 0.5;
      if (LOWER_THRESHOLD < -50.0) LOWER_THRESHOLD = -50.0;
      if (LOWER_THRESHOLD > UPPER_THRESHOLD - 0.5) LOWER_THRESHOLD = UPPER_THRESHOLD - 0.5;
      Serial.print("Lower Threshold: ");
      Serial.println(LOWER_THRESHOLD);
    }
    else if (currentMode == SET_UPPER) {
      UPPER_THRESHOLD += delta * 0.5;
      if (UPPER_THRESHOLD > 100.0) UPPER_THRESHOLD = 100.0;
      if (UPPER_THRESHOLD < LOWER_THRESHOLD + 0.5) UPPER_THRESHOLD = LOWER_THRESHOLD + 0.5;
      Serial.print("Upper Threshold: ");
      Serial.println(UPPER_THRESHOLD);
    }

    updateDisplay(readTemperature());
  }

  if (digitalRead(SW_PIN) == LOW) {
    if (!swPressed && (millis() - lastSwPress > 200)) {
      swPressed = true;
      lastSwPress = millis();
      toggleMode();
    }
  }
  else {
    swPressed = false;
  }
}

void toggleMode() {
  switch (currentMode) {
    case VIEW:
      currentMode = SET_LOWER;
      break;
    case SET_LOWER:
      currentMode = SET_UPPER;
      break;
    case SET_UPPER:
      currentMode = VIEW;
      myEnc->write(0);
      break;
  }
  Serial.print("Mode changed to: ");
  switch (currentMode) {
    case VIEW:
      Serial.println("VIEW");
      break;
    case SET_LOWER:
      Serial.println("SET LOWER");
      break;
    case SET_UPPER:
      Serial.println("SET UPPER");
      break;
  }
}
