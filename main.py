import tkinter as tk
from tkinter import messagebox
from menu import MenuApp
import queue
from config import verificacion
import sys


if verificacion() == False:
       sys.exit()


class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ING Lector")

        # Ajusta las dimensiones de la ventana de inicio de sesión
        self.root.geometry("600x400")

        # Cargar el logo
        self.logo = tk.PhotoImage(file="data/logo.png")
        self.label_logo = tk.Label(root, image=self.logo)
        self.label_logo.pack(pady=10)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.label_username = tk.Label(root, text="Usuario:")
        self.entry_username = tk.Entry(root, textvariable=self.username_var)
        self.label_password = tk.Label(root, text="Contraseña:")
        self.entry_password = tk.Entry(root, textvariable=self.password_var, show="*")
        self.btn_login = tk.Button(root, text="Iniciar Sesión", command=self.iniciar_sesion)

        self.label_username.pack()
        self.entry_username.pack()
        self.label_password.pack()
        self.entry_password.pack()
        self.btn_login.pack()

    def iniciar_sesion(self):
        # Lógica de autenticación (puedes personalizar esto según tus necesidades)
        if self.username_var.get() == "admin" and self.password_var.get() == "admin1":
            # Luego, abrir la ventana de menú
            self.abrir_ventana_menu()
        else:
            messagebox.showerror("Error de Inicio de Sesión", "Credenciales incorrectas.")

    def abrir_ventana_menu(self):
        self.label_logo.destroy()
        self.label_username.destroy()
        self.entry_username.destroy()
        self.label_password.destroy()
        self.entry_password.destroy()
        self.btn_login.destroy()

        console_queue = queue
        MenuApp(self.root,console_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()

