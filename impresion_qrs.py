import tkinter as tk
import tkinter.messagebox
import csv
import subprocess
from datetime import datetime
import sys
import os


class ImpresionQRWindow:
    def __init__(self, root, data):
        self.root = root
        self.data = data

        self.top = tk.Toplevel(root)
        self.top.title("Impresión de QRs")

        # Variables para almacenar la cantidad de QRs y el RUT
        self.cantidad_qrs = tk.IntVar()
        self.rut = tk.StringVar()

        # Etiqueta y cuadro de entrada para la cantidad de QRs
        tk.Label(self.top, text="Cantidad de QRs a imprimir:").pack()
        entry_cantidad = tk.Entry(self.top, textvariable=self.cantidad_qrs)
        entry_cantidad.pack()

        # Etiqueta y cuadro de entrada para el RUT
        tk.Label(self.top, text="Rut sin dv:").pack()
        entry_rut = tk.Entry(self.top, textvariable=self.rut)
        entry_rut.pack()

        # Botón para iniciar la impresión
        btn_imprimir = tk.Button(self.top, text="Imprimir QRs", command=self.verificar_rut_e_imprimir_qrs)
        btn_imprimir.pack()

    def rut_existe(self, rut):
        # Verifica si el RUT existe en los datos
        return any(row['rut'] == rut for row in self.data)

    def obtener_ultimo_correlativo(self, id_persona):
        try:
            with open('data\lecturas.csv', 'r', newline='') as lecturas_file:
                reader = csv.DictReader(lecturas_file)

                # Filtra las filas según el ID de la persona
                filas_filtradas = [row for row in reader if row['ID Persona'] == id_persona]

                # Verifica si hay filas después del filtrado
                if filas_filtradas:
                    # Encuentra el máximo en la columna 'ultimo Leido' de las filas filtradas
                    max_correlativo = max(row['ultimo Leido']for row in filas_filtradas)
                    max_correlativo = int(max_correlativo) + 1
                    max_correlativo = str(max_correlativo)
                    return max_correlativo
                else:
                    tk.messagebox.showwarning("Advertencia",
                                              f"No hay filas para el ID de persona {id_persona}. "
                                              f"Se empezará por el 001")
                    return "001"

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "El archivo 'lecturas.csv' no se encuentra.")
            return None

    def verificar_rut_e_imprimir_qrs(self):
        rut_ingresado = self.rut.get()
        if self.rut_existe(rut_ingresado):
            # Obtener ID relacionado con el RUT
            id_relacionado = self.obtener_id_relacionado(rut_ingresado)
            if id_relacionado is not None:
                # Obtener último correlativo desde lecturas.csv
                ultimo_correlativo = self.obtener_ultimo_correlativo(id_relacionado)
                ultimo_correlativo = ultimo_correlativo[3:]
                cantidad = self.cantidad_qrs.get()
                cantidad = int(cantidad) + (3 - int(cantidad)%3)%3
                cod_impresion = str(id_relacionado) + str(ultimo_correlativo).zfill(6) + str(cantidad).zfill(3)
                self.llamar_aplicacion_externa(cod_impresion)
            else:
                tk.messagebox.showwarning("Advertencia", f"El RUT {rut_ingresado} no tiene ID asociado.")
        else:
            tk.messagebox.showwarning("Advertencia", f"El RUT {rut_ingresado} no existe en los datos.")

    def obtener_id_relacionado(self, rut):
        for row in self.data:
            if row['rut'] == rut:
                return row['id']
        return None

    def llamar_aplicacion_externa(self, codigo_impresion):
        try:
            # Ruta completa al ejecutable de la aplicación externa
            ruta_ejecutable = r'ImpQR\ImpQr.exe'

            # Construir la línea de comando con el ejecutable y el parámetro
            comando = [ruta_ejecutable, codigo_impresion]

            # Llamar a la aplicación externa usando subprocess
            subprocess.run(comando, check=True)

            # Resto de tu código...
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al llamar a la aplicación externa: {str(e)}")

    def guardar_datos_en_csv(self):
        # Lógica para guardar los datos en el archivo CSV
        try:
            with open('data/cantidadQr.csv', 'a', newline='') as file:
                fieldnames = ['rut', 'cantidad', 'fecha_impresion']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Si el archivo está vacío, escribe los encabezados
                if file.tell() == 0:
                    writer.writeheader()

                # Escribe la nueva fila
                nueva_fila = {'rut': self.rut.get(), 'cantidad': self.cantidad_qrs.get(),
                              'fecha_impresion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                writer.writerow(nueva_fila)
        except Exception as e:
            tk.messagebox.showerror("Error al guardar datos en CSV: {str(e)}")



