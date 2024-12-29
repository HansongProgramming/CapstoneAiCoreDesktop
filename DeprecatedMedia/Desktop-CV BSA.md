[[Deliverables-Tasks]] 


### Desktop_CVBSA.py
![[Desktop_CVBSA.py]]

### Code Breakdown:

#### Imports
Makes use of the following libraries to deliver the solution
```python
import numpy as np
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
```

#### Class App
A class is made to allow object oriented programming, App() will be used to store the features within one class
```python
class App(ctk.CTk):
```

### Initialization
```python
    def __init__(self):
        super().__init__()
        self.title("AiCore")
        self.geometry("1200x700")

        self.file_options = ["Open"]
        self.optionmenu_var = ctk.StringVar(value=self.file_options[0])
        self.option_menu = ctk.CTkOptionMenu(
            self,
            variable=self.optionmenu_var,
            values=self.file_options,
            command=self.menu_command
        )
        self.option_menu.pack(pady=10)
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y")

        self.layer_label = ctk.CTkLabel(self.sidebar_frame, text="Layers")
        self.layer_label.pack(pady=10)

        self.original_button = ctk.CTkButton(self.sidebar_frame, text="Original", command=lambda: self.change_layer(0))

        self.original_button.pack(pady=5)

        self.satellite_points_button = ctk.CTkButton(self.sidebar_frame, text="Satellite Points", command=lambda: self.change_layer(1))
        self.satellite_points_button.pack(pady=5)

        self.lines_button = ctk.CTkButton(self.sidebar_frame, text="Lines", command=lambda: self.change_layer(2))

        self.lines_button.pack(pady=5)
        self.info_label = ctk.CTkLabel(self.sidebar_frame, text="Information")
        self.info_label.pack(pady=10)

  
        self.zoom_slider = ctk.CTkSlider(self.sidebar_frame, from_=1, to=3, number_of_steps=200, command=self.update_image)
        self.zoom_slider.set(1)
        self.zoom_slider.pack(pady=20)

        self.rotation_slider = ctk.CTkSlider(self.sidebar_frame, from_=0, to=360, number_of_steps=360, command=self.update_image)
        self.rotation_slider.set(0)
        self.rotation_slider.pack(pady=20)

        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(side="right", expand=True, fill="both")
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="gray")
        self.canvas.pack(expand=True, fill="both")
  
        self.current_image = None
        self.zoom_scale = 1
        self.rotation_angle = 0
        self.image_layers = []
        self.current_layer = 0

        self.pan_offset_x, self.pan_offset_y = 0, 0
        self.drag_start_x, self.drag_start_y = -1, -1
        self.dragging = False
```

### Menu Commands
```python
    def menu_command(self, choice):
        if choice == "Open":
            self.open_image()
```

### Open Image
```python
    def open_image(self):
        file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.load_image(file_path)
```
### Load Image
```python
     def load_image(self, file_path):
        image = cv2.imread(file_path) 
        self.image_layers = [
            image.copy(),
            self.detect_satellite_points(image.copy()),
            self.detect_lines(image.copy())
        ]
        self.current_layer = 0
        self.display_image()
```

### Display Image
```python
    def display_image(self):
        if self.image_layers:
            image = self.image_layers[self.current_layer]
            image = self.apply_transformations(image)
            
            bgr_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(bgr_image)
            
            imgtk = ImageTk.PhotoImage(image=pil_image)
            img_width, img_height = pil_image.size
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = (canvas_width // 2) - (img_width // 2)
            y = (canvas_height // 2) - (img_height // 2)

            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor="nw", image=imgtk)
            self.canvas.image = imgtk
```

### Apply Transformation
```python
    def apply_transformations(self, image):
        width = int(image.shape[1] * self.zoom_scale)
        height = int(image.shape[0] * self.zoom_scale)
        image = cv2.resize(image, (width, height))

        if self.rotation_angle != 0:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h))
        image = self.apply_pan(image)
        return image
```
### Apply Pan
```python
    def apply_pan(self, img):
        h, w = img.shape[:2]
        new_w = int(w * self.zoom_scale)
        new_h = int(h * self.zoom_scale)
        
        max_x_offset = max(0, new_w - w)
        max_y_offset = max(0, new_h - h)

        offset_x = min(max(self.pan_offset_x, -max_x_offset), max_x_offset)
        offset_y = min(max(self.pan_offset_y, -max_y_offset), max_y_offset)

        return img[max(0, offset_y):min(new_h, h + offset_y), max(0, offset_x):min(new_w, w + offset_x)]
```
### Update Image
```python
    def update_image(self, value=None):
        self.zoom_scale = self.zoom_slider.get()
        self.rotation_angle = self.rotation_slider.get()
        self.display_image()
```

### Change Layer
```python
	self.current_layer = layer_index
	self.display_image()
```
### Detect Satellite Points
```python
def detect_satellite_points(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 50, 255, 
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.rectangle(image, 
                (cx - 5, cy - 5), (cx + 5, cy + 5), (0, 255, 0), 2)

        return image
```
###  Detect Lines
```python
    def detect_lines(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  
        _, thresh = cv2.threshold(blurred, 50, 255, 
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
                            cv2.line(image, (cx_main, cy_main), 
                            (cx, cy), (255, 0, 0), 2)
        return image
```

### Call the class
```python
if __name__ == "__main__":
    app = App()
    app.mainloop()
```

**A System By *Cre8Tive Sync***
Flores Hans Harold L. &  Reburiano Augnina Krizel P.  @2024 All Rights Reserved.