from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os
import random
from typing import Optional, Dict, Any

class BackgroundError(Exception):
    """Custom exception untuk error terkait background"""
    pass

    
class QuoteGeneratorGUI:
    def _validate_resources(self):
        """Validate required resources"""
        resource_dir = Path("resource")
        required_files = {
            "watermark": resource_dir / "Img-3.png",
            "font": resource_dir / "PlusJakartaSans-SemiBold.ttf"
        }

        missing_files = []
        for name, path in required_files.items():
            if not path.exists():
                missing_files.append(str(path))

        if missing_files:
            messagebox.showerror(
                "Error",
                f"Resource files missing:\n{', '.join(missing_files)}\n"
                f"Please ensure the 'resource' folder contains all required files."
            )
            raise FileNotFoundError("Required resource files are missing.")
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Quote Generator")
        self.root.geometry("1200x800")

        # Validasi resource sebelum melanjutkan
        self._validate_resources()
        
        # State variables
        self.current_background: Optional[Image.Image] = None
        self.background_preview: Optional[ImageTk.PhotoImage] = None
        self.selected_color = tk.StringVar(value="white")
        self.config: Dict[str, Any] = {}
        
        self._setup_styles()
        self._create_main_layout()
        self._load_config()
        
    def _setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.configure('Preview.TFrame', background='#2b2b2b')
        style.configure('Controls.TFrame', background='#f0f0f0')
        style.configure('Path.TFrame', padding="5 5 5 5")
        
    def _create_main_layout(self):
        """Create main application layout"""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (Preview)
        preview_frame = ttk.Frame(main_container, style='Preview.TFrame')
        main_container.add(preview_frame, weight=2)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(padx=10, pady=10, expand=True)
        
        # Right panel (Controls)
        controls_frame = ttk.Frame(main_container, style='Controls.TFrame')
        main_container.add(controls_frame, weight=1)
        
        self._create_controls(controls_frame)
        
    def _create_controls(self, parent: ttk.Frame):
        """Create control widgets"""
        # Background selection
        ttk.Label(parent, text="Background Selection").pack(pady=(10,5))
        
        # Path input frame
        path_frame = ttk.Frame(parent, style='Path.TFrame')
        path_frame.pack(fill=tk.X, padx=10)
        
        # Path entry
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        ttk.Button(
            path_frame,
            text="Browse",
            command=self._browse_file
        ).pack(side=tk.LEFT, padx=(5,0))
        
        # Random button
        ttk.Button(
            path_frame,
            text="Random",
            command=self._load_random_background
        ).pack(side=tk.LEFT, padx=(5,0))
        
        # Example paths
        example_frame = ttk.Frame(parent)
        example_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            example_frame,
            text="Contoh format path yang didukung:",
            font=('TkDefaultFont', 9, 'bold')
        ).pack(anchor='w')
        
        examples = [
            f"- Nama file saja: background.jpg",
            f"- Path relatif: {os.path.join('folder', 'subfolder', 'background.jpg')}"
        ]
        
        if os.name == 'nt':  # Windows
            examples.append(f"- Path absolut: C:{os.path.join(os.sep, 'Users', 'Pictures', 'background.jpg')}")
        else:  # Unix-like
            examples.append(f"- Path absolut: {os.path.join(os.sep, 'home', 'user', 'Pictures', 'background.jpg')}")
            
        for example in examples:
            ttk.Label(
                example_frame,
                text=example,
                wraplength=350,
                font=('TkDefaultFont', 8)
            ).pack(anchor='w')
        
        # Text input
        ttk.Label(parent, text="Quote Text").pack(pady=(20,5))
        self.text_inputs = tk.Text(parent, wrap=tk.WORD, height=5)  # Wrap text dan atur tinggi
        self.text_inputs.pack(fill=tk.X, padx=10, pady=5)
        
        self._create_color_controls(parent)
        self._create_action_buttons(parent)
        
    def _create_color_controls(self, parent):
        """Create color selection controls"""
        ttk.Label(parent, text="Text Color").pack(pady=(20,5))
        color_frame = ttk.Frame(parent)
        color_frame.pack(fill=tk.X, padx=10)
    
    # def _create_color_controls(self, parent):
    #     """Create color selection controls"""
    #     ttk.Label(parent, text="Text Color").pack(pady=(20, 5))

        # Tombol untuk memilih warna
        self.selected_color = "#FFFFFF"  # Default: putih
        ttk.Button(
            parent,
            text="Choose Text Color",
            command=self._choose_color
        ).pack(pady=5)    
     
    def _choose_color(self):
        """Open color chooser dialog and set selected color"""
        color = tk.colorchooser.askcolor(title="Choose Text Color")
        if color[1]:  # color[1] adalah kode hex warna yang dipilih
            self.selected_color = color[1]
                
        
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(
            btn_frame,
            text="Preview",
            command=self._preview_quote
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Save",
            command=self._save_quote
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Clear",
            command=self._clear_form
        ).pack(side=tk.LEFT, padx=5)

    def _load_config(self):
        """Load application configuration"""
        config_path = Path("config.json")
        
        # Default config
        default_config = {
            "backgrounds_dir": str(Path("backgrounds")),
            "output_dir": str(Path("Quotes")),
            "font_size": 40,
            "font_family": str(Path("resource/PlusJakartaSans-SemiBold.ttf"))
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                # Create config file if it doesn't exist
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                    
            # Create output directory if it doesn't exist
            Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading config: {str(e)}")
            self.config = default_config
    
    def _update_preview(self):
        """Update preview image with current background and quote"""
        if not self.current_background:
            return
            
        # Create a copy of the background for preview
        preview = self.current_background.copy()
        
        # Resize to fit preview area while maintaining aspect ratio
        preview.thumbnail((800, 600))
        
        # Convert to PhotoImage for display
        self.background_preview = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.background_preview)
    
    def _split_text_into_lines(self, text: str, max_chars: int = 48) -> list[str]:
        """Split text into lines with a maximum character limit per line."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:

        # Jika menambahkan kata berikutnya melebihi batas karakter
            if len(current_line) + len(word) + 1 > max_chars:
                lines.append(current_line.strip())  # Simpan baris saat ini
                current_line = word  # Mulai baris baru dengan kata saat ini
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        # Tambahkan baris terakhir jika ada
        if current_line:
            lines.append(current_line.strip())

        return lines


    # def _calculate_text_position(self, image_width: int, image_height: int, num_lines: int, font_size: int):
    #     """
    #     Hitung posisi teks secara dinamis berdasarkan ukuran gambra dan jumlah baris kata
    #     """

    #     # Padding dari pinggir gambar (dalam persentase)
    #     padding_x_percent = 0.103 # 10% dari lebar gambar
    #     padding_y_percent = 2.00 # 10% dari tinggi gambar

    #     # Hitung Padding dalam pixel
    #     padding_x = int(image_width * padding_x_percent)
    #     padding_y = int(image_height * padding_y_percent)

    #     # print(f"padding_x: {padding_x}, padding_y: {padding_y}")  # Debugging

    #     # Posisi X (horizontal): padding dari kiri
    #     x = padding_x

    #     # Posisi Y (vertikal): tengah gambar secara vertikal
    #     total_text_height = num_lines * (font_size + 10) # Font size + jarak antar baris
    #     y_start = 990 # (image_height - total_text_height) // 2

    #     # Jarak antar baris
    #     line_height = font_size + 10 # font size + 10 pixel

    #     # print(f"line_height: {line_height}, num_lines: {num_lines}")  # Debugging
    #     return x, y_start, line_height
    
    
    def _preview_quote(self):
        """Preview quote on background"""
        if not self.current_background:
            messagebox.showwarning("Warning", "Please select a background image first")
            return

        # Cek keberadaan Watermark
        watermark_path = Path("resource/Img-3.png")  
        if not watermark_path.exists():
            messagebox.showwarning("Warning", "Watermark file not found in 'resource' folder.")
            return
        
        # Create a copy of the background
        preview = self.current_background.copy()

        # Add Watermark ti preview
        watermark = Image.open(watermark_path).convert("RGBA")
        preview.paste(watermark, watermark) 
        
        # Get quote text dari tk.Text
        quote_text = self.text_inputs.get("1.0", tk.END).strip()  # Ambil semua teks dari text widget
        
        if not quote_text:
            messagebox.showwarning("Warning", "Please enter some text for the quote")
            return
            
        # Create preview with quote text
        # Note: This is a simplified version. You might want to add more text styling options
        # from PIL import ImageDraw, ImageFont
        
        # Bagi teks menjadi baris-baris dengan maksimal 48 karakter per baris
        quote_lines = self._split_text_into_lines(quote_text, max_chars=48)

        # Draw text on the Image
        draw = ImageDraw.Draw(preview)
        # font = ImageFont.truetype(self.config["font_family"], self.config["font_size"])
        font = ImageFont.truetype(str(Path("resource/PlusJakartaSans-SemiBold.ttf")), self.config ["font_size"])

        # Posisi Statis
        x_start = 90
        y_start = 990
        line_height = 51
              
        # Draw each line
        y = y_start # Gunakan y_start sebagai posisi Y awal
        for line in quote_lines:
            draw.text((x_start, y), line, font=font, fill=self.selected_color)
            y += line_height # Update posisi Y untuk baris berikutnya
        
        # Update preview
        preview.thumbnail((800, 600))
        self.background_preview = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.background_preview)
        
    def _save_quote(self):
        """Save quote image"""
        if not self.current_background:
            messagebox.showwarning("Warning", "Please select a background image first")
            return
            
                # Get quote text
        quote_text = self.text_inputs.get("1.0", tk.END).strip()
        
        if not quote_text:
            messagebox.showwarning("Warning", "Please enter some text for the quote")
            return
            
        # Create final image
        final = self.current_background.copy()

        # Add watermark
        watermark_path = Path("resource/Img-3.png")
        if watermark_path.exists():
            watermark = Image.open(watermark_path).convert("RGBA")
            final.paste (watermark, watermark)

        # Bagi teks menjadi baris-baris dengan maksimal 48 karakter per baris
        quote_lines = self._split_text_into_lines(quote_text, max_chars=48)
        
        # Add quote text
        draw = ImageDraw.Draw(final)
        font = ImageFont.truetype(self.config["font_family"], self.config["font_size"])
        
        # Bagi teks menjadi baris-baris dengan maksimal 48 karakter per baris
        quote_lines = self._split_text_into_lines(quote_text, max_chars=48)

        # Draw text on the Image
        draw = ImageDraw.Draw(final)
        # font = ImageFont.truetype(self.config["font_family"], self.config["font_size"])
        font = ImageFont.truetype(str(Path("resource/PlusJakartaSans-SemiBold.ttf")), self.config ["font_size"])

        # Posisi Statis
        x_start = 100
        y_start = 990
        line_height = 51
              
        # Draw each line
        y = y_start # Gunakan y_start sebagai posisi Y awal
        for line in quote_lines:
            draw.text((x_start, y), line, font=font, fill=self.selected_color)
            y += line_height # Update posisi Y untuk baris berikutnya
        
        # Save dialog
        file_path = filedialog.asksaveasfilename(
            initialdir=self.config["output_dir"],
            title="Save Quote Image",
            defaultextension=".png",
            filetypes=[("JPG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                final.save(file_path)
                messagebox.showinfo("Success", "Quote image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving image: {str(e)}")
                
    def _clear_form(self):
        """Clear all form inputs"""
        self.path_var.set("")
        self.text_inputs.delete("1.0", tk.END) # Hapus semua teks dari teks widget 
        self.selected_color = "#FFFFFF"   # Reset ke warna default
        self.current_background = None
        self.preview_label.configure(image="")
        
    def _browse_file(self):
        """Open file browser dialog"""
        filetypes = [
            ('Image files', '*.jpg;*.jpeg;*.png'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes,
            initialdir=self.config["backgrounds_dir"]
        )
        
        if filename:
            self.path_var.set(filename)
            self._load_background_from_path(filename)
            
    def _normalize_path(self, input_path: str) -> Path:
        """Normalize input path"""
        base_path = Path(self.config["backgrounds_dir"]).resolve()
        
        # Normalize slashes
        normalized_input = input_path.replace('\\', '/')
        path = Path(normalized_input)
        
        # If relative, combine with base path
        if not path.is_absolute():
            path = base_path / path
            
        return path.resolve()
        
    def _load_background_from_path(self, path_str: str):
        """Load background from given path"""
        try:
            file_path = self._normalize_path(path_str)
            
            # Check extension
            if file_path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                raise BackgroundError("Format file tidak didukung. Gunakan file .jpg, .jpeg, atau .png")
                
            # Try to load image
            self.current_background = Image.open(file_path)
            self._update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _load_random_background(self):
        """Load random background from default directory"""
        base_path = Path(self.config["backgrounds_dir"]).resolve()
        
        # Get all image files
        valid_files = []
        for ext in ('.jpg', '.jpeg', '.png'):
            valid_files.extend(base_path.glob(f'*{ext}'))
            
        if not valid_files:
            messagebox.showwarning(
                "Warning",
                f"Tidak ada file gambar di folder {self.config['backgrounds_dir']}"
            )
            return
            
        # Choose random file
        file_path = random.choice(valid_files)
        self.path_var.set(str(file_path))
        self._load_background_from_path(str(file_path))

def main():
    root = tk.Tk()
    app = QuoteGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()