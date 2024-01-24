import tkinter as tk
from tkinter import ttk
from itertools import cycle
from impresion_qrs import ImpresionQRWindow
from lectura_qrs import LecturaQRWindow
import csv
import sys


def digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    return (-s) % 11
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ING-Lectura")

        # Variables
        self.rut_var = tk.StringVar()
        self.digito_var = tk.StringVar()
        self.nombre_var = tk.StringVar()

        # Crear Treeview
        self.tree = ttk.Treeview(root, columns=('ID', 'RUT', 'Digito', 'Nombre'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('RUT', text='RUT')
        self.tree.heading('Digito', text='Dígito')
        self.tree.heading('Nombre', text='Nombre')

        # Configurar el ancho y alineación de las columnas
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('RUT', width=80, anchor='center')
        self.tree.column('Digito', width=80, anchor='center')
        self.tree.column('Nombre', width=150, anchor='center')

        self.tree.pack()

        # Formulario de entrada
        self.rut_label = tk.Label(root, text='RUT:')
        self.rut_entry = tk.Entry(root, textvariable=self.rut_var)
        self.digito_label = tk.Label(root, text='Dígito Verificador:')
        self.digito_entry = tk.Entry(root, textvariable=self.digito_var)
        self.nombre_label = tk.Label(root, text='Nombre:')
        self.nombre_entry = tk.Entry(root, textvariable=self.nombre_var)

        self.rut_label.pack()
        self.rut_entry.pack()
        self.digito_label.pack()
        self.digito_entry.pack()
        self.nombre_label.pack()
        self.nombre_entry.pack()

        # Botones
        self.btn_crear = tk.Button(root, text='Crear', command=self.crear_registro)
        self.btn_eliminar = tk.Button(root, text='Eliminar', command=self.eliminar_registro)

        self.btn_crear.pack()
        self.btn_eliminar.pack()

        # Botón para abrir la ventana de impresión de QRs
        self.btn_imprimir_qrs= tk.Button(root, text='Imprimir QRs', command=self.abrir_ventana_imprimir)
        self.btn_imprimir_qrs.pack()

        # Botón para abrir la ventana de lectura de QRs
        self.btn_leer_qrs = tk.Button(root, text='Leer QRs', command=self.abrir_ventana_leer_qrs)
        self.btn_leer_qrs.pack()

        # Cargar datos desde el archivo CSV
        self.cargar_datos()

    def abrir_ventana_imprimir(self):
        # Obtener datos de la segunda columna del archivo CSV
        data = self.obtener_datos_columna(['id', 'rut'])
        # Verificar si hay datos antes de abrir la ventana de impresión
        if data:
            ImpresionQRWindow(self.root, data)
        else:
            tk.messagebox.showwarning("Advertencia", "No hay datos disponibles para imprimir QRs.")

    def abrir_ventana_leer_qrs(self):
        # Abre la ventana de lectura de QRs
        LecturaQRWindow()

    def obtener_datos_columna(self, columnas):
        # Función para obtener datos de columnas específicas del archivo CSV
        try:
            with open('data/datos.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                return [dict(row) for row in reader]
        except FileNotFoundError:
            tk.messagebox.showerror("Error", "El archivo 'datos.csv' no se encuentra.")
            return []

    def cargar_datos(self):
        try:
            with open('data/datos.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.tree.insert('', 'end', values=(row['id'], row['rut'], row['digito'], row['nombre']))
        except FileNotFoundError:
            # Si el archivo no existe, simplemente continúa sin cargar datos
            pass

    def guardar_datos(self):
        with open('data/datos.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'rut', 'digito', 'nombre'])
            for child in self.tree.get_children():
                values = self.tree.item(child, 'values')
                writer.writerow(values)

    def crear_registro(self):
        rut = self.rut_var.get()
        digito = self.digito_var.get()
        nombre = self.nombre_var.get()

        try:
            # Intenta convertir rut y digito a enteros
            if digito == "K":
                digito = 10
            rut_entero = int(rut)
            digito_entero = int(digito)
            if digito == "10":
                digito = "K"

            print(digito_verificador(rut_entero))

            if rut_entero > 0 and digito_entero >= 0 and nombre:
                if digito_verificador(rut_entero) == digito_entero:
                    # Obtener el próximo ID con formato de tres dígitos
                    nuevo_id = f"{len(self.tree.get_children()) + 1:03d}"
                    self.tree.insert('', 'end', values=(nuevo_id, rut, digito, nombre))
                    self.guardar_datos()
                else:
                    print("El dígito verificador no coincide")
            else:
                print("Los valores de RUT y Dígito deben ser números enteros no negativos.")
        except ValueError:
            print("Error al convertir RUT o Dígito a número entero.")
    def eliminar_registro(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.guardar_datos()

if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()

