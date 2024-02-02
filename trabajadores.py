import tkinter as tk
from tkinter import ttk
from itertools import cycle
import csv


def digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    return (-s) % 11


class CRUDApp:
    def __init__(self, root, title="ING-Lectura"):
        self.root = root
        self.root.title(title)

        # Variables
        self.id_var = tk.StringVar()
        self.rut_var = tk.StringVar()
        self.digito_var = tk.StringVar()
        self.nombre_var = tk.StringVar()

        # Crear Treeview
        self.tree = ttk.Treeview(root, columns=('ID', 'RUT', 'Digito', 'Nombre'), show='headings', height=26)
        self.tree.heading('ID', text='ID')
        self.tree.heading('RUT', text='RUT')
        self.tree.heading('Digito', text='Dígito')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.winfo_geometry()

        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)


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

        # Estilo de los botones
        button_style = ("Helvetica", 12)  # Fuente y tamaño
        bg_color = "#656565"  # Color de fondo
        fg_color = "white"  # Color del texto

        # Configurar y empaquetar los botones
        for button in [self.btn_crear, self.btn_eliminar]:
            button.config(font=button_style, bg=bg_color, fg=fg_color, padx=20, pady=10, height=1, width=10)
            button.pack(pady=10)

        self.btn_eliminar.config(font=button_style, bg="#FF0000", fg="black", padx=20, pady=10, height=1, width=10)

        # Cargar datos desde el archivo CSV
        self.cargar_datos()

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
        # Actualizar las variables con los valores ingresados en el formulario
        rut = self.rut_var.get()
        digito = self.digito_var.get()
        nombre = self.nombre_var.get()


        try:
            # Verificar que todos los campos estén completos
            if not nombre:
                print("Por favor, complete todos los campos.")
                return

            if not rut or not digito:
                rut = '0'
                digito = '0'
            # Intenta convertir rut a entero
            rut_entero = int(rut)

            # Si el dígito es "K", guárdalo como "K", de lo contrario, conviértelo a entero
            if digito == "K":
                digito_entero = "K"
            else:
                digito_entero = int(digito)

            if rut_entero >= 0 and digito_entero >= 0:
                if digito_verificador(rut_entero) == digito_entero:
                    # Obtener el próximo ID con formato de tres dígitos
                    nuevo_id = f"{len(self.tree.get_children()) + 1:03d}"
                    print(f"Nuevo ID: {nuevo_id}")
                    if rut_entero == 0:
                        rut = ''
                        digito = ''
                    self.tree.insert('', 'end', values=(nuevo_id, rut, digito, nombre))
                    self.guardar_datos()
                else:
                    print("El dígito verificador no coincide")
            else:
                print("Los valores de RUT y Dígito deben ser números enteros no negativos.")
        except ValueError as e:
            print(f"Error al convertir RUT o Dígito a número entero: {e}")

    def eliminar_registro(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.guardar_datos()


if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()