from PIL import ImageEnhance, Image
import customtkinter as ctk


class ImageEditor:
    def __init__(self, title: str, geometry: list):
        self.__title = title
        self.__geometry = geometry
        
        self.img = Image.open(self.open_image())

        # Fuck HSL am I right
        if self.img.mode != "RGB":
            self.img = self.img.convert('RGB')

        self.original_image = self.img.copy()
        self.enhancements = {
            'contrast': 0.5,
            'brightness': 0.5,
            'sharpness': 0.5,
            'saturation': 0.5 
        }

        self.build()

    def open_image(self):
        file_path = ctk.filedialog.askopenfilename(defaultextension=".jpg", 
                                                   filetypes=[("JPEG files", "*.jpg"),
                                                              ("PNG files", "*.png"),
                                                              ("All files", "*.*")])
        if file_path:
            return file_path

    def apply_enhancements(self):
        enhanced_image = self.original_image.copy()

        for enhancement, value in self.enhancements.items():
            if enhancement == 'contrast':
                enhanced_image = ImageEnhance.Contrast(enhanced_image).enhance(value)

            elif enhancement == 'brightness':
                enhanced_image = ImageEnhance.Brightness(enhanced_image).enhance(value)

            elif enhancement == 'sharpness':
                enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(value)

            elif enhancement == 'saturation':
                enhanced_image = ImageEnhance.Color(enhanced_image).enhance(value)

        return enhanced_image

    def change_enhancement(self, enhancement: str, value: float):
        self.enhancements[enhancement] = float(value) / 50  # Scale to [0.0, 2.0]
        enhanced_image = self.apply_enhancements()
        self.update_displayed_image(enhanced_image)

    def update_displayed_image(self, img):
        self.enhanced_image = ctk.CTkImage(img, size=(400, 400))
        self.enhanced_image_display.configure(image=self.enhanced_image)
        self.enhanced_image_display.image = self.enhanced_image  # Keep a reference to avoid garbage collection


    def save_image(self):
        enhanced_image = self.apply_enhancements()
        file_path = ctk.filedialog.asksaveasfilename(defaultextension=".jpg", 
                                                   filetypes=[("JPEG files", "*.jpg"),
                                                              ("PNG files", "*.png"),
                                                              ("All files", "*.*")])
        if file_path:
            enhanced_image.save(file_path)


    def build(self):
        root = ctk.CTk()
        root.title(self.__title)
        root.geometry(f"{self.__geometry[0]}x{self.__geometry[1]}")
        root.minsize(1280, 720)

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        contrast_variable = ctk.IntVar()
        contrast_variable.set(self.enhancements['contrast'])

        brightness_variable = ctk.IntVar()

        image_frame = ctk.CTkFrame(root)
        image_frame.pack(pady=10, fill="both", expand=True)

        original_frame = ctk.CTkFrame(image_frame)
        original_frame.pack(side="left", padx=10, fill="both", expand=True)

        original_image = ctk.CTkImage(self.img, size=(400, 400))
        original_image_label = ctk.CTkLabel(original_frame, text="Original Image:", anchor="n")
        original_image_label.pack()

        self.original_image_display = ctk.CTkLabel(original_frame, text='', image=original_image)
        self.original_image_display.pack()

        enhanced_frame = ctk.CTkFrame(image_frame)
        enhanced_frame.pack(side="left", padx=10, fill="both", expand=True)

        self.enhanced_image = ctk.CTkImage(self.img, size=(400, 400))
        enhanced_image_label = ctk.CTkLabel(enhanced_frame, text="Enhanced Image:", anchor="n")
        enhanced_image_label.pack()

        self.enhanced_image_display = ctk.CTkLabel(enhanced_frame, text='', image=self.enhanced_image)
        self.enhanced_image_display.pack()

        contrast_label = ctk.CTkLabel(enhanced_frame, text="Contrast")
        
        contrast_slider = ctk.CTkSlider(enhanced_frame, from_=0, to=100,  command=lambda x: self.change_enhancement('contrast', x))
        contrast_label.pack(), contrast_slider.pack()

        brightness_slider = ctk.CTkSlider(enhanced_frame, from_=0, to=100, command=lambda x: self.change_enhancement('brightness', x))
        brightness_slider.pack()

        sharpness_slider = ctk.CTkSlider(enhanced_frame, from_=0, to=100, command=lambda x: self.change_enhancement('sharpness', x))
        sharpness_slider.pack()

        saturation_slider = ctk.CTkSlider(enhanced_frame, from_=0, to=100, command=lambda x: self.change_enhancement('saturation', x))
        saturation_slider.pack()

        save_button = ctk.CTkButton(enhanced_frame, text="Save image as...", command=self.save_image)
        save_button.pack()

        self.update_displayed_image(self.img)

        root.mainloop()


app = ImageEditor(title="Image Editor", geometry=[1280, 720])
