import os.path
from tkinter import messagebox, DoubleVar
import customtkinter as ctk
from PIL import Image, ImageEnhance
import image_processor


class ImageEditor:
    processor = image_processor.ImageProcessor()

    def __init__(self, title: str, geometry: list = []):
        self.min_width = 1280
        self.min_height = 720
        self._title = title
        self._geometry = geometry or [self.min_width, self.min_height]

        try:
            # TODO: #2 Is there a way to save path to the latest image more efficiently?
            if os.path.exists("img_path.txt"):
                with open("img_path.txt", "r") as file:
                    image_path = file.readline().strip()
            else:
                image_path = self.processor.open_image()

            if image_path:
                self.img = Image.open(image_path)

                with open("img_path.txt", "w") as file:
                    file.write(image_path)

        except Exception as e:
            messagebox.showerror("An error occurred.", str(e))
            self.img = None

        self.original_image = self.img.copy() if self.img else None
        self.preview_image = self.img.copy().resize((400, 400)) if self.img else None
        self.enhancements = {
            "contrast": 1,
            "brightness": 1,
            "sharpness": 1,
            "saturation": 1,
        }

        self.update_timer = None  # Timer for throttling slider updates
        self.build()

    def apply_enhancements(self, image):
        """Apply all enhancements to a given image."""
        enhanced_image = image.copy()
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
        self.enhancements[enhancement] = round(float(value) / 100, 2)

        if self.update_timer:
            self.root.after_cancel(self.update_timer)

        self.update_timer = self.root.after(100, self.update_preview)

    def update_preview(self):
        enhanced_preview = self.apply_enhancements(self.preview_image)
        self.update_displayed_image(enhanced_preview)

    def update_displayed_image(self, img):
        self.enhanced_image = ctk.CTkImage(img, size=(400, 400))
        self.enhanced_image_display.configure(image=self.enhanced_image)

    def build(self):
        self.root = ctk.CTk()
        self.root.title(self._title)
        self.root.minsize(self.min_width, self.min_height)

        image_frame = ctk.CTkFrame(self.root)

        enhanced_frame = ctk.CTkFrame(
            image_frame,
            width=self.original_image.width,
            height=self.original_image.height,
        )
        self.enhanced_image = ctk.CTkImage(self.img, size=(400, 400))

        self.enhanced_image_display = ctk.CTkLabel(
            enhanced_frame,
            text="",
            image=self.enhanced_image,
        )

        open_new_image_button = ctk.CTkButton(
            enhanced_frame,
            text="Open new image...",
            command=lambda: self.processor.open_image,
        )

        sliders = [
            ("Contrast", "contrast"),
            ("Brightness", "brightness"),
            ("Sharpness", "sharpness"),
            ("Saturation", "saturation"),
        ]

        variables = {
            name: DoubleVar(value=self.enhancements[enh] * 100) for name, enh in sliders
        }

        def bind_slider_and_entry(slider, entry, variable, enhancement):
            def slider_callback(value):
                variable.set(float(value))
                self.change_enhancement(enhancement, value)

            def entry_callback(*args):
                try:
                    value = float(variable.get())
                    slider.set(value)
                    self.change_enhancement(enhancement, value)
                except ValueError:
                    pass

            variable.trace_add("write", entry_callback)
            slider.configure(command=slider_callback)
            slider.set(variable.get())
            entry.configure(textvariable=variable)

        controls_frame = ctk.CTkFrame(enhanced_frame)
        for idx, (label_text, enhancement) in enumerate(sliders):
            label = ctk.CTkLabel(controls_frame, text=f"{label_text}:")
            entry = ctk.CTkEntry(controls_frame, width=50)
            slider = ctk.CTkSlider(controls_frame, from_=0, to=100)
            bind_slider_and_entry(slider, entry, variables[label_text], enhancement)

            label.grid(row=idx, column=0, padx=5, pady=5)
            slider.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
            entry.grid(row=idx, column=2, padx=5, pady=5)

        save_button = ctk.CTkButton(
            enhanced_frame, text="Save image as...", command=self.processor.save_image
        )

        def pack_widgets():
            image_frame.pack(pady=10, fill="both", expand=True)

            enhanced_frame.pack(side="left", padx=10, fill="both", expand=True)
            self.enhanced_image_display.pack()

            controls_frame.pack(fill="x", padx=10, pady=10)
            save_button.pack(pady=10)
            # TODO: #1 New image does not open.
            open_new_image_button.pack()

        pack_widgets()
        self.root.mainloop()


app = ImageEditor(title="Py Image Editor")
