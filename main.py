import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import time
from collections import deque

class FrequencyBarsApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        root.geometry("800x600")
        
        self.num_bars = 200
        self.max_amplitude = 300
        self.amplitude_step = 15 

        self.current_amplitude = 0
        self.target_amplitude = 0
        self.is_mouse_down = False  # Track mouse state

        self.running = True
        self.last_frame_time = time.time()
        self.frame_duration = 1/120  # Target 120 FPS
        
        # Movement speed
        self.movement_speed = 2  # Pixels per frame
        
        # Decay parameters
        self.decay_rate = 0.95  # Rate at which bars decay (0.95 = 5% reduction per frame)
        self.min_height = 0  # Minimum height before bar disappears

        self.width = root.winfo_width() 
        self.height = root.winfo_height()

        # Store bars as (x, height) pairs
        self.bars = []
        
        # Pre-calculate random data
        self.random_data = np.random.rand(1000)
        self.random_index = 0

        self.calculate_bar_dimensions()

        # Cache rectangle objects
        self.bar_objects = []
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Optimize resize handling
        self.resize_after_id = None
        self.root.bind("<Configure>", self.on_resize)
        
        # Pre-create background
        self.create_rounded_window()
        
        self.animate()

    def calculate_bar_dimensions(self):
        self.bar_spacing = 1  # Reduced spacing for better performance
        total_width = self.width * 0.8
        self.bar_width = (total_width / self.num_bars) - self.bar_spacing
        self.x_offset = (self.width - total_width) / 2

    def on_resize(self, event):
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        if event.width != self.width or event.height != self.height:
            self.resize_after_id = self.root.after(100, lambda: self.handle_resize(event))

    def handle_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.calculate_bar_dimensions()
        self.create_rounded_window()
        self.bars.clear()

    def create_rounded_window(self):
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        corner_radius = min(50, self.width//20)
        draw.rounded_rectangle([(0, 0), (self.width, self.height)], radius=corner_radius, fill=(0, 0, 0))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def on_mouse_down(self, event):
        self.is_mouse_down = True
        self.target_amplitude = self.max_amplitude

    def on_mouse_up(self, event):
        self.is_mouse_down = False
        self.target_amplitude = 0

    def update_amplitude(self):
        if self.current_amplitude < self.target_amplitude:
            self.current_amplitude += self.amplitude_step
        else:
            self.current_amplitude -= self.amplitude_step
        self.current_amplitude = max(0, min(self.current_amplitude, self.target_amplitude))

    def get_audio_data(self):
        if self.random_index >= len(self.random_data):
            self.random_index = 0
        data = self.random_data[self.random_index:self.random_index + 1]
        self.random_index += 1
        return data * 100

    def update_bars(self):
        # Apply decay to existing bars
        self.bars = [(x - self.movement_speed, max(h * self.decay_rate, self.min_height)) 
                    for x, h in self.bars]
        
        # Remove bars that are off screen or below minimum height
        self.bars = [bar for bar in self.bars if bar[0] > -self.bar_width and bar[1] > self.min_height]
        
        # Add new bar at the right
        new_magnitude = self.get_audio_data()[0]
        max_value = max(new_magnitude, 1)
        
        # Scale the height based on current amplitude
        bar_height = int((new_magnitude / max_value) * self.current_amplitude)
        
        # If mouse is not down, create small bars that will decay
        if not self.is_mouse_down:
            bar_height = min(bar_height, 20)  # Limit height when mouse is up
            
        # Add new bar at the right edge
        self.bars.append((self.width - self.x_offset, bar_height))

    def draw_bars(self):
        self.canvas.delete("bars")
        
        for x, height in self.bars:
            y0 = (self.height // 2) - (height // 2)
            x1 = x + self.bar_width
            y1 = (self.height // 2) + (height // 2)
            
            self.canvas.create_rectangle(
                x + self.x_offset, y0,
                x1 + self.x_offset, y1,
                fill="white", outline="white",
                tags="bars"
            )

    def animate(self):
        if not self.running:
            return

        current_time = time.time()
        
        self.update_amplitude()
        self.update_bars()
        self.draw_bars()
        
        # Calculate precise frame timing
        frame_end_time = time.time()
        elapsed = frame_end_time - current_time
        wait_time = max(1, int((self.frame_duration - elapsed) * 1000))
        
        self.root.after(1, self.animate)

    def close(self):
        self.running = False

# Create the Tkinter window
root = tk.Tk()
root.title("Frequency Visualizer")
root.minsize(400, 300)

app = FrequencyBarsApp(root)
root.protocol("WM_DELETE_WINDOW", lambda: (app.close(), root.destroy()))

try:
    icon_image = Image.open("get-out970.jpg")
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, icon_photo)
except:
    pass

root.mainloop()

