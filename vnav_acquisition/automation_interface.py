import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from automation_playwright import run_automation
from vnav_acquisition.config import config
import subprocess
import threading
import time
import requests
import os
import sys
import signal

webserver_process = None  
root = None  

def get_flask_port():
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            port = f.read().strip()
            return port
    else:
        raise Exception("Flask port file not found.")

def start_webserver():
    """Webserver'ın açık olup olmadığını kontrol et ve kapalıysa başlat"""
    global webserver_process  
    
    flask_port = get_flask_port()

    try:
        response = requests.get(f"http://localhost:{flask_port}")
        if response.status_code == 200:
            print(f"Webserver zaten çalışıyor (Port: {flask_port})")
            return None
    except requests.ConnectionError:
        pass 

    print(f"Webserver {flask_port} portunda başlatılıyor...")

    try:
        if webserver_process and webserver_process.poll() is None:
            print("Eski Webserver süreci çalışıyor, kapatılıyor...")
            webserver_process.terminate()
            webserver_process.wait()
            print("Eski Webserver kapandı.")

        if os.name == "nt":  # for Windows
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:  # if Linux/Mac 
            creation_flags = 0

        webserver_process = subprocess.Popen(
            ["python", "webserver.py"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=creation_flags
        )

        # wait for the webserver to start
        time.sleep(3)

        return webserver_process
    except Exception as e:
        print(f"Webserver başlatılamadı! Hata: {e}")
        return None
    
def on_closing():
    """GUI kapatıldığında webserver'ı da kapat"""
    global webserver_process, root  # use global variables

    if webserver_process:
        print("Webserver kapanıyor...")
        try:
            webserver_process.terminate()  # terminate the webserver process
            webserver_process.wait()  # wait for the process to finish
            print("Webserver kapandı.")
        except Exception as e:
            print(f"Webserver kapatma hatası: {e}")

    if root is not None:
        print("GUI kapanıyor...")
        root.quit()  
        root.destroy()  
        print("GUI kapandı.")


def create_gui():
    global root  # make root global to access it in on_closing

    setup_json_path = r'C:\Users\ucunb\OneDrive\Masaüstü\acquisition-master2\setup.json'
    config.load_from_json(setup_json_path)
    
    # Start the webserver when the GUI is created
    start_webserver()
    
    def update_positions_visibility(event):
        selected_option = position_type_var.get()
        if selected_option == "Only Up and Down":
            p2_label.grid_forget()
            p2_x_entry.grid_forget()
            p2_y_entry.grid_forget()
            p2_z_entry.grid_forget()
        elif selected_option == "Up, Down, Forward":
            p2_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')
            p2_x_entry.grid(row=5, column=1, padx=10, pady=10)
            p2_y_entry.grid(row=5, column=2, padx=10, pady=10)
            p2_z_entry.grid(row=5, column=3, padx=10, pady=10)
        root.update_idletasks()
        root.geometry("")

    def change_theme(theme):
        root.set_theme(theme)
        root.update_idletasks()
        
    def update_speed_label(event=None):
        selected_index = speed_combobox.current()
        if selected_index == 0:
            speed_label.config(text="Speed: 10", foreground="red")
        elif selected_index == 1:
            speed_label.config(text="Speed: 15", foreground="red")
        elif selected_index == 2:
            speed_label.config(text="Speed: 25", foreground="red")

    """async def show_camera_feed():
        reader = imageio.get_reader('<video0>', 'ffmpeg')
        while True:
            frame = reader.get_next_data()
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_canvas.create_image(0, 0, anchor='nw', image=imgtk)
            camera_canvas.imgtk = imgtk  # Keep a reference to avoid garbage collection
            await asyncio.sleep(0.03)  # Add a small delay to reduce CPU usage

    def start_camera_feed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(show_camera_feed())"""

    root = ThemedTk()
    root.title("Berke - Acquisition Tool Vibronav Automation Setup")
    root.configure(background='#f0f0f0')
    
    # Set the size of the window 
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    pil_image = Image.open("Vibronav-256px.png")
    width, height = pil_image.size
    background_image = ImageTk.PhotoImage(pil_image)

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.create_image(0, 0, anchor='nw', image=background_image)
    canvas.grid(row=0, column=10, rowspan=10, columnspan=4, sticky="ne")

    style = ttk.Style()
    style.theme_use('plastik')

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    theme_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Themes", menu=theme_menu)

    themes = root.get_themes()
    for theme in themes:
        theme_menu.add_command(label=theme, command=partial(change_theme, theme))

    username_label = ttk.Label(root, text="Username:", font=('Helvetica', 12))
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    username_var = tk.StringVar()
    username_entry = ttk.Entry(root, textvariable=username_var, width=30, font=('Helvetica', 12))
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    material_label = ttk.Label(root, text="Material:", font=('Helvetica', 12))
    material_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    material_var = tk.StringVar()
    material_combobox = ttk.Combobox(root, textvariable=material_var, values=config["materials"], state="readonly", font=('Helvetica', 12))
    material_combobox.grid(row=1, column=1, padx=10, pady=10)
    material_combobox.current(0)
    

    speed_label = ttk.Label(root, text="Speed:", font=('Helvetica', 12))
    speed_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    speed_var = tk.StringVar()
    speed_combobox = ttk.Combobox(root, textvariable=speed_var, values=config["speeds"], state="readonly", font=('Helvetica', 12))
    speed_combobox.grid(row=2, column=1, padx=10, pady=10)
    speed_combobox.current(0)
    speed_combobox.bind("<<ComboboxSelected>>", update_speed_label)
    
    update_speed_label()

    position_type_label = ttk.Label(root, text="Position Type:", font=('Helvetica', 12))
    position_type_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
    position_type_var = tk.StringVar(value="Only Up and Down")
    position_type_combobox = ttk.Combobox(root, textvariable=position_type_var, values=["Only Up and Down", "Up, Down, Forward"], state="readonly", font=('Helvetica', 12))
    position_type_combobox.grid(row=3, column=1, padx=10, pady=10)
    position_type_combobox.bind("<<ComboboxSelected>>", update_positions_visibility)

    p1_label = ttk.Label(root, text="P1 Position (X, Y, Z):", font=('Helvetica', 12))
    p1_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')
    
    p1_x_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p1_x_entry.grid(row=4, column=1, padx=10, pady=10)
    p1_x_entry.insert(0, "300")  # Default value for X (P1)

    p1_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p1_y_entry.grid(row=4, column=2, padx=10, pady=10)
    p1_y_entry.insert(0, "0")  # Default value for Y (P1)

    p1_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p1_z_entry.grid(row=4, column=3, padx=10, pady=10)
    p1_z_entry.insert(0, "-20")  # Default value for Z (P1)

    p2_label = ttk.Label(root, text="P2 Position (X, Y, Z):", font=('Helvetica', 12))
    p2_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')
    p2_x_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_x_entry.grid(row=5, column=1, padx=10, pady=10)
    p2_x_entry.insert(0, "300")  # Default value for X (P2)

    p2_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_y_entry.grid(row=5, column=2, padx=10, pady=10)
    p2_y_entry.insert(0, "0")  # Default value for Y (P2)

    p2_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_z_entry.grid(row=5, column=3, padx=10, pady=10)
    p2_z_entry.insert(0, "-20")  # Default value for Z (P2)

    p3_label = ttk.Label(root, text="P3 Position (X, Y, Z):", font=('Helvetica', 12))
    p3_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')
    p3_x_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_x_entry.grid(row=6, column=1, padx=10, pady=10)
    p3_x_entry.insert(0, "300")  # Default value for X (P3)

    p3_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_y_entry.grid(row=6, column=2, padx=10, pady=10)
    p3_y_entry.insert(0, "0")  # Default value for Y (P3)

    p3_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_z_entry.grid(row=6, column=3, padx=10, pady=10)
    p3_z_entry.insert(0, "-90")  # Default value for Z (P3)
    
    # Add label and entry for number of iterations
    iterations_label = ttk.Label(root, text="Number of Iterations:", font=('Helvetica', 12))
    iterations_label.grid(row=7, column=0, padx=10, pady=10, sticky='w')
    iterations_var = tk.StringVar(value="22")  # Default value
    iterations_entry = ttk.Entry(root, textvariable=iterations_var, width=10, font=('Helvetica', 12))
    iterations_entry.grid(row=7, column=1, padx=10, pady=10)
    
    def on_submit():
        username = username_var.get()
        material = material_var.get()
        speed = speed_var.get()
        position_type = position_type_var.get()
        p1 = (float(p1_x_entry.get()), float(p1_y_entry.get()), float(p1_z_entry.get()), 0)  # sending in correct format
        p2 = (float(p2_x_entry.get()), float(p2_y_entry.get()), float(p2_z_entry.get()), 0) if position_type == "Up, Down, Forward" else (0, 0, 0, 0)
        p3 = (float(p3_x_entry.get()), float(p3_y_entry.get()), float(p3_z_entry.get()), 0)  # sending in correct format
        
        num_iterations = int(iterations_var.get())  # Get the number of iterations from the entry

        run_automation(username, material, speed, position_type, p1, p2, p3, num_iterations)

    submit_button = ttk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=11, column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
