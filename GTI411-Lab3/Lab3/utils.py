from PyQt5.QtGui import QPixmap, QImage


def np_array_to_pixmap(array):
    height, width, channel = array.shape
    # Convertir le tableau en QImage
    if channel == 3:  # Si l'image est en RGB
        qimage = QImage(array.data, width, height, 3 * width, QImage.Format_RGB888)
    elif channel == 4:  # Si l'image est en RGBA
        qimage = QImage(array.data, width, height, 4 * width, QImage.Format.Format_RGBA8888)
    else:
        raise ValueError("Le tableau numpy doit avoir 3 canaux (RGB) ou 4 canaux (RGBA)")

    # Convertir QImage en QPixmap
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap

