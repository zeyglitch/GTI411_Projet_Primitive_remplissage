import os
import sys
import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy, QSlider, QCheckBox
)


# --- parametres du pipeline (a regler en regardant les etapes) ---
FLOU_ENTREE = (7, 7)        # lissage gaussien avant la soustraction (enleve le bruit du capteur)
SEUIL_SURE_FOND = 40        # pixels encore proches du fond utilises pour corriger l'exposition
SEUIL_DEFAUT = 28           # seuil sur la difference (modifiable avec le curseur : 10..80)
NOYAU_OUVERTURE = 5         # ouverture : enleve les petits points isoles du fond
NOYAU_FERMETURE = 21        # fermeture : recolle les trous dans la personne (pull blanc / mur blanc)
AIRE_MIN = 0.01             # on garde seulement les regions de plus de 1 % de l'image
FLOU_BORDURE = (9, 9)       # adoucit le bord du masque pour que le collage soit moins dur
MELANGE_PRECEDENT = 0.4     # part du masque de l'image d'avant (limite le scintillement)
FLOU_FOND = (0, 0)          # (0, 0) : OpenCV calcule la taille a partir du sigma
SIGMA_FOND = 15             # intensite du flou du fond


class BackgroundRemover:
    def __init__(self):
        self.background_image = None
        self.background_flou = None
        self.replacement_image = None
        self.masque_precedent = None
        self.seuil = SEUIL_DEFAUT
        self.voir_masque = False
        self.modify_effect = "blur"

    
    def set_modify_effect(self, mode:str):
        self.modify_effect = mode


    def set_seuil(self, valeur: int):
        self.seuil = int(valeur)


    def set_voir_masque(self, actif: bool):
        self.voir_masque = bool(actif)


    def set_background_image(self, bg_image):
        self.background_image = bg_image
        # on lisse le fond une seule fois (il ne change plus tant qu'on ne le re-sauvegarde pas)
        self.background_flou = cv2.GaussianBlur(bg_image, FLOU_ENTREE, 0)
        self.masque_precedent = None


    def set_replacement_image(self, image):
        """Image (RGB) qui remplace le fond quand l'effet est 'replace'."""
        self.replacement_image = image


    # ------------------------------------------------------------------
    # Etapes du pipeline (chacune est une petite fonction pour pouvoir
    # les montrer / les capturer separement dans le rapport)
    # ------------------------------------------------------------------
    def corriger_luminosite(self, image_flou):
        """Compense le changement d'exposition de la webcam en ajustant R, G, B
        d'apres la moyenne des pixels qui ressemblent encore au fond."""
        diff = cv2.absdiff(image_flou, self.background_flou).max(axis=2)
        fond_calme = diff < SEUIL_SURE_FOND
        if fond_calme.sum() < 0.05 * fond_calme.size:
            return image_flou

        gain = (self.background_flou[fond_calme].mean(axis=0)
                / np.maximum(image_flou[fond_calme].mean(axis=0), 1.0))
        corrige = image_flou.astype(np.float32) * gain
        return np.clip(corrige, 0, 255).astype(np.uint8)


    def soustraire_fond(self, image_corrigee):
        """Difference entre l'image et le fond (cours C09), puis seuillage binaire simple."""
        distance = cv2.absdiff(image_corrigee, self.background_flou).max(axis=2)
        _, masque = cv2.threshold(distance, self.seuil, 255, cv2.THRESH_BINARY)
        return distance, masque


    def nettoyer_masque(self, masque):
        """Ouverture (enleve le bruit), fermeture (recolle la personne)."""
        noyau_o = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (NOYAU_OUVERTURE, NOYAU_OUVERTURE))
        noyau_f = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (NOYAU_FERMETURE, NOYAU_FERMETURE))
        masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, noyau_o)
        masque = cv2.morphologyEx(masque, cv2.MORPH_CLOSE, noyau_f)
        return masque


    def garder_grandes_regions(self, masque):
        """On garde les contours assez grands et on les remplit completement
        (ca bouche les trous a l'interieur de la personne, ex. le pull blanc)."""
        contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        resultat = np.zeros_like(masque)
        aire_min = AIRE_MIN * masque.shape[0] * masque.shape[1]
        for c in contours:
            if cv2.contourArea(c) >= aire_min:
                cv2.drawContours(resultat, [c], -1, 255, thickness=cv2.FILLED)
        return resultat


    def adoucir_masque(self, masque):
        """Flou du bord + melange avec le masque precedent. Resultat : alpha entre 0 et 1."""
        alpha = cv2.GaussianBlur(masque, FLOU_BORDURE, 0).astype(np.float32) / 255.0
        if self.masque_precedent is not None and self.masque_precedent.shape == alpha.shape:
            alpha = (1 - MELANGE_PRECEDENT) * alpha + MELANGE_PRECEDENT * self.masque_precedent
        self.masque_precedent = alpha
        return alpha


    def calculer_masque(self, image):
        """Toutes les etapes. Retourne l'alpha final et un dict des etapes (pour le rapport)."""
        etapes = {}
        image_flou = cv2.GaussianBlur(image, FLOU_ENTREE, 0)
        corrigee = self.corriger_luminosite(image_flou)
        distance, brut = self.soustraire_fond(corrigee)
        propre = self.nettoyer_masque(brut)
        regions = self.garder_grandes_regions(propre)
        alpha = self.adoucir_masque(regions)

        etapes["1_image_corrigee"] = corrigee
        etapes["2_distance"] = distance
        etapes["3_masque_brut"] = brut
        etapes["4_masque_morpho"] = propre
        etapes["5_masque_regions"] = regions
        etapes["6_alpha"] = (alpha * 255).astype(np.uint8)
        return alpha, etapes


    def fond_de_remplacement(self, shape):
        """Image de remplacement a la taille de la video (on coupe pour garder les proportions)."""
        h, w = shape[:2]
        if self.replacement_image is None:
            return np.full((h, w, 3), (30, 60, 120), dtype=np.uint8)
        rh, rw = self.replacement_image.shape[:2]
        echelle = max(w / rw, h / rh)
        grande = cv2.resize(self.replacement_image, None, fx=echelle, fy=echelle,
                            interpolation=cv2.INTER_LINEAR)
        y0 = (grande.shape[0] - h) // 2
        x0 = (grande.shape[1] - w) // 2
        return grande[y0:y0 + h, x0:x0 + w]


    def remove_background(self, image:np.ndarray) -> np.ndarray:
        """Remove the background from an RGB image

        Args:
            image (np.ndarray): (h, w, 3) image

        Returns:
            np.ndarray: (h, w, 3) image with removed background
        """

        if self.background_image is None:
            return image

        # le fond sauvegarde doit avoir la meme taille que l'image
        if self.background_image.shape != image.shape:
            return image

        alpha, _ = self.calculer_masque(image)
        if self.voir_masque:
            masque_u8 = (alpha * 255).astype(np.uint8)
            return np.stack([masque_u8, masque_u8, masque_u8], axis=2)

        if self.modify_effect == "blur":
            nouveau_fond = cv2.GaussianBlur(image, FLOU_FOND, SIGMA_FOND)

        elif self.modify_effect == "replace":
            nouveau_fond = self.fond_de_remplacement(image.shape)

        else:
            return image

        # collage : personne * alpha + nouveau fond * (1 - alpha)
        alpha3 = alpha[:, :, None]
        resultat = image.astype(np.float32) * alpha3 + nouveau_fond.astype(np.float32) * (1 - alpha3)
        return resultat.astype(np.uint8)





class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTI411 - Laboratoire 3 - Partie 3")
        self.setGeometry(100, 100, 640, 480)

        # CHANGER CE PARAMETRE SI VOTRE ORDINATEUR N'EST PAS ASSEZ PUISSANT
        frames_per_second = 30

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit()

        self.bg_remover = BackgroundRemover()
        image_remplacement = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "images", "fond_remplacement.jpg"))
        if image_remplacement is not None:
            self.bg_remover.set_replacement_image(cv2.cvtColor(image_remplacement, cv2.COLOR_BGR2RGB))

        # Create UI
        self.init_ui()

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.timer.start(round(1/frames_per_second * 1000))


    def init_ui(self):
        # Webcam feed area (s'adapte quand on redimensionne la fenetre)
        self.image_label = QLabel("Starting webcam...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setMinimumSize(320, 240)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # Buttons
        self.save_backgroud_image_btn = QPushButton("Save background image")
        self.blur_background_btn = QPushButton("Blur background")
        self.replace_background_btn = QPushButton("Replace background")

        # Curseur simple pour regler le seuil en direct (10..80)
        self.seuil_label = QLabel(f"Seuil : {SEUIL_DEFAUT}")
        self.seuil_slider = QSlider(Qt.Horizontal)
        self.seuil_slider.setRange(10, 80)
        self.seuil_slider.setValue(SEUIL_DEFAUT)
        self.seuil_slider.setMaximumWidth(160)
        self.voir_masque_cb = QCheckBox("Voir masque")

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_backgroud_image_btn)
        btn_layout.addWidget(self.blur_background_btn)
        btn_layout.addWidget(self.replace_background_btn)
        btn_layout.addWidget(self.seuil_label)
        btn_layout.addWidget(self.seuil_slider)
        btn_layout.addWidget(self.voir_masque_cb)
        btn_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, stretch=1)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.save_backgroud_image_btn.clicked.connect(self.update_bg_image)
        self.blur_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("blur"))
        self.replace_background_btn.clicked.connect(lambda : self.bg_remover.set_modify_effect("replace"))
        self.seuil_slider.valueChanged.connect(self.update_seuil)
        self.voir_masque_cb.toggled.connect(self.bg_remover.set_voir_masque)


    def update_seuil(self, val):
        self.seuil_label.setText(f"Seuil : {val}")
        self.bg_remover.set_seuil(val)



    def update_bg_image(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert the image from BGR (OpenCV) to RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bg_remover.set_background_image(rgb_image)



    def update_frame(self):
        """Grab a frame from the webcam and display it."""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert the image from BGR (OpenCV) to RGB (Qt)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result_image = self.bg_remover.remove_background(rgb_image)

        h, w, ch = result_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(result_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display image
        self.image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.image_label.size(), Qt.KeepAspectRatio))


    def closeEvent(self, event):
        """Release the webcam when closing the window."""
        if self.cap.isOpened():
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())
