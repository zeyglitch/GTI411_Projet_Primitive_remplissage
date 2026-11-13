from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np

from Lab3.utils import np_array_to_pixmap
from Lab3.events import event_manager



def create_color_palette(height:int, width: int, rgbcolor:list[int]):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    h, w, c = image.shape
    for widx in range(w):
        color = 255*(widx/ w) * np.array(rgbcolor)
        for hidx in range(h):
            image[hidx, widx] = color
    return image


class SliderWithImage(QtWidgets.QSlider):
    def __init__(self, image, parent):
        super().__init__(QtCore.Qt.Horizontal, parent)
        self.image = image


    def paintEvent(self, event):
        if self.image is None:
            super().paintEvent(event)
            return
        # Création du QPainter pour dessiner l'image de fond
        painter = QtGui.QPainter(self)
        qpixmap = np_array_to_pixmap(self.image)
        painter.drawPixmap(self.rect(), qpixmap)
        # Appel de la méthode paintEvent de la classe de base pour dessiner le reste du slider
        super().paintEvent(event)



def create_slider(parent, name:str,
                  minval:int=0,
                  maxval: int=255,
                  default_value: int = 0,
                  slider_palette: np.ndarray = None
                  ):
    horizontal_layout = QtWidgets.QHBoxLayout()

    slider = SliderWithImage(slider_palette, parent)
    slider.setMinimum(minval)
    slider.setMaximum(maxval)
    slider.setValue(default_value)

    label = QtWidgets.QLabel(parent)
    label.setText(name)

    # SpinBox pour pouvoir aussi taper directement la valeur (0..255)
    spinbox = QtWidgets.QSpinBox(parent)
    spinbox.setRange(minval, maxval)
    spinbox.setValue(default_value)
    spinbox.setMinimumWidth(55)

    slider.valueChanged['int'].connect(spinbox.setValue)
    spinbox.valueChanged['int'].connect(slider.setValue)

    slider.setMinimumSize(QtCore.QSize(267, 22))

    horizontal_layout.addWidget(label)
    horizontal_layout.addWidget(slider)
    horizontal_layout.addWidget(spinbox)
    return horizontal_layout, slider



class RGBColorPicker(QThread):
    my_signal = pyqtSignal(int, int, int, bool)
    width: int = 267
    height: int = 22

    def setup_ui(self, parent, event_name:str, couleur_initiale=(255, 0, 0)):
        self.event_name = event_name
        centralwidget = QtWidgets.QWidget(parent)

        layout = QtWidgets.QVBoxLayout(centralwidget)
        r0, g0, b0 = (int(c) for c in couleur_initiale)

        red_palette = create_color_palette(self.height, self.width, [1, 0, 0])
        red_layout, self.red_slider = create_slider(centralwidget, "R", default_value=r0, slider_palette=red_palette)

        # Green channel
        green_palette = create_color_palette(self.height, self.width, [0, 1, 0])
        green_layout, self.green_slider = create_slider(centralwidget, "G", default_value=g0, slider_palette=green_palette)

        # Blue channel
        blue_palette = create_color_palette(self.height, self.width, [0, 0, 1])
        blue_layout, self.blue_slider = create_slider(centralwidget, "B", default_value=b0, slider_palette=blue_palette)

        # Petit apercu visuel de la couleur choisie
        self.apercu_couleur = QtWidgets.QLabel(centralwidget)
        self.apercu_couleur.setMinimumHeight(24)
        self.apercu_couleur.setStyleSheet(f"background-color: rgb({r0}, {g0}, {b0}); border: 1px solid #555;")

        # Listen for changes
        self.red_slider.valueChanged['int'].connect(self.value_changed)
        self.green_slider.valueChanged['int'].connect(self.value_changed)
        self.blue_slider.valueChanged['int'].connect(self.value_changed)

        layout.addLayout(red_layout)
        layout.addLayout(green_layout)
        layout.addLayout(blue_layout)
        layout.addWidget(self.apercu_couleur)

        parent.setCentralWidget(centralwidget)


    def value_changed(self):
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        self.apercu_couleur.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #555;")

        event_manager.trigger(self.event_name, r,g,b)

        # self.setLayout(layout)