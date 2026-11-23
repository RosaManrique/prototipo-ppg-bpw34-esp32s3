# Sistema de adquisición fotopletismográfica (PPG) para evaluación no invasiva de hemoglobina

**Proyecto de Instrumentación Electrónica – Grupo 08**

**Universidad Nacional Mayor de San Marcos**  
Facultad de Ingeniería Electrónica y Eléctrica  
Escuela Profesional de Ingeniería Biomédica

## Descripción del proyecto

El presente repositorio contiene los archivos de programación, adquisición, procesamiento y visualización desarrollados para el prototipo de un sistema de instrumentación biomédica basado en fotopletismografía (PPG).

El proyecto busca desarrollar una plataforma de adquisición óptica que permita obtener señales fisiológicas mediante diferentes longitudes de onda, con miras a investigar su utilización en la estimación no invasiva de hemoglobina.

La primera versión del prototipo está orientada a comprobar experimentalmente una cadena de adquisición PPG propia, utilizando un fotodiodo BPW34, un amplificador operacional MCP6002 y un convertidor analógico-digital ADS1115, controlados mediante un microcontrolador ESP32-S3.

## Arquitectura de la primera versión

La cadena de adquisición implementada contempla los siguientes elementos:

- **ESP32-S3:** unidad central de control, adquisición y comunicación.
- **LED rojo:** emisor óptico para las primeras pruebas de reflectancia.
- **BPW34:** fotodiodo encargado de recibir la radiación óptica reflejada.
- **MCP6002:** acondicionamiento analógico mediante amplificación de transimpedancia y generación de referencia.
- **ADS1115:** conversión analógico-digital de 16 bits mediante comunicación I²C.
- **Python:** recepción, almacenamiento, visualización y análisis preliminar de las señales.

La lectura analógica se realiza de manera diferencial entre las entradas A0 y A1 del ADS1115, permitiendo observar las variaciones de la señal respecto a la referencia de polarización del amplificador.

## Estructura del repositorio

```text
prototipo-ppg-bpw34-esp32s3/
│
├── firmware/
│   ├── 01_escaner_i2c.ino
│   ├── 02_prueba_led.ino
│   └── 03_adquisicion_ppg_ads1115.ino
│
├── python/
│   ├── capturar_ppg.py
│   ├── graficar_ppg.py
│   └── requirements.txt
│
├── datos/
│
└── README.md
```

## Firmware del ESP32-S3

La carpeta `firmware` contiene los programas desarrollados para:

1. Verificar la comunicación I²C entre el ESP32-S3 y el ADS1115.
2. Comprobar la activación del LED mediante una etapa de conmutación.
3. Adquirir la señal analógica de manera diferencial y transmitir los resultados mediante comunicación serial USB.

## Procesamiento en Python

La carpeta `python` contiene las herramientas desarrolladas para:

- Capturar datos provenientes del ESP32-S3.
- Registrar mediciones en archivos CSV.
- Organizar las capturas según las condiciones experimentales.
- Representar gráficamente las señales PPG.
- Realizar una inspección preliminar de sus componentes AC y DC.

### Instalación de dependencias

Se requiere Python 3 y las bibliotecas indicadas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Ejecución de los programas

Para registrar las mediciones:

```bash
python capturar_ppg.py
```

Para visualizar una captura:

```bash
python graficar_ppg.py
```

## Proyección de desarrollo

La primera versión constituye una etapa inicial de instrumentación y adquisición óptica.

Las siguientes etapas contemplan:

- Incorporación de emisores de 660, 730, 850 y 940 nm.
- Desarrollo de la adquisición multiespectral.
- Implementación del convertidor ADS1220.
- Integración de sensores auxiliares de fuerza y temperatura.
- Reproducción de señales PPG mediante un convertidor DAC MCP4921.
- Integración del procesamiento digital y evaluación de algoritmos de clasificación.
- Validación experimental progresiva del sistema.

## Consideraciones

Los resultados obtenidos corresponden a un prototipo académico experimental. El sistema no constituye un dispositivo médico certificado, no realiza diagnósticos y su primera versión no proporciona estimaciones clínicas de hemoglobina.

## Autores

**Grupo 08 – Proyecto de Instrumentación Electrónica**

Universidad Nacional Mayor de San Marcos  
Escuela Profesional de Ingeniería Biomédica
