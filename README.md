<div align="center">
  <h1>Analizador de Ficheros para SMAP</h1>
  <p>
    Una aplicación de escritorio para el análisis de datos del grupo de investigación SMAP de la Universidad de Valladolid.
  </p>
</div>

---

## 1. ¿Qué es?

Esta aplicación permite seleccionar y procesar conjuntos de ficheros de datos (compatibles con el formato de salida de ZPlot) mediante una interfaz gráfica sencilla. Ha sido desarrollada para el grupo de investigación **Superficies y Materiales Porosos (SMAP)** de la Universidad de Valladolid con el objetivo de automatizar una serie de cálculos específicos entre vectores de números complejos.

## 2. Características Principales

- **Interfaz Gráfica de Usuario (GUI)**: Creada con Tkinter para una experiencia de usuario sencilla e intuitiva.
- **Selección de Ficheros**: Permite seleccionar exactamente **3 o 5 ficheros** para el análisis.
- **Parseo Inteligente**: Lee ficheros con cabeceras de longitud variable, identificando el bloque de datos a partir de los marcadores `Data Points:` y `End Comments`.
- **Extracción de Vectores**: Crea automáticamente un vector de números complejos por cada fichero, utilizando la **columna 5 como parte real** y la **columna 6 como parte imaginaria**.
- **Cálculos Automatizados**:
  - **Con 3 ficheros**: Calcula el vector resultante punto a punto usando la fórmula:
    `Resultado = (V3 - V2) / (1 - ((V3 - V2) / V1))`
  - **Con 5 ficheros**: Calcula el vector resultante usando la fórmula:
    `Resultado = (V4 * (V3 - V2) * (V1 - V5)) / ((V1 - V3) * (V5 - V2))`
- **Visualización de Resultados**: Muestra en pantalla las matrices originales, los vectores complejos extraídos y el vector resultante final, con un formato claro y alineado.
- **Manejo de Errores**: Informa al usuario sobre ficheros con formato incorrecto o divisiones por cero durante el cálculo.

## 3. Tecnologías Utilizadas

- **Lenguaje**: Python 3
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