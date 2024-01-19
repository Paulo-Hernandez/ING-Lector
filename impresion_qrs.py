import tkinter as tk
import tkinter.messagebox
import csv
from datetime import datetime
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

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

    def verificar_rut_e_imprimir_qrs(self):
        rut_ingresado = self.rut.get()
        if self.rut_existe(rut_ingresado):
            self.imprimir_qrs()
        else:
            tk.messagebox.showwarning("Advertencia", f"El RUT {rut_ingresado} no existe en los datos.")

    def rut_existe(self, rut):
        # Verifica si el RUT existe en los datos
        return any(row['rut'] == rut for row in self.data)

    def imprimir_qrs(self):
        try:
            cantidad = self.cantidad_qrs.get()
            if cantidad > 0:
                # Obtener la fecha y hora actual
                fecha_impresion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Obtener el ID en formato 000
                id_formato = self.obtener_id_formato()

                # Generar y guardar los QRs
                qr_data_list = []
                for i in range(1, cantidad + 1):
                    qr_data = f"{id_formato}{i:06d}"  # Formato: ID + 6 dígitos para la cantidad
                    qr_data_list.append(qr_data)
                    self.guardar_qr(qr_data)

                    # Agregar una nueva página en el PDF si es necesario
                    if i % 3 == 0 or i == cantidad:
                        self.generar_pdf(qr_data_list, 3)
                        if i < cantidad:
                            qr_data_list = [qr_data]

                # Generar el PDF para los QR restantes
                if qr_data_list:
                    self.generar_pdf(qr_data_list, 3)

                # Ejemplo de cómo podrías hacerlo:
                nueva_fila = {'rut': self.rut.get(), 'cantidad': cantidad, 'fecha_impresion': fecha_impresion}
                self.data.append(nueva_fila)
                self.guardar_datos_en_csv()

                tk.messagebox.showinfo("Éxito", f"{cantidad} QRs generados e impresos.")
                self.top.destroy()
            else:
                tk.messagebox.showwarning("Advertencia", "La cantidad de QRs debe ser mayor a 0.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al imprimir QRs: {str(e)}")

    def generar_pdf(self, qr_data_list):
        try:
            pdf_filename = f"qrs_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)

            # Ajusta el tamaño del QR
            x_margin = 0.75 * inch
            y_margin = 0.75 * inch
            qr_size = 0.5 * inch

            for i, qr_data in enumerate(qr_data_list):
                col = i % 3
                row = i // 3

                # Ajusta el tamaño de la página según la cantidad de QRs
                if col == 0 and i > 0:
                    c.setPageSize((c._pagesize[0], (row + 1) * (qr_size + 0.5 * inch) + y_margin))

                x = x_margin + col * (qr_size + 0.5 * inch)
                y = y_margin + row * (qr_size + 0.5 * inch)

                c.drawInlineImage(f"qr_{qr_data}.png", x, y, width=qr_size, height=qr_size)

            c.save()

            tk.messagebox.showinfo("Éxito", f"PDF generado: {pdf_filename}")
            self.top.destroy()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

    def obtener_id_formato(self):
        # Obtener el ID en formato 000
        id_actual = len(self.data)
        return f"{id_actual:03d}"

    def guardar_qr(self, qr_data):
        # Guardar el QR en un archivo de imagen
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"qr_{qr_data}.png")

    def guardar_datos_en_csv(self):
        # Lógica para guardar los datos en el archivo CSV
        try:
            with open('cantidadQr.csv', 'a', newline='') as file:
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
            tk.messagebox.showerror("Error", f"Error al guardar datos en CSV: {str(e)}")
