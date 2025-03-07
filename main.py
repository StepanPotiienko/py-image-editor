import os
from tkinter import messagebox, DoubleVar
import customtkinter as ctk
from PIL import Image, ImageEnhance
import tempfile
import dotenv

# TODO: #6 Add background eraser tool when they update it to Python 3.13 >:(
# import rembg

from logger import Logger
from file_processor import FileProcessor


class ImageEditor:
    processor = FileProcessor()
    logger = Logger()

    def __init__(self, title: str, geometry: list = []):
        self._min_width = 1280
        self._min_height = 720
        self._title = title
        self._geometry = geometry or [self._min_width, self._min_height]

        self.root = ctk.CTk()
        self.root.title(self._title)

        dotenv.load_dotenv()
        icon_path = os.environ.get("ICON_PATH")

        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            self.logger.info("Set application's icon.")
        else:
            self.logger.error(f"Icon file not found at: {icon_path}")

        self.root.minsize(self._min_width, self._min_height)

        self.logger.info("Building process initalizing...")

        self.img = None
        self.last_edited_file = os.path.join(
            tempfile.gettempdir(), "last_edited_image.png"
        )
        self.enhanced_image = None

        try:
            self.logger.info("Searching for last edited picture...")

            if (
                os.path.exists(self.last_edited_file)
                and os.path.getsize(self.last_edited_file) > 0
            ):
                self.img = Image.open(self.last_edited_file)
                self.logger.info(
                    f"Opened last edited image from {self.last_edited_file}."
                )
            else:
                self.logger.info("No image found in temporary storage.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.logger.error(f"Failed to load image: {str(e)}")
            self.img = None

        self.original_image = self.img.copy() if self.img else None
        self.preview_image = (
            self.img.copy().resize((400, int(400 * self.img.height / self.img.width)))
            if self.img and self.img.width > self.img.height
            else (
                self.img.copy().resize(
                    (int(400 * self.img.width / self.img.height), 400)
                )
                if self.img
                else None
            )
        )

        self.enhancements = {
            "contrast": 1,
            "brightness": 1,
            "sharpness": 1,
            "saturation": 1,
        }

        self.update_timer = None
        self.build()

    def open_new_image(self):
        try:
            image_path = self.processor.open_image()
            if image_path:
                self.img = Image.open(image_path)
                self.logger.info("Opened new image.")

                self.img.save(self.last_edited_file, format="PNG")

                self.original_image = self.img.copy()
                self.preview_image = self.img.copy()
                self.fit_preview(self.preview_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
            self.logger.error(f"Failed to open image: {str(e)}")

    def handle_save_image(self):
        try:
            save_path = self.processor.save_image()
            if save_path and self.enhanced_image:
                enhanced_full_image = self.apply_enhancements(self.original_image)
                enhanced_full_image.save(save_path, format="PNG")
                self.logger.info(f"Image saved to {save_path}.")

                enhanced_full_image.save(self.last_edited_file, format="PNG")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            self.logger.error(f"Failed to save image: {str(e)}")

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

    def open_new_image(self):
        try:
            image_path = self.processor.open_image()
            if image_path:
                self.img = Image.open(image_path)
                self.logger.info("Opened new image.")

                self.img.save(self.last_edited_file, format="PNG")

                self.original_image = self.img.copy()
                self.preview_image = self.img.copy()
                self.fit_preview(self.preview_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
            self.logger.error(f"Failed to open image: {str(e)}")

    def handle_save_image(self):
        try:
            save_path = self.processor.save_image()
            if save_path and self.enhanced_image:
                enhanced_full_image = self.apply_enhancements(self.original_image)
                enhanced_full_image.save(save_path, format="PNG")
                self.logger.info(f"Image saved to {save_path}.")

                enhanced_full_image.save(self.last_edited_file, format="PNG")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            self.logger.error(f"Failed to save image: {str(e)}")
            return False

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
        return True

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
            self.fit_preview(enhanced_preview)

    def fit_preview(self, img):
        self.root.after(100, lambda: self.fit_preview(self.preview_image))

        if img:
            image_frame_width = self.root.winfo_width() // 2
            image_frame_height = self.root.winfo_height()

            image_frame_width = max(image_frame_width, 400)
            image_frame_height = max(image_frame_height, 400)

            img_ratio = img.width / img.height
            frame_ratio = image_frame_width / image_frame_height

            if img_ratio > frame_ratio:
                new_width = image_frame_width
                new_height = int(new_width / img_ratio)
            else:
                new_height = image_frame_height
                new_width = int(new_height * img_ratio)

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
                self.logger.info("Opened new image.")

                self.img.save(self.last_edited_file, format="PNG")

                self.original_image = self.img.copy()
                self.preview_image = self.img.copy()
                self.fit_preview(self.preview_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
            self.logger.error(f"Failed to open image: {str(e)}")

    def build(self):
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.logger.info("Finished building root.")

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
            command=self.handle_save_image,
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
        self.logger.info("Finished building widgets.")

        self.root.bind("<Up>", lambda e: self.adjust_enhancement("brightness", 5))
        self.root.bind("<Down>", lambda e: self.adjust_enhancement("brightness", -5))
        self.root.bind("<Right>", lambda e: self.adjust_enhancement("contrast", 5))
        self.root.bind("<Left>", lambda e: self.adjust_enhancement("contrast", -5))
        self.root.bind("w", lambda e: self.adjust_enhancement("sharpness", 5))
        self.root.bind("s", lambda e: self.adjust_enhancement("sharpness", -5))
        self.root.bind("d", lambda e: self.adjust_enhancement("saturation", 5))
        self.root.bind("a", lambda e: self.adjust_enhancement("saturation", -5))

        self.logger.info("Finished adding key binds.")

        if self.preview_image:
            self.fit_preview(self.preview_image)

        self.root.mainloop()

    def adjust_enhancement(self, enhancement, step):
        new_value = self.enhancements[enhancement] * 100 + step
        new_value = max(0, min(new_value, 100))

        self.enhancements[enhancement] = new_value / 100
        self.slider_vars[enhancement.capitalize()].set(new_value)

        self.update_preview()


if __name__ == "__main__":
    app_title: str = "CatCut"
    app = ImageEditor(title=app_title)
