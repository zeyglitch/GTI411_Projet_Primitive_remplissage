from PyQt5 import QtWidgets
from Lab3.views import Lab3_Window
from Lab3.events import event_manager
from Lab3.models import DrawShapeModel, BoundaryFillModel, FloodFillModel


class Lab3Controller:
    def __init__(self) -> None:

        self.shape_model = DrawShapeModel()
        self.boundary_model = BoundaryFillModel()
        self.flood_model = FloodFillModel()
        self.start_point, self.end_point = None, None
        
        self.window = QtWidgets.QMainWindow()
        self.ui = Lab3_Window()

        self.fill_method = "Boundary"
        self.ui.setupUi(self.window)

        self.ui.update_canvas(self.shape_model.image)
        self.window.show()

        event_manager.register("on_shape_type_changed", self.shape_type_changed)
        event_manager.register("on_mouse_click_pressed", self.on_mouse_click_pressed)
        event_manager.register("on_mouse_click_move", self.on_mouse_click_move)
        event_manager.register("on_mouse_click_released", self.on_mouse_click_released)
        event_manager.register("on_shape_color_changed", self.shape_color_changed)
        event_manager.register("on_fill_color_changed", self.fill_color_changed)
        event_manager.register("on_boundary_color_changed", self.boundary_color_changed)

        event_manager.register("on_fill_color", self.on_fill_color)
        event_manager.register("on_floodfill_low_update", self.flood_model.set_low_threshold)
        event_manager.register("on_floodfill_high_update", self.flood_model.set_high_threshold)
        event_manager.register("set_fill_method", self.set_fill_method)
        event_manager.register("on_load_image", self.load_image)

        event_manager.register("on_canvas_reset", self.reset_canvas)


    def set_fill_method(self, method):
        self.fill_method = method
        print(f"New fillmethod = {method}")


    def reset_canvas(self):
        self.shape_model.reset_image()
        self.ui.update_canvas(self.shape_model.image)



    def load_image(self, path:str):
        if not path:
            return
        import cv2
        image = cv2.imread(path)
        if image is None:
            return
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.shape_model.image = image
        self.ui.update_canvas(self.shape_model.image)


    def shape_color_changed(self, r, g, b):
        self.shape_model.update_color(r, g, b)
        self.ui.maj_couleur_forme(r, g, b)


    def fill_color_changed(self, r, g, b):
        print(f"New fill Color {r, g, b}")
        self.boundary_model.set_fill_color([r, g, b])
        self.flood_model.set_fill_color([r, g, b])
        self.ui.maj_couleur_remplissage(r, g, b)


    def boundary_color_changed(self, r, g, b):
        print(f"New boundary Color {r, g, b}")
        self.boundary_model.set_boundary_color([r, g, b])
        self.ui.maj_couleur_bordure(r, g, b)


    def shape_type_changed(self, shape_type):
        self.shape_model.update_shape_type(shape_type)


    def on_mouse_click_pressed(self, x, y):
        self.start_point = (x, y)
        self.end_point = (x, y)


    def on_mouse_click_move(self, x, y):
        if self.start_point is None:
            self.start_point = (x, y)
        self.end_point = (x, y)
        # Previsualisation temporaire pendant qu'on maintient le clic gauche
        apercu = self.shape_model.preview_shape(self.start_point, self.end_point)
        self.ui.update_canvas(apercu)


    def on_mouse_click_released(self):
        image = self.shape_model.draw_shape(self.start_point, self.end_point)
        self.start_point = None
        self.end_point = None
        if image is not None:
            self.ui.update_canvas(image)
        else:
            self.ui.update_canvas(self.shape_model.image)


    def on_fill_color(self, x, y):
        image = self.shape_model.image

        if self.fill_method == "Boundary":
            image = self.boundary_model.boundary_fill(image, x, y)
        elif self.fill_method == "Flood":
            image = self.flood_model.fill(image, x, y)
        self.ui.update_canvas(image)
