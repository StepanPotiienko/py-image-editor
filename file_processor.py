import customtkinter as ctk
from PIL import Image


class FileProcessor:
    def open_image(self):
        file_path = ctk.filedialog.askopenfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            return file_path

    def save_image(self, img: Image.Image):
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

                img.save(file_path)
