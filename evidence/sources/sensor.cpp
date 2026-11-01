#include <Arduino.h>
#include <DHT.h>              // Include if using DHT22
#include <DHT_U.h>            // Include if using DHT22
#include <OneWire.h>          // Include if using DS18B20
//#include <DallasTemperature.h>// Include if using DS18B20
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <Encoder.h>

// Added for PlatformIO main.cpp (Arduino .ino generates these automatically).
void displayInfo(String message);
void updateDisplay(float currentTemp);
float readTemperature();
void updateRelay(float temperature);
void handleEncoder();
void toggleMode();

// ===================== Configuration =====================

// Choose your sensor type
#define SENSOR_TYPE_DHT22
// #define SENSOR_TYPE_DS18B20

// DHT22 Configuration
#ifdef SENSOR_TYPE_DHT22
  #define DHTTYPE DHT22
  #define DHTPIN 16  // Changed from GPIO4 to GPIO16
#endif

// DS18B20 Configuration (if used)
#ifdef SENSOR_TYPE_DS18B20
  #define ONE_WIRE_BUS 16  // Ensure it's not conflicting with other pins
#endif

// Relay Configuration
#define RELAY_PIN 5  // GPIO connected to the relay

// ILI9341 Display Configuration
#define TFT_CS    14    // Changed from GPIO15 to GPIO14
#define TFT_RST   17    // Changed from GPIO2 to GPIO17
#define TFT_DC    4     // Kept GPIO4
#define TFT_MOSI  23
#define TFT_SCLK  18
#define TFT_MISO  19 // Not used but required by the library

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

// Rotary Encoder Configuration
#define ENCODER_CLK 25
#define ENCODER_DT  26
#define ENCODER_SW  27

// Construct after the ESP32 scheduler starts, not during global initialization.
Encoder *myEnc = nullptr;
const int SW_PIN = ENCODER_SW;

// Temperature Thresholds
float LOWER_THRESHOLD = 20.0; // Initial lower temperature in °C
float UPPER_THRESHOLD = 25.0; // Initial upper temperature in °C

// State Variables
bool relayState = false;
long oldPosition  = -999;
bool swPressed = false;
unsigned long lastSwPress = 0;

// Mode Selection
enum Mode { VIEW, SET_LOWER, SET_UPPER };
Mode currentMode = VIEW;

// ===================== Sensor Initialization =====================

#ifdef SENSOR_TYPE_DHT22
  DHT dht(DHTPIN, DHTTYPE);
#endif

//#ifdef SENSOR_TYPE_DS18B20
 // OneWire oneWire(ONE_WIRE_BUS);
 // DallasTemperature sensors(&oneWire);
//#endif

// ===================== Setup Function =====================

void setup() {
  Serial.begin(115200);

  static Encoder encoder(ENCODER_CLK, ENCODER_DT);
  myEnc = &encoder;

  // Initialize Relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Assuming LOW is OFF

  // Initialize Display
  tft.begin();
  tft.setRotation(1); // Landscape
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  displayInfo("Initializing...");

  // Initialize Sensor
  #ifdef SENSOR_TYPE_DHT22
    dht.begin();
  #endif

  //#ifdef SENSOR_TYPE_DS18B20
   // sensors.begin();
  //#endif

  // Initialize Rotary Encoder Button
  pinMode(SW_PIN, INPUT_PULLUP);

  // Small delay to allow sensors and display to initialize
  delay(2000);
}

// ===================== Loop Function =====================

void loop() {
  static unsigned long lastUpdate = 0;
  unsigned long currentMillis = millis();

  // Update display every 1 second
  if (currentMillis - lastUpdate >= 1000) {
    lastUpdate = currentMillis;
    float temperature = readTemperature();

    // Update Relay State
    updateRelay(temperature);
    Serial.printf("[SAMPLE] ms=%lu temp=%.1f output=%d\n", millis(), temperature, (int)relayState);

    // Update Display
    updateDisplay(temperature);
  }

  // Handle Rotary Encoder
  handleEncoder();
}

// ===================== Temperature Reading =====================

float readTemperature() {
  float temperature = 0.0;

  #ifdef SENSOR_TYPE_DHT22
    temperature = dht.readTemperature();
    if (isnan(temperature)) {
      Serial.println("Failed to read from DHT sensor!");
      temperature = 0.0;
    }
  #endif

  #ifdef SENSOR_TYPE_DS18B20
    sensors.requestTemperatures();
    temperature = sensors.getTempCByIndex(0);
    if (temperature == DEVICE_DISCONNECTED_C) {
      Serial.println("Error: Could not read temperature data");
      temperature = 0.0;
    }
  #endif

  return temperature;
}

// ===================== Relay Control =====================

void updateRelay(float temperature) {
  if (temperature < LOWER_THRESHOLD && !relayState) {
    digitalWrite(RELAY_PIN, HIGH); // Activate relay
    relayState = true;
    Serial.println("Relay Activated.");
  }
  else if (temperature >= UPPER_THRESHOLD && relayState) {
    digitalWrite(RELAY_PIN, LOW); // Deactivate relay
    relayState = false;
    Serial.println("Relay Deactivated.");
  }
}

// ===================== Display Functions =====================

void displayInfo(String message) {
  tft.fillScreen(ILI9341_BLACK);
  tft.setCursor(10, 10);
  tft.println(message);
}

void updateDisplay(float currentTemp) {
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);

  // Display Mode
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

  // Display Current Temperature
  tft.setCursor(10, 40);
  tft.print("Room Temp: ");
  tft.print(currentTemp, 1);
  tft.println(" C");

  // Display Lower Threshold
  tft.setCursor(10, 70);
  tft.print("Lower Set: ");
  tft.print(LOWER_THRESHOLD, 1);
  tft.println(" C");

  // Display Upper Threshold
  tft.setCursor(10, 100);
  tft.print("Upper Set: ");
  tft.print(UPPER_THRESHOLD, 1);
  tft.println(" C");

  // Indicate if in SET mode
  if (currentMode == SET_LOWER || currentMode == SET_UPPER) {
    tft.setCursor(10, 130);
    tft.print("Rotate to adjust, Press to confirm.");
  }
}

// ===================== Rotary Encoder Handling =====================

void handleEncoder() {
  static long lastPosition = 0;
  long newPosition = myEnc->read() / 4; // Adjust for encoder resolution

  if (newPosition != lastPosition) {
    long delta = newPosition - lastPosition;
    lastPosition = newPosition;

    if (currentMode == SET_LOWER) {
      LOWER_THRESHOLD += delta * 0.5; // Adjust step size as needed
      if (LOWER_THRESHOLD < -50.0) LOWER_THRESHOLD = -50.0;
      if (LOWER_THRESHOLD > UPPER_THRESHOLD - 0.5) LOWER_THRESHOLD = UPPER_THRESHOLD - 0.5;
      Serial.print("Lower Threshold: ");
      Serial.println(LOWER_THRESHOLD);
    }
    else if (currentMode == SET_UPPER) {
      UPPER_THRESHOLD += delta * 0.5; // Adjust step size as needed
      if (UPPER_THRESHOLD > 100.0) UPPER_THRESHOLD = 100.0;
      if (UPPER_THRESHOLD < LOWER_THRESHOLD + 0.5) UPPER_THRESHOLD = LOWER_THRESHOLD + 0.5;
      Serial.print("Upper Threshold: ");
      Serial.println(UPPER_THRESHOLD);
    }

    updateDisplay(readTemperature());
  }

  // Handle button press with debounce
  if (digitalRead(SW_PIN) == LOW) {
    if (!swPressed && (millis() - lastSwPress > 200)) { // Debounce delay
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
      myEnc->write(0); // Reset encoder position after setting
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

// ===================== End of Code =====================
