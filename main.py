import os.path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageEnhance

import image_processor


class ImageEditor:
    processor = image_processor.ImageProcessor()

    def __init__(self, title: str, geometry: list = []):
        """App builds itself on __init__ call, so no need to app.build()"""

        self.min_width = 1280
        self.min_height = 720

        self._title = title
        self._geometry = geometry

        if self._geometry == []:
            self._geometry.append(self.min_width)
            self._geometry.append(self.min_height)

        try:
            if os.path.exists("img_path.txt"):
                with open("img_path.txt", "r") as file:
                    image_path = file.readline()

            else:
                image_path = self.processor.open_image()

            if image_path is not None:
                self.img = Image.open(image_path)

                with open("img_path.txt", "w") as file:
                    file.write(image_path)

        except Exception as e:
            messagebox.showerror("An error occurred. Details: ", str(e))

        # TODO: Fuck HSL am I right?
        if self.img.mode != "RGB":
            self.img = self.img.convert("RGB")

        self.original_image = self.img.copy()
        self.enhancements = {
            "contrast": 0.5,
            "brightness": 0.5,
            "sharpness": 0.5,
            "saturation": 0.5,
        }

        self.build()

    def apply_enhancements(self):
        enhanced_image = self.img.copy()

        for enhancement, value in self.enhancements.items():
            if enhancement == "contrast":
                enhanced_image = ImageEnhance.Contrast(enhanced_image).enhance(value)

            elif enhancement == "brightness":
                enhanced_image = ImageEnhance.Brightness(enhanced_image).enhance(value)

            elif enhancement == "sharpness":
                enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(value)

            elif enhancement == "saturation":
                enhanced_image = ImageEnhance.Color(enhanced_image).enhance(value)

        return enhanced_image

    def change_enhancement(self, enhancement: str, value: float):
        self.enhancements[enhancement] = float(value) / 100
        enhanced_image = self.apply_enhancements()
        self.update_displayed_image(enhanced_image)

    def update_displayed_image(self, img):
        self.enhanced_image = ctk.CTkImage(img, size=(400, 400))
        self.enhanced_image_display.configure(image=self.enhanced_image)

    def update_images(self, img):
        self.original_image = ctk.CTkImage(Image.open(img), size=(400, 400))
        self.original_image_display.configure(image=self.original_image)

        self.enhanced_image = ctk.CTkImage(Image.open(img), size=(400, 400))
        self.enhanced_image_display.configure(image=self.enhanced_image)

    def save_image(self):
        enhanced_image = self.apply_enhancements()
        file_path = ctk.filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            with open("img_path.txt", "w") as file:
                file.write(file_path)

            enhanced_image.save(file_path)

    def build(self):
        root = ctk.CTk()
        root.title(self._title)
        root.minsize(self.min_width, self.min_height)

        image_frame = ctk.CTkFrame(root)

        # I really hate how adding widgets is implemented in CTk.
        # Is there a way to build my own?

        # Open by defalt the last one, add "Open new image" button
        original_frame = ctk.CTkFrame(image_frame)
        original_image = ctk.CTkImage(self.img, size=(400, 400))
        original_image_label = ctk.CTkLabel(
            original_frame, text="Original Image:", anchor="n"
        )

        self.original_image_display = ctk.CTkLabel(
            original_frame, text="", image=original_image
        )

        open_new_image_button = ctk.CTkButton(
            original_frame,
            text="Open new image...",
            command=lambda: self.update_images(self.processor.open_image()),
        )

        enhanced_frame = ctk.CTkFrame(image_frame)
        self.enhanced_image = ctk.CTkImage(self.img, size=(400, 400))
        enhanced_image_label = ctk.CTkLabel(
            enhanced_frame, text="Enhanced Image:", anchor="n"
        )

        self.enhanced_image_display = ctk.CTkLabel(
            enhanced_frame, text="", image=self.enhanced_image
        )

        contrast_label = ctk.CTkLabel(enhanced_frame, text="Contrast: ")
        contrast_slider = ctk.CTkSlider(
            enhanced_frame,
            from_=int(self.enhancements["contrast"]),
            to=100,
            command=lambda x: self.change_enhancement("contrast", x),
        )

        brightness_label = ctk.CTkLabel(enhanced_frame, text="Brightness: ")
        brightness_slider = ctk.CTkSlider(
            enhanced_frame,
            from_=int(self.enhancements["brightness"]),
            to=100,
            command=lambda x: self.change_enhancement("brightness", x),
        )

        sharpness_label = ctk.CTkLabel(enhanced_frame, text="Sharpness: ")
        sharpness_slider = ctk.CTkSlider(
            enhanced_frame,
            from_=int(self.enhancements["sharpness"]),
            to=100,
            command=lambda x: self.change_enhancement("sharpness", x),
        )

        saturation_label = ctk.CTkLabel(enhanced_frame, text="Saturation: ")
        saturation_slider = ctk.CTkSlider(
            enhanced_frame,
            from_=int(self.enhancements["saturation"]),
            to=100,
            command=lambda x: self.change_enhancement("saturation", x),
        )

        save_button = ctk.CTkButton(
            enhanced_frame, text="Save image as...", command=self.save_image
        )

        def pack_widgets():
            image_frame.pack(pady=10, fill="both", expand=True)
            original_frame.pack(side="left", padx=10, fill="both", expand=True)

            original_image_label.pack()

            self.original_image_display.pack()

            open_new_image_button.pack()

            enhanced_frame.pack(side="left", padx=10, fill="both", expand=True)
            enhanced_image_label.pack()

            self.enhanced_image_display.pack()

            contrast_label.pack()
            contrast_slider.pack()

            brightness_label.pack()
            brightness_slider.pack()

            sharpness_label.pack()
            sharpness_slider.pack()

            saturation_label.pack()
            saturation_slider.pack()

            save_button.pack()

        pack_widgets()
        self.update_displayed_image(self.img)
        root.mainloop()


app = ImageEditor(title="Py Image Editor")
