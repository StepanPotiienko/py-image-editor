import os
from tkinter import messagebox, DoubleVar
import customtkinter as ctk
from PIL import Image, ImageEnhance
import tempfile
import logging
import image_processor


class ImageEditor:
    processor = image_processor.ImageProcessor()

    def __init__(self, title: str, geometry: list = []):
        self.min_width = 1280
        self.min_height = 720
        self._title = title
        self._geometry = geometry or [self.min_width, self.min_height]

        self.img = None
        self.temp_image_file = None
        self.enhanced_image = None

        try:
            self.temp_image_file = tempfile.NamedTemporaryFile(
                prefix="py_image_editor_", suffix=".png", delete=False
            )

            if (
                os.path.exists(self.temp_image_file.name)
                and os.path.getsize(self.temp_image_file.name) > 0
            ):
                self.img = Image.open(self.temp_image_file.name)
            else:
                logging.info("No image found in temporary storage.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.img = None

        self.original_image = self.img.copy() if self.img else None
        self.preview_image = self.img.copy().resize((400, 400)) if self.img else None
        self.enhancements = {
            "contrast": 1,
            "brightness": 1,
            "sharpness": 1,
            "saturation": 1,
        }

        self.update_timer = None
        self.build()

    def apply_enhancements(self, image):
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
        if self.preview_image:
            enhanced_preview = self.apply_enhancements(self.preview_image)
            self.update_displayed_image(enhanced_preview)

    def update_displayed_image(self, img):
        if img:
            window_width = self.root.winfo_width() or self.min_width
            window_height = self.root.winfo_height() or self.min_height

            target_width = window_width // 2
            target_height = window_height // 2

            img_ratio = img.width / img.height
            window_ratio = target_width / target_height

            if img_ratio > window_ratio:
                new_width = target_width
                new_height = int(target_width / img_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * img_ratio)

            resized_image = img.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            self.enhanced_image = ctk.CTkImage(
                resized_image, size=(new_width, new_height)
            )
            self.enhanced_image_display.configure(image=self.enhanced_image, text="")

    def open_new_image(self):
        try:
            image_path = self.processor.open_image()
            if image_path:
                self.img = Image.open(image_path)

                self.img.save(self.temp_image_file.name, format="PNG")

                self.original_image = self.img.copy()
                self.preview_image = self.img.copy()
                self.update_displayed_image(self.preview_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")

    def build(self):
        self.root = ctk.CTk()
        self.root.title(self._title)
        self.root.minsize(self.min_width, self.min_height)

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        image_frame = ctk.CTkFrame(self.root)
        self.controls_frame = ctk.CTkFrame(self.root, fg_color="transparent")

        image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.controls_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        self.controls_frame.grid_propagate(False)
        self.controls_frame.grid_rowconfigure(tuple(range(10)), weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.enhanced_image_display = ctk.CTkLabel(
            image_frame,
            text="No Image Loaded" if not self.img else "",
            image=self.enhanced_image if self.enhanced_image else None,
        )
        self.enhanced_image_display.pack(expand=True, fill="both")

        open_new_image_button = ctk.CTkButton(
            self.controls_frame,
            text="Open new image...",
            command=self.open_new_image,
        )
        save_button = ctk.CTkButton(
            self.controls_frame,
            text="Save image as...",
            command=lambda: self.handle_save_image(),
        )

        sliders = [
            ("Contrast", "contrast"),
            ("Brightness", "brightness"),
            ("Sharpness", "sharpness"),
            ("Saturation", "saturation"),
        ]

        self.slider_vars = {
            name: DoubleVar(value=self.enhancements[enh] * 100) for name, enh in sliders
        }
        self.sliders = {}

        for idx, (label_text, enhancement) in enumerate(sliders):
            ctk.CTkLabel(self.controls_frame, text=f"{label_text}:").grid(
                row=idx, column=0, padx=0, pady=0
            )

            slider = ctk.CTkSlider(
                self.controls_frame,
                from_=0,
                to=100,
                variable=self.slider_vars[label_text],
                command=lambda value, enh=enhancement: self.change_enhancement(
                    enh, value
                ),
            )
            slider.grid(row=idx, column=1, padx=0, pady=0, sticky="ew")
            self.sliders[enhancement] = slider

        open_new_image_button.grid(row=len(sliders), column=0, columnspan=2, pady=0)
        save_button.grid(row=len(sliders) + 1, column=0, columnspan=2, pady=0)

        self.root.bind("<Up>", lambda e: self.adjust_enhancement("brightness", 5))
        self.root.bind("<Down>", lambda e: self.adjust_enhancement("brightness", -5))
        self.root.bind("<Right>", lambda e: self.adjust_enhancement("contrast", 5))
        self.root.bind("<Left>", lambda e: self.adjust_enhancement("contrast", -5))
        self.root.bind("w", lambda e: self.adjust_enhancement("sharpness", 5))
        self.root.bind("s", lambda e: self.adjust_enhancement("sharpness", -5))
        self.root.bind("d", lambda e: self.adjust_enhancement("saturation", 5))
        self.root.bind("a", lambda e: self.adjust_enhancement("saturation", -5))

        self.root.mainloop()

    def adjust_enhancement(self, enhancement, step):
        new_value = self.enhancements[enhancement] * 100 + step
        new_value = max(0, min(new_value, 100))

        self.enhancements[enhancement] = new_value / 100
        self.slider_vars[enhancement.capitalize()].set(new_value)

        self.update_preview()


app = ImageEditor(title="Py Image Editor")
