import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('cropped_image.jpg')

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

# Сортируем цвета по вертикальной координате центра контура
sorted_colors = sorted(contours_centers, key=contours_centers.get)

# Выводим порядок цветов сверху вниз
print("Порядок цветов сверху вниз:")
for color in sorted_colors:
    print(color)

# Рисуем контуры на исходном изображении и подписываем цвет контура
image_with_contours = image.copy()
for color_name in sorted_colors:
    contour = contours_dict[color_name]
    # Рисуем контур
    cv2.drawContours(image_with_contours, [contour], -1, colors[color_name], 2)

    # Определяем цвет контура текстом
    color = colors[color_name]
    text_color = (255 - color[0], 255 - color[1], 255 - color[2])  # негатив цвета
    # Получаем центр контура для размещения текста
    M = cv2.moments(contour)
    cx = int(M["m10"] / (M["m00"] + 1e-5))  # Избегаем деление на ноль
    cy = int(M["m01"] / (M["m00"] + 1e-5))  # Избегаем деление на ноль
    # Подписываем цвет контура
    cv2.putText(image_with_contours, color_name, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

# Отображаем результат
cv2.imshow('Contours', image_with_contours)
cv2.waitKey(0)
cv2.destroyAllWindows()
