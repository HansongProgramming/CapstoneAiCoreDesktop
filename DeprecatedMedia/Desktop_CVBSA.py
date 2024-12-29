import numpy as np
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title                  ("AiCore")
        self.geometry               ("1200x700")
        # self.overrideredirect(True)

# Top menu bar, contains the buttons : file , Edit, Simulator
        # Variable name         Variable Type       (Reference, Values)
        self.menubar_frame      = ctk.CTkFrame      (self, height=30)
        self.file_button        = ctk.CTkButton     (self.menubar_frame,text="file", height=30, fg_color='#2a2a2a', command=lambda: self.open_image(), width=60)
        self.edit_button        = ctk.CTkButton     (self.menubar_frame,text="edit", height=30, fg_color='#2a2a2a', command=lambda: self.open_image(), width=60)
        self.simulator_button   = ctk.CTkButton     (self.menubar_frame,text="simulator", height=30, fg_color='#2a2a2a', command=lambda: self.open_image(), width=60)
        self.image              = ctk.CTkImage      (light_image=Image.open(r"2-Codes\Computer Vision\aicore.png"),size=(30, 30))
        self.logoicon           = ctk.CTkButton     (self.menubar_frame, image=self.image, text="", fg_color='#2a2a2a', height=30, width=30)        

# Side bar, contains the buttons : layers, information
        # Variable name         Variable Type       (Reference, Values)
        self.sidebar_frame      = ctk.CTkFrame      (self, width=200)
        self.layer_label        = ctk.CTkLabel      (self.sidebar_frame, text="Layers")
        self.original_button    = ctk.CTkButton     (self.sidebar_frame, text="Original", command=lambda: self.change_layer(0), fg_color='#2a2a2a')
        self.satellite_button   = ctk.CTkButton     (self.sidebar_frame, text="Count Satellite Points", command=lambda: self.change_layer(1),fg_color='#2a2a2a')
        self.lines_button       = ctk.CTkButton     (self.sidebar_frame, text="Convergence Point", command=lambda: self.change_layer(2),fg_color='#2a2a2a')
        self.Segment            = ctk.CTkButton     (self.sidebar_frame, text="Segment Blood Spatter", command=lambda: self.AiSegment(), fg_color='#2a2a2a')
        self.info_label         = ctk.CTkLabel      (self.sidebar_frame, text="Information")
        self.spatter_count      = ctk.CTkLabel      (self.sidebar_frame, text="Spatter Count:")
        self.zoom_slider        = ctk.CTkSlider     (self.sidebar_frame, from_=1, to=3, number_of_steps=200, command=self.update_image)
        self.canvas_frame       = ctk.CTkFrame      (self, bg_color="black")
        self.canvas             = ctk.CTkCanvas     (self.canvas_frame, bg="#2a2a2a", highlightthickness = 0)

# Packing of components
        # Variable to pack                          Values Associated
        self.menubar_frame.pack                     (side="top", fill="x")
        self.logoicon.pack                          (padx=2, side="left")
        self.file_button.pack                       (padx=5, side="left")
        self.edit_button.pack                       (padx=5, side="left")
        self.simulator_button.pack                  (padx=5, side="left")
        self.sidebar_frame.pack                     (side="left", fill="y")
        self.layer_label.pack                       (pady=10)
        self.original_button.pack                   (pady=5)
        self.satellite_button.pack                  (pady=5)
        self.lines_button.pack                      (pady=5)
        self.info_label.pack                        (pady=10)
        self.spatter_count.pack                     (pady=10)
        self.zoom_slider.pack                       (pady=20)
        self.canvas_frame.pack                      (side="right", expand=True, fill="both")
        self.canvas.pack                            (expand=True, fill="both")

# Initial Values of information
        # Variable                                  Initial Value set
        self.zoom_slider.set                        (1)
        self.current_image                          = None
        self.zoom_scale                             = 1
        self.image_layers                           = []
        self.current_layer                          = 0

        self.pan_offset_x, self.pan_offset_y        = 0, 0
        self.drag_start_x, self.drag_start_y        = -1, -1
        self.dragging                               = True

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        image                   = cv2.imread(file_path)
        self.image_layers       = [image.copy(), self.detect_satellite_points(image.copy()),self.detect_lines(image.copy())]
        self.current_layer      = 0
        self.display_image()

    def display_image(self):
        if self.image_layers:
            image                   = self.image_layers[self.current_layer]
            image                   = self.apply_transformations(image)

            bgr_image               = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image               = Image.fromarray(bgr_image)
            imgtk                   = ImageTk.PhotoImage(image=pil_image)

            img_width, img_height   = pil_image.size

            canvas_width            = self.canvas.winfo_width()
            canvas_height           = self.canvas.winfo_height()

            x = (canvas_width // 2)  - (img_width // 2)
            y = (canvas_height // 2) - (img_height // 2)

            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor="nw", image=imgtk)
            self.canvas.image = imgtk

    def apply_transformations(self, image):
        width = int(image.shape[1] * self.zoom_scale)
        height = int(image.shape[0] * self.zoom_scale)
        image = cv2.resize(image, (width, height))
        return image

    def update_image(self, value=None):
        self.zoom_scale = self.zoom_slider.get()

        self.display_image()

    def change_layer(self, layer_index):
        self.current_layer = layer_index
        self.display_image()

    def detect_satellite_points(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.rectangle(image, (cx - 5, cy - 5), (cx + 5, cy + 5), (0, 255, 0), 2)
            self.spatter_count.configure(text=f"Spatter Count: {len(cnt )}")
        return image

    def detect_lines(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            main_stain = max(contours, key=cv2.contourArea)
            M_main = cv2.moments(main_stain)
            if M_main["m00"] != 0:
                cx_main = int(M_main["m10"] / M_main["m00"])
                cy_main = int(M_main["m01"] / M_main["m00"])
                for cnt in contours:
                    if cnt is not main_stain:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            cv2.line(image, (cx_main, cy_main), (cx, cy), (255, 0, 0), 2)

        return image

if __name__ == "__main__":
    app = App()
    app.mainloop()
