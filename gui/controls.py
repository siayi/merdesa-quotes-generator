import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path

class Controls:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        # Background selection
        ttk.Label(parent, text="Background Selection").pack(pady=(10, 5))

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
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Random button
        ttk.Button(
            path_frame,
            text="Random",
            command=self._load_random_background
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Text input
        ttk.Label(parent, text="Quote Text").pack(pady=(20, 5))
        self.text_input = tk.Text(parent, wrap=tk.WORD, height=5)
        self.text_input.pack(fill=tk.X, padx=10, pady=5)

        # Color selection
        ttk.Label(parent, text="Text Color").pack(pady=(20, 5))
        self.selected_color = "#FFFFFF"  # Default: putih
        ttk.Button(
            parent,
            text="Choose Text Color",
            command=self._choose_color
        ).pack(pady=5)

        # Action buttons
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

    def _browse_file(self):
        """Open file browser dialog"""
        filetypes = [
            ('Image files', '*.jpg;*.jpeg;*.png'),
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=filetypes,
            initialdir=self.main_window.config["backgrounds_dir"]
        )

        if filename:
            self.path_var.set(filename)
            self.main_window.image_processor.load_background(filename)

    def _load_random_background(self):
        """Load random background from default directory"""
        # Implementasi sesuai kebutuhan
        pass

    def _choose_color(self):
        """Open color chooser dialog and set selected color"""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:  # color[1] adalah kode hex warna yang dipilih
            self.selected_color = color[1]

    def _preview_quote(self):
        """Preview quote on background"""
        quote_text = self.text_input.get("1.0", tk.END).strip()
        if not quote_text:
            messagebox.showwarning("Warning", "Please enter some text for the quote")
            return

        # Process image with quote
        self.main_window.image_processor.add_text(quote_text, self.selected_color)
        preview_image = self.main_window.image_processor.get_preview()
        self.main_window.preview_label.configure(image=preview_image)
        self.main_window.preview_label.image = preview_image

    def _save_quote(self):
        """Save quote image"""
        quote_text = self.text_input.get("1.0", tk.END).strip()
        if not quote_text:
            messagebox.showwarning("Warning", "Please enter some text for the quote")
            return

        # Save dialog
        file_path = filedialog.asksaveasfilename(
            initialdir=self.main_window.config["output_dir"],
            title="Save Quote Image",
            defaultextension=".png",
            filetypes=[("JPG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.main_window.image_processor.save_image(file_path)
                messagebox.showinfo("Success", "Quote image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving image: {str(e)}")

    def _clear_form(self):
        """Clear all form inputs"""
        self.path_var.set("")
        self.text_input.delete("1.0", tk.END)
        self.selected_color = "#FFFFFF"
        self.main_window.preview_label.configure(image="")