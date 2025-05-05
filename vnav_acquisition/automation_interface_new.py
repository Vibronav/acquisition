import os
import sys
import subprocess
import threading
import time
import requests
from PIL import Image
import customtkinter as ctk
from automation_playwright import run_automation
from vnav_acquisition.config import config

# Global variables
webserver_process = None

# Configuration
SETUP_JSON_PATH = r'C:\Users\ucunb\OneDrive\Masaüstü\acquisition-master2\setup.json'
IMAGE_PATH = "Vibronav-256px.png"  # Background or logo image

def get_flask_port():
    port_file = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file):
        with open(port_file, 'r') as f:
            return f.read().strip()
    raise FileNotFoundError("Flask port file not found.")

def start_webserver():
    global webserver_process
    port = get_flask_port()
    try:
        requests.get(f"http://localhost:{port}")
        return
    except requests.ConnectionError:
        pass

    
    if webserver_process and webserver_process.poll() is None:
        webserver_process.terminate()
        webserver_process.wait()

    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    webserver_process = subprocess.Popen(
        [sys.executable, 'webserver.py'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=flags
    )
    
    time.sleep(3)

def stop_webserver():
    global webserver_process
    if webserver_process and webserver_process.poll() is None:
        webserver_process.terminate()
        webserver_process.wait()

class AcquisitionGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Acquisition Tool - Vibronav Automation")
        self.geometry("900x475")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Load config
        config.load_from_json(SETUP_JSON_PATH)

        # Start webserver in background
        threading.Thread(target=start_webserver, daemon=True).start()

        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Input frame
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Background/logo image
        if os.path.exists(IMAGE_PATH):
            pil_img = Image.open(IMAGE_PATH)
            self.bg_image = ctk.CTkImage(pil_img, size=(300,300))
            ctk.CTkLabel(
                self.main_frame,
                image=self.bg_image,
                text=""
            ).grid(row=0, column=1, sticky="ne", padx=(10,0), pady=(10,0))

        # Build inputs
        self._create_inputs()

    def _create_inputs(self):
        i = 0
        # Username
        ctk.CTkLabel(self.input_frame, text="Username:").grid(row=i, column=0, sticky="w", pady=5)
        self.username_var = ctk.StringVar()
        ctk.CTkEntry(self.input_frame, textvariable=self.username_var, width=300).grid(row=i, column=1, pady=5)
        i += 1

        # Material
        ctk.CTkLabel(self.input_frame, text="Material:").grid(row=i, column=0, sticky="w", pady=5)
        self.material_var = ctk.StringVar(value=config["materials"][0])
        ctk.CTkOptionMenu(
            self.input_frame,
            values=config["materials"],
            variable=self.material_var
        ).grid(row=i, column=1, pady=5)
        i += 1

        # Speed
        ctk.CTkLabel(self.input_frame, text="Speed:").grid(row=i, column=0, sticky="w", pady=5)
        self.speed_var = ctk.StringVar(value=config["speeds"][0])
        ctk.CTkOptionMenu(
            self.input_frame,
            values=config["speeds"],
            variable=self.speed_var
        ).grid(row=i, column=1, pady=5)
        i += 1

        # Position Type
        ctk.CTkLabel(self.input_frame, text="Position Type:").grid(row=i, column=0, sticky="w", pady=5)
        self.position_type_var = ctk.StringVar(value="Only Up and Down")
        ctk.CTkOptionMenu(
            self.input_frame,
            values=["Only Up and Down", "Up, Down, Forward"],
            variable=self.position_type_var,
            command=self._toggle_p2_inputs
        ).grid(row=i, column=1, pady=5)
        i += 1

        # P1, P2, P3 rows
        self.p1_entries = self._position_row(i, "P1 Position (X,Y,Z):", (300, 0, -20)); i += 1
        self.p2_entries = self._position_row(i, "P2 Position (X,Y,Z):", (300, 0, -20)); i += 1
        self.p3_entries = self._position_row(i, "P3 Position (X,Y,Z):", (300, 0, -90)); i += 1

        # Iterations
        ctk.CTkLabel(self.input_frame, text="Iterations:").grid(row=i, column=0, sticky="w", pady=5)
        self.iter_var = ctk.StringVar(value="22")
        ctk.CTkEntry(self.input_frame, textvariable=self.iter_var).grid(row=i, column=1, pady=5)
        i += 1

        # App Theme
        ctk.CTkLabel(self.input_frame, text="App Theme:").grid(row=i, column=0, sticky="w", pady=5)
        ctk.CTkOptionMenu(
            self.input_frame,
            values=["light", "dark", "system"],
            command=ctk.set_appearance_mode
        ).grid(row=i, column=1, pady=5)
        i += 1

        # Submit button
        submit_btn = ctk.CTkButton(
            self.input_frame,
            text="Submit",
            command=self._on_submit,
            width=200,
            height=30
        )
        submit_btn.grid(row=i, column=0, columnspan=2, pady=20)

        # Disable P2 row initially
        self._toggle_p2_inputs(self.position_type_var.get())

    def _position_row(self, row, label, defaults):
        ctk.CTkLabel(self.input_frame, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entries = []
        for j, val in enumerate(defaults):
            sv = ctk.StringVar(value=str(val))
            ent = ctk.CTkEntry(self.input_frame, textvariable=sv, width=60)
            ent.grid(row=row, column=1+j, padx=2, pady=5)
            entries.append(ent)
        return entries

    def _toggle_p2_inputs(self, choice):
        disabled = (choice == "Only Up and Down")
        for ent in self.p2_entries:
            ent.configure(
                state="disabled" if disabled else "normal",
                fg_color="#6c6c6c" if disabled else ctk.ThemeManager.theme["CTkEntry"]["fg_color"]
            )

    def _on_submit(self):
        user   = self.username_var.get()
        mat    = self.material_var.get()
        spd    = self.speed_var.get()
        ptype  = self.position_type_var.get()

        # Build 4-element tuples (x, y, z, orientation=0)
        p1_vals = [float(ent.get()) for ent in self.p1_entries]
        p1 = (*p1_vals, 0)

        if ptype == "Up, Down, Forward":
            p2_vals = [float(ent.get()) for ent in self.p2_entries]
            p2 = (*p2_vals, 0)
        else:
            p2 = (0, 0, 0, 0)

        p3_vals = [float(ent.get()) for ent in self.p3_entries]
        p3 = (*p3_vals, 0)

        iters = int(self.iter_var.get())

        run_automation(user, mat, spd, ptype, p1, p2, p3, iters)

    def on_closing(self):
        stop_webserver()
        self.destroy()

if __name__ == '__main__':
    app = AcquisitionGUI()
    app.mainloop()
