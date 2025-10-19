# Analizador de Ficheros para SMAP

Una aplicación de escritorio para el análisis de datos del grupo de investigación SMAP de la Universidad de Valladolid.

## 1. ¿Qué es?

Esta aplicación permite seleccionar y procesar conjuntos de ficheros de datos (compatibles con el formato de salida de ZPlot) mediante una interfaz gráfica sencilla. Ha sido desarrollada para el grupo de investigación **Superficies y Materiales Porosos (SMAP)** de la Universidad de Valladolid con el objetivo de automatizar una serie de cálculos específicos entre vectores de números complejos.

## 2. Características Principales

- **Interfaz Gráfica de Usuario (GUI)**: Creada con Tkinter para una experiencia de usuario sencilla e intuitiva.
- **Selección Flexible de Ficheros**: Permite asignar ficheros a 5 ranuras (V1 a V5), permitiendo cambiar un fichero individualmente sin reiniciar todo el proceso. El análisis se ejecuta con 3 o 5 ficheros.
- **Parseo Inteligente**: Lee ficheros con cabeceras de longitud variable, identificando el bloque de datos a partir de los marcadores `Data Points:` y `End Comments`.
- **Extracción de Vectores**: Crea automáticamente un vector de números complejos por cada fichero, utilizando la **5ª columna como parte real** y la **6ª columna como parte imaginaria**.
- **Cálculos Automatizados**:
  - **Con 3 ficheros**: Calcula el vector resultante punto a punto usando la fórmula:
    `Resultado = V1 * ((V2 - V3) / (V3 - V1))`
  - **Con 5 ficheros**: Calcula el vector resultante usando la fórmula:
    `Resultado = (V4 * (V3 - V2) * (V1 - V5)) / ((V1 - V3) * (V5 - V2))`
- **Visualización de Resultados**: Muestra en pantalla las matrices originales, los vectores complejos extraídos y el vector resultante final, con un formato claro y alineado.
- **Exportación Automática**: Al finalizar un análisis con éxito, genera y guarda automáticamente un nuevo fichero (`.z`) con el resultado. Este fichero usa el tercer fichero (V3) como plantilla, sustituyendo las columnas 5 y 6 por los nuevos valores calculados en notación científica.
- **Manejo de Errores**: Informa al usuario sobre ficheros con formato incorrecto o divisiones por cero durante el cálculo.

## 3. Tecnologías Utilizadas

- **Lenguaje**: Python 3 (3.10.11)
- **Interfaz Gráfica**: Tkinter (biblioteca estándar de Python)
- **Cálculo Numérico**: NumPy

## 4. Requisitos

- Python 3.8+ (recomendado)
- Paquetes Python:
  - `numpy`

Para instalar la única dependencia necesaria, abre una terminal y ejecuta:

```powershell
pip install numpy
```

## Uso

1. Abrir una terminal (Windows PowerShell) en la carpeta del proyecto.
2. Ejecutar la aplicación:

```powershell
python app.py
```

3. Usar el botón "Subir Ficheros" y seleccionar los 3 o 5 ficheros a analizar.
4. Pulsar "Analizar ficheros" para obtener los resultados.

Los resultados se muestran en la interfaz y pueden copiarse desde el área de texto.

## Notas y consideraciones

- El parser omite la cabecera hasta `End Comments` y usa la línea `Data Points:` para saber cuántas filas de datos leer. Si un fichero no contiene esas marcas, el comportamiento por defecto puede fallar; en ese caso conviene revisar el fichero.
- Los cálculos se realizan punto a punto y asumen que todos los ficheros tienen el mismo número de puntos y el mismo orden de frecuencias.
- Se recomiendan copias de seguridad de los datos originales antes de procesarlos.

## Contacto
Proyecto realizado por Fernando Carmona para el grupo el grupo SMAP — Universidad de Valladolid.
Para dudas o mejoras, contactar con los responsables del repositorio.