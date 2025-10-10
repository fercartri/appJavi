import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import re

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Ficheros ZPlot-Javier Carmona")
        self.root.geometry("1000x800")
        
        # Variables
        self.files = []
        self.file_labels = []
        
        # Crea marco principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón para añadir ficheros
        self.add_button = ttk.Button(self.main_frame, text="Subir Ficheros", command=self.add_files)
        self.add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Botón para borrar ficheros
        self.clear_button = ttk.Button(self.main_frame, text="Borrar Ficheros", command=self.delete_files)
        self.clear_button.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Cuadro de listado de ficheros
        self.files_list_frame = ttk.LabelFrame(self.main_frame, text="Ficheros seleccionados")
        self.files_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Mensaje por defecto cuando no hay ficheros
        self.empty_label = ttk.Label(self.files_list_frame, text="No hay ficheros seleccionados")
        self.empty_label.grid(row=0, column=0, sticky=tk.W)

        # Botón para analizar ficheros
        self.analyze_button = ttk.Button(self.main_frame, text="Analizar Ficheros", command=self.analizar_ficheros)
        self.analyze_button.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Mensaje de resultado
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    def add_files(self):
        self.delete_files()

        new_files = filedialog.askopenfilenames(
            title="Seleccionar ficheros",
            filetypes=[("All files", "*.*")]
        )

        # Comprobar número de ficheros válido
        if len(new_files) != 0 and len(new_files) != 3 and len(new_files) != 5:
            messagebox.showerror("Error", "Debe seleccionar 3 o 5 ficheros")
            return

        # Remove empty label if present
        if self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None
        
        for file in new_files:
            label = ttk.Label(self.files_list_frame, text=file)
            label.grid(row=len(self.file_labels), column=0, sticky=tk.W)
            self.files.append(file)
            self.file_labels.append(label)

        text = f"Se han subido {len(self.file_labels)} ficheros"
        self.result_label.config(text=text)
    
    def delete_files(self):
        # Limpiar la lista de archivos
        self.files.clear()
        
        # Destruir los widgets de las etiquetas existentes
        for label in self.file_labels:
            label.destroy()
        self.file_labels.clear()
        
        # Limpiar el mensaje de resultado
        self.result_label.config(text="")
        
        # Mostrar el mensaje de "no hay ficheros"
        self.empty_label = ttk.Label(self.files_list_frame, text="No hay ficheros seleccionados")
        self.empty_label.grid(row=0, column=0, sticky=tk.W)

    def read_matrix(self, filepath):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()

                for i, line in enumerate(lines):
                    if "Data Points:" in line:
                        data_points = int(line.split(":")[1].strip())
                    if "End Comments:" in line:
                        data_start = i + 1
                        break
                
                # Extraer los datos numéricos
                data_lines = lines[data_start:]
                data = []
                for line in data_lines:
                    # Eliminar espacios en blanco extras y dividir por tabulaciones o espacios
                    values = re.split(r'\s+', line.strip())
                    # Convertir strings a números flotantes, ignorando valores vacíos
                    try:
                        row = [float(val) for val in values if val]
                        if row:  # Solo agregar si la fila tiene datos
                            data.append(row)
                    except ValueError:
                        continue  # Ignorar líneas que no se pueden convertir a números
                
                return np.array(data), data_points
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo {filepath}: {str(e)}")
            return None, None

    def analizar_ficheros(self):
        num_files = len(self.files)
        if num_files == 0:
            messagebox.showwarning("Aviso", "No hay ficheros seleccionados para analizar")
            return
        
        # Diccionario para almacenar las matrices de datos y número de puntos
        matrices_datos = {}
        num_puntos = {}
        
        # Procesar cada archivo
        for file in self.files:
            matriz, puntos = self.read_matrix(file)
            if matriz is not None:
                matrices_datos[file] = matriz
                num_puntos[file] = puntos
        
        # Actualizar el mensaje de resultado
        num_matrices = len(matrices_datos)
        if num_matrices > 0:
            resultado = []
            for file in matrices_datos:
                shape = matrices_datos[file].shape
                puntos = num_puntos[file]
                nombre_archivo = file.split("\\")[-1]  # Obtener solo el nombre del archivo
                resultado.append(f"{nombre_archivo}: {shape[0]}x{shape[1]} (Puntos de datos: {puntos})")
            
            self.result_label.config(
                text="Archivos procesados:\n" + "\n".join(resultado)
            )
        else:
            self.result_label.config(text="No se pudo procesar ningún archivo correctamente")
        
        return matrices_datos, num_puntos

        if num_files == 0:
            messagebox.showerror("Error", "Debe seleccionar 3 o 5 ficheros")
            return
        
        # Diccionario para almacenar las matrices de datos
        matrices_datos = {}
        
        # Procesar cada archivo
        for file in self.files:
            matriz = self.read_matrix(file)
            if matriz is not None:
                matrices_datos[file] = matriz
        
        # Actualizar el mensaje de resultado
        num_matrices = len(matrices_datos)
        if num_matrices > 0:
            shapes = [matriz.shape for matriz in matrices_datos.values()]
            shapes_str = ", ".join([f"{shape[0]}x{shape[1]}" for shape in shapes])
            self.result_label.config(
                text=f"Se han procesado {num_matrices} archivos. Dimensiones de las matrices: {shapes_str}"
            )
        else:
            self.result_label.config(text="No se pudo procesar ningún archivo correctamente")
        
        return matrices_datos

        

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()