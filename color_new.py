import cv2
import numpy as np
import colorsys
from PIL import Image
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
EDGE_THRESHOLD = 0.1
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

        # Уточненные пороговые значения для бирюзового цвета
        lower_turquoise = np.array([70, 80, 80])
        upper_turquoise = np.array([110, 255, 255])  # оттенок для бирюзового по границам увеличен

        mask = cv2.inRange(hsv_image, lower_turquoise, upper_turquoise)

        # Морфологические операции для улучшения маски
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Вычисляем центр изображения
        center_x, center_y = processed_image.width // 2, processed_image.height // 2
        edge_x_threshold = processed_image.width * EDGE_THRESHOLD
        edge_y_threshold = processed_image.height * EDGE_THRESHOLD

        # Выбираем контур, наиболее подходящий по размеру и форме
        biggest_contour = None
        max_area = 0
        min_distance = float('inf')
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h

            # Рассчитываем расстояние от центра изображения
            contour_center_x = x + w // 2
            contour_center_y = y + h // 2
            distance_to_center = ((contour_center_x - center_x) ** 2 + (contour_center_y - center_y) ** 2) ** 0.5

            # Проверяем, находится ли контур достаточно далеко от краёв изображения
            if x > edge_x_threshold and (x + w) < (processed_image.width - edge_x_threshold) and \
               y > edge_y_threshold and (y + h) < (processed_image.height - edge_y_threshold):
                # Выбираем контур с максимальной площадью и ближайший к центру изображения
                if area > max_area and 0.8 <= aspect_ratio <= 1.2 and (biggest_contour is None or distance_to_center < min_distance):
                    max_area = area
                    min_distance = distance_to_center
                    biggest_contour = contour

        if biggest_contour is not None:
            # Получаем ограничивающий прямоугольник для самого большого контура
            x, y, w, h = cv2.boundingRect(biggest_contour)

            # Обрезаем изображение по контуру
            cropped_image = processed_image.crop((x, y, x + w, y + h))

            # Сохраняем обрезанное изображение
            cropped_image_path = "cropped_image.jpg"
            cropped_image.save(cropped_image_path)

            # Вторая часть программы
            analyze_contours(cropped_image_path)

            # Отображаем изображения на экране
            fig, axes = plt.subplots(2, 2, figsize=(10, 10))

            # Оригинальное изображение
            axes[0, 0].imshow(original_image)
            axes[0, 0].set_title('Original Image')

            # Обработанное изображение
            axes[0, 1].imshow(processed_image)
            axes[0, 1].set_title('Processed Image')

            # Обрезанное изображение по контуру
            axes[1, 0].imshow(cropped_image)
            axes[1, 0].set_title('Cropped Image')

            # Четвертое изображение (с контуром)
            final_image = Image.open("final_image_with_contours.jpg")
            axes[1, 1].imshow(final_image)
            axes[1, 1].set_title('Final Image with Contours')

            plt.show()

            # Сохраняем результат на компьютер
            save_processed_image(processed_image_path, cropped_image_path)

            # Отображаем обработанное изображение в окне Tkinter
            display_image_on_label(cropped_image_path)
        else:
            messagebox.showerror("Error", "Бирюзовая рамка не найдена.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def display_image_on_label(image_path):
    img = Image.open(image_path)
    img = ImageTk.PhotoImage(img)
    image_label.config(image=img)
    image_label.image = img  # Сохраняем ссылку на изображение, чтобы избежать сборки мусора

def analyze_contours(image_path):
    # Загрузка изображения
    image = cv2.imread(image_path)
    image_with_contours = image.copy()

    # Определение цветов
    colors = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255),
        "pink": (255, 0, 255)
    }

    # Пороговые значения для каждого цвета
    thresholds = {
        "red": ((0, 0, 150), (100, 100, 255)),
        "green": ((0, 150, 0), (100, 255, 100)),
        "blue": ((150, 0, 0), (255, 100, 100)),
        "yellow": ((0, 150, 150), (100, 255, 255)),
        "pink": ((150, 0, 150), (255, 100, 255))
    }

    # Найдем контуры для каждого цвета
    contours_dict = {}
    contours_centers = {}
    for color_name, color in colors.items():
        lower, upper = thresholds[color_name]
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # Применяем пороговое значение
        mask = cv2.inRange(image, lower, upper)

        # Находим контуры
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:  # Проверяем, что найдены контуры
            # Выбираем максимальный контур по площади
            max_contour = max(contours, key=cv2.contourArea)
            contours_dict[color_name] = max_contour

            # Вычисляем центр контура для сортировки
            M = cv2.moments(max_contour)
            cx = int(M["m10"] / (M["m00"] + 1e-5))  # Избегаем деление на ноль
            cy = int(M["m01"] / (M["m00"] + 1e-5))  # Избегаем деление на ноль
            contours_centers[color_name] = cy

            # Подписываем цвет контура
            text_color = (255 - color[0], 255 - color[1], 255 - color[2])  # негатив цвета
            cv2.putText(image_with_contours, color_name, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    # Сортируем цвета по вертикальной координате центра контура
    sorted_colors = sorted(contours_centers, key=contours_centers.get)

    # Выводим порядок цветов сверху вниз
    print("Порядок цветов сверху вниз:")
    for color in sorted_colors:
        print(color)

    # Сохраняем изображение с контурами
    final_image_path = "final_image_with_contours.jpg"
    cv2.imwrite(final_image_path, image_with_contours)

def select_file_and_process():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_and_display_images(file_path)

def save_processed_image(processed_image_path, cropped_image_path):
    # Копирование файлов и сохранение на компьютер
    import shutil
    shutil.copyfile(processed_image_path, "new1233_processed_image.jpg")
    shutil.copyfile(cropped_image_path, "new1233_cropped_image.jpg")

def center_window(window, width=300, height=200):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Рассчитываем позицию окна для центрирования
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Устанавливаем размеры и позицию окна
    window.geometry(f'{width}x{height}+{x}+{y}')

# Создаем главное окно
root = tk.Tk()
root.title("Image Processor")
root.geometry("300x150")
center_window(root, 400, 300)

# Создаем кнопку для выбора файла и запуска обработки
btn = tk.Button(root, text="Select Image", command=select_file_and_process)
btn.pack(pady=20, padx=20, expand=True)

# Добавляем Label для отображения изображения
image_label = tk.Label(root)
image_label.pack(expand=True)

# Запускаем главный цикл обработки событий
root.mainloop()

