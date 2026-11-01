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

void qaInitEarly(); void qaInitOutput(); void qaStart(); void qaSample(float); void qaFrame(float); void qaMode();
extern volatile bool qaReadValid;

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
  qaInitEarly();

  static Encoder encoder(ENCODER_CLK, ENCODER_DT);
  myEnc = &encoder;

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  qaInitOutput();

  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  displayInfo("Initializing...");

  dht.begin();

  pinMode(SW_PIN, INPUT_PULLUP);

  delay(2000);
  qaStart();
}

void loop() {
  static unsigned long lastUpdate = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastUpdate >= 1000) {
    lastUpdate = currentMillis;
    float temperature = readTemperature();

    updateRelay(temperature);
    qaSample(temperature);

    updateDisplay(temperature);
  }

  handleEncoder();
}

float readTemperature() {
  float temperature = 0.0;

  temperature = dht.readTemperature();
  qaReadValid = !isnan(temperature);
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
  qaFrame(currentTemp);
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
  qaMode();
}

#include <driver/gpio.h>
const int QA_CLK=13, QA_DT=12, QA_SW=32, QA_DHT=33;
const int QA_NO=34, QA_NC=35, QA_REQ=36;
volatile bool qaReady=false, qaFault=false, qaReadValid=false;
volatile int16_t qaTemperature=240;
volatile uint32_t qaLowAt=0;
volatile bool qaSending=false;
volatile uint32_t qaEdges=0, qaHighEdges=0;
volatile uint32_t qaFrameMs=0, qaAcceptedMs=0;
volatile int qaFrameMode=-1;

void IRAM_ATTR qaRequestEdge() {
  qaEdges++;
  if (gpio_get_level((gpio_num_t)QA_REQ)) qaHighEdges++;
}
void IRAM_ATTR qaDhtEdge() {
  if (qaSending) return;
  int level=gpio_get_level((gpio_num_t)QA_DHT);
  if (!level) { qaLowAt=micros(); return; }
  uint32_t began=qaLowAt; qaLowAt=0;
  if (!began || (uint32_t)(micros()-began)<900 || qaFault) return;
  qaSending=true;
  int16_t temperature=qaTemperature;
  uint16_t raw=temperature<0 ? (uint16_t)(-temperature)|0x8000 : (uint16_t)temperature;
  uint8_t bytes[5]={1,144,(uint8_t)(raw>>8),(uint8_t)raw,0};
  bytes[4]=(uint8_t)(bytes[0]+bytes[1]+bytes[2]+bytes[3]);
  delayMicroseconds(20);
  gpio_set_level((gpio_num_t)QA_DHT,0); delayMicroseconds(80);
  gpio_set_level((gpio_num_t)QA_DHT,1); delayMicroseconds(80);
  for(int b=0;b<5;b++) for(int bit=7;bit>=0;bit--) {
    gpio_set_level((gpio_num_t)QA_DHT,0); delayMicroseconds(50);
    gpio_set_level((gpio_num_t)QA_DHT,1); delayMicroseconds((bytes[b]&(1<<bit))?70:26);
  }
  gpio_set_level((gpio_num_t)QA_DHT,0); delayMicroseconds(50);
  gpio_set_level((gpio_num_t)QA_DHT,1);
  qaLowAt=0;qaSending=false;
}
void qaInitEarly() {
  pinMode(QA_NO,INPUT);pinMode(QA_NC,INPUT);pinMode(QA_REQ,INPUT);
  attachInterrupt(digitalPinToInterrupt(QA_REQ),qaRequestEdge,CHANGE);
  Serial.printf("[QA_BOOT] phase=early ms=%lu pin=%d no=%d nc=%d\n",millis(),digitalRead(QA_REQ),digitalRead(QA_NO),digitalRead(QA_NC));
}
void qaInitOutput() {
  Serial.printf("[QA_BOOT] phase=output_init ms=%lu mode=%d lower=%.1f upper=%.1f req=%d pin=%d no=%d nc=%d\n",millis(),(int)currentMode,LOWER_THRESHOLD,UPPER_THRESHOLD,(int)relayState,digitalRead(QA_REQ),digitalRead(QA_NO),digitalRead(QA_NC));
}
void qaSample(float temperature) {
  Serial.printf("[QA_SAMPLE] ms=%lu valid=%d temp=%.1f req=%d pin=%d no=%d nc=%d mode=%d lower=%.1f upper=%.1f enc=%ld edges=%lu high_edges=%lu\n",
    millis(),(int)qaReadValid,temperature,(int)relayState,digitalRead(QA_REQ),digitalRead(QA_NO),digitalRead(QA_NC),(int)currentMode,LOWER_THRESHOLD,UPPER_THRESHOLD,myEnc->read(),qaEdges,qaHighEdges);
}
void qaFrame(float temperature) {
  qaFrameMs=millis();qaFrameMode=(int)currentMode;
  Serial.printf("[QA_FRAME] ms=%lu temp=%.1f mode=%d lower=%.1f upper=%.1f\n",qaFrameMs,temperature,(int)currentMode,LOWER_THRESHOLD,UPPER_THRESHOLD);
}
void qaMode() {
  qaAcceptedMs=millis();
  Serial.printf("[QA_MODE] ms=%lu mode=%d\n",qaAcceptedMs,(int)currentMode);
}
void qaServiceDht() {
  if(!gpio_get_level((gpio_num_t)QA_DHT)) {
    uint32_t began=micros();
    while(!gpio_get_level((gpio_num_t)QA_DHT) && (uint32_t)(micros()-began)<2000) {}
    if(gpio_get_level((gpio_num_t)QA_DHT)) { qaLowAt=micros()-1100;qaDhtEdge(); }
  }
}
void qaWait(uint32_t ms) {
  uint32_t began=millis();
  do { qaServiceDht();vTaskDelay(1); } while((uint32_t)(millis()-began)<ms);
}
void qaTurn(int count,int direction) {
  const uint8_t sequence[2][4]={{1,0,2,3},{2,0,1,3}};
  for(int i=0;i<count;i++) for(int j=0;j<4;j++) {
    uint8_t value=sequence[direction<0?1:0][j];
    digitalWrite(QA_CLK,(value&2)?HIGH:LOW);digitalWrite(QA_DT,(value&1)?HIGH:LOW);
    qaWait(5);
  }
}
void qaTask(void*) {
  pinMode(QA_CLK,OUTPUT);pinMode(QA_DT,OUTPUT);pinMode(QA_SW,OUTPUT);
  digitalWrite(QA_CLK,HIGH);digitalWrite(QA_DT,HIGH);digitalWrite(QA_SW,HIGH);
  gpio_set_direction((gpio_num_t)QA_DHT,GPIO_MODE_INPUT_OUTPUT_OD);
  gpio_set_pull_mode((gpio_num_t)QA_DHT,GPIO_PULLUP_ONLY);
  gpio_set_level((gpio_num_t)QA_DHT,1);
  disableCore0WDT();
  qaReady=true;
  Serial.println("[QA_READY] protocol=DHT22 source=GPIO33 clk=13 dt=12 sw=32");
  char buffer[96];int used=0;
  for(;;) {
    while(Serial.available()) {
      char c=(char)Serial.read();
      if(c=='\r')continue;
      if(c=='\n') {
        buffer[used]=0;used=0;char id[20]={0},op[20]={0};int a=0,b=0;
        if(sscanf(buffer,"%19s %19s %d %d",id,op,&a,&b)<2)continue;
        uint32_t began=millis();
        if(!strcmp(op,"TEMP"))qaTemperature=(int16_t)a;
        else if(!strcmp(op,"FAULT"))qaFault=a!=0;
        else if(!strcmp(op,"TURN"))qaTurn(a,b);
        else if(!strcmp(op,"PRESS")) { digitalWrite(QA_SW,LOW);qaWait(a);digitalWrite(QA_SW,HIGH);qaWait(b); }
        else if(!strcmp(op,"BOUNCE")) {
          digitalWrite(QA_SW,LOW);qaWait(1100);digitalWrite(QA_SW,HIGH);qaWait(5);
          digitalWrite(QA_SW,LOW);qaWait(20);digitalWrite(QA_SW,HIGH);qaWait(250);
        }
        else if(!strcmp(op,"RESET")) {
          Serial.printf("[QA_ACK] id=%s op=RESET begin=%lu end=%lu\n",id,began,millis());qaWait(100);ESP.restart();
        }
        else if(strcmp(op,"PING")) { Serial.printf("[QA_ERROR] id=%s op=%s\n",id,op);continue; }
        Serial.printf("[QA_ACK] id=%s op=%s begin=%lu end=%lu a=%d b=%d\n",id,op,began,millis(),a,b);
      } else if(used<(int)sizeof(buffer)-1)buffer[used++]=c;
    }
    qaWait(1);
  }
}
void qaStart() {
  xTaskCreatePinnedToCore(qaTask,"qa-controller",6144,nullptr,1,nullptr,0);
  while(!qaReady)delay(1);
}
