import tkinter as tk
from tkinter import messagebox
from lectura_qrs import LecturaQRWindow
from trabajadores import CRUDApp
from impresion_qrs import ImpresionQRWindow
from informes import VentanaInformes
from config import PrinterInfoWindow
import csv
import pandas as pd
import os
import queue
from _datetime import datetime


class MenuApp:
    def __init__(self, root, console_queue):
        self.root = root
        self.root.title("Menu")
        self.console_queue = console_queue

        # Ajusta las dimensiones de la ventana de menú
        self.root.geometry("600x800")

        # Cargar el logo para la ventana del menú
        self.logo = tk.PhotoImage(file="data/logo.png")
        self.label_logo = tk.Label(root, image=self.logo)
        self.label_logo.pack(pady=10)

        # Labels
        self.btn_trabajadores = tk.Button(root, text="Trabajadores", command=self.abrir_ventana_trabajador)
        self.btn_lecturas = tk.Button(root, text="Leer QrS", command=self.abrir_ventana_lectura)
        self.btn_imprimir = tk.Button(root, text="Imprimir Qrs", command=self.abrir_ventana_imprimir)
        self.btn_user = tk.Button(root, text="Usuarios", command=self.abrir_ventana_lectura)
        self.btn_info = tk.Button(root, text="Informes", command=self.abrir_ventana_informes)
        self.btn_Config = tk.Button(root, text="Configuracion", command=self.abrir_ventana_pinter)

        # Estilo de los botones
        button_style = ("Helvetica", 12)  # Fuente y tamaño
        bg_color = "#656565"  # Color de fondo
        fg_color = "white"  # Color del texto

        # Configurar y empaquetar los botones
        for button in [self.btn_trabajadores, self.btn_lecturas, self.btn_imprimir, self.btn_user, self.btn_info,
                       self.btn_Config]:
            button.config(font=button_style, bg=bg_color, fg=fg_color, padx=20, pady=10, height=2, width=15)
            button.pack(pady=10)

        self.btn_user.pack_forget()

    def abrir_ventana_lectura(self):
        LecturaQRWindow(self.console_queue)

    def abrir_ventana_trabajador(self):
        top_level = tk.Toplevel(self.root)
        CRUDApp(top_level)

    def abrir_ventana_imprimir(self):
        # Obtener datos de la segunda columna del archivo CSV
        data = self.obtener_datos_columna(['id', 'rut'])
        # Verificar si hay datos antes de abrir la ventana de impresión
        if data:
            ImpresionQRWindow(self.root, data)
        else:
            tk.messagebox.showwarning("Advertencia", "No hay datos disponibles para imprimir QRs.")

    def abrir_ventana_informes(self):
        top_level = tk.Toplevel(self.root)
        VentanaInformes(top_level)

    def obtener_datos_columna(self, columnas):
        # Función para obtener datos de columnas específicas del archivo CSV
        try:
            with open('data/datos.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                return [dict(row) for row in reader]
        except FileNotFoundError:
            tk.messagebox.showerror("Error", "El archivo 'datos.csv' no se encuentra.")
            return []

    def abrir_ventana_pinter(self):
        PrinterInfoWindow(self.root)

    def csv_to_excel(self, csv_path):
        # Cargar el archivo CSV en un DataFrame
        df = pd.read_csv(csv_path)

        # Obtener la fecha actual en el formato dd/mm/aa
        current_date = datetime.now().strftime("%d%m%y")

        # Obtener el nombre base del archivo (sin extensión)
        base_name = os.path.splitext(os.path.basename(csv_path))[0]

        # Crear el nombre del archivo Excel con el formato deseado
        excel_file_name = f"{current_date}_{base_name}.xlsx"

        # Ruta completa para guardar el archivo Excel en la carpeta 'informes'
        excel_file_path = os.path.join("informes", excel_file_name)

        # Guardar el DataFrame como archivo Excel
        df.to_excel(excel_file_path, index=False, engine='openpyxl')

        print(f"Archivo Excel guardado: {excel_file_path}")

    def informes(self):

        informe_cantidadQR = "data/cantidadQr.csv"
        self.csv_to_excel(informe_cantidadQR)

        informe_trabajadores = "data/datos.csv"
        self.csv_to_excel(informe_trabajadores)

        informe_lecturas = "data/lecturas.csv"
        self.csv_to_excel(informe_lecturas)


if __name__ == "__main__":
    root = tk.Tk()
    console_queue = queue
    app = MenuApp(root,console_queue)
    root.mainloop()
