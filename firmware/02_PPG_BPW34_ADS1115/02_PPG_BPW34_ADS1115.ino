#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <string.h>

// Primera versión: LED rojo fijo + BPW34/TIA (MCP6002) + ADS1115 + ESP32-S3.
// A0 = salida del TIA; A1 = VREF_BUF (~1.65 V); lectura diferencial A0-A1.
// GPIO4 controla el transistor del LED rojo.

#define SDA_PIN 8
#define SCL_PIN 9
#define LED_PIN 4
#define ADS_ADDRESS 0x48  // ADDR conectado a GND
#define SERIAL_BAUD 115200

Adafruit_ADS1115 ads;
uint32_t sampleIndex = 0;
bool ledOn = true;

void processSerialCommands() {
  // Comandos no bloqueantes: L1 = LED encendido; L0 = LED apagado.
  static char command[4];
  static uint8_t pos = 0;

  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      command[pos] = '\0';
      if (strcmp(command, "L1") == 0) {
        ledOn = true;
        digitalWrite(LED_PIN, HIGH);
        Serial.println("# LED=ON");
      } else if (strcmp(command, "L0") == 0) {
        ledOn = false;
        digitalWrite(LED_PIN, LOW);
        Serial.println("# LED=OFF");
      }
      pos = 0;
    } else if (pos < sizeof(command) - 1) {
      command[pos++] = c;
    } else {
      pos = 0; // descartar comando demasiado largo
    }
  }
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED encendido para primera captura PPG

  Serial.begin(SERIAL_BAUD);
  delay(1000);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);

  if (!ads.begin(ADS_ADDRESS)) {
    digitalWrite(LED_PIN, LOW);
    Serial.println("# ERROR: ADS1115 no detectado en 0x48");
    while (true) delay(1000);
  }

  ads.setGain(GAIN_TWO);                 // +/-2.048 V diferencial
  ads.setDataRate(RATE_ADS1115_128SPS); // tasa nominal seleccionada

  Serial.println("# PPG BPW34 - MCP6002 - ADS1115");
  Serial.println("# A0=TIA_OUT; A1=VREF_BUF; medir diferencial A0-A1");
  Serial.println("# Comandos: L1 enciende LED; L0 apaga LED");
  Serial.println("sample_idx,t_us,adc_counts,differential_V,led_on");
}

void loop() {
  processSerialCommands();

  // Conversión diferencial en modo single-shot. La función espera el resultado.
  int16_t adcCounts = ads.readADC_Differential_0_1();
  uint32_t timestampUs = micros();
  float differentialV = ads.computeVolts(adcCounts);

  Serial.print(sampleIndex++);
  Serial.print(',');
  Serial.print(timestampUs);
  Serial.print(',');
  Serial.print(adcCounts);
  Serial.print(',');
  Serial.print(differentialV, 6);
  Serial.print(',');
  Serial.println(ledOn ? 1 : 0);
}
