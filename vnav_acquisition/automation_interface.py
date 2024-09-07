import tkinter as tk
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from automation_playwright import run_automation
from vnav_acquisition.config import config

def create_gui():
    setup_json_path = r'C:\Users\ucunb\OneDrive\Masaüstü\Vibronav\acquisition-master\setup.json'
    config.load_from_json(setup_json_path)
    
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

    root = ThemedTk()
    root.title("Berke - Acquisition Tool Vibronav Automation Setup")
    root.configure(background='#f0f0f0')
    
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
    p1_x_entry.insert(0, "350")  # Varsayılan değer X için

    p1_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p1_y_entry.grid(row=4, column=2, padx=10, pady=10)
    p1_y_entry.insert(0, "0")  # Varsayılan değer Y için

    p1_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p1_z_entry.grid(row=4, column=3, padx=10, pady=10)
    p1_z_entry.insert(0, "40")  # Varsayılan değer Z için (P1)

    p2_label = ttk.Label(root, text="P2 Position (X, Y, Z):", font=('Helvetica', 12))
    p2_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')
    p2_x_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_x_entry.grid(row=5, column=1, padx=10, pady=10)
    p2_x_entry.insert(0, "350")  # Varsayılan değer X için

    p2_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_y_entry.grid(row=5, column=2, padx=10, pady=10)
    p2_y_entry.insert(0, "0")  # Varsayılan değer Y için

    p2_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p2_z_entry.grid(row=5, column=3, padx=10, pady=10)
    p2_z_entry.insert(0, "0")  # Varsayılan değer Z için (P2)

    p3_label = ttk.Label(root, text="P3 Position (X, Y, Z):", font=('Helvetica', 12))
    p3_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')
    p3_x_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_x_entry.grid(row=6, column=1, padx=10, pady=10)
    p3_x_entry.insert(0, "350")  # Varsayılan değer X için

    p3_y_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_y_entry.grid(row=6, column=2, padx=10, pady=10)
    p3_y_entry.insert(0, "0")  # Varsayılan değer Y için

    p3_z_entry = ttk.Entry(root, width=10, font=('Helvetica', 12))
    p3_z_entry.grid(row=6, column=3, padx=10, pady=10)
    p3_z_entry.insert(0, "-20")  # Varsayılan değer Z için (P3)

    def on_submit():
        username = username_var.get()
        material = material_var.get()
        speed = speed_var.get()
        position_type = position_type_var.get()
        p1 = (float(p1_x_entry.get()), float(p1_y_entry.get()), float(p1_z_entry.get()), 0)  # Doğru formatta gönderiyoruz
        p2 = (float(p2_x_entry.get()), float(p2_y_entry.get()), float(p2_z_entry.get()), 0) if position_type == "Up, Down, Forward" else (0, 0, 0, 0)
        p3 = (float(p3_x_entry.get()), float(p3_y_entry.get()), float(p3_z_entry.get()), 0)  # Doğru formatta gönderiyoruz

        run_automation(username, material, speed, position_type, p1, p2, p3)

    submit_button = ttk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=7, column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
