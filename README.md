# GTI411 - Lab 3 : Primitives, remplissage et soustraction de fond

Tracé de primitives géométriques, remplissage de régions et soustraction d'arrière-plan en temps réel avec du traitement d'image classique (OpenCV / NumPy / PyQt5), sans apprentissage profond.

- **Partie 1** : dessin de primitives à la souris (ligne avec Bresenham dans les 8 octants, cercle par point milieu, rectangle et ellipse) avec prévisualisation en direct.
- **Partie 2** : remplissage au clic droit avec `BoundaryFill` (récursif à 4 voisins + version avec pile si la zone dépasse la limite de récursion) et `FloodFill` (`cv2.floodFill` avec seuils `low` et `high`).
- **Partie 3** : soustraction de fond sur la webcam (ou sur la vidéo fournie), nettoyage morphologique du masque et alpha-blending pour flouter l'arrière-plan ou le remplacer par une image.

## Organisation

- `GTI411-Lab3/`
  - `MainWindow.py` : lance l'interface Paint (Parties 1 et 2)
  - `test_fill.py` : test rapide du `BoundaryFill` récursif sur `images/test.png`
  - `part3_background_remover.py` : pipeline de soustraction de fond et interface webcam (Partie 3)
  - `Lab3/models/`
    - `draw_shape_model.py` : Bresenham, cercle point milieu, rectangle, ellipse et prévisualisation
    - `boundary_fill_model.py` : remplissage `BoundaryFill` (4 voisins)
    - `flood_fill_model.py` : remplissage `FloodFill` avec seuils `low` et `high`
  - `Lab3/views/` : fenêtre principale (`Lab3_Window.py`) et sélecteur de couleur RGB (`rgb_color_picker.py`)
  - `Lab3/controllers/lab3controller.py` : contrôleur MVC
- `GTI411-Lab3_part3_no_webcam/`
  - `background_remover-nocam.py` : Partie 3 sur la vidéo fournie `webcam_video.avi` (sans webcam)

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Lancer

**Parties 1 et 2 (Paint) :**
```bash
cd GTI411-Lab3
python MainWindow.py
```
Clic gauche glissé pour dessiner une forme, clic droit pour remplir une zone.

**Partie 3 (avec webcam) :**
```bash
cd GTI411-Lab3
python part3_background_remover.py
```

**Partie 3 (sans webcam, avec la vidéo fournie) :**
```bash
cd GTI411-Lab3_part3_no_webcam
python background_remover-nocam.py
```
Touches : `ESPACE` pour mettre en pause, `R` pour basculer entre flou et remplacement de fond, `Q` ou `ESC` pour quitter.
