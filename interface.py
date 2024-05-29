import cv2
import numpy as np
import colorsys
from PIL import Image
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

img = 0

def process_and_display_images(input_path):
    try:
        # Открываем изображение
        original_image = Image.open(input_path)

        # Создаем копию изображения для обработки
        processed_image = original_image.copy()

        # Получаем данные
        original_pixels = original_image.load()
        processed_pixels = processed_image.load()

        # Проходимся по каждому пикселю в обработанном изображении
        for i in range(processed_image.width):
            for j in range(processed_image.height):
                # Получаем значения цветовых каналов из оригинального изображения
                r, g, b = original_pixels[i, j]

                # Конвертация RGB в HSV
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                h = h * 360
                s *= 100

                if 0 <= h <= 30 or 345 <= h <= 360:  # red
                    processed_pixels[i, j] = (255, 0, 0)
                elif 90 <= h <= 150:  # green
                    processed_pixels[i, j] = (0, 255, 0)
                elif 207 <= h <= 270:  # blue
                    processed_pixels[i, j] = (0, 0, 255)
                elif 36 <= h <= 90:  # yellow
                    processed_pixels[i, j] = (255, 255, 0)
                elif 170 <= h < 207:  # cyan
                    processed_pixels[i, j] = (0, 255, 255)
                elif 260 <= h <= 345:  # pink
                    processed_pixels[i, j] = (255, 0, 255)

                if s < 15 and v > 50:
                    processed_pixels[i, j] = (255, 255, 255)

                if (s < 15 and v < 50) or v < 15:
                    processed_pixels[i, j] = (0, 0, 0)

        # Сохраняем обработанное изображение
        processed_image_path = "processed_image.jpg"
        processed_image.save(processed_image_path)

        # Находим контуры бирюзового цвета на обработанном изображении
        processed_cv_image = cv2.imread(processed_image_path)
        processed_cv_image = cv2.cvtColor(processed_cv_image, cv2.COLOR_BGR2RGB)
        hsv_image = cv2.cvtColor(processed_cv_image, cv2.COLOR_RGB2HSV)

        lower_blue = np.array([85, 100, 100])
        upper_blue = np.array([130, 255, 255])

        mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Выбираем самый большой контур
        biggest_contour = max(contours, key=cv2.contourArea)

        # Получаем ограничивающий прямоугольник для самого большого контура
        x, y, w, h = cv2.boundingRect(biggest_contour)

        # Обрезаем изображение по контуру
        cropped_image = processed_image.crop((x, y, x + w, y + h))

        # Сохраняем обрезанное изображение
        cropped_image_path = "cropped_image.jpg"
        cropped_image.save(cropped_image_path)

        # Отображаем изображения на экране
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Оригинальное изображение
        select_file_and_process_second(cropped_image)
        axes[0].imshow(original_image)
        axes[0].set_title('Original Image')

        # Обработанное изображение
        axes[1].imshow(processed_image)
        axes[1].set_title('Processed Image')

        # Обрезанное изображение по контуру
        axes[2].imshow(cropped_image)
        axes[2].set_title('Cropped Image')

        plt.show()

        # Сохраняем результат на компьютер
        save_processed_image(processed_image_path, cropped_image_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_file_and_process():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_and_display_images(file_path)

def process_and_display_images_second(image):
    # Код обработки и отображения изображения
    pass

def select_file_and_process_second(imga):
    # Код обработки и отображения изображения
    pass

def save_processed_image(processed_image_path, cropped_image_path):
    # Копирование файлов и сохранение на компьютер
    import shutil
    shutil.copyfile(processed_image_path, "new1233_processed_image.jpg")
    shutil.copyfile(cropped_image_path, "new1233_cropped_image.jpg")

# Создаем главное окно
root = tk.Tk()
root.title("Image Processor")

# Создаем кнопку для выбора файла и запуска обработки
btn = tk.Button(root, text="Select Image and Process", command=select_file_and_process)
btn.pack(pady=20)

# Запускаем главный цикл обработки событий
root.mainloop()
