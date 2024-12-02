import cv2
import numpy as np
import os
from multiprocessing import Pool, cpu_count
import time

# Directorios
INPUT_DIR = "images/"
OUTPUT_DIR = "output/"

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filtros a aplicar
def apply_filters(image_path):
    try:
        # Leer la imagen
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error al cargar la imagen: {image_path}")
            return

        # Escalado a niveles de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Suavizado con filtro Gaussiano
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detección de bordes con Sobel
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        edges = cv2.magnitude(sobelx, sobely)

        # Normalizar bordes para visualización
        edges = cv2.convertScaleAbs(edges)

        # Guardar resultados
        base_name = os.path.basename(image_path)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"gray_{base_name}"), gray)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"blurred_{base_name}"), blurred)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"edges_{base_name}"), edges)
        print(f"Procesada: {base_name}")

    except Exception as e:
        print(f"Error procesando {image_path}: {e}")

# Función principal
def main():
    # Obtener todas las imágenes en el directorio de entrada
    image_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.png', '.bmp', '.tiff'))]

    if not image_files:
        print("No se encontraron imágenes en el directorio de entrada.")
        return

    print(f"Imágenes encontradas: {len(image_files)}")

    # Procesamiento secuencial
    start_seq = time.time()
    for img in image_files:
        apply_filters(img)
    end_seq = time.time()

    print(f"Tiempo secuencial: {end_seq - start_seq:.2f} segundos")

    # Procesamiento en paralelo
    start_par = time.time()
    with Pool(cpu_count()) as pool:
        pool.map(apply_filters, image_files)
    end_par = time.time()

    print(f"Tiempo paralelo: {end_par - start_par:.2f} segundos")

    # Speedup
    speedup = (end_seq - start_seq) / (end_par - start_par)
    print(f"Speedup logrado: {speedup:.2f}")

if __name__ == "__main__":
    main()
