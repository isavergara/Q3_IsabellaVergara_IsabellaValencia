from clases import Imagen, ProcesadorDICOM
import os
import pydicom
import nibabel as nib
from PIL import Image
import numpy as np
import dicom2nifti
from nilearn import plotting
import shutil
import cv2
import matplotlib.pyplot as plt

def main():

    pacientes = {}
    archivos_procesados = {}
    procesadorDicom = ProcesadorDICOM()
    while True:
        print("\nMENU PRINCIPAL:")
        print("1. Ingresar paciente (DICOM)")
        print("2. Ingresar imágenes (JPG/PNG)")
        print("3. Realizar transformación geométrica de rotación (DICOM)")
        print("4. Realizar binarización y transformación morfológica (JPG/PNG)")
        print("5. Imprimir Diccionarios")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            carpetas = input("Ingrese los nombres de las carpetas separadas por comas: ")
            carpetas = carpetas.split(',')
            procesadorDicom.cargar_carpetas_dicom(carpetas,pacientes,archivos_procesados)
        
            for clave, paciente in pacientes.items():
                print(clave, ":", "nombre: ", paciente.nombre, "edad: ", paciente.edad, 
                    "id: ", paciente.ID, "imagen_asociada: ", paciente.imagen_asociada)
        elif opcion == "2":
            ruta_imagen = input("Ingrese la ruta de la imagen: ")
            clave = input("Ingrese una clave para la imagen: ")
            imagen = Imagen(ruta_imagen)
            archivos_procesados[clave] = imagen

        elif opcion == "3":
            valor = input("Ingrese la clave del archivo DICOM para rotar: ")
            file_path = archivos_procesados[valor]
            rotation_angle = int(input("Ingrese el ángulo de rotación (90, 180 o 270): "))

            original_image = pydicom.dcmread(file_path, force=True).pixel_array.copy()

            rotated_image = procesadorDicom.rotate_dicom_image(file_path, rotation_angle)

            plt.subplot(1, 2, 1)
            plt.imshow(original_image, cmap='gray')
            plt.title('Imagen Original')
            plt.axis('off')

            plt.subplot(1, 2, 2)
            plt.imshow(rotated_image, cmap='gray')
            plt.title(f'Imagen Rotada {rotation_angle} grados')
            plt.axis('off')

            plt.show()
        elif opcion == "4":
            clave = input("Ingrese la clave del archivo de imagen para binarizar y transformar: ")
            imagen = archivos_procesados[clave]
            umbral = int(input("Ingrese el umbral de binarización: "))
            tamaño_kernel = int(input("Ingrese el tamaño del kernel para la transformación morfológica: "))
            imagen_transformada = imagen.binarizacion_y_transformacion(umbral, tamaño_kernel)
            cv2.imshow("Imagen transformada", imagen_transformada)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        elif opcion == "5":
            procesadorDicom.imprimir_diccionarios(pacientes,archivos_procesados)
        elif opcion == "6":
            break
        else:
            print("Opción no válida. Por favor, ingrese una opción válida.")


if __name__ == "__main__":
    main()
