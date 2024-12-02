import cv2
import cupy as cp
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
import time

# Directorios
INPUT_DIR = "images/"
OUTPUT_DIR = "output/"

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filtros a aplicar usando GPU
def apply_filters_gpu(image_path):
    try:
        # Leer la imagen
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error al cargar la imagen: {image_path}")
            return

        # Convertir imagen a GPU (CuPy)
        gpu_image = cp.asarray(image)

        # Escalado a niveles de gris
        gray = cp.dot(gpu_image[..., :3], cp.array([0.299, 0.587, 0.114])).astype(cp.uint8)

        # Suavizado con filtro Gaussiano usando OpenCV (en CPU)
        blurred = cv2.GaussianBlur(cp.asnumpy(gray), (5, 5), 0)

        # Convertir la imagen suavizada de vuelta a GPU
        blurred_gpu = cp.asarray(blurred)

        # Detección de bordes con Sobel usando OpenCV (en CPU)
        sobelx = cv2.Sobel(cp.asnumpy(blurred_gpu), cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(cp.asnumpy(blurred_gpu), cv2.CV_64F, 0, 1, ksize=3)

        # Calculamos los bordes
        edges = cp.sqrt(cp.asarray(sobelx) ** 2 + cp.asarray(sobely) ** 2).astype(cp.uint8)

        # Guardar resultados
        base_name = os.path.basename(image_path)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"gray_{base_name}"), cp.asnumpy(gray))
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"blurred_{base_name}"), cp.asnumpy(blurred_gpu))
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"edges_{base_name}"), cp.asnumpy(edges))
        print(f"Procesada en GPU: {base_name}")

    except Exception as e:
        print(f"Error procesando {image_path} en GPU: {e}")

# Función para procesamiento secuencial
def process_sequential(image_files):
    for image_path in image_files:
        apply_filters_gpu(image_path)

# Función principal
def main():
    # Obtener todas las imágenes en el directorio de entrada
    image_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.png', '.bmp', '.tiff'))]

    if not image_files:
        print("No se encontraron imágenes en el directorio de entrada.")
        return

    print(f"Imágenes encontradas: {len(image_files)}")

    # 1. Procesamiento secuencial
    start_seq = time.time()
    process_sequential(image_files)
    end_seq = time.time()
    sequential_time = end_seq - start_seq
    print(f"Tiempo de procesamiento secuencial: {sequential_time:.2f} segundos")

    # 2. Procesamiento paralelo
    start_par = time.time()
    with ThreadPoolExecutor() as executor:
        executor.map(apply_filters_gpu, image_files)
    end_par = time.time()
    parallel_time = end_par - start_par
    print(f"Tiempo de procesamiento paralelo: {parallel_time:.2f} segundos")

    # 3. Calcular speedup
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"Speedup: {speedup:.2f}")
    else:
        print("Error: Tiempo paralelo no puede ser 0.")

if __name__ == "__main__":
    main()
