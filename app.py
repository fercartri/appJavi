import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Analyzer")
        self.root.geometry("600x400")
        
        # Variables
        self.files = []
        self.file_labels = []
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add file button
        self.add_button = ttk.Button(self.main_frame, text="Add Files", command=self.add_files)
        self.add_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Clear files button
        self.clear_button = ttk.Button(self.main_frame, text="Clear Files", command=self.clear_files)
        self.clear_button.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Files list frame
        self.files_list_frame = ttk.LabelFrame(self.main_frame, text="Selected Files")
        self.files_list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Analyze button
        self.analyze_button = ttk.Button(self.main_frame, text="Analyze Files", command=self.analyze_files)
        self.analyze_button.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Result label
        self.result_label = ttk.Label(self.main_frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    def add_files(self):
        """Add files to the list"""
        new_files = filedialog.askopenfilenames(
            title="Select files",
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
                    label = ttk.Label(self.files_list_frame, text=file)
                    label.grid(row=len(self.file_labels), column=0, sticky=tk.W)
                    self.file_labels.append(label)

    def clear_files(self):
        """Clear all files from the list"""
        self.files.clear()
        for label in self.file_labels:
            label.destroy()
        self.file_labels.clear()
        self.result_label.config(text="")

    def analyze_files(self):
        """Analyze the selected files"""
        num_files = len(self.files)
        
        if num_files not in [3, 5]:
            messagebox.showerror("Error", "Please select exactly 3 or 5 files.")
            return
        
        if num_files == 3:
            self.result_label.config(text="Función 1: Análisis para 3 archivos")
        else:
            self.result_label.config(text="Función 2: Análisis para 5 archivos")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()