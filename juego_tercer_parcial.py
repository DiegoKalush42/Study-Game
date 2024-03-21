import tkinter as tk
from tkinter import messagebox
import random
import pandas as pd
import os
import sys
import pygame



class StudyGame:
    def __init__(self, master, excel_path):
        self.master = master
        self.master.title("Juego de Estudio - Elige tu parcial")
        self.excel_path = excel_path
        pygame.init()
        self.start_game()
    
    def start_game(self):
        self.setup_initial_screen()

    def setup_initial_screen(self):
        # Limpia la ventana principal
        for widget in self.master.winfo_children():
            widget.destroy()

    # Obtén las dimensiones de la ventana
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        # Configura la ventana para que coincida con el tamaño de la pantalla
        self.master.geometry(f"{width}x{height}")

        # Configura la imagen de fondo
        self.master.update()  # Actualiza la ventana principal para obtener sus dimensiones
        background_image = tk.PhotoImage(file=resource_path("kemointo.png"))
        background_label = tk.Label(self.master, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = background_image
            # Crea botones para elegir el parcial
        style = {'padx': 10, 'pady': 5, 'bd': 4, 'font': ('Arial', 12, 'bold')}
        btn_first_partial = tk.Button(self.master, text="Primer Parcial",
                                      command=lambda: self.load_game("datos_derecho_1.xlsx"),
                                      **style)
        btn_first_partial.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        btn_second_partial = tk.Button(self.master, text="Tercer Parcial",
                                       command=lambda: self.load_game("datos_derecho_2.xlsx"),
                                       **style)
        btn_second_partial.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Crea botón para iniciar/detener la música
        btn_music = tk.Button(self.master, text="Reproducir/Pausar Música",
                              command=self.toggle_music, **style)
        btn_music.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        

        self.music_paused = False
        self.play_music(resource_path('AtLast.mp3')) 

        btn_instructions = tk.Button(self.master, text="Instrucciones",
                             command=self.show_instructions, **style)
        btn_instructions.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    def toggle_music(self):
        if self.music_paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.music_paused = not self.music_paused

    def play_music(self, music_file):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)

    def show_instructions(self):
        instructions_text = ("Seleccionar los botones en el siguiente orden:\n\n"
                         "Término: Azul claro\n"
                         "Definición: Rosa\n"
                         "Ejemplo: Blanco")
        messagebox.showinfo("Instrucciones", instructions_text)

    def load_game(self, excel_file):
        # Configura la ruta del archivo Excel basada en la elección del usuario
        self.excel_path = resource_path(excel_file)
        # Inicia el juego con el archivo Excel seleccionado
        self.initialize_game(self.master, self.excel_path)

    def initialize_game(self, master, excel_path):
        # Configura la ventana y carga los datos
        master.state('zoomed')  # Pantalla completa
        self.data = self.load_data_from_excel(excel_path)
        # Configuraciones de paginación
        self.cards_per_page = 8  # 8 tríos
        self.current_page = 0
        self.total_pages = len(self.data) // self.cards_per_page
        self.setup_game()

        
    def load_data_from_excel(self, path):
            df = pd.read_excel(path)
            return df.to_dict(orient='records')
    
    def setup_game(self):
        # limpiar si hay botones
        for widget in self.master.winfo_children():
            widget.destroy()

        #Agarramos un subset de datos para la página actual
        start = self.current_page * self.cards_per_page
        end = start + self.cards_per_page
        page_data = self.data[start:end]

        # Mezcalmos los datos para esta página
        mixed_cards = []
        for item in page_data:
            mixed_cards.extend([(item["term"], "term"), (item["definition"], "definition"), (item["example"], "example")])
        random.shuffle(mixed_cards)

        # El estaod del juego
        self.selected_cards = []
        self.correct_count = 0

        # Creamos los botoens para termino, deinición y ejemplo
        self.buttons = []
        rows = 8
        columns = 3
        button_width = 20
        wrap_length = 290
        colors = {
                "term": "lightblue",
                "definition": "pink",
                "example": "white"
            }

        for i, (text, card_type) in enumerate(mixed_cards):
                btn = tk.Button(self.master, text=text,
                                command=lambda i=i, text=text, card_type=card_type: self.select_card(i, text, card_type),
                                font=("Arial", 10), 
                                bg=colors[card_type],  #dependiedo que tipo es, le damos ese color 
                                fg="black",
                                padx=10, pady=5, width=button_width, wraplength=wrap_length)
                btn.grid(row=i // columns, column=i % columns, sticky="nsew", padx=5, pady=5)
                self.buttons.append(btn)

        # Configure grid for even distribution
        for i in range(rows):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(columns):
            self.master.grid_columnconfigure(i, weight=1)

    def disable_matched_buttons(self):
        for index, _, _ in self.selected_cards:
            self.buttons[index].config(state="disabled")
        self.correct_count += 1

        # checa si todos los triós han sido elegidos
        trios_per_page = self.cards_per_page *3 // 3
        if self.correct_count == trios_per_page:
            messagebox.showinfo("Excelente", "Moviendo a el siguiente set...")
            self.current_page += 1
            self.correct_count = 0  # Se reinicia la cuenta para la sigueitne página
            if self.current_page < self.total_pages:
                self.setup_game()  # enseña la siguiente págian
            else:
                messagebox.showinfo("Juego terminado", "Felicidades, completaste el juego!, Tienes todo para sobresalir!")
                self.end_game()  #nos lleva a la pantalla de inicio


    def check_match(self):
        selected_types = [card_type for _, _, card_type in self.selected_cards]
        selected_texts = [text for _, text, _ in self.selected_cards]

        # Checar si estpa en el orden correcto
        if selected_types == ["term", "definition", "example"]:
            # Calcular los indices del  incio y el final  para la ppagina actual 
            start = self.current_page * self.cards_per_page
            end = start + self.cards_per_page

            # cehcar si todas las seleccioens perteneces al mimso término 
            term_matched = any(
                selected_texts[0] == item['term'] and
                selected_texts[1] == item['definition'] and
                selected_texts[2] == item['example']
                for item in self.data[start:end]  # Checar contra la pagina actual de datos
            )
            if term_matched:
                messagebox.showinfo("Correcto!", "Match correcto!")
                self.disable_matched_buttons()
            else:
                messagebox.showinfo("Incorrecto", "Vuelve a intentar!")
                self.reset_selected_buttons()
                self.print_correct_pairs()
        else:
            messagebox.showinfo("Incorrecto", "Selecciona en el orden: Término, Definición, Ejemplo.")
            self.reset_selected_buttons()
            self.print_correct_pairs()

        self.selected_cards = []

    def select_card(self, index, text, card_type):
        if len(self.selected_cards) < 3:
            self.selected_cards.append((index, text, card_type))
            if len(self.selected_cards) == 3:
                self.check_match()

    def reset_selected_buttons(self):
        for index, _, _ in self.selected_cards:
            self.buttons[index].config(state="normal")
        self.selected_cards = []


    def print_correct_pairs(self):
        print("Correct pairs are:")
        for item in self.data:
            print(f"Term: {item['term']}, Definition: {item['definition']}, Example: {item['example']}")


    def end_game(self):
        # Se llama cuando el juego termina, vuelve a la pantalla inicial
        self.setup_initial_screen()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


#Cerar ventatna principal para inicar el juego
root = tk.Tk()
game = StudyGame(root,None)
root.geometry("800x600")
root.mainloop()

