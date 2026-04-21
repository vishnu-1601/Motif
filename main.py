import customtkinter as ctk
from PIL import Image
import os
import time
from pygame import mixer
from mutagen.mp3 import MP3
from tkinter import filedialog

# Set the theme
ctk.set_appearance_mode("Dark")

class MotifPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Get the absolute path to the directory where main.py is located
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        # Link to the assets folder
        self.assets_path = os.path.join(self.base_path, "assets")

        # ENGINE SETUP
        self.is_paused = False
        self.filename = None
        mixer.init()

        # Window Setup
        self.title("Motif")
        self.geometry("1100x750") # Slightly taller for better proportions
        self.configure(fg_color="#0F0F0F") 

        # GRID LAYOUT
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR SETUP
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#161616")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MOTIF", 
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color="#1DB954")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        self.create_nav_button("🏠  Home", 1)
        self.create_nav_button("🔍  Search", 2)
        self.create_nav_button("📚  Library", 3)
        self.create_nav_button("🎵  Playlists", 4)

        self.open_btn = ctk.CTkButton(self.sidebar_frame, text="📁 Choose File", 
                                      fg_color="#2A2A2A", hover_color="#333333",
                                      corner_radius=8, height=40,
                                      command=self.choose_music) 
        self.open_btn.grid(row=5, column=0, padx=20, pady=(30, 10))

        # 2. MAIN CONTENT AREA
        self.main_content = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(self.main_content, placeholder_text="Search for music...",
                                         width=400, height=35, fg_color="#1A1A1A", border_width=0)
        self.search_entry.pack(anchor="w", pady=(0, 20))

        self.section_label = ctk.CTkLabel(self.main_content, text="Recently Played", 
                                          font=ctk.CTkFont(size=22, weight="bold"))
        self.section_label.pack(anchor="w", pady=(10, 20))

        self.album_grid = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.album_grid.pack(fill="both", expand=True)

        album_data = [
            ("Stardust Echoes", "Luna Wave"), ("Midnight Drive", "SYNTHWAVE"),
            ("Santlina", "SYNTHWAVE"), ("Sterneal Drive", "Stellara"),
            ("Stardua Droes", "SYNTHWAVE"), ("Merrisy Drive", "SYNTHWAVE"),
            ("Manight Drive", "SYNTHWAVE"), ("Porany Soums", "Stellara")
        ]

        for i, (title, artist) in enumerate(album_data):
            row, col = divmod(i, 4) 
            self.create_album_card(self.album_grid, title, artist, row, col)

        # 3. SLIM GLASS PLAYER BAR
        self.player_bar = ctk.CTkFrame(self, height=90, # Reduced height for a sleeker look
                                       fg_color="#121212", # Darker hex to blend better (lower opacity look)
                                       corner_radius=0, 
                                       border_width=1, 
                                       border_color="#1F1F1F") # Very subtle border
        self.player_bar.place(relx=0, rely=1, relwidth=1, anchor="sw")

        # LEFT Side
        self.song_info_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.song_info_frame.pack(side="left", padx=30, pady=10)

        self.now_playing_title = ctk.CTkLabel(self.song_info_frame, text="No Song Selected", 
                                              font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        self.now_playing_title.pack(anchor="w")

        self.now_playing_artist = ctk.CTkLabel(self.song_info_frame, text="Select a file", 
                                               font=ctk.CTkFont(size=11), text_color="#777777", anchor="w")
        self.now_playing_artist.pack(anchor="w")

        # CENTER Side (Spacing)
        self.controls_master = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.controls_master.pack(expand=True, fill="both", pady=5)

        self.btns_frame = ctk.CTkFrame(self.controls_master, fg_color="transparent")
        self.btns_frame.pack(pady=(5, 0))

        icons = ["🔀", "⏮", "▶", "⏭", "🔁"]
        for i, icon in enumerate(icons):
            is_main = icon == "▶"
            btn = ctk.CTkButton(self.btns_frame, text=icon, width=35 if not is_main else 45,
                                height=35 if not is_main else 45, corner_radius=22,
                                fg_color="white" if is_main else "transparent",
                                text_color="black" if is_main else "white",
                                hover_color="#EEEEEE" if is_main else "#242424",
                                font=ctk.CTkFont(size=16 if not is_main else 20))
            btn.grid(row=0, column=i, padx=8)
            if is_main:
                self.play_btn = btn
                self.play_btn.configure(command=self.toggle_playback)

        self.progress_container = ctk.CTkFrame(self.controls_master, fg_color="transparent")
        self.progress_container.pack(fill="x", padx=200, pady=(0, 5))

        self.start_time = ctk.CTkLabel(self.progress_container, text="0:00", font=("Arial", 10), text_color="#777777")
        self.start_time.pack(side="left", padx=5)

        self.main_slider = ctk.CTkSlider(self.progress_container, from_=0, to=100, height=12, 
                                         progress_color="#1DB954", button_color="#FFFFFF", button_length=12)
        self.main_slider.set(0)
        self.main_slider.pack(side="left", expand=True, fill="x")

        self.end_time = ctk.CTkLabel(self.progress_container, text="0:00", font=("Arial", 10), text_color="#777777")
        self.end_time.pack(side="left", padx=5)

        # RIGHT Side (Volume)
        self.volume_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.volume_frame.pack(side="right", padx=30, pady=(0, 10))

        self.vol_slider = ctk.CTkSlider(self.volume_frame, from_=0, to=1, width=80, height=12,
                                        progress_color="#1DB954", command=self.set_volume)
        self.vol_slider.set(0.7)
        self.vol_slider.pack(side="left")

    # LOGIC METHODS
    def choose_music(self):
        file_path = filedialog.askopenfilename(filetypes=[("Music Files", "*.mp3")])
        if file_path:
            self.filename = file_path
            self.now_playing_title.configure(text=os.path.basename(file_path))
            self.now_playing_artist.configure(text="Local File")
            
            mixer.music.load(self.filename)
            mixer.music.play()
            
            self.play_btn.configure(text="⏸")
            self.is_paused = False
            
            audio = MP3(self.filename)
            self.song_length = audio.info.length
            self.end_time.configure(text=time.strftime('%M:%S', time.gmtime(self.song_length)))
            self.main_slider.configure(to=self.song_length)
            
            self.update_progress()

    def toggle_playback(self):
        if not self.filename: return
        if self.is_paused:
            mixer.music.unpause()
            self.play_btn.configure(text="⏸")
            self.is_paused = False
        else:
            mixer.music.pause()
            self.play_btn.configure(text="▶")
            self.is_paused = True

    def update_progress(self):
        if mixer.music.get_busy() and not self.is_paused:
            current_pos = mixer.music.get_pos() / 1000
            self.main_slider.set(current_pos)
            self.start_time.configure(text=time.strftime('%M:%S', time.gmtime(current_pos)))
        self.after(1000, self.update_progress)

    def set_volume(self, val):
        mixer.music.set_volume(float(val))

    def create_album_card(self, master, title, artist, row, col):
        card = ctk.CTkFrame(master, fg_color="#1E1E1E", corner_radius=15, width=190, height=260)
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False)
        # LOAD IMAGE FROM ASSETS
        img_path = os.path.join(self.assets_path, "3m.jpg")
        try:
            # Using CTkImage is the modern way to handle images in CustomTkinter
            cover_img = ctk.CTkImage(light_image=Image.open(img_path),
                                     dark_image=Image.open(img_path),
                                     size=(170, 170))
            art_placeholder = ctk.CTkLabel(card, text="", image=cover_img, corner_radius=10)
        except Exception as e:
            # Fallback if image is missing
            art_placeholder = ctk.CTkLabel(card, text="🎵", font=("Arial", 50), 
                                           fg_color="#2A2A2A", width=170, height=170, corner_radius=10)
        art_placeholder.pack(pady=10, padx=10)

    def create_nav_button(self, text, row_index):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, anchor="w", fg_color="transparent", 
                            text_color="#AAAAAA", hover_color="#222222")
        btn.grid(row=row_index, column=0, padx=20, pady=5, sticky="ew")

if __name__ == "__main__":
    app = MotifPro()
    app.mainloop()