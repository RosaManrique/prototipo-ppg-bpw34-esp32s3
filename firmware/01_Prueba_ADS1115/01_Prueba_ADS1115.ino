#include <Wire.h>
#include <Adafruit_ADS1X15.h>

#define SDA_PIN 8
#define SCL_PIN 9
#define ADS_ADDRESS 0x48  // ADDR del ADS1115 conectado a GND

Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);  // I2C conservador para la primera prueba

  if (!ads.begin(ADS_ADDRESS)) {
    Serial.println("ERROR: ADS1115 no detectado. Revise VDD, GND, SDA, SCL y ADDR.");
    while (true) delay(1000);
  }

  ads.setGain(GAIN_TWO);                 // +/-2.048 V
  ads.setDataRate(RATE_ADS1115_128SPS); // 128 conversiones/s nominales

  Serial.println("A0_V,A1_V,A0_A1_V,A0_A1_counts");
}

void loop() {
  int16_t a0 = ads.readADC_SingleEnded(0);
  int16_t a1 = ads.readADC_SingleEnded(1);
  int16_t diff = ads.readADC_Differential_0_1();

  Serial.print(ads.computeVolts(a0), 6);
  Serial.print(',');
  Serial.print(ads.computeVolts(a1), 6);
  Serial.print(',');
  Serial.print(ads.computeVolts(diff), 6);
  Serial.print(',');
  Serial.println(diff);

  delay(250);
}
