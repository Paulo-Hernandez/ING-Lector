import tkinter as tk
import tkinter.messagebox
import csv
import subprocess
from datetime import datetime


class ImpresionQRWindow:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.top = tk.Toplevel(root)
        self.top.title("Impresión de QRs")
        self.top.geometry("400x300")

        # Variables para almacenar la cantidad de QRs y el RUT
        self.cantidad_qrs = tk.IntVar()
        self.id_persona = tk.StringVar()

        # Etiqueta y cuadro de entrada para la cantidad de QRs
        tk.Label(self.top, text="Cantidad de QRs a imprimir:").pack()
        entry_cantidad = tk.Entry(self.top, textvariable=self.cantidad_qrs)
        entry_cantidad.pack()

        # Etiqueta y cuadro de entrada para el ID de la persona
        tk.Label(self.top, text="ID de la persona:").pack()
        entry_id_persona = tk.Entry(self.top, textvariable=self.id_persona)
        entry_id_persona.pack()

        # Botón para iniciar la impresión
        btn_imprimir = tk.Button(self.top, text="Imprimir QRs", command=self.verificar_rut_e_imprimir_qrs)
        btn_imprimir.pack()

    def id_persona_existe(self, id_persona):
        # Verifica si el ID de la persona existe en los datos
        return any(row['id'] == id_persona for row in self.data)

    def obtener_ultimo_correlativo(self, id_persona):
        try:
            with open('data\lecturas.csv', 'r', newline='') as lecturas_file:
                reader = csv.DictReader(lecturas_file)
                # Filtra las filas según el ID de la persona
                filas_filtradas = [row for row in reader if row['ID Persona'] == id_persona]
                # Verifica si hay filas después del filtrado
                if filas_filtradas:
                    # Encuentra el máximo en la columna 'ultimo Leido' de las filas filtradas
                    max_correlativo = max(row['ultimo_leido']for row in filas_filtradas).zfill(9)
                    max_correlativo = int(max_correlativo) + 1
                    max_correlativo = str(max_correlativo).zfill(9)
                    max_correlativo.zfill(9)
                    return max_correlativo
                else:
                    tk.messagebox.showwarning("Advertencia",
                                              f"No hay filas para el ID de persona {id_persona}. "
                                              f"Se empezará por el 000001")
                    return "000001"

        except FileNotFoundError:
            tk.messagebox.showerror("Error", "El archivo 'lecturas.csv' no se encuentra.")
            return None

    def verificar_rut_e_imprimir_qrs(self):
        id_persona_ingresado = self.id_persona.get()
        if self.id_persona_existe(id_persona_ingresado):
                # Obtener último correlativo desde lecturas.csv
                ultimo_correlativo = self.obtener_ultimo_correlativo(id_persona_ingresado)
                ultimo_correlativo = ultimo_correlativo[3:]
                cantidad = self.cantidad_qrs.get()
                cantidad = int(cantidad) + (3 - int(cantidad)%3)%3
                cod_impresion = str(id_persona_ingresado) + str(ultimo_correlativo).zfill(6) + str(cantidad).zfill(3)
                self.guardar_datos_en_csv()
                self.llamar_aplicacion_externa(cod_impresion)
        else:
            tk.messagebox.showwarning("Advertencia", f"El ID {id_persona_ingresado} no existe en los datos.")

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
                fieldnames = ['id', 'cantidad', 'fecha_impresion']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Si el archivo está vacío, escribe los encabezados
                if file.tell() == 0:
                    writer.writeheader()

                # Escribe la nueva fila
                nueva_fila = {'id': self.id_persona.get(), 'cantidad': self.cantidad_qrs.get(),
                              'fecha_impresion': datetime.now().strftime("%Y-%m-%d %H:%M")}
                writer.writerow(nueva_fila)
        except Exception as e:
            tk.messagebox.showerror("Error al guardar datos en CSV: {str(e)}")


