import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import re
from pathlib import Path
import io

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Ficheros ZPlot-Javier Carmona")
        self.root.geometry("1000x800")
        self.root.state('zoomed')
        
        # Variables
        self.files = [None] * 5  # Lista de 5 ranuras para ficheros
        self.file_widgets = [] # Para guardar las etiquetas y entradas de la UI
        self.vector_resultado = None
        
        # Crea marco principal
        # Usaremos pack para dividir la ventana en el marco principal y la barra de estado
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Barra de estado en la parte inferior
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(2, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        author_label = ttk.Label(self.status_bar, text="Desarrollado por Fernando Carmona Palacio", anchor=tk.E)
        author_label.pack(fill=tk.X)
        
        # Configurar el grid del main_frame para que la fila de resultados se expanda
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        # Botón para borrar ficheros
        self.clear_button = ttk.Button(self.main_frame, text="Borrar Ficheros", command=self.delete_files)
        self.clear_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Cuadro de listado de ficheros
        self.files_list_frame = ttk.LabelFrame(self.main_frame, text="Ficheros seleccionados")
        self.files_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Crear 5 ranuras para ficheros
        for i in range(5):
            slot_frame = ttk.Frame(self.files_list_frame)
            slot_frame.grid(row=i, column=0, sticky=tk.EW, pady=2)
            self.files_list_frame.columnconfigure(0, weight=1)

            label = ttk.Label(slot_frame, text=f"Fichero {i+1} (V{i+1}):")
            label.grid(row=0, column=0, padx=5, sticky=tk.W)

            entry = ttk.Entry(slot_frame, width=80, state="readonly")
            entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
            slot_frame.columnconfigure(1, weight=1)

            # Usamos una función lambda para capturar el valor de 'i'
            select_button = ttk.Button(slot_frame, text="Seleccionar...", command=lambda i=i: self.select_file_for_slot(i))
            select_button.grid(row=0, column=2, padx=5)

            clear_button = ttk.Button(slot_frame, text="Quitar", command=lambda i=i: self.clear_slot(i))
            clear_button.grid(row=0, column=3, padx=5)

            self.file_widgets.append({'entry': entry, 'select_button': select_button, 'clear_button': clear_button})

        # Botón para analizar ficheros
        self.analyze_button = ttk.Button(self.main_frame, text="Analizar Ficheros", command=self.analyze_files)
        self.analyze_button.grid(row=0, column=1, sticky=tk.W, pady=10, padx=5)
        
        # Mensaje de resultado
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Frame para mostrar las matrices
        self.matrices_frame = ttk.LabelFrame(self.main_frame, text="Contenido de las Matrices")
        self.matrices_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.matrices_frame.rowconfigure(0, weight=1)
        self.matrices_frame.columnconfigure(0, weight=1)

        self.matrices_text = tk.Text(self.matrices_frame, wrap="none", height=10)
        self.matrices_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.scrollbar_y = ttk.Scrollbar(self.matrices_frame, orient=tk.VERTICAL, command=self.matrices_text.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.matrices_text.config(yscrollcommand=self.scrollbar_y.set)

    def select_file_for_slot(self, slot_index):
        new_file = filedialog.askopenfilename(
            title=f"Seleccionar Fichero {slot_index + 1}",
            filetypes=[("All files", "*.*")]
        )

        if not new_file: # Si el usuario cancela la selección
            return

        # Comprobar si el fichero ya ha sido añadido
        if new_file in [f for f in self.files if f is not None]:
            messagebox.showwarning("Fichero duplicado", "Este fichero ya ha sido añadido a la lista.")
            return
        
        # Actualizar la ranura
        self.files[slot_index] = new_file
        entry = self.file_widgets[slot_index]['entry']
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, Path(new_file).name)
        entry.config(state="readonly")

    def clear_slot(self, slot_index):
        self.files[slot_index] = None
        entry = self.file_widgets[slot_index]['entry']
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.config(state="readonly")
    
    def delete_files(self):
        # Limpiar todas las ranuras
        for i in range(5):
            self.clear_slot(i)
        
        # Limpiar el mensaje de resultado
        self.result_label.config(text="")

        # Limpiar el área de texto de las matrices
        self.matrices_text.delete("1.0", tk.END)

        # Resetear el resultado
        self.vector_resultado = None

    def read_matrix(self, filepath):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
    
                data_points = None
                data_start = 0
                
                for i, line in enumerate(lines):
                    # Buscar el número de datos
                    if "Data Points:" in line:
                        data_points = int(line.split(":")[1].strip())
                    # Los datos numéricos comienzan después de "End Comments"
                    if "End Comments" in line:
                        data_start = i + 1
                        break

                data = []

                if data_points is not None:
                    # Procesar solo las líneas que contienen valores numéricos
                    for line in lines[data_start:]:
                        line = line.strip()
                        if not line:  # Saltar líneas vacías
                            continue
                            
                        values = re.split(r'\s+', line)
                        try:
                            # Intentar convertir a float para verificar si es una línea de datos
                            row = [float(val) for val in values if val]
                            if row:  # Solo agregar si la fila tiene datos
                                data.append(row)
                                # Detener cuando hayamos procesado todos los puntos de datos esperados
                                if len(data) >= data_points:
                                    break
                        except ValueError:
                            # Ignorar líneas que no se pueden convertir a float (posibles comentarios extra)
                            continue
                else:
                    messagebox.showerror("Error", f"No se encontró 'Data Points:' o 'End Comments' en el fichero: {Path(filepath).name}")
                    return None, None
                
                return np.array(data), data_points
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo {filepath}: {str(e)}")
            return

    def analyze_files(self):
        # Resetear estado previo
        self.vector_resultado = None

        # Obtener la lista de ficheros reales (no None)
        selected_files = [f for f in self.files if f is not None]
        num_files = len(selected_files)

        if num_files not in [3, 5]:
            messagebox.showerror("Error de Análisis", f"Se requieren 3 o 5 ficheros para el análisis, pero hay {num_files} en la lista.")
            return
        
        # Diccionario para almacenar las matrices de datos y número de puntos
        matrices_datos = {}
        errores = []

        for file in selected_files:
            matriz, puntos = self.read_matrix(file)
            if matriz is not None:
                matrices_datos[file] = matriz
            else:
                errores.append(Path(file).name)
        
        # Si hubo errores, informar al usuario
        if errores:
            messagebox.showwarning("Aviso", "Algunos ficheros no se pudieron procesar:\n" + "\n".join(errores))
        
        # Limpiar el área de texto antes de mostrar nuevos resultados
        self.matrices_text.delete("1.0", tk.END)

        # Actualizar el mensaje de resultado
        num_matrices = len(matrices_datos)
        if num_matrices > 0:
            resultado = []
            for file in matrices_datos:
                # Comprobar si la matriz está vacía
                if matrices_datos[file].size == 0:
                    continue
                shape = matrices_datos[file].shape
                nombre_archivo = Path(file).name # Obtener solo el nombre del archivo
                resultado.append(f"{nombre_archivo}: {shape[0]}x{shape[1]}")
            
                # Imprimir la matriz en el widget de texto
                self.matrices_text.insert(tk.END, f"--- Matriz de: {nombre_archivo} ---\n")
                # Usar np.savetxt con un buffer en memoria para un formato limpio,
                # sin corchetes y con columnas bien alineadas.
                string_buffer = io.StringIO()
                np.savetxt(string_buffer, matrices_datos[file], fmt='%.6f', delimiter='\t\t')
                matriz_str = string_buffer.getvalue()
                self.matrices_text.insert(tk.END, matriz_str + "\n\n")

            self.result_label.config(
                text="Archivos procesados:\n" + "\n".join(resultado)
            )
        else:
            self.result_label.config(text="No se pudo procesar ningún archivo correctamente")
            return # Salir si no hay matrices que procesar
        
        # --- PASO 2: Crear vectores complejos a partir de las matrices ---
        vectores_complejos = []
        archivos_vectores = []  # Guardar los nombres de archivo correspondientes

        # Iterar sobre los ficheros seleccionados para mantener el orden
        for file in selected_files:
            # Si un fichero falló en la lectura, no estará en matrices_datos
            if file not in matrices_datos:
                continue

            matriz = matrices_datos[file]
            nombre_archivo = Path(file).name
            # Comprobar si la matriz tiene suficientes columnas
            if matriz.shape[1] < 6:
                messagebox.showwarning("Aviso", f"El fichero '{nombre_archivo}' tiene menos de 6 columnas y no se puede procesar para obtener el vector complejo.")
                continue

            # Columna 5 (índice 4) es la parte real, Columna 6 (índice 5) es la imaginaria
            parte_real = matriz[:, 4]
            parte_imaginaria = matriz[:, 5]
            
            vectores_complejos.append(parte_real + 1j * parte_imaginaria)
            archivos_vectores.append(nombre_archivo)

        # --- Mostrar los vectores complejos creados ---
        if vectores_complejos:
            self.matrices_text.insert(tk.END, "============================================================\n")
            self.matrices_text.insert(tk.END, "--- Vectores Complejos (Columna 5: Real, Columna 6: Imag) ---\n")
            self.matrices_text.insert(tk.END, "============================================================\n\n")

            for i, vector in enumerate(vectores_complejos):
                nombre_archivo = archivos_vectores[i]
                self.matrices_text.insert(tk.END, f"--- Vector de: {nombre_archivo} ---\n")

                # Formatear cada número complejo y unirlo con saltos de línea
                vector_str = "\n".join([f"{c.real: >12.6f} {c.imag: >+12.6f}j" for c in vector])

                self.matrices_text.insert(tk.END, "      Real         Imaginario\n")
                self.matrices_text.insert(tk.END, vector_str + "\n\n")

        # --- PASO 3: Calcular el vector resultante según el número de ficheros ---
        self.vector_resultado = None
        num_vectores = len(vectores_complejos)

        # Validar que todos los ficheros seleccionados produjeron un vector complejo
        if num_vectores == num_files:
            if num_vectores == 3:
                V1, V2, V3 = vectores_complejos[0], vectores_complejos[1], vectores_complejos[2]
                
                # Fórmula: (V3 - V2) / (1 - ((V3 - V2) / V1))
                numerador = V3 - V2
                # Evitar división por cero en el término intermedio
                with np.errstate(divide='ignore', invalid='ignore'):
                    termino_division = np.divide(numerador, V1)
                    termino_division[V1 == 0] = np.inf # Si V1 es 0, el término es infinito
                denominador = 1 - termino_division
                
                # Evitar división por cero en el cálculo final
                with np.errstate(divide='ignore', invalid='ignore'):
                    self.vector_resultado = np.divide(numerador, denominador)
                    self.vector_resultado[denominador == 0] = np.nan # Marcar como NaN si el denominador es 0

            elif num_vectores == 5:
                V1, V2, V3, V4, V5 = vectores_complejos[0], vectores_complejos[1], vectores_complejos[2], vectores_complejos[3], vectores_complejos[4]
                
                # Fórmula: (V4 * (V3 - V2) * (V1 - V5)) / ((V1 - V3) * (V5 - V2))
                numerador = V4 * (V3 - V2) * (V1 - V5)
                denominador = (V1 - V3) * (V5 - V2)

                with np.errstate(divide='ignore', invalid='ignore'):
                    self.vector_resultado = np.divide(numerador, denominador)
                    self.vector_resultado[denominador == 0] = np.nan # Marcar como NaN si el denominador es 0

        # --- Mostrar el vector resultado ---
        if self.vector_resultado is not None:
            self.matrices_text.insert(tk.END, "============================================================\n")
            self.matrices_text.insert(tk.END, f"--- VECTOR RESULTADO (Cálculo con {num_vectores} ficheros) ---\n")
            self.matrices_text.insert(tk.END, "============================================================\n\n")
            vector_str = "\n".join([f"{c.real: >12.6f} {c.imag: >+12.6f}j" if not np.isnan(c) else "      Cálculo inválido (división por cero)" for c in self.vector_resultado])
            self.matrices_text.insert(tk.END, "      Real         Imaginario\n")
            self.matrices_text.insert(tk.END, vector_str + "\n\n")
            
            # Guardar el fichero automáticamente
            self._save_result_file_auto()

    def _save_result_file_auto(self):
        """Guarda el fichero de resultado automáticamente en el mismo directorio que el fichero plantilla."""
        if self.vector_resultado is None:
            return
        
        # El tercer fichero (ranura 3, índice 2) se usa como plantilla
        if self.files[2] is None:
            messagebox.showerror("Error al guardar", "La ranura del Fichero 3 está vacía y se necesita como plantilla para guardar.")
            return

        template_filepath = Path(self.files[2])
        output_dir = template_filepath.parent

        new_filename = f"{template_filepath.stem}_AJUSTADA{template_filepath.suffix}"
        save_path = output_dir / new_filename
        try:
            with open(template_filepath, 'r') as infile, open(save_path, 'w', newline='\n') as outfile:
                data_started = False
                data_idx = 0
                for line in infile:
                    if "End Comments" in line:
                        data_started = True
                        outfile.write(line)
                        continue
                    
                    if not data_started:
                        outfile.write(line)
                    else:
                        # Es una línea de datos
                        cols = re.split(r'\s+', line.strip())
                        if len(cols) < 6: # Si es una línea de datos mal formada o vacía
                            outfile.write(line)
                            continue

                        result_val = self.vector_resultado[data_idx]

                        if not np.isnan(result_val):
                            cols[4] = f"{result_val.real:.6E}"
                            cols[5] = f"{result_val.imag:.6E}"
                        
                        outfile.write("\t".join(cols) + "\n")
                        data_idx += 1
            
            self.result_label.config(text=self.result_label.cget("text") + f"\nResultado guardado en: {save_path}")

        except Exception as e:
            messagebox.showerror("Error al guardar automáticamente", f"No se pudo guardar el fichero:\n{str(e)}")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()