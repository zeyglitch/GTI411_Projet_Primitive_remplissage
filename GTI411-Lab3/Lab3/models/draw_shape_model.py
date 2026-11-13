import numpy as np
import cv2

import sys
sys.setrecursionlimit(100000)


def is_close(vec1, vec2):
    max_diff = np.max(np.abs(vec1 - vec2))
    return max_diff < 50


class DrawShapeModel:
    def __init__(self) -> None:
        w, h = 1250, 490
        self.shape_type = 'Circle'
        self.color = [255, 0, 0]
        self.line_thickness = 3
        self.rectangle_avec_cv2 = False   # True : rectangle avec cv2 pour comparer avec Bresenham
        self.reset_image(h, w)
        
        self.fill_color = np.array([255, 255, 0])
        self.boundary_color = np.array([255, 0, 0])


    def reset_image(self, h=490, w=1250):
        self.image = np.ones((h, w, 3)) * np.array([255, 255, 255])
        self.image = self.image.astype(np.uint8)
        
    
    def update_shape_type(self, shape_type:str):
        print(f"New shape type {shape_type}")
        self.shape_type = shape_type


    def update_color(self, r, g, b):
        self.color = [r, g, b]



    # ------------------------------------------------------------------
    # Outils de base (partie 1)
    # ------------------------------------------------------------------
    def set_pixel(self, x, y):
        """Allume un pixel de la couleur choisie (carre de cote line_thickness autour du point)."""
        h, w = self.image.shape[:2]
        demi = self.line_thickness // 2
        x_min, x_max = max(0, x - demi), min(w, x + demi + 1)
        y_min, y_max = max(0, y - demi), min(h, y + demi + 1)
        if x_min < x_max and y_min < y_max:
            self.image[y_min:y_max, x_min:x_max] = self.color


    def bresenham(self, x1, y1, x2, y2):
        """Ligne par l'algorithme du point milieu (cours C08 P01), pour tous les cas de pente.

        Le cours donne la version avec restrictions (x1 < x2 et 0 < dy/dx < 1).
        On se ramene a ce cas puis on remet les points dans le bon ordre.
        """
        # |pente| > 1 : on echange le role de x et y
        raide = abs(y2 - y1) > abs(x2 - x1)
        if raide:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        # x1 > x2 : on echange les deux points
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1

        dx = x2 - x1
        dy = abs(y2 - y1)
        pas_y = 1 if y1 < y2 else -1      # pente negative : on descend en y

        inc_e = 2 * dy
        inc_ne = 2 * dy - 2 * dx
        d = 2 * dy - dx

        points = []
        y = y1
        for x in range(x1, x2 + 1):
            # si on avait echange x et y, on remet (y, x) pour dessiner
            points.append((y, x) if raide else (x, y))
            if d <= 0:
                d += inc_e                # pixel E
            else:
                d += inc_ne               # pixel NE
                y += pas_y
        return points


    def draw_line(self, p1, p2):
        for x, y in self.bresenham(p1[0], p1[1], p2[0], p2[1]):
            self.set_pixel(x, y)


    def draw_rectangle(self, p1, p2):
        """Rectangle = 4 lignes Bresenham (p1 haut gauche, p2 bas droite)."""
        # on accepte aussi de tirer la souris dans un autre sens
        x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
        y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])

        if self.rectangle_avec_cv2:
            cv2.rectangle(self.image, (x_min, y_min), (x_max, y_max), tuple(self.color),
                          self.line_thickness, cv2.LINE_8)
            return

        self.draw_line((x_min, y_min), (x_max, y_min))   # haut
        self.draw_line((x_max, y_min), (x_max, y_max))   # droite
        self.draw_line((x_max, y_max), (x_min, y_max))   # bas
        self.draw_line((x_min, y_max), (x_min, y_min))   # gauche


    def draw_circle(self, centre, rayon):
        """Cercle par le point milieu (cours C08 P01) : on calcule 1/8 du cercle
        centre en (0,0) puis on utilise les 8 symetries et on translate vers le centre."""
        cx, cy = centre
        x = 0
        y = rayon
        d = 5.0 / 4.0 - rayon

        while x <= y:
            for dx, dy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.set_pixel(cx + dx, cy + dy)

            if d < 0:
                d += 2.0 * x + 3.0                  # pixel E
            else:
                d += 2.0 * (x - y) + 5.0            # pixel SE
                y -= 1
            x += 1


    def draw_ellipse(self, centre, bout):
        """Ellipse avec cv2 (autorise par le docx) : p1 = centre, p2 = bout du semi-grand axe,
        semi-petit axe = moitie du grand."""
        dx = bout[0] - centre[0]
        dy = bout[1] - centre[1]
        grand = int(round(np.hypot(dx, dy)))
        petit = grand // 2
        angle = np.degrees(np.arctan2(dy, dx))      # le grand axe suit la direction de la souris
        cv2.ellipse(self.image, centre, (grand, petit), angle, 0, 360,
                    tuple(self.color), self.line_thickness, cv2.LINE_8)


    def _tracer(self, start_point, end_point):
        """Trace la forme choisie sur self.image sans affichage console."""
        p1 = (int(start_point[0]), int(start_point[1]))
        p2 = (int(end_point[0]), int(end_point[1]))

        if self.shape_type == "Line":
            self.draw_line(p1, p2)

        elif self.shape_type == "Circle":
            rayon = int(round(np.hypot(p2[0] - p1[0], p2[1] - p1[1])))
            self.draw_circle(p1, rayon)

        elif self.shape_type == "Rectangle":
            self.draw_rectangle(p1, p2)

        elif self.shape_type.lower().startswith("ell"):
            # la liste deroulante de la vue ecrit "Ellispis" (faute du prof), d'ou le startswith
            self.draw_ellipse(p1, p2)


    def preview_shape(self, start_point, end_point):
        """Previsualise la forme sur une copie temporaire pendant qu'on glisse la souris."""
        if start_point is None or end_point is None or len(start_point) == 0 or len(end_point) == 0:
            return self.image
        copie = self.image.copy()
        image_originale = self.image
        self.image = copie
        self._tracer(start_point, end_point)
        self.image = image_originale
        return copie


    def draw_shape(self, start_point:tuple[int], end_point:tuple[int]):
        """Draw shape at the desired location based on the starting point and end point.

        You can use self.color to get the color selected with the picker
        Implement the logic for 'Line', 'Circle' and 'Rectangle'

        Args:
            start_point (tuple[int]): Coordinates (x,y) of the click point
            end_point (tuple[int]): Coordinates (x,y) of the released point

        Returns:
            np.ndarray: Image with the shape on it
        """
        if start_point is None or end_point is None or len(start_point) == 0 or len(end_point) == 0:
            return
        print(f"Drawing shape {self.shape_type} at p1={start_point} p2={end_point}")

        self._tracer(start_point, end_point)
        return self.image