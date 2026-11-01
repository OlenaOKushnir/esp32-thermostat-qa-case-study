/* Hardware doubles for component tests, not an ESP32/Wokwi emulator.
   Firmware function bodies are appended without modification by the runner. */
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#define HIGH 1
#define LOW 0
#define SENSOR_TYPE_DHT22
#define RELAY_PIN 5
#define ILI9341_BLACK 0
#define ILI9341_WHITE 1
#define isnan(x) ((x) != (x))
static unsigned long fake_time = 1000;
static int button_level = HIGH;
static int output_level = LOW;
static long encoder_count = 0;
static float sensor_value = 24.0;
static int displayed_mode = -1;
static int frame_count = 0;
unsigned long millis(void) { return fake_time; }
int digitalRead(int pin) { return button_level; }
void digitalWrite(int pin, int level) { output_level = level; }
static void ignored() {}
static void new_frame(int color) { frame_count++; }
static void display_line(const char *line) {
    if (!strcmp(line, "VIEW")) displayed_mode = 0;
    if (!strcmp(line, "SET LOWER")) displayed_mode = 1;
    if (!strcmp(line, "SET UPPER")) displayed_mode = 2;
}
static float sensor_read(void) { return sensor_value; }
static long encoder_read(void) { return encoder_count; }
static void encoder_write(long count) { encoder_count = count; }
struct SerialDouble { void (*print)(); void (*println)(); } Serial = {ignored, ignored};
struct DisplayDouble {
    void (*fillScreen)(int);
    void (*setTextColor)();
    void (*setTextSize)();
    void (*setCursor)();
    void (*print)();
    void (*println)(const char *);
} tft = {new_frame, ignored, ignored, ignored, ignored, display_line};
struct SensorDouble { float (*readTemperature)(void); } dht = {sensor_read};
struct EncoderDouble { long (*read)(void); void (*write)(long); } encoder = {encoder_read, encoder_write};
struct EncoderDouble *myEnc = &encoder;
const int SW_PIN = 27;
void updateDisplay(float currentTemp);
float readTemperature(void);
void updateRelay(float temperature);
void handleEncoder(void);
void toggleMode(void);
void loop(void);
typedef enum Mode Mode;
