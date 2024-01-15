import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import keyboard 

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autoclicker Avançado")

        # Estilizando a interface
        style = ttk.Style()
        style.theme_use('clam')  # Escolha um tema adequado, como 'clam', 'alt', 'default', ou outro

        # Configurações da interface
        config_frame = ttk.Frame(root)
        config_frame.pack(padx=10, pady=10)

        ttk.Label(config_frame, text="Número de Cliques:").grid(row=0, column=0, sticky="w")
        self.clicks_entry = ttk.Entry(config_frame, width=10)
        self.clicks_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(config_frame, text="Intervalo (segundos):").grid(row=1, column=0, sticky="w")
        self.interval_entry = ttk.Entry(config_frame, width=10)
        self.interval_entry.insert(0, "0.1")
        self.interval_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(config_frame, text="Botão do Mouse:").grid(row=2, column=0, sticky="w")
        self.mouse_button_var = tk.StringVar(root)
        self.mouse_button_var.set("left")
        ttk.OptionMenu(config_frame, self.mouse_button_var, "left", "right").grid(row=2, column=1, sticky="w")

        self.position_label = ttk.Label(config_frame, text="Nenhuma posição definida")
        self.position_label.grid(row=3, column=0, columnspan=2)

        self.positions = []

        ttk.Button(config_frame, text="Definir Posição", command=self.set_click_position).grid(row=4, column=0, columnspan=2)

        self.add_position_button = ttk.Button(config_frame, text="Adicionar Novo Local de Clique", command=self.set_click_position)
        self.add_position_button.grid(row=5, column=0, columnspan=2)
        self.add_position_button['state'] = tk.DISABLED

        self.start_button = ttk.Button(config_frame, text="Iniciar Cliques", command=self.start_clicker)
        self.start_button.grid(row=6, column=0, columnspan=2)

        self.stop_button = ttk.Button(config_frame, text="Parar Cliques", command=self.stop_clicker)
        self.stop_button.grid(row=7, column=0, columnspan=2)
        self.stop_button['state'] = tk.DISABLED

        # Lista para mostrar as posições
        self.positions_listbox = tk.Listbox(config_frame, height=6)
        self.positions_listbox.grid(row=8, column=0, columnspan=2)

        # Checkbox para ignorar o limite de cliques
        self.ignore_limit_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Ignorar limite de cliques", variable=self.ignore_limit_var).grid(row=9, column=0, columnspan=2, sticky="w")
            # Checkbox para usar imagem de referência
        self.use_reference_image_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Usar imagem de referência", variable=self.use_reference_image_var).grid(row=10, column=0, columnspan=2, sticky="w")

        # Botão Redefinir
        self.reset_button = ttk.Button(config_frame, text="Redefinir", command=self.reset_all)
        self.reset_button.grid(row=11, column=0, columnspan=2)

        self.running = False
        self.click_thread = None

    def validate_number(self, P):
        return str.isdigit(P) or P == ""

    def set_click_position(self):
        # A transparent fullscreen window to capture the click position
        position_window = tk.Toplevel(self.root)
        position_window.attributes("-alpha", 0.3)  # Semi-transparency
        position_window.attributes("-fullscreen", True) # Fullscreen overlay
        position_window.wait_visibility()
        position_window.bind('<Button-1>', self.capture_click_position)
        position_window.bind('<Escape>', lambda e: position_window.destroy())

    def capture_click_position(self, event):
        position_window = event.widget
        self.positions.append((event.x_root, event.y_root))
        self.position_label.config(text=f"Posições definidas: {len(self.positions)}")
        position_window.destroy()  # Close the transparent window after selection
        self.update_positions_listbox()
        self.add_position_button['state'] = tk.NORMAL

    def start_clicker(self):
        if not self.running:
            self.running = True
            self.click_thread = threading.Thread(target=self.auto_clicker)
            self.click_thread.start()
            self.update_ui_state()

    def stop_clicker(self):
        self.running = False
        self.update_ui_state()
        
    def setup_keyboard_listeners(self):
        keyboard.add_hotkey('F9', self.start_clicker_from_keyboard)
        keyboard.add_hotkey('F10', self.stop_clicker_from_keyboard)

    def start_clicker_from_keyboard(self):
        if not self.running:
            self.root.after(0, self.start_clicker)  # Chama a função start_clicker na thread da GUI

    def stop_clicker_from_keyboard(self):
        if self.running:
            self.root.after(0, self.stop_clicker)  # Chama a função stop_clicker na thread da GUI

    def update_ui_state(self):
        if self.running:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL
            self.add_position_button['state'] = tk.DISABLED
        else:
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.add_position_button['state'] = tk.NORMAL

    def reset_all(self):
        self.stop_clicker()

        # Limpar a lista de posições e a interface
        self.positions.clear()
        self.positions_listbox.delete(0, tk.END)
        self.position_label.config(text="Nenhuma posição definida")

        # Resetar os campos de entrada
        self.clicks_entry.delete(0, tk.END)
        self.interval_entry.delete(0, tk.END)
        self.interval_entry.insert(0, "0.1")

        # Resetar as checkboxes
        self.ignore_limit_var.set(False)
        self.use_reference_image_var.set(False)

        # Atualizar o estado da UI
        self.update_ui_state()

    def update_positions_listbox(self):
        self.positions_listbox.delete(0, tk.END)
        for idx, pos in enumerate(self.positions):
            self.positions_listbox.insert(idx, f"{idx+1}: ({pos[0]}, {pos[1]})")

    def auto_clicker(self):
        interval = float(self.interval_entry.get())
        button = self.mouse_button_var.get()
        queue_message_path = "caminho_para_a_imagem_da_mensagem.png"  # Substitua com o caminho correto da sua imagem
        confidence_level = 0.6  # A
        while self.running:
            if self.use_reference_image_var.get():
                try:
                    if pyautogui.locateOnScreen(queue_message_path, confidence=confidence_level):
                        print("Mensagem de fila detectada, parando autoclicker.")
                        self.stop_clicker()
                        break
                except pyautogui.ImageNotFoundException:
                    pass  # Imagem não encontrada, continue o autoclicker

            for pos in self.positions:
                pyautogui.click(x=pos[0], y=pos[1], button=button)
                if not self.ignore_limit_var.get():
                    pyautogui.sleep(interval)

            # Se o checkbox de ignorar limite estiver marcado, continua indefinidamente
            if self.ignore_limit_var.get():
                continue
            else:
                break

        self.running = False
        self.update_ui_state()
        
root = tk.Tk()
app = AutoClickerApp(root)
app.setup_keyboard_listeners() 
root.mainloop()