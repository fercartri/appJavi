# Análisis de ficheros para el grupo SMAP de la Universidad de Valladolid.

## Qué es

Esta aplicación permite seleccionar y procesar conjuntos de ficheros de datos (formatos tipo Z de ZPlot u otros con columnas numéricas) mediante una interfaz gráfica sencilla creada con Tkinter. Está pensada para uso del grupo SMAP para automatizar el cálculo de vectores complejos y operaciones entre ellos según el número de ficheros cargados (3 o 5).

## Características principales

- Interfaz gráfica basada en Tkinter.
- Selección de exactamente 3 o 5 ficheros para el análisis.
- Lectura de ficheros con cabeceras de longitud variable (se omite todo hasta `End Comments` y se respeta el campo `Data Points`).
- Conversión de las columnas de datos a tipos numéricos y creación de vectores complejos a partir de las columnas 5 (parte real) y 6 (parte imaginaria).
- Cálculos automáticos:
	- Si se cargan 3 ficheros: calcula el vector resultado punto a punto usando la fórmula (V3 - V2) / (1 - ((V3 - V2) / V1)).
	- Si se cargan 5 ficheros: calcula el vector resultado usando (V4 * (V3 - V2) * (V1 - V5)) / ((V1 - V3) * (V5 - V2)).

## Archivos relevantes

- `appv4.py` / `appv5.py` (según versión): implementaciones de la aplicación Tkinter para seleccionar, parsear y procesar ficheros.

## Requisitos

- Python 3.8+ (recomendado)
- Paquetes Python:
	- `numpy`

Instalación de dependencias (ejemplo):

```powershell
pip install numpy
```

## Uso

1. Abrir una terminal (Windows PowerShell) en la carpeta del proyecto.
2. Ejecutar la aplicación:

```powershell
python app.py
```

3. Usar el botón "Add Files" para seleccionar exactamente 3 o 5 ficheros.
4. Pulsar "Process Files" (o "Analyze Files" en versiones más simples) para obtener los resultados.

Los resultados se muestran en la interfaz y pueden copiarse desde el área de texto.

## Notas y consideraciones

- El parser omite la cabecera hasta `End Comments` y usa la línea `Data Points:` para saber cuántas filas de datos leer. Si un fichero no contiene esas marcas, el comportamiento por defecto puede fallar; en ese caso conviene revisar el fichero.
- Los cálculos se realizan punto a punto y asumen que todos los ficheros tienen el mismo número de puntos y el mismo orden de frecuencias.
- Se recomiendan copias de seguridad de los datos originales antes de procesarlos.

## Contacto

Proyecto mantenido para el grupo SMAP — Universidad de Valladolid.
Para dudas o mejoras, contactar con los responsables del repositorio.