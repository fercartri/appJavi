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
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add file button
        self.add_button = ttk.Button(self.main_frame, text="Subir Ficheros", command=self.add_files)
        self.add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Clear files button
        self.clear_button = ttk.Button(self.main_frame, text="Borrar Ficheros", command=self.clear_files)
        self.clear_button.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Files list frame
        self.files_list_frame = ttk.LabelFrame(self.main_frame, text="Ficheros seleccionados")
        self.files_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Default empty label shown when no files are selected
        self.empty_label = ttk.Label(self.files_list_frame, text="No hay ficheros seleccionados")
        self.empty_label.grid(row=0, column=0, sticky=tk.W)
        
        # Analyze button
        self.analyze_button = ttk.Button(self.main_frame, text="Analizar Ficheros", command=self.analyze_files)
        self.analyze_button.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Result label
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    def add_files(self):
        new_files = filedialog.askopenfilenames(
            title="Seleccionar ficheros",
            filetypes=[("All files", "*.*")]
        )
        
        if new_files:
            # Clear existing files if adding new ones would exceed 5
            if len(self.files) + len(new_files) > 5:
                self.clear_files()
            
            # Add new files
            for file in new_files:
                if len(self.files) < 5:
                    self.files.append(file)
                    # Remove the default empty label once we add the first file
                    if getattr(self, 'empty_label', None) is not None:
                        try:
                            self.empty_label.destroy()
                        except Exception:
                            pass
                        self.empty_label = None

                    label = ttk.Label(self.files_list_frame, text=file)
                    label.grid(row=len(self.file_labels), column=0, sticky=tk.W)
                    self.file_labels.append(label)

    def clear_files(self):
        self.files.clear()
        for label in self.file_labels:
            label.destroy()
        self.file_labels.clear()
        self.result_label.config(text="")
        # Restore default empty label
        if getattr(self, 'empty_label', None) is None:
            self.empty_label = ttk.Label(self.files_list_frame, text="No hay ficheros seleccionados")
            self.empty_label.grid(row=0, column=0, sticky=tk.W)

    def analyze_files(self):
        num_files = len(self.files)
        
        if num_files not in [3, 5]:
            messagebox.showerror("Error", "Please select exactly 3 or 5 files.")
            return
        
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

            # Display summary
            lines = [f"Procesados {len(matrices)} ficheros:"]
            for name, shape in summaries:
                lines.append(f" - {name}: {shape[0]} filas x {shape[1]} columnas")
            if num_files == 3:
                lines.append("Aplicada: Función 1 (3 archivos)")
            else:
                lines.append("Aplicada: Función 2 (5 archivos)")

            self.result_label.config(text="\n".join(lines))

            # Show matrices in a new window
            # self._show_matrices_window(matrices, self.files)

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
                for line in f:
                    if 'Data Points:' in line:
                        m = re.search(r"(\d+)", line)
                        if m:
                            data_points = int(m.group(1))
                    if line.strip() == 'End Comments':
                        break

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