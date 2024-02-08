import tkinter as tk
from tkinter import ttk
import csv


class CRUDApp:
    def __init__(self, root, title="ING-Lectura"):
        self.root = root
        self.root.title(title)

        # Variables
        self.id_var = tk.StringVar()
        self.nombre_var = tk.StringVar()

        # Crear Treeview
        self.tree = ttk.Treeview(root, columns=('ID', 'Nombre'), show='headings', height=26)
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')

        self.tree.bind('<Double-1>', self.editar_registro)

        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Configurar el ancho y alineación de las columnas
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Nombre', width=150, anchor='center')

        self.tree.pack()

        # Formulario de entrada
        self.nombre_label = tk.Label(root, text='Nombre:')
        self.nombre_entry = tk.Entry(root, textvariable=self.nombre_var)

        self.nombre_label.pack()
        self.nombre_entry.pack()

        # Botones
        self.btn_crear = tk.Button(root, text='Crear', command=self.crear_registro)
        self.btn_eliminar = tk.Button(root, text='Eliminar', command=self.eliminar_registro)

        self.btn_crear.pack()
        self.btn_eliminar.pack()

        # Cargar datos desde el archivo CSV
        self.cargar_datos()

    def cargar_datos(self):
        try:
            with open('data/datos.csv', 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.tree.insert('', 'end', values=(row['id'], row['nombre']))
        except FileNotFoundError:
            # Si el archivo no existe, simplemente continúa sin cargar datos
            pass

    def guardar_datos(self):
        with open('data/datos.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'nombre'])
            for child in self.tree.get_children():
                values = self.tree.item(child, 'values')
                writer.writerow(values)

    def crear_registro(self):
        # Actualizar las variables con los valores ingresados en el formulario
        nombre = self.nombre_var.get()

        try:
            # Verificar que todos los campos estén completos
            if not nombre:
                print("Por favor, complete todos los campos.")
                return
            else:
                nuevo_id = f"{len(self.tree.get_children()) + 1:03d}"
                self.tree.insert('', 'end', values=(nuevo_id, nombre))
                self.guardar_datos()
        except ValueError as e:
            print(f"Error al convertir RUT o Dígito a número entero: {e}")

    def eliminar_registro(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.guardar_datos()

    def editar_registro(self, event):
        item = self.tree.selection()[0]
        nombre_anterior = self.tree.item(item, 'values')[1]
        nuevo_nombre = self.nombre_var.get()
        self.tree.item(item, values=(self.tree.item(item, 'values')[0], nuevo_nombre))
        self.guardar_datos()


if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()
