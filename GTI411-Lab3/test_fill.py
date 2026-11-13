import numpy as np
import cv2
import matplotlib.pyplot as plt

import sys
sys.setrecursionlimit(100000)



boundary_color = np.array([255, 0, 0])
# boundary_color = [0, 0, 0]
fill_color = np.array([0, 255, 255])

image = cv2.imread("images/test.png")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)



# TODO: IMPLEMENTER CETTE FONCTION
def boundary_fill(x, y):
    # meme algo que dans models/boundary_fill_model.py (4 voisins, cours C08 P02)
    h, w = image.shape[:2]
    if x < 0 or x >= w or y < 0 or y >= h:
        return
    pixel = image[y, x]
    if np.array_equal(pixel, boundary_color) or np.array_equal(pixel, fill_color):
        return
    image[y, x] = fill_color
    boundary_fill(x + 1, y)
    boundary_fill(x - 1, y)
    boundary_fill(x, y + 1)
    boundary_fill(x, y - 1)


def main():
    plt.subplot(1, 2, 1)
    plt.title("Forme initiale")
    plt.imshow(image)
    boundary_fill(15, 15)
    # boundary_fill(559, 258)
    plt.subplot(1, 2, 2)
    plt.title("Résultat attendu")
    plt.imshow(image)
    plt.show()
    



if __name__ == "__main__":
    main()