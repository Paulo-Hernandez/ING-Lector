import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk
import pandas as pd
import os
from datetime import datetime, time


class VentanaInformes:
    def __init__(self, root, title="ING-Lectura"):
        self.root = root
        self.root.title(title)

        # Variables
        self.label_from = tk.Label(self.root, text="Desde:")
        self.label_from_date = tk.Label(self.root, text="Fecha:")
        self.entry_from_date = DateEntry(self.root, date_pattern='yyyy-mm-dd')
        self.label_from_time = tk.Label(self.root, text="Hora:")
        self.entry_from_time = ttk.Combobox(self.root, values=self.get_time_values())

        self.label_to = tk.Label(self.root, text="Hasta:")
        self.label_to_date = tk.Label(self.root, text="Fecha:")
        self.entry_to_date = DateEntry(self.root, date_pattern='yyyy-mm-dd')
        self.label_to_time = tk.Label(self.root, text="Hora:")
        self.entry_to_time = ttk.Combobox(self.root, values=self.get_time_values())

        self.btn_ok = tk.Button(self.root, text="Aceptar", command=self.ok_button)
        self.btn_cancel = tk.Button(self.root, text="Cancelar", command=self.destroy)

        # Organizar elementos en la cuadrícula
        self.label_from.grid(row=0, column=0, pady=10, sticky=tk.W)
        self.label_from_date.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.entry_from_date.grid(row=0, column=2, pady=5)
        self.label_from_time.grid(row=0, column=3, pady=5, sticky=tk.W)
        self.entry_from_time.grid(row=0, column=4, pady=5)

        self.label_to.grid(row=1, column=0, pady=10, sticky=tk.W)
        self.label_to_date.grid(row=1, column=1, pady=5, sticky=tk.W)
        self.entry_to_date.grid(row=1, column=2, pady=5)
        self.label_to_time.grid(row=1, column=3, pady=5, sticky=tk.W)
        self.entry_to_time.grid(row=1, column=4, pady=5)

        self.btn_ok.grid(row=2, column=0, columnspan=5, pady=10)
        self.btn_cancel.grid(row=3, column=0, columnspan=5, pady=5)

        self.result = None

        # Cambiar el tamaño de la ventana
        self.root.geometry("500x300")  # Ajusta el tamaño según tus necesidades

    def ok_button(self):
        # Obtener los valores de las fechas y las horas
        from_date = self.entry_from_date.get()
        from_time = self.entry_from_time.get()
        to_date = self.entry_to_date.get()
        to_time = self.entry_to_time.get()

        # Combina las fechas y las horas según sea necesario
        from_datetime_str = f"{from_date} {from_time}" if from_date and from_time else None
        to_datetime_str = f"{to_date} {to_time}" if to_date and to_time else None

        # Convertir las cadenas de fecha y hora a objetos datetime
        try:
            from_datetime = datetime.strptime(from_datetime_str, "%Y-%m-%d %H:%M") if from_datetime_str else None
            to_datetime = datetime.strptime(to_datetime_str, "%Y-%m-%d %H:%M") if to_datetime_str else None
        except ValueError as e:
            print(f"Error al parsear las fechas: {e}")
            return

        # Llamar al método informes con las fechas proporcionadas
        self.informes(from_datetime, to_datetime)

    def destroy(self):
        # Define el comportamiento cuando se hace clic en el botón Cancelar
        self.root.destroy()

    def csv_to_excel(self, df, base_name):
        # Obtener la fecha actual en el formato dd/mm/aa
        current_date = datetime.now().strftime("%d%m%y")

        # Crear el nombre del archivo Excel con el formato deseado
        excel_file_name = f"{current_date}_{base_name}.xlsx"

        # Ruta completa para guardar el archivo Excel en la carpeta 'informes'
        excel_file_path = os.path.join("informes", excel_file_name)

        # Guardar el DataFrame como archivo Excel
        df.to_excel(excel_file_path, index=False, engine='openpyxl')

        print(f"Archivo Excel de {base_name} guardado: {excel_file_path}")

    def informes(self, from_datetime, to_datetime):

        df_cantidadQr = pd.read_csv("data/cantidadQr.csv")
        df_lecturas = pd.read_csv("data/lecturas.csv")
        df_lecturas2 = pd.read_csv("data/lecturas2.csv")

        # Modificación en la lectura de fechas y horas
        df_cantidadQr['fecha_impresion'] = pd.to_datetime(df_cantidadQr['fecha_impresion'], errors='coerce')
        df_lecturas = df_lecturas.rename(columns={'ultimo Leído': 'ultimo_leido'})
        df_lecturas['Fecha'] = pd.to_datetime(df_lecturas['Fecha'], errors='coerce')
        df_lecturas2 = df_lecturas2.rename(columns={'ultimo Leído': 'ultimo_leido'})
        df_lecturas2['Fecha'] = pd.to_datetime(df_lecturas2['Fecha'], errors='coerce')

        # Filtrar los datos dentro del rango de fechas y horas
        df_cantidadQR_filtered = df_cantidadQr[
            (df_cantidadQr['fecha_impresion'] >= from_datetime) & (df_cantidadQr['fecha_impresion'] <= to_datetime)]
        df_lecturas_filtered = df_lecturas[
            (df_lecturas['Fecha'] >= from_datetime) & (df_lecturas['Fecha'] <= to_datetime)]
        df_lecturas2_filtered = df_lecturas2[
            (df_lecturas2['Fecha'] >= from_datetime) & (df_lecturas2['Fecha'] <= to_datetime)]

        # Concatenar ambos DataFrames verticalmente
        df_combined = pd.concat([df_lecturas_filtered, df_lecturas2_filtered], ignore_index=True)

        # Cambiar el nombre de la columna 'ultimo Leído'
        df_combined.rename(columns={'ultimo Leído': 'ultimo_leido'}, inplace=True)

        # Eliminar duplicados basados en la columna 'ultimo_leido'
        df_combined = df_combined[~df_combined.duplicated(subset=['ultimo_leido'])]

        #  Generar el archivo 'resumen.csv'
        self.generar_resumen_info(df_combined)

        # Guardar los informes filtrados en archivos Excel
        self.csv_to_excel(df_cantidadQR_filtered, 'cantidadQR')
        self.csv_to_excel(df_combined, 'lecturas')

    def get_time_values(self):
        # Create a list of time values for the time picker
        time_values = []
        for hour in range(24):
            for minute in range(0, 60, 15):  # 15-minute intervals
                time_values.append(f"{hour:02d}:{minute:02d}")
        return time_values

    def generar_resumen_info(self,df_combined):
        try:
            # Cargar datos del archivo datos.csv
            datos_df = pd.read_csv('data/datos.csv')

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

            # Generar un excel con el dataframe
            self.csv_to_excel(resumen_df,"Resumen")

            print("Archivo resumen.csv generado correctamente.")

        except FileNotFoundError:
            print("Archivo no encontrado. Asegúrate de tener los archivos necesarios.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaInformes(root)
    root.mainloop()

