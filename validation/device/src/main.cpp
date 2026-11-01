#include <Arduino.h>
#include <DHT.h>

#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <Encoder.h>

void validationFrame(int mode);
void validationMode(int mode, uint32_t acceptedAt);
void validationStart();

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
  validationStart();
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
  validationFrame((int)currentMode);
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
  const uint32_t valAcceptedAt = millis();
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
  validationMode((int)currentMode, valAcceptedAt);
}

volatile uint32_t valFrameAt = 0, valModeAt = 0, valFrameCount = 0;
volatile int valFrameMode = -1, valObservedMode = 0;
const int VAL_STIM_PIN = 32;
void validationFrame(int mode) {
  valFrameMode = mode; valFrameAt = millis(); valFrameCount++;
  Serial.printf("[VAL_FRAME] ms=%lu mode=%d\n", (unsigned long)valFrameAt, mode);
}
void validationMode(int mode, uint32_t acceptedAt) {
  valModeAt = acceptedAt; valObservedMode = mode;
  Serial.printf("[VAL_MODE] ms=%lu mode=%d\n", (unsigned long)acceptedAt, mode);
}
int observedMode() { return valObservedMode; }
void valWait(uint32_t ms) { vTaskDelay(pdMS_TO_TICKS(ms)); }
bool waitNewFrame(uint32_t before, uint32_t timeout=4000) {
  uint32_t start=millis();
  while (valFrameCount==before && millis()-start<timeout) valWait(1);
  return valFrameCount!=before;
}
bool physicalPress(uint32_t holdAfterAccept=60) {
  int before=observedMode(); uint32_t start=millis();
  digitalWrite(VAL_STIM_PIN,LOW);
  while (observedMode()==before && millis()-start<2500) valWait(1);
  bool accepted=observedMode()!=before;
  valWait(holdAfterAccept); digitalWrite(VAL_STIM_PIN,HIGH); valWait(300);
  return accepted;
}
bool returnToView() {
  for(int i=0;i<3 && observedMode()!=0;i++) if(!physicalPress()) return false;
  return observedMode()==0;
}
void validationTask(void*) {
  Serial.println("[VAL_BEGIN] instrumented ESP32 GPIO32->GPIO27; no logical-state injection");
  if(!waitNewFrame(0)) { Serial.println("[VAL_ABORT] no initial frame"); vTaskDelete(nullptr); return; }
  valWait(10);

  int before=observedMode(); uint32_t start=millis();
  digitalWrite(VAL_STIM_PIN,LOW);
  while(observedMode()==before && millis()-start<2500) valWait(1);
  if(observedMode()==before) { digitalWrite(VAL_STIM_PIN,HIGH); Serial.println("[VAL_ABORT] no accepted press"); vTaskDelete(nullptr); return; }
  int target=observedMode(); uint32_t accepted=valModeAt;
  valWait(60); digitalWrite(VAL_STIM_PIN,HIGH);
  start=millis();
  while(valFrameMode!=target && millis()-start<4000) valWait(1);
  uint32_t elapsed=valFrameAt-accepted;
  Serial.printf("[VAL_RESULT] case=T05 accepted_ms=%lu frame_ms=%lu elapsed_ms=%lu budget_ms=500 actual_mode=%d frame_mode=%d pass=%d\n",
    (unsigned long)accepted,(unsigned long)valFrameAt,(unsigned long)elapsed,target,valFrameMode,(int)(valFrameMode==target && elapsed<=500));
  valWait(350);
  if(!returnToView()) { Serial.println("[VAL_ABORT] could not return to VIEW"); vTaskDelete(nullptr); return; }

  uint32_t count=valFrameCount; waitNewFrame(count); valWait(10);
  digitalWrite(VAL_STIM_PIN,LOW); valWait(1100);
  digitalWrite(VAL_STIM_PIN,HIGH); valWait(150);
  Serial.printf("[VAL_RESULT] case=T04_CLEAN actual_mode=%d expected_mode=1 pass=%d\n",observedMode(),(int)(observedMode()==1));
  valWait(300);
  if(!returnToView()) { Serial.println("[VAL_ABORT] could not reset after control"); vTaskDelete(nullptr); return; }

  count=valFrameCount; waitNewFrame(count); valWait(10);
  uint32_t pressAt=millis(); digitalWrite(VAL_STIM_PIN,LOW); valWait(1100);
  uint32_t releaseAt=millis(); digitalWrite(VAL_STIM_PIN,HIGH); valWait(5);
  uint32_t bounceAt=millis(); digitalWrite(VAL_STIM_PIN,LOW); valWait(20);
  digitalWrite(VAL_STIM_PIN,HIGH); valWait(150);
  Serial.printf("[VAL_RESULT] case=T04_BOUNCE press_ms=%lu release_ms=%lu bounce_ms=%lu rebound_low_ms=20 actual_mode=%d expected_mode=1 pass=%d\n",
    (unsigned long)pressAt,(unsigned long)releaseAt,(unsigned long)bounceAt,observedMode(),(int)(observedMode()==1));
  Serial.println("[VAL_END] stimulus pin HIGH; original control logic retained");
  vTaskDelete(nullptr);
}
void validationStart() {
  pinMode(VAL_STIM_PIN,OUTPUT); digitalWrite(VAL_STIM_PIN,HIGH);
  xTaskCreatePinnedToCore(validationTask,"validation",6144,nullptr,1,nullptr,0);
}
