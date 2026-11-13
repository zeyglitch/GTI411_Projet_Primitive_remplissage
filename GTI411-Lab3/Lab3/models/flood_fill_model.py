import cv2
import numpy as np

class FloodFillModel:
    def __init__(self) -> None:
        self.low_threshold = 0
        self.high_treshold = 0

        self.fill_color = [0, 200, 255]


    def fill(self, image, x, y):
        """Flood fill avec OpenCV (autorise pour cette methode).

        On remplit tous les pixels 4-reliés au pixel de depart dont la couleur est entre
        couleur_depart - low et couleur_depart + high (cours C08 P02 + diapo du lab).
        """
        return self.fill_temp(image, x, y)


    # Hint: Vous pouvez utiliser la fonction d'OpenCV
    def fill_temp(self, image, x, y):
        h, w = image.shape[:2]
        if x < 0 or x >= w or y < 0 or y >= h:
            return image

        image = np.ascontiguousarray(image, dtype=np.uint8)
        low = int(self.low_threshold)
        high = int(self.high_treshold)

        # FIXED_RANGE : on compare avec le pixel de depart (et pas avec le voisin deja traite),
        # sinon un degrade finirait par tout remplir.
        flags = 4 | cv2.FLOODFILL_FIXED_RANGE
        couleur = tuple(int(c) for c in self.fill_color)
        cv2.floodFill(image, None, (int(x), int(y)), couleur,
                      (low, low, low), (high, high, high), flags)
        return image


    def set_fill_color(self, color):
        self.fill_color = color


    def set_low_threshold(self, val):
        self.low_threshold = val
        print(f"New low threshold = {val}")


    def set_high_threshold(self, val):
        self.high_treshold = val
        print(f"New high threshold = {val}")

