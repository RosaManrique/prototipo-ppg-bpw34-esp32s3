#include <Wire.h>

// Pines acordados para la versión inicial (verificar el modelo exacto de ESP32-S3).
#define SDA_PIN 8
#define SCL_PIN 9

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  Serial.println("\nEscaner I2C iniciado");
}

void loop() {
  byte count = 0;
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Dispositivo encontrado: 0x");
      if (address < 16) Serial.print('0');
      Serial.println(address, HEX);
      count++;
    }
  }
  if (count == 0) Serial.println("No se detectaron dispositivos I2C.");
  Serial.println("---");
  delay(3000);
}
