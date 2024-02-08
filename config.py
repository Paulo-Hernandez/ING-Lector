import tkinter as tk
from win32print import GetDefaultPrinter
import uuid
import pandas as pd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib



def obtener_direccion_mac():
    try:
        direccion_mac = '-'.join(['{:02X}'.format(int(x, 16)) for x in ('{:012X}'.format(uuid.getnode())[i:i+2] for i in range(0, 12, 2))])
        return direccion_mac
    except Exception as e:
        print("Error al obtener la dirección MAC:", str(e))
        return None


def decrypt_string(ciphertext, key):
    # Decodificar el texto cifrado desde base64
    ciphertext = base64.b64decode(ciphertext)

    # Crear un objeto AES cipher
    key_hash = hashlib.md5(key.encode('utf-8')).digest()
    cipher = Cipher(algorithms.AES(key_hash), modes.ECB(), backend=default_backend())

    # Crear un objeto para descifrar
    decryptor = cipher.decryptor()

    # Descifrar el texto
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Despadding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # Decodificar a cadena de texto
    decrypted_text = unpadded_data.decode('utf-8')

    return decrypted_text


def verificacion():
    # Clave proporcionada
    clave = "IngMetrica8897"

    # Texto cifrado
    df = pd.read_csv("data\llaves.csv")
    nombrecol = 'KEY'
    texto_cifrado_lista = df[nombrecol].tolist()
    # Dirección MAC
    dire = obtener_direccion_mac()
    # Iterar a través de la lista y descifrar cada cadena
    for texto_cifrado in texto_cifrado_lista:
        # Descifrar el texto
        texto_descifrado = decrypt_string(texto_cifrado, clave)


        if dire in texto_descifrado:
            return True

    return False


class PrinterInfoWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Información de la Impresora")

        # Obtener la impresora predeterminada
        default_printer = GetDefaultPrinter()

        # Etiqueta para mostrar la impresora predeterminada
        self.label_printer_info = tk.Label(root, text=f"Impresora Predeterminada: {default_printer}")
        self.label_printer_info.pack(pady=20)

        # Botón para cerrar la ventana
        self.btn_close = tk.Button(root, text="Cerrar", command=self.close_window)
        self.btn_close.pack(pady=10)

    def close_window(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PrinterInfoWindow(root)
    root.mainloop()
