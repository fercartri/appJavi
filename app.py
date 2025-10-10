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
        self.clear_button = ttk.Button(self.main_frame, text="Borrar Ficheros", command=self.clear_files)
        self.clear_button.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Cuadro de listado de ficheros
        self.files_list_frame = ttk.LabelFrame(self.main_frame, text="Ficheros seleccionados")
        self.files_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Mensaje por defecto cuando no hay ficheros
        self.empty_label = ttk.Label(self.files_list_frame, text="No hay ficheros seleccionados")
        self.empty_label.grid(row=0, column=0, sticky=tk.W)

        # Botón para analizar ficheros
        self.analyze_button = ttk.Button(self.main_frame, text="Analizar Ficheros", command=self.analyze_files)
        self.analyze_button.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Mensaje de resultado
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    def add_files(self):
        self.clear_files()

        new_files = filedialog.askopenfilenames(
            title="Seleccionar ficheros",
            filetypes=[("All files", "*.*")]
        )

        # Comprobar número de ficheros válido
        if len(new_files) != 3 and len(new_files) != 5:
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
    
    def clear_files(self):
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

    def analyze_files(self):
        num_files = len(self.files)

        try:
            matrices = []
            summaries = []
            for filepath in self.files:
                matrix = self._parse_z_like_file(filepath)
                if matrix is None:
                    raise ValueError(f"No se ha podido extraer la matriz de: {filepath}")
                matrices.append(matrix)
                summaries.append((filepath, matrix.shape))

            # Store matrices in the instance for later use
            self.matrices = matrices

            # Create complex vectors from columns 5 (index 4) and 6 (index 5)
            vectors = []
            for m in matrices:
                real = m[:, 4]
                imag = m[:, 5]

                vec = real + 1j * imag
                vectors.append(vec)

            # store vectors
            self.vectors = vectors

            

            # Prepare summary lines so they can be updated with result or errors
            lines = [f"Procesados {len(matrices)} ficheros:"]
            for name, shape in summaries:
                lines.append(f" - {name}: {shape[0]} filas x {shape[1]} columnas")
            if num_files == 3:
                lines.append("Aplicada: Función 1 (3 archivos)")
            else:
                lines.append("Aplicada: Función 2 (5 archivos)")

            # (V3 - V2) / (1 - ((V3 - V2) / V1))
            if len(matrices) == 3:
                try:
                    V1, V2, V3 = vectors[0], vectors[1], vectors[2]
                    delta = V3 - V2
                    # compute ratio = delta / V1 safely (avoid divide-by-zero warnings)
                    with np.errstate(divide='ignore', invalid='ignore'):
                        ratio = np.empty_like(delta, dtype=complex)
                        # where V1 is finite and not NaN, divide; otherwise keep NaN
                        valid_v1 = ~np.isnan(V1)
                        ratio[:] = np.nan + 1j * np.nan
                        np.divide(delta, V1, out=ratio, where=valid_v1)
                        denom = 1 - ratio
                        # avoid division where denom is (close to) zero
                        safe = ~np.isclose(denom, 0)
                        result = np.empty_like(delta, dtype=complex)
                        result[:] = np.nan + 1j * np.nan
                        np.divide(delta, denom, out=result, where=safe)

                    self.result_vector = result
                    # append a short preview to the summary lines
                    preview_n = 10
                    preview = []
                    for val in result[:preview_n]:
                        if np.isnan(val.real) and np.isnan(val.imag):
                            preview.append('nan')
                        else:
                            preview.append(f"{val.real:.6f}{val.imag:+.6f}j")
                    lines.append("Resultado (primeras {} entradas): {}".format(preview_n, ', '.join(preview)))
                except Exception as e:
                    # store nothing on failure, but continue
                    self.result_vector = None
                    lines.append(f"No se pudo calcular el vector resultado: {e}")
            else:
                try:
                    V1, V2, V3, V4, V5 = vectors[0], vectors[1], vectors[2], vectors[3], vectors[4]
                    # formula: (V4*(V3-V2)*(V1-V5))/((V1-V3)*(V5-V2))
                    num = V4 * (V3 - V2) * (V1 - V5)
                    den = (V1 - V3) * (V5 - V2)
                    with np.errstate(divide='ignore', invalid='ignore'):
                        result5 = np.empty_like(num, dtype=complex)
                        result5[:] = np.nan + 1j * np.nan
                        safe = ~np.isclose(den, 0)
                        np.divide(num, den, out=result5, where=safe)

                    self.result_vector = result5
                    preview_n = 10
                    preview = []
                    for val in result5[:preview_n]:
                        if np.isnan(val.real) and np.isnan(val.imag):
                            preview.append('nan')
                        else:
                            preview.append(f"{val.real:.6f}{val.imag:+.6f}j")
                    lines.append("Resultado (primeras {} entradas): {}".format(preview_n, ', '.join(preview)))
                except Exception as e:
                    self.result_vector = None
                    lines.append(f"No se pudo calcular el vector resultado (5 ficheros): {e}")

            # Display completion message (summary + result preview or errors)
            self.result_label.config(text="\n".join(lines))

            # Show result vector in a new window
            if hasattr(self, 'result_vector') and self.result_vector is not None:
                win = tk.Toplevel(self.root)
                win.title("Vector resultante")
                win.geometry("800x600")
                txt = tk.Text(win, wrap='none', font=('Courier', 10))
                txt.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                vsb = ttk.Scrollbar(win, orient='vertical', command=txt.yview)
                vsb.pack(side=tk.RIGHT, fill=tk.Y)
                txt.configure(yscrollcommand=vsb.set)

                txt.insert(tk.END, "Vector resultante:\n")
                for idx, val in enumerate(self.result_vector):
                    if np.isnan(val.real) and np.isnan(val.imag):
                        txt.insert(tk.END, f"{idx}: nan\n")
                    else:
                        txt.insert(tk.END, f"{idx}: {val.real:.6f}{val.imag:+.6f}j\n")
                txt.configure(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _parse_z_like_file(self, filepath):
        """Parse a ZPlot-like ASCII file and return a numeric matrix (numpy array).

        Behavior:
        - Scan header for 'Data Points:' to determine number of data rows.
        - Stop header at the line 'End Comments'.
        - Read the indicated number of non-empty data lines, split by whitespace/tabs,
          convert to float, and return as numpy array. If rows have different
          lengths, pad with NaN to create a rectangular array.
        """
        data_points = None
        data_lines = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                header_found = False
                for line in f:
                    if 'Data Points:' in line:
                        m = re.search(r"(\d+)", line)
                        if m:
                            data_points = int(m.group(1))
                    if line.strip() == 'End Comments':
                        header_found = True
                        break
                
                if not header_found:
                    raise ValueError("No se encontró la sección 'End Comments' en el archivo")

                # Read data lines
                if data_points is None:
                    # read until EOF
                    for line in f:
                        if line.strip():
                            data_lines.append(line.strip())
                else:
                    while len(data_lines) < data_points:
                        line = f.readline()
                        if not line:
                            break
                        if line.strip():
                            data_lines.append(line.strip())

            # Parse numeric rows
            matrix = []
            for line in data_lines:
                parts = [p for p in re.split(r"\s+", line.strip()) if p != '']
                try:
                    row = [float(p.replace(',', '.')) for p in parts]
                    matrix.append(row)
                except Exception:
                    # skip non-numeric lines
                    continue

            if not matrix:
                return None

            max_cols = max(len(r) for r in matrix)
            norm = [r + [np.nan] * (max_cols - len(r)) for r in matrix]
            return np.array(norm, dtype=float)

        except Exception:
            return None

    def _show_matrices_window(self, matrices, filepaths):
        win = tk.Toplevel(self.root)
        win.title("Matrices extraídas")
        win.geometry("1000x1000")

        # Text widget with scrollbar
        txt = tk.Text(win, wrap='none', font=('Courier', 10))
        txt.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(win, orient='vertical', command=txt.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(win, orient='horizontal', command=txt.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for idx, matrix in enumerate(matrices):
            header = f"Archivo: {filepaths[idx]} -- {matrix.shape[0]} filas x {matrix.shape[1]} columnas\n"
            txt.insert(tk.END, header)
            # Format matrix rows
            for row in matrix:
                row_str = '\t\t'.join(("{:.6f}".format(x) if not np.isnan(x) else "nan") for x in row)
                txt.insert(tk.END, row_str + "\n")
            txt.insert(tk.END, "\n")

        # Make read-only
        txt.configure(state='disabled')

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()