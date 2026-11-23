# Integrante 4 - Firmware y adquisición PPG V1

## Hardware asumido
- ESP32-S3 DevKit; pines I2C propuestos: SDA GPIO8, SCL GPIO9.
- ADS1115 alimentado a 3.3 V; ADDR a GND (dirección 0x48).
- MCP6002-I/P como TIA, alimentado a 3.3 V.
- BPW34 conectado al TIA.
- Salida del TIA a ADS1115 A0.
- Salida bufferizada VREF (~1.65 V) a ADS1115 A1.
- LED rojo convencional accionado por transistor desde GPIO4.
- GND común.

Verificar que el módulo ADS1115 tenga pull-ups I2C adecuados a 3.3 V. No aplicar 5 V a los GPIO del ESP32-S3 ni a las entradas ADS1115 cuando se alimentan a 3.3 V.

## Firmware Arduino IDE
Instalar desde Library Manager:
- Adafruit ADS1X15
- Adafruit BusIO (normalmente se instala como dependencia)

Orden sugerido:
1. Abrir `firmware/00_Escaner_I2C.ino` y confirmar que aparece 0x48.
2. Abrir `firmware/01_Prueba_ADS1115.ino` y comprobar A0, A1 y A0-A1.
3. Abrir `firmware/02_PPG_BPW34_ADS1115.ino` para adquisición continua.

El firmware de adquisición usa:
- GPIO4 para el driver del LED (LED encendido al iniciar).
- GPIO8 SDA, GPIO9 SCL.
- ADS1115 diferencial A0-A1.
- Ganancia GAIN_TWO (+/-2.048 V) y tasa nominal 128 SPS.
- Salida serial CSV a 115200 baudios.

Comandos por serial:
- `L1` + Enter: LED encendido.
- `L0` + Enter: LED apagado.

La función de lectura diferencial de la biblioteca inicia una conversión y espera su resultado. La frecuencia efectiva puede ser menor que 128 SPS por el tiempo de conversión y el envío serial; por eso el firmware registra `t_us` y Python calcula la frecuencia real. No afirmar 128 SPS efectivos sin medirlos.

## Python
Instalar Python 3.10 o superior. Desde esta carpeta:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Capturar:

```bash
python capturar_ppg.py
```

El script pregunta puerto COM, código anónimo, condición y duración. Cierra Arduino Serial Monitor/Plotter antes de usarlo. Las capturas se guardan en `datos/raw`.

Graficar:

```bash
python graficar_ppg.py
```

O pasar un archivo:

```bash
python graficar_ppg.py "..\\datos\\raw\\archivo.csv"
```

## Interpretación y límites
- El ADC mide `A0 - A1`, es decir, salida TIA menos referencia bufferizada. Esto permite observar la señal diferencial centrada en VREF.
- A0 y A1 deben permanecer individualmente dentro de GND y VDD; la ganancia diferencial no permite sobrepasar los límites de los pines.
- El ADS1115 es una sustitución de prototipo, no equivalente al ADS1220 de la arquitectura multiespectral final.
- El LED rojo convencional no puede declararse como 660 nm sin datasheet.
- Las capturas obtenidas con BPW34/MCP6002 no deben mezclarse sin más con el dataset del MAX30102. Reentrenar el clasificador con registros de la cadena nueva.
- El montaje es experimental, no diagnóstico. Para ensayos con dedo, usar alimentación por batería sin cargador conectado y no conectar simultáneamente osciloscopios/equipos referenciados a red sin evaluación de aislamiento.

## Modelo preliminar de calidad
Después de reunir capturas nuevas de la cadena BPW34 + MCP6002 + ADS1115 (varios participantes y ambas condiciones), instalar los paquetes adicionales de `requirements.txt` y ejecutar:

```bash
python entrenar_calidad.py
```

Se extraen cuatro características por captura completa: media diferencial, desviación AC, amplitud robusta y desviación de diferencias. El árbol se evalúa separando participantes, no ventanas aleatorias de la misma captura. Se necesita un mínimo práctico de 3 participantes y ambas etiquetas en entrenamiento y prueba.

Para evaluar una captura nueva:

```bash
python predecir_captura.py "..\\datos\\raw\\P01_prueba_YYYYMMDD_HHMMSS.csv"
```

El modelo debe entrenarse con capturas de esta nueva cadena analógica. No reutilizar directamente el modelo entrenado con MAX30102, porque la escala, respuesta espectral, geometría y acondicionamiento son diferentes.
