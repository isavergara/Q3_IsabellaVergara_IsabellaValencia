import os
import pydicom
import dicom2nifti
import shutil
import cv2
import numpy as np
import matplotlib.pyplot as plt

class Paciente:
    def __init__(self, nombre, edad, ID, imagen_asociada):
        self.nombre = nombre
        self.edad = edad
        self.ID = ID
        self.imagen_asociada = imagen_asociada

class Imagen:
    def __init__(self, ruta):
        self.ruta = ruta
        self.imagen = self.cargar_imagen()

    def cargar_imagen(self):
        img = cv2.imread(self.ruta)
        if img is None:
            print("Error al cargar la imagen.")
        return img

    def binarizacion_y_transformacion(self, umbral, tamaño_kernel):
        gray = cv2.cvtColor(self.imagen, cv2.COLOR_BGR2GRAY)
        ret, binarizada = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (tamaño_kernel, tamaño_kernel))
        transformada = cv2.morphologyEx(binarizada, cv2.MORPH_OPEN, kernel)

        texto = f"Imagen binarizada, umbral: {umbral}, tamaño del kernel: {tamaño_kernel}"
        cv2.putText(transformada, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        self.guardar_imagen(self.ruta + "-T.jpg", transformada)

        return transformada

    def guardar_imagen(self, ruta, imagen):
        cv2.imwrite(ruta, imagen)
        print("Imagen guardada correctamente.")

class ProcesadorDICOM:

    def cargar_carpetas_dicom(self, carpetas, pacientes,archivos_procesados):
        for carpeta in carpetas:
            if os.path.exists(carpeta) and os.path.isdir(carpeta):
                for archivo in os.listdir(carpeta):
                    archivo_path = os.path.join(carpeta, archivo)
                    paciente = self.leer_datos_paciente(archivo_path, carpeta)
                    if paciente:
                        pacientes[paciente.nombre] = paciente
                        break
                for indice, archivo in enumerate(os.listdir(carpeta)):
                    archivo_path = os.path.join(carpeta, archivo)
                    valor = str(indice) + "-DICOM"
                    archivos_procesados[valor] = archivo_path
            else:
                print(f"La carpeta {carpeta} no existe.")
        return pacientes, archivos_procesados

    def leer_datos_paciente(self, ruta, ruta_carpeta):
        data = ""
        if ruta.endswith('.dcm'):
            data = pydicom.dcmread(ruta)
        
        nombre = data.PatientName
        edad = data.PatientAge
        paciente_id = data.PatientID

        self.crear_nifti(ruta_carpeta)

        nombre_archivo = self.obtener_nombre_archivo_en_carpeta(ruta_carpeta + "nifti")

        imagen_asociada = ruta_carpeta + "nifti" + "\\" + nombre_archivo 

        if data == "":
            return None

        return Paciente(nombre, edad, paciente_id, imagen_asociada)

    def obtener_nombre_archivo_en_carpeta(self, ruta_carpeta):
        archivos_en_carpeta = os.listdir(ruta_carpeta)
        if not archivos_en_carpeta:
            print("La carpeta está vacía.")
            return None

        nombre_archivo = archivos_en_carpeta[0]

        return nombre_archivo


    def crear_nifti(self, dicom_directory):
        ruta_nueva_carpeta = dicom_directory + "nifti"
        if os.path.exists(ruta_nueva_carpeta):
            shutil.rmtree(ruta_nueva_carpeta)
        os.mkdir(ruta_nueva_carpeta)
        dicom2nifti.convert_directory(dicom_directory,ruta_nueva_carpeta) 


    def rotate_dicom_image(self, file_path, rotation_angle):
        dicom_data = pydicom.dcmread(file_path, force=True)
        image = dicom_data.pixel_array
        row, col = np.shape(image)

        # Matriz de rotación y tamaño
        MR = cv2.getRotationMatrix2D((col/2,row/2), rotation_angle, 1)
        row, col = np.shape(image)

        # Rotación
        rot = cv2.warpAffine(image, MR, (col,row))

        return rot

    def imprimir_diccionarios(self,pacientes,archivos_procesados):
        print("------------************---------------****************")
        print("DICCIONARIO PACIENTES:")
        for clave, paciente in pacientes.items():
            print(clave, ":", "nombre: ", paciente.nombre, "edad: ", paciente.edad, 
                  "id: ", paciente.ID, "imagen_asociada: ", paciente.imagen_asociada)
        print("------------************---------------****************")
        print("DICCIONARIO ARCHIVOS PROCESADOS:")
        print(archivos_procesados)