import queue
import tkinter as tk
import pandas as pd
from tkinter import ttk
import threading
import time
from queue import Queue
import csv
from datetime import datetime
import sys
import os
from collections import defaultdict
from config import verificacion


if verificacion() == False:
       sys.exit()


class LecturaQRWindow:
    def __init__(self, console_queue):
        self.root = tk.Tk()
        self.root.title("Lectura de QRs")
        self.console_queue = console_queue
        self.qr_contados = {}
        self.ultimo_qr_leido = {}
        self.bucle_activo = False
        self.filtro_eventos = set()

        # Diccionarios para mantener cantidades acumuladas y diarias
        self.qr_contados_acumulado = {}
        self.qr_contados_diario = {}

        # Obtener la fecha actual y formatearla
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.escribir_fecha(fecha_actual)

        # Etiqueta para mostrar la fecha
        tk.Label(self.root, text=f"Fecha de Lecturas: {fecha_actual}").pack()

        self.lectura_cont = 0

        # StringVar para almacenar el valor de lectura_cont
        self.lectura_cont_var = tk.StringVar()
        self.lectura_cont_var.set(f"Lecturas de QR: {self.lectura_cont}")

        # Label para mostrar el número de lecturas de QR
        tk.Label(self.root, textvariable=self.lectura_cont_var, foreground="white", font=("Arial", 15)).pack()

        # Crear Treeview para mostrar los resultados en forma de tabla
        self.tree = ttk.Treeview(self.root,
                                 columns=('ID Persona', 'Cantidad Acumulada', 'Cantidad Diaria', 'Último Leído'))
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('ID Persona', text='ID Persona')
        self.tree.heading('Cantidad Acumulada', text='Cantidad Acumulada')
        self.tree.heading('Cantidad Diaria', text='Cantidad Diaria')
        self.tree.heading('Último Leído', text='Último Leído')
        self.tree.column('#0', width=0, stretch=tk.NO)

        # Configurar columnas para centrar el contenido
        for col in ('ID Persona', 'Cantidad Acumulada', 'Cantidad Diaria', 'Último Leído'):
            self.tree.column(col, anchor='center')

        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Variables para actualizar la GUI
        self.cantidad_diaria = 0
        self.id_persona_var = tk.StringVar()
        self.cantidad_var = tk.StringVar()
        self.cantidad_diaria_var = tk.StringVar()
        self.ultimo_leido_var = tk.StringVar()

        # Diccionario para mantener un historial de cantidades diarias por ID de persona
        self.cantidad_diaria_historial = defaultdict(list)

        # Conjunto para mantener los últimos leídos en la ejecución actual
        self.ultimos_leidos_actuales = set()

        # Etiquetas actualizadas automáticamente
        tk.Label(self.root, textvariable=self.id_persona_var).pack()
        tk.Label(self.root, textvariable=self.cantidad_var).pack()
        tk.Label(self.root, textvariable=self.cantidad_diaria_var).pack()
        tk.Label(self.root, textvariable=self.ultimo_leido_var).pack()

        self.root.tk_setPalette(background="#656565", foreground="white", activeBackground="#656565",
                                activeForeground="white")

        # Obtén la ruta del directorio donde se encuentra el ejecutable
        self.ejecutable_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
            __file__)

        # Botón para iniciar/detener el bucle
        self.btn_iniciar_detener = tk.Button(self.root, text='Iniciar Lector 1', command=self.toggle_bucle)
        self.btn_iniciar_detener.pack()

        # Botón para iniciar/detener el bucle
        self.btn_iniciar_detener2 = tk.Button(self.root, text='Iniciar Lector 2', command=self.toggle_bucle2)
        self.btn_iniciar_detener2.pack()

        # Botón para pausar/reanudar el bucle
        self.btn_pausar_reanudar = tk.Button(self.root, text='Pausar/Reanudar', command=self.toggle_pausa)
        self.btn_pausar_reanudar.pack()

        # Botón para generar el resumen
        self.btn_reinicio_dia = tk.Button(self.root, text='Nueva jornada', command=self.reinicio_cantidad)
        self.btn_reinicio_dia.pack()

        # Cola para manejar entradas/salidas de consola
        self.console_queue = Queue()

        # Estilo de los botones
        button_style = ("Helvetica", 9)  # Fuente y tamaño
        bg_color = "#656565"  # Color de fondo
        fg_color = "white"  # Color del texto

        # Configurar y empaquetar los botones con grid
        for idx, button in enumerate([self.btn_iniciar_detener, self.btn_iniciar_detener2, self.btn_pausar_reanudar]):
            button.config(font=button_style, bg=bg_color, fg=fg_color, padx=25, pady=10, height=2, width=10)
            button.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_reinicio_dia.config(font=button_style, bg="Green", fg=fg_color, padx=10, pady=5, height=2, width=10)
        self.btn_reinicio_dia.pack(side=tk.LEFT, pady=10)

        # Iniciar hilo para la lectura continua
        self.thread_lectura = threading.Thread(target=self.iniciar_lectura_continua, daemon=True)
        self.thread_lectura.start()

        # Iniciar hilo para manejar la consola
        self.thread_console = threading.Thread(target=self.procesar_consola, daemon=True)
        self.thread_console.start()

        # Cargar datos iniciales
        # self.cargar_datos()

        # Llamar a la función actualizar_treeview cada segundo
        self.root.after(1000, self.actualizar_treeview_from_csv)

        self.root.mainloop()

    def actualizar_treeview_from_csv(self):
        try:
            # Cargar los datos del archivo resumen2.csv
            df_resumen = pd.read_csv('data/resumen2.csv')

            # Limpiar el Treeview antes de actualizarlo
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Iterar sobre los datos y actualizar el Treeview
            for index, row in df_resumen.iterrows():
                id_persona = row['id']
                cantidad_acumulada = row['Cantidad']
                cantidad_diaria = row['Cantidad Diaria']
                ultimo_leido = row['ultimo_leido']
                self.actualizar_treeview(id_persona, cantidad_acumulada, cantidad_diaria, ultimo_leido)

        except FileNotFoundError:
            print("Archivo resumen2.csv no encontrado.")

        # Programar la próxima actualización después de 1 segundo
        self.root.after(1000, self.actualizar_treeview_from_csv)
    def escribir_fecha(self, fecha):
        try:
            with open('data/fechas.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(['Fecha'])

                writer.writerow([fecha])

        except Exception as e:
            print(f"Error al guardar en CSV: {e}")

    def reinicio_cantidad(self):

        lectura = pd.read_csv('data/lecturas.csv', dtype={'ID Persona': str, 'ultimo_leido': str})
        lectura['Cantidad Diaria'] = 0

        lectura2 = pd.read_csv('data/lecturas2.csv', dtype={'ID Persona': str, 'ultimo_leido': str})
        lectura2['Cantidad Diaria'] = 0

        # Reiniciar las cantidades diarias
        self.qr_contados_diario = {}

        # Convertir 'ID Persona' y 'ultimo_leido' a cadenas para mantener el formato
        lectura['ID Persona'] = lectura['ID Persona'].astype(str)
        lectura['ultimo_leido'] = lectura['ultimo_leido'].astype(str)
        lectura2['ID Persona'] = lectura2['ID Persona'].astype(str)
        lectura2['ultimo_leido'] = lectura2['ultimo_leido'].astype(str)

        # Escribir el archivo CSV sin index
        lectura.to_csv('data/lecturas.csv', index=False)
        lectura2.to_csv('data/lecturas2.csv', index=False)

        self.cargar_datos()

    def generar_resumen(self):
        try:
            # Cargar dos archivos csv lectores 1
            lector_1_path = 'data/lecturas.csv'
            lector_1_df = pd.read_csv(lector_1_path)

            # Cargar dos archivos csv lectores 2
            lector_2_path = 'data/lecturas2.csv'
            lector_2_df = pd.read_csv(lector_2_path)

            # Concatenar los dos archivos csv
            df_concat = pd.concat([lector_1_df,lector_2_df], ignore_index=True)

            # Eliminacion de duplicados
            df_concat = df_concat[~df_concat.duplicated(subset=['ultimo_leido'])]

            self.generar_resumen_info(df_concat)




        except FileNotFoundError:
            print("Archivo no encontrado. Asegúrate de tener los archivos necesarios.")

    def generar_resumen_info(self,df_combined):
        try:
            # Cargar datos del archivo datos.csv
            datos_df = pd.read_csv('data/datos.csv', encoding='latin1')

            # Crear un DataFrame para el resumen
            resumen_df = pd.DataFrame(columns=['id', 'nombre', 'Cantidad', 'ultimo_leido'])

            # Iterar sobre cada ID en datos.csv
            for index, row in datos_df.iterrows():
                id_persona = row['id']
                nombre = row['nombre']

                # Verificar si la columna 'ID Persona' está presente en df_combined
                if 'ID Persona' in df_combined.columns:
                    # Filtrar el DataFrame combinado por ID
                    df_filtrado = df_combined[df_combined['ID Persona'] == id_persona]
                else:
                    # Si 'ID Persona' no existe, intentar buscar una columna similar
                    persona_column = [col for col in df_combined.columns if 'persona' in col.lower()]
                    if persona_column:
                        df_filtrado = df_combined[df_combined[persona_column[0]] == id_persona]
                    else:
                        print(f"No se encontró la columna para ID {id_persona}")
                        continue

                # Calcular la cantidad de filas y obtener el máximo de 'ultimo Leído'
                cantidad = len(df_filtrado)
                ultimo_leido = df_filtrado['ultimo_leido'].max()

                # Crear un DataFrame temporal con la información actual
                temp_df = pd.DataFrame(
                    {'id': [id_persona], 'nombre': [nombre], 'Cantidad': [cantidad], 'ultimo_leido': [ultimo_leido]})

                # Concatenar el DataFrame temporal a resumen_df
                resumen_df = pd.concat([resumen_df, temp_df], ignore_index=True)
                resumen_df.to_csv('data/resumen2.csv')

            print("Archivo resumen.csv generado correctamente.")

        except FileNotFoundError:
            print("Archivo no encontrado. Asegúrate de tener los archivos necesarios.")
    def obtener_rut(self, id_persona):
        # Cargar datos desde datos.csv
        try:
            with open('data/datos.csv', 'r', newline='') as datos_file:
                datos_reader = csv.DictReader(datos_file)
                for row in datos_reader:
                    if row['id'] == id_persona:
                        return row['rut']
        except FileNotFoundError:
            print("Archivo datos.csv no encontrado.")
        return None

    def obtener_faltantes(self, rut, fecha_resumen):
        # Cargar datos desde cantidadQr.csv
        faltantes = []
        try:
            with open('data/cantidadQr.csv', 'r', newline='') as cantidadQr_file:
                cantidadQr_reader = csv.DictReader(cantidadQr_file)
                for row in cantidadQr_reader:
                    if row['rut'] == rut and row['fecha_impresion'] > fecha_resumen:
                        faltantes.append(row)
        except FileNotFoundError:
            print("Archivo cantidadQr.csv no encontrado.")
        return faltantes

    def toggle_bucle(self):
        self.bucle_activo = not self.bucle_activo

        if self.bucle_activo:
            self.btn_iniciar_detener.config(text='Detener')
        else:
            self.btn_iniciar_detener.config(text='Iniciar Lector 1')

    def toggle_bucle2(self):
        self.bucle_activo = not self.bucle_activo

        if self.bucle_activo:
            self.btn_iniciar_detener2.config(text='Detener')
        else:
            self.btn_iniciar_detener2.config(text='Iniciar Lector 2')

    def toggle_pausa(self):
        self.bucle_activo = not self.bucle_activo
        if self.bucle_activo:
            self.btn_pausar_reanudar.config(text='Pausar')
        else:
            self.btn_pausar_reanudar.config(text='Reanudar')

    def iniciar_lectura_continua(self):
        while True:
            if self.bucle_activo:
                try:
                    qr = self.console_queue.get_nowait()
                    self.actualizar_resultados(qr)
                except queue.Empty:
                    pass
                time.sleep(0.1)

    def procesar_consola(self):
        while True:
            if self.bucle_activo:
                qr = input("Ingrese el código QR: ")
                self.lectura_cont = self.lectura_cont+1
                self.lectura_cont_var.set(f"Lecturas de QR: {self.lectura_cont}")
                self.console_queue.put(qr)
            time.sleep(0.1)

    def cargar_datos(self):
        try:
            with open('data/lecturas.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    id_persona = row['ID Persona'].zfill(3)

                    cantidad_acumulada = int(row['Cantidad Acumulada'])
                    cantidad_diaria = int(row['Cantidad Diaria'])
                    ultimo_leido = row['ultimo_leido']

                    # Verificar si el ID de la persona ya existe en el archivo CSV
                    if not self.id_persona_existe_en_csv(id_persona):
                        # Si no existe, establecer las cantidades iniciales correctamente
                        self.qr_contados_acumulado[id_persona] = cantidad_acumulada

                    # Utilizar diccionarios separados para acumulado y diario
                    self.qr_contados_diario[id_persona] = cantidad_diaria
                    self.ultimo_qr_leido[id_persona] = max(self.ultimo_qr_leido.get(id_persona, ''), ultimo_leido)

                    self.actualizar_treeview(id_persona, cantidad_acumulada, cantidad_diaria, ultimo_leido)

                    self.id_persona_var.set(f"ID Persona: {id_persona}")
                    self.cantidad_var.set(f"Cantidad Acumulada: {cantidad_acumulada}")
                    self.cantidad_diaria_var.set(f"Cantidad Diaria: {cantidad_diaria}")
                    self.ultimo_leido_var.set(f"Último Leído: {self.ultimo_qr_leido.get(id_persona, '')}")
        except FileNotFoundError:
            pass

    def actualizar_resultados(self, qr):
        if len(qr) != 9 or qr in self.filtro_eventos:
            return

        self.filtro_eventos.add(qr)

        if len(self.filtro_eventos) > 100:
            self.filtro_eventos.clear()

        # Formatear 'ID Persona' y 'Último Leído'
        id_persona = qr[0:3].zfill(3)
        ultimo_leido = qr.zfill(9)

        # Verificar si el último leído ya existe en el DataFrame
        if ultimo_leido in self.ultimos_leidos_actuales:
            return  # No actualizar si el último leído ya existe

        # Verificar si la clave existe en los diccionarios antes de acceder a ellas
        cantidad_acumulada = self.qr_contados_acumulado.get(id_persona, 0)
        cantidad_diaria = self.qr_contados_diario.get(id_persona, 0)
        self.contar_qr(id_persona)
        self.contar_qr_diaria(id_persona)
        self.ultimo_qr_leido[id_persona] = qr

        # Escribir en el archivo CSV solo si el último leído no existe
        if not self.ultimo_leido_existe(id_persona, ultimo_leido):
            self.escribir_en_csv(id_persona, cantidad_acumulada, cantidad_diaria, ultimo_leido)
            self.escribir_en_csv2(id_persona, cantidad_acumulada, cantidad_diaria, ultimo_leido)

        self.id_persona_var.set(f"ID Persona: {id_persona}")
        self.cantidad_var.set(f"Cantidad Acumulada: {cantidad_acumulada}")
        self.cantidad_diaria_var.set(f"Cantidad Diaria: {cantidad_diaria}")
        self.ultimo_leido_var.set(f"Último Leído: {self.ultimo_qr_leido.get(id_persona, '')}")

        self.actualizar_treeview(
            id_persona,
            cantidad_acumulada,
            cantidad_diaria,
            self.ultimo_qr_leido.get(id_persona, '')
        )

        # Agregar el último leído al conjunto de la ejecución actual
        self.ultimos_leidos_actuales.add(ultimo_leido)

    def ultimo_leido_existe(self, id_persona, ultimo_leido):
        # Verificar si el último leído ya existe en el conjunto de la ejecución actual
        if ultimo_leido in self.ultimos_leidos_actuales:
            return True

        # Verificar si el último leído ya existe en el archivo CSV
        try:
            lectura = pd.read_csv('data/lecturas.csv')
            filtro = (lectura['ID Persona'] == id_persona) & (lectura['ultimo_leido'] == ultimo_leido)
            return not lectura[filtro].empty
        except FileNotFoundError:
            return False

    def obtener_cantidad_acumulada(self, id_persona):
        # Obtener la cantidad acumulada actual para un ID de persona
        try:
            lectura = pd.read_csv('data/lecturas.csv')
            filtro = lectura['ID Persona'] == id_persona
            return lectura[filtro]['Cantidad Acumulada'].iloc[0]
        except FileNotFoundError:
            return 0

    def contar_qr(self, id_persona):
        if id_persona not in self.qr_contados_acumulado:
            self.qr_contados_acumulado[id_persona] = 1
            # Verificar si el ID de persona ya existe en el archivo CSV
            if not self.id_persona_existe_en_csv(id_persona):
                # Si no existe, contar el primer QR
                self.qr_contados_acumulado[id_persona] = 1
                self.qr_contados_acumulado[id_persona] += 1
            else:
                # Si existe, obtener la cantidad acumulada actual y sumar 1
                self.qr_contados_acumulado[id_persona] = self.obtener_cantidad_acumulada(id_persona) + 1
                self.qr_contados_acumulado[id_persona] += 1
        else:
            self.qr_contados_acumulado[id_persona] += 1

    def contar_qr_diaria(self, id_persona):
        if id_persona not in self.qr_contados_diario:
            if not self.id_persona_existe_en_csv2(id_persona):
                self.qr_contados_diario[id_persona] = 1
                self.qr_contados_diario[id_persona] += 1
        else:
            self.qr_contados_diario[id_persona] += 1

    def id_persona_existe_en_csv(self, id_persona):
        try:
            lectura = pd.read_csv('data/lecturas.csv')
            filtro = lectura['ID Persona'] == id_persona
            return not lectura[filtro].empty
        except FileNotFoundError:
            return False

    def id_persona_existe_en_csv2(self, id_persona):
        try:
            lectura = pd.read_csv('data/lecturas2.csv')
            filtro = lectura['ID Persona'] == id_persona
            return not lectura[filtro].empty
        except FileNotFoundError:
            return False

    def actualizar_treeview(self, id_persona, cantidad, cantidad_diaria, ultimo_leido):
        item_id = None
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values and values[0] == id_persona:
                item_id = item
                break

        if item_id:
            self.tree.item(item_id, values=(id_persona, cantidad, cantidad_diaria, ultimo_leido))
        else:
            self.tree.insert('', 'end', values=(id_persona, cantidad, cantidad_diaria, ultimo_leido))

    def escribir_en_csv(self, id_persona, cantidad, cantidad_diaria, ultimo_leido):
        try:
            with open('data/lecturas.csv', 'a', newline='') as file:
                writer = csv.writer(file)

                if file.tell() == 0:
                    writer.writerow(['ID Persona', 'Cantidad Acumulada', 'Cantidad Diaria', 'ultimo_leido', 'Fecha'])

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                id_persona_formatted = f"{int(id_persona):03d}"
                ultimo_leido = ultimo_leido.zfill(9)
                writer.writerow([id_persona_formatted, cantidad, cantidad_diaria, ultimo_leido, fecha_actual])
        except Exception as e:
            print(f"Error al guardar en CSV: {e}")

    def escribir_en_csv2(self, id_persona, cantidad, cantidad_diaria, ultimo_leido):
        try:
            with open('data/lecturas2.csv', 'a', newline='') as file:
                writer = csv.writer(file)

                if file.tell() == 0:
                    writer.writerow(['ID Persona', 'Cantidad Acumulada', 'Cantidad Diaria', 'ultimo_leido', 'Fecha'])

                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                id_persona_formatted = f"{int(id_persona):03d}"
                ultimo_leido = ultimo_leido.zfill(9)
                writer.writerow([id_persona_formatted, cantidad, cantidad_diaria, ultimo_leido, fecha_actual])
        except Exception as e:
            print(f"Error al guardar en CSV: {e}")


if __name__ == "__main__":
    console_queue = Queue()
    lectura_qr_window = LecturaQRWindow(console_queue)