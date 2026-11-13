import numpy as np

import sys
sys.setrecursionlimit(100000)



class BoundaryFillModel:
    def __init__(self) -> None:
        self.fill_color = np.array([0, 200, 255])
        self.boundary_color = np.array([255, 0, 0])
        self.image = None

    

    def boundary_fill(self, image, x, y):
        self.image = image
        try:
            self.fill(x, y)
        except RecursionError:
            # La region est trop grande pour la pile de Python : on termine avec la
            # version iterative (meme algorithme, mais avec notre propre pile).
            print("Maximum recursion reached, switching to the iterative version")
            self.fill_iteratif(x, y)
        return self.image
    
    
    def est_a_remplir(self, x, y):
        """Un pixel est a remplir s'il est dans l'image, pas de la couleur de la bordure
        et pas deja de la couleur de remplissage (cours C08 P02)."""
        h, w = self.image.shape[:2]
        if x < 0 or x >= w or y < 0 or y >= h:
            return False
        pixel = self.image[y, x]
        if np.array_equal(pixel, self.boundary_color):
            return False
        if np.array_equal(pixel, self.fill_color):
            return False
        return True


    # Boundary fill 4-voisins, recursif (cours C08 P02)
    def fill(self, x, y):
        if self.est_a_remplir(x, y):
            self.image[y, x] = self.fill_color
            self.fill(x + 1, y)
            self.fill(x - 1, y)
            self.fill(x, y + 1)
            self.fill(x, y - 1)


    # Meme chose sans recursion : une pile explicite (le cours parle de "grande pile").
    # On garde un tableau "visite" car apres l'echec de la version recursive une partie de la
    # region est deja coloriee : on doit pouvoir la reparcourir pour atteindre le reste.
    def fill_iteratif(self, x, y):
        h, w = self.image.shape[:2]
        visite = np.zeros((h, w), dtype=bool)
        pile = [(x, y)]
        while pile:
            px, py = pile.pop()
            if px < 0 or px >= w or py < 0 or py >= h or visite[py, px]:
                continue
            visite[py, px] = True
            if np.array_equal(self.image[py, px], self.boundary_color):
                continue
            self.image[py, px] = self.fill_color
            pile.append((px + 1, py))
            pile.append((px - 1, py))
            pile.append((px, py + 1))
            pile.append((px, py - 1))


    def set_fill_color(self, color):
        self.fill_color = np.array(color)


    def set_boundary_color(self, color):
        self.boundary_color = np.array(color)
