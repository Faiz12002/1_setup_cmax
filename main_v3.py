# Imports:
import customtkinter as ctk #Clean
from customtkinter import filedialog as filedialog #Clean
from csvtolist import extract_csv_data #Clean
from pathlib import Path #Clean
from copy import deepcopy #Clean
import solver_choice #Clean
import solver_random #Clean
from matplotlib.figure import Figure #Clean
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk #Clean
import networkx as nx #Clean
from CTkTable import * #Clean

# define global variables
processing_times_global = []
setup_matrix_global = []
start_times_global = []
task_sequence_global = []
makespan_global = float('inf')
display_width = 14
display_height = 6 


# Initialize the root:
root = ctk.CTk(fg_color='#0E0E0E')

# Define constants & config: 

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_title = '1|set-up|Cmax'
size_input_level_window_title = 'Saisir la taille des données'
value_input_level_window_title = 'Saisir les valeurs'
task_input_level_window_title = 'Choisir la première tâche'
# icon_path = 'App\icon.ico'
normal_font = ctk.CTkFont(family="Roboto Semi Bold", size=17)
title_font = ctk.CTkFont(family="Roboto Bold", size=27)
sub_title_font = ctk.CTkFont(family='Roboto Bold', size = 21)
sidebar_color = '#222222'
hover_color = '#404040'
# image = ctk.CTkImage(light_image=Image.open(icon_path), size=(180,180))

# define events

def clear_display_frame(): #Cleared
    """Clears the current content in the display frame."""
    for widget in display_results_frame.winfo_children():
        widget.destroy()

def create_gantt_frame(master, start_times, processing_times, task_sequence): #Cleared
    global display_width, display_height
    clear_display_frame()
    frame = ctk.CTkFrame(master)
    
    fig = Figure(figsize=(display_width, display_height))
    ax = fig.add_subplot(111)
    
    # Plot Gantt chart
    for start, duration, task_label in zip(start_times, processing_times, task_sequence):
        ax.barh(0, duration, left=start, height=0.4, color='#b6465f', edgecolor='black')
        ax.text(start + duration/2, 0, f"{task_label}", 
                ha='center', va='center', color='white', 
                fontsize=10, weight='bold')
    
    # Customize chart
    ax.set_yticks([])
    ax.set_xlim(0, max(start + duration for start, duration in zip(start_times, processing_times)) + 1)
    ax.set_xlabel("Temps")
    ax.set_title("Diagramme de Gantt")
    ax.set_ylim(-0.5, 0.5)
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xticks(range(0, max(start_times) + max(processing_times) + 2))
    
    # Create canvas and toolbar
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()
    
    frame.pack()

def create_hamiltonian_frame(master, distance_matrix, indexes): #Cleared
    global display_width, display_height
    clear_display_frame()
    frame = ctk.CTkFrame(master)
    
    fig = Figure(figsize=(display_width, display_height))
    ax = fig.add_subplot(111)
    
    # Adjusting indexes to be zero-based for Python indexing
    indexes = [i - 1 for i in indexes]

    # Create a directed graph from the distance matrix
    G = nx.MultiDiGraph()
    nodes = range(len(distance_matrix))

    for i in nodes:
        for j in nodes:
            if i != j:  # Ignore self-loops
                G.add_edge(i, j, weight=distance_matrix[i][j])

    # Define node positions
    pos = nx.circular_layout(G)

    # Draw all edges with default color
    nx.draw_networkx_edges(G, pos, edge_color="gray", connectionstyle="arc3,rad=0.2", arrows=True, ax=ax)

    # Draw the Hamiltonian path with distinct color
    hamiltonian_edges = [(indexes[i], indexes[i + 1]) for i in range(len(indexes) - 1)]
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=hamiltonian_edges,
        edge_color="#e01e37",
        width=2,
        connectionstyle="arc3,rad=0.2",
        arrows=True,
        ax=ax
    )

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color="lightgray", node_size=700, ax=ax)

    # Highlight Hamiltonian path nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=indexes,
        node_color="#b6465f",
        node_size=700,
        ax=ax
    )

    # Add node labels
    nx.draw_networkx_labels(G, pos, {i: i + 1 for i in nodes}, font_color="white", ax=ax)

    # Add all edge weights
    edge_labels = {(i, j): f"{distance_matrix[i][j]}" for i in nodes for j in nodes if i != j}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_color="gray", label_pos=0.3, ax=ax
    )

    # Highlight edge weights for Hamiltonian path
    hamiltonian_edge_labels = {
        (indexes[i], indexes[i + 1]): f"{distance_matrix[indexes[i]][indexes[i + 1]]}"
        for i in range(len(indexes) - 1)
    }
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=hamiltonian_edge_labels, font_color="#b6465f", label_pos=0.3, ax=ax
    )

    
    
    # Customize chart

    ax.set_title("Chemin hamiltonien")
    
    # Create canvas and toolbar
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()
    
    frame.pack()


def load_csv(): #Cleared
    global processing_times_global
    global setup_matrix_global
    csv_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    if csv_path:
        try:
            pi, cij = extract_csv_data(csv_path)
            # print(pi, cij)
            processing_times_global.clear()
            setup_matrix_global.clear()
            processing_times_global = deepcopy(pi)
            setup_matrix_global = deepcopy(cij)
            print(processing_times_global)
            print(setup_matrix_global)
            load_data1_display.configure(state = 'normal')
            load_data1_display.delete('1.0', ctk.END)
            load_data1_display.insert('0.0', f'{Path(csv_path).name}')
            load_data1_display.configure(state = 'disabled')
        except IOError:
            print('Error opening file')
    
def define_data_size(): #Cleared
    
    global screen_height
    global screen_width
    global title_font
    global normal_font
    global hover_color

    dark_theme = {
        "fg_color": "#0E0E0E",     # Background color for frames
        "text_color": "white",      # Text color for better contrast
        "entry_color": "#1A1A1A"    # Slightly lighter than background for entries
    }
    # Initializing toplevel window
    size_input_level_window = ctk.CTkToplevel(root, fg_color='#0E0E0E')
    size_input_level_window.grab_set()
    # Top level config
    size_input_level_window.title(size_input_level_window_title)
    size_input_level_window.configure(fg_color=dark_theme['fg_color'])
    size_input_level_window.geometry(f'{screen_width//2}x{screen_height//2}+0+0')
    size_input_level_window.resizable(False, False)
    # define events
    def define_data_values():
        # Initializing toplevel window 
        value_input_level_window = ctk.CTkToplevel(size_input_level_window, fg_color='#0E0E0E')
        value_input_level_window.grab_set()
        # Top level config
        value_input_level_window.title(value_input_level_window_title)
        value_input_level_window.geometry(f'{screen_width}x{screen_height}+0+0')
        # Configure grid weight for resizing
        value_input_level_window.grid_rowconfigure(0, weight=1)
        value_input_level_window.grid_columnconfigure(0, weight=1)
        # define events

        def get_table_data(): # Cleared
            global processing_times_global
            global setup_matrix_global
            """Retrieve vector and matrix data and print it."""
            # Retrieve vector input
            vector_data = [int(vector_entries[i].get()) for i in range(n)]
            print("Vector Data:", vector_data)

            # Retrieve matrix input
            matrix_data = []
            for i in range(n):
                row_data = [int(matrix_entries[i][j].get()) for j in range(n)]
                matrix_data.append(row_data)
            print("Matrix Data:", matrix_data)

            processing_times_global.clear()
            setup_matrix_global.clear()
            processing_times_global = deepcopy(vector_data)
            setup_matrix_global = deepcopy(matrix_data)
            load_data2_display.configure(state = 'normal')
            load_data2_display.delete('1.0', ctk.END)
            load_data2_display.insert('0.0', 'Succées')
            load_data2_display.configure(state = 'disabled')
            print(processing_times_global)
            print(setup_matrix_global)

            value_input_level_window.destroy()
            size_input_level_window.destroy()



        def move_to_next_cell(event, current_row, current_col, is_vector):
            """Move to the next cell when Enter is pressed."""
            if is_vector:
                if current_col < n - 1:
                    vector_entries[current_col + 1].focus()
                else:
                    if n > 1 and matrix_entries[0][1]:
                        matrix_entries[0][1].focus()
            else:
                next_col = (current_col + 1) % n
                next_row = current_row + 1 if next_col == 0 else current_row

                # Skip diagonals
                while next_row < n and next_col < n and next_row == next_col:
                    next_col = (next_col + 1) % n
                    if next_col == 0:
                        next_row += 1

                if next_row < n:
                    matrix_entries[next_row][next_col].focus()
        
        def move_to_previous_cell(event, current_row, current_col, is_vector):
            """Move to the previous cell when Backspace is pressed."""
            if is_vector:
                if current_col > 0 and not vector_entries[current_col].get():
                    vector_entries[current_col - 1].focus()
            else:
                if not matrix_entries[current_row][current_col].get():
                    prev_col = (current_col - 1 + n) % n
                    prev_row = current_row - 1 if current_col == 0 else current_row

                    # Skip diagonals
                    while prev_row >= 0 and prev_col >= 0 and prev_row == prev_col:
                        prev_col = (prev_col - 1 + n) % n
                        if prev_col == n - 1:
                            prev_row -= 1

                    if prev_row >= 0:
                        matrix_entries[prev_row][prev_col].focus()

        def on_ctrl_enter(event):
            """Submit data when Ctrl+Enter is pressed."""
            if event.state & 0x4:  # Check if Control key is pressed
                get_table_data()



        # Layout

        # Create a scrollable canvas
        canvas = ctk.CTkCanvas(value_input_level_window, bg=dark_theme['fg_color'])
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = ctk.CTkScrollbar(value_input_level_window, orientation="vertical", command=canvas.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ctk.CTkScrollbar(value_input_level_window, orientation="horizontal", command=canvas.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Define the vector size and matrix dimensions
        n = int(step1_text_input.get())  # Change `n` as needed

        # --- Add Widgets Directly to Canvas ---
        widget_frame = ctk.CTkFrame(canvas, fg_color=dark_theme['fg_color'])
        canvas.create_window((0, 0), window=widget_frame, anchor="nw")

        ctk.CTkLabel(widget_frame, text_color=dark_theme['text_color'], text='Etape 2 : Saisir les valeurs', font=title_font).grid(row=0, column=0, columnspan=n, pady=(10, 5))
        ctk.CTkLabel(widget_frame, text_color=dark_theme['text_color'], text='Remplir le temps de traitements de vos tâches, ainsi que leurs temps de transition', font=normal_font).grid(row=1, column=0, columnspan=n, pady=(10, 5))
        # --- Vector Input ---
        ctk.CTkLabel(widget_frame, text_color = dark_theme['text_color'], text=f"Saisir le temps de traitements de vos {n} tâches:").grid(row=3, column=0, columnspan=n, pady=(10, 5))

        vector_entries = []
        for i in range(n):
            entry = ctk.CTkEntry(widget_frame, width=80, justify="center", fg_color=dark_theme['entry_color'], text_color=dark_theme['text_color'])
            entry.grid(row=4, column=i, padx=5, pady=5)
            entry.bind("<Return>", lambda event, col=i: move_to_next_cell(event, 0, col, True))
            entry.bind("<BackSpace>", lambda event, col=i: move_to_previous_cell(event, 0, col, True))
            vector_entries.append(entry)
    
        # --- Matrix Input ---
        ctk.CTkLabel(widget_frame, text_color=dark_theme['text_color'] ,text=f"Saisir leur temps de transition:").grid(row=5, column=0, columnspan=n, pady=(10, 5))

        matrix_entries = []
        for i in range(n):
            row_entries = []
            for j in range(n):
                if i == j:
                    # Diagonal is pre-filled with 0 and non-editable
                    entry = ctk.CTkEntry(widget_frame, width=80, justify="center", fg_color=dark_theme['entry_color'], text_color=dark_theme['text_color'])
                    entry.insert(0, "0")
                    entry.configure(state="disabled")
                else:
                    entry = ctk.CTkEntry(widget_frame, width=80, justify="center", fg_color=dark_theme['entry_color'], text_color=dark_theme['text_color'])
                    entry.bind("<Return>", lambda event, row=i, col=j: move_to_next_cell(event, row, col, False))
                    entry.bind("<BackSpace>", lambda event, row=i, col=j: move_to_previous_cell(event, row, col, False))
                entry.grid(row=i+3 + 3, column=j, padx=5, pady=5)
                row_entries.append(entry)
            matrix_entries.append(row_entries)

        # Create a Submit button
        submit_button = ctk.CTkButton(widget_frame, text="Submit", command=get_table_data)
        submit_button.grid(row=n+3 + 3, column=0, columnspan=n, pady=10)

        # Update scroll region
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        widget_frame.bind("<Configure>", update_scroll_region)

        # Bind Ctrl+Enter for submitting data
        value_input_level_window.bind("<Control-Return>", on_ctrl_enter)

        # Layout config


        
        

    # ----


    # Layout
    step1_text = ctk.CTkLabel(size_input_level_window, text='Etape 1: Combien de tâches avez-vous ?', font=title_font)

    step1_description = ctk.CTkLabel(size_input_level_window, text='Cette étape va déterminer la taille de votre liste des tâches et la taille de votre matrice de transisiton', font=('Roboto', 14))

    step1_text_input = ctk.CTkEntry(size_input_level_window, placeholder_text='Saisir le nombe de tâches ici')

    step1_next_button = ctk.CTkButton(size_input_level_window, text='Suivant', font=normal_font, command=define_data_values) # add button command


    # Layout config
    step1_text.place(x = 5, y = 5)

    step1_description.place(x = 5, y = 50)

    step1_text_input.place(x=5, y = 100)
    step1_text_input.configure(
        width = 400,
        height=35
    )

    step1_next_button.place(x = 470, y = 320)

def choose_task(): #Cleared
    dark_theme = {
        "fg_color": "#0E0E0E",     
        "text_color": "white",      
        "entry_color": "#1A1A1A"    
    }
    # Initializing toplevel window
    task_input_level_window = ctk.CTkToplevel(root, fg_color='#0E0E0E')
    task_input_level_window.grab_set()
    
    # Top level config
    task_input_level_window.title(task_input_level_window_title)
    task_input_level_window.configure(fg_color=dark_theme['fg_color'])
    task_input_level_window.geometry(f'{screen_width//2}x{screen_height//2}+0+0')
    task_input_level_window.resizable(False, False)

    # define events

    def choice_solve():
        global processing_times_global
        global setup_matrix_global
        global task_sequence_global
        global start_times_global
        global makespan_global
        global display_results_frame

        start_times, makespan, task_sequence = solver_choice.solve_setup_scheduling(processing_times_global, setup_matrix_global, int(choice_step1_text_input.get()))

        start_times_global = start_times
        makespan_global = makespan
        task_sequence_global = task_sequence

        processing_times_modified = [0] + processing_times_global
        processing_times_modified = [processing_times_modified[i] for i in task_sequence_global]

        create_gantt_frame(display_results_frame, start_times_global, processing_times_modified, task_sequence_global)

        print('Task sequence: ', task_sequence_global)
        print('Start times', start_times_global)
        print('Processing Times ordered: ', processing_times_modified)



        task_input_level_window.destroy()
        


    # Layout
    choice_step1_text = ctk.CTkLabel(task_input_level_window, text='Etape 1: Choisir la première tâche', font=title_font)

    choice_step1_description = ctk.CTkLabel(task_input_level_window, text='Cette étape va influencer sur la solution', font=('Roboto', 14))

    choice_step1_text_input = ctk.CTkEntry(task_input_level_window, placeholder_text=f'Saisir le nom de la tâche ici (1-{len(processing_times_global)})')

    choice_step1_next_button = ctk.CTkButton(task_input_level_window, text='Saisir', font=normal_font, command=choice_solve) # add button command


    # Layout config
    choice_step1_text.place(x = 5, y = 5)

    choice_step1_description.place(x = 5, y = 50)

    choice_step1_text_input.place(x=5, y = 100)
    choice_step1_text_input.configure(
        width = 400,
        height=35
    )

    choice_step1_next_button.place(x = 470, y = 320)

def random_solve(): #Cleared
    global processing_times_global
    global setup_matrix_global
    global task_sequence_global
    global start_times_global
    global makespan_global
    global display_results_frame

    start_times, makespan, task_sequence = solver_random.solve_setup_scheduling(processing_times_global, setup_matrix_global)

    makespan_global = makespan
    task_sequence_global = task_sequence
    start_times_global = start_times

    processing_times_modified = [0] + processing_times_global
    processing_times_modified = [processing_times_modified[i] for i in task_sequence_global]

    create_gantt_frame(display_results_frame, start_times_global, processing_times_modified, task_sequence_global)

    print('Task sequence: ', task_sequence)
    print('Start times', start_times)
    print('Processing Times ordered: ', processing_times_modified)

def onclick_gantt_frame(): #Cleared
    global processing_times_global
    global setup_matrix_global
    global task_sequence_global
    global start_times_global
    global display_results_frame
    
    processing_times_modified = [0] + processing_times_global
    processing_times_modified = [processing_times_modified[i] for i in task_sequence_global]

    create_gantt_frame(display_results_frame, start_times_global, processing_times_modified, task_sequence_global)


def onclick_hamiltonian_frame(): #Cleared
    global setup_matrix_global
    global task_sequence_global
    global display_results_frame

    create_hamiltonian_frame(display_results_frame, setup_matrix_global, task_sequence_global)

def onclick_details_frame(): #Cleared
    global processing_times_global 
    global setup_matrix_global
    global task_sequence_global
    global start_times_global
    global makespan_global
    global display_results_frame

    processing_times_modified = [0] + processing_times_global
    processing_times_modified = [processing_times_modified[i] for i in task_sequence_global]

    clear_display_frame()

    summary = f"""Ordonnancement final:

Séquence des tâches: {task_sequence_global}
Dates de début: {start_times_global}
Séquence ordonnée des temps de traitements: {processing_times_modified}
Longueur de l'ordonnancement: {makespan_global}
Détails: 
    """

    display_results_frame_textbox = ctk.CTkTextbox(display_results_frame, width=900, height=450)
    display_results_frame_textbox.pack(fill = 'both', expand = True)
    display_results_frame_textbox.configure(state = 'normal')
    display_results_frame_textbox.delete('1.0', ctk.END)

    display_results_frame_textbox.insert(ctk.END, summary)  

    for i, task in enumerate(task_sequence_global):
        # Display the task start time and processing time
        display_results_frame_textbox.insert(
            ctk.END, 
            f'\nTâche {task} commence à {start_times_global[i]}, temps de traitement: {processing_times_modified[i]}'
        )

        # Check if there is a next task to calculate the setup time
        if i < len(task_sequence_global) - 1:
            next_task_start_time = start_times_global[i + 1]
            current_task_end_time = start_times_global[i] + processing_times_modified[i]
            setup_time = next_task_start_time - current_task_end_time

            # Display the setup time if it's greater than 0
            if setup_time > 0:
                display_results_frame_textbox.insert(
                    ctk.END, 
                    f'\nTemps de transition avant la tâche {task_sequence_global[i + 1]}: {setup_time}'
                )


    display_results_frame_textbox.configure(state = 'disabled')

def onclick_about():
    dark_theme = {
        "fg_color": "#0E0E0E",    
        "text_color": "white",      
        "entry_color": "#1A1A1A"    
    }


    text = """
Application solveur du problème 1|set-up|Cmax
Par:
212132018908 | Tchekiken Faiz | M1 BigData Analytics
212133010390 | Badis Abdelkader Amine | M1 BigData Analytics 

Pour:
Mr. Mourad Boudhar
"""

    toplevel_about = ctk.CTkToplevel(root, fg_color=dark_theme['fg_color'])
    toplevel_about.grab_set()
    # Top level config
    toplevel_about.title('À propos')
    toplevel_about.configure(fg_color=dark_theme['fg_color'])
    toplevel_about.geometry(f'{screen_width//2}x{screen_height//2}+0+0')
    toplevel_about.resizable(False, False)
    ctk.CTkLabel(toplevel_about, text=text, font=normal_font, text_color=dark_theme['text_color']).pack()

def onclick_help():
    dark_theme = {
        "fg_color": "#0E0E0E",    
        "text_color": "white",      
        "entry_color": "#1A1A1A"    
    }


    text = """
Utilisation de l'application: 
1) Charger les données (Par fichier .csv ou par saisit)
2) Résoudre (Soit rapide soit par choix de la première tâche)
3) Explorer les differentes affichages (Diagramme de Gantt, graphe et le chemin hamiltonien, affichage texte)

Redimensionnement de l'affichage: 
1) Clicker sur le boutton de redimension
2) Définir les parametres (Largeur, Longeur) 
3) Confirmer les parametres
4) Appliquer les parametres en affichant l'un des graphiques (Gantt ou chemin hamiltonien)
"""

    toplevel_about = ctk.CTkToplevel(root, fg_color=dark_theme['fg_color'])
    toplevel_about.grab_set()
    # Top level config
    toplevel_about.title('Aide')
    toplevel_about.configure(fg_color=dark_theme['fg_color'])
    toplevel_about.geometry(f'{screen_width//1.3}x{screen_height//1.3}+0+0')
    toplevel_about.resizable(False, False)
    ctk.CTkLabel(toplevel_about, text=text, font=normal_font, text_color=dark_theme['text_color']).pack()

def onclick_showdata():
    global processing_times_global
    global setup_matrix_global
    # Set the appearance mode to dark
    ctk.set_appearance_mode("dark")

    # Define theme colors
    dark_theme = {
        "fg_color": "#0E0E0E",
        "text_color": "white",
    }

    def create_task_headers(size):
        """Create headers with task names based on size"""
        return ["Tâche"] + [f"T{i+1}" for i in range(size)]

    def format_vector_data(vector):
        """Format vector data with headers and task names"""
        headers = create_task_headers(len(vector))
        return [headers, ["Temps"] + vector]

    def format_matrix_data(matrix):
        """Format matrix data with headers and task names"""
        if not matrix or len(matrix) != len(matrix[0]):  # Check if matrix is square
            raise ValueError("Matrix must be square (equal rows and columns)")
        
        size = len(matrix)
        headers = create_task_headers(size)
        formatted_data = [headers]
        
        for i, row in enumerate(matrix):
            formatted_data.append([f"T{i+1}"] + row)
        
        return formatted_data


    # Create TopLevel window
    window = ctk.CTkToplevel(root)
    window.geometry("800x600")
    window.title('Affichage des données')
    window.configure(fg_color=dark_theme["fg_color"])
    window.grab_set()  # Make the window modal

    # Format data
    vector_data = format_vector_data(processing_times_global)
    matrix_data = format_matrix_data(setup_matrix_global)

    # Vector section
    vector_title = ctk.CTkLabel(
        window,
        text="Temps de traitements",
        font=("Arial", 16, "bold"),
        text_color=dark_theme["text_color"]
    )
    vector_title.pack(pady=(20, 5))

    ctkvector = CTkTable(
        master=window,
        row=len(vector_data),
        column=len(vector_data[0]),
        values=vector_data,
        header_color="#1a1a1a",
        fg_color="#2d2d2d",
        text_color=dark_theme["text_color"],
        hover_color="#404040"
    )
    ctkvector.pack(padx=20, pady=(0, 20))

    # Matrix section
    matrix_title = ctk.CTkLabel(
        window,
        text="Temps de transitions",
        font=("Arial", 16, "bold"),
        text_color=dark_theme["text_color"]
    )
    matrix_title.pack(pady=(20, 5))

    # Create a scrollable frame for the matrix
    scroll_frame = ctk.CTkScrollableFrame(
        window,
        width=600,
        height=300,
        fg_color=dark_theme["fg_color"]
    )
    scroll_frame.pack(padx=20, pady=(0, 20), expand=True, fill="both")

    ctkmatrix = CTkTable(
        master=scroll_frame,
        row=len(matrix_data),
        column=len(matrix_data[0]),
        values=matrix_data,
        header_color="#1a1a1a",
        fg_color="#2d2d2d",
        text_color=dark_theme["text_color"],
        hover_color="#404040"
    )
    ctkmatrix.pack(expand=True, fill="both")

def onclick_display_settings():
    global display_width, display_height
    
    # Set the appearance mode to dark
    ctk.set_appearance_mode("dark")

    # Define theme colors
    dark_theme = {
        "fg_color": "#0E0E0E",
        "text_color": "white",
    }

    def update_values():
        """Update global variables with current slider values"""
        global display_width, display_height
        display_width = int(width_slider.get())
        display_height = int(height_slider.get())
        window.destroy()

    # Create TopLevel window
    window = ctk.CTkToplevel(root)
    window.geometry("800x600")
    window.configure(fg_color=dark_theme["fg_color"])
    window.grab_set()  # Make the window modal
    
    # Title
    title = ctk.CTkLabel(
        window,
        text="Redimension de l'affichage",
        font=("Arial", 20, "bold"),
        text_color=dark_theme["text_color"]
    )
    title.pack(pady=(40, 30))

    # Create frame for sliders
    slider_frame = ctk.CTkFrame(
        window,
        fg_color="transparent"
    )
    slider_frame.pack(fill="both", padx=40, pady=20)

    # Width slider section
    width_label = ctk.CTkLabel(
        slider_frame,
        text="Largeur:",
        font=("Arial", 14),
        text_color=dark_theme["text_color"]
    )
    width_label.pack(pady=(0, 5))

    width_slider = ctk.CTkSlider(
        slider_frame,
        from_=0,
        to=16,
        number_of_steps=16,
        width=400
    )
    width_slider.set(display_width if 'display_width' in globals() else 8)
    width_slider.pack(pady=(0, 20))

    width_value = ctk.CTkLabel(
        slider_frame,
        text=str(int(width_slider.get())),
        font=("Arial", 12),
        text_color=dark_theme["text_color"]
    )
    width_value.pack(pady=(0, 20))

    # Height slider section
    height_label = ctk.CTkLabel(
        slider_frame,
        text="Longueur:",
        font=("Arial", 14),
        text_color=dark_theme["text_color"]
    )
    height_label.pack(pady=(0, 5))

    height_slider = ctk.CTkSlider(
        slider_frame,
        from_=0,
        to=16,
        number_of_steps=16,
        width=400
    )
    height_slider.set(display_height if 'display_height' in globals() else 8)
    height_slider.pack(pady=(0, 20))

    height_value = ctk.CTkLabel(
        slider_frame,
        text=str(int(height_slider.get())),
        font=("Arial", 12),
        text_color=dark_theme["text_color"]
    )
    height_value.pack(pady=(0, 20))

    # Update value labels when sliders change
    def update_width_label(value):
        width_value.configure(text=str(int(float(value))))

    def update_height_label(value):
        height_value.configure(text=str(int(float(value))))

    width_slider.configure(command=update_width_label)
    height_slider.configure(command=update_height_label)

    # Confirm button
    confirm_button = ctk.CTkButton(
        window,
        text="Confirmer",
        font=("Arial", 14),
        command=update_values,
        width=200
    )
    confirm_button.pack(pady=30)

# App config:

root.title(app_title)
root.geometry(f'{screen_width}x{screen_height}+0+0')
# root.iconbitmap(icon_path)


# Layout
    # Master window 
        # Creating the logo
logo_container = ctk.CTkFrame(root)
logo_text = ctk.CTkLabel(root, text='1|set-up|C', font=title_font)
sub_logo_text = ctk.CTkLabel(root, text='max', font=('Roboto Bold', 15))
        # Creating the sidebar

sidebar = ctk.CTkFrame(root)
    # frame: sidebar
load_data_text = ctk.CTkLabel(sidebar, text='Charger les données', font=sub_title_font)
load_data1_button = ctk.CTkButton(sidebar, text='Dans un fichier CSV', font=normal_font, hover_color=hover_color, command=load_csv) 

arrow1 = ctk.CTkLabel(sidebar, text='→ ', font=sub_title_font)

load_data1_display = ctk.CTkTextbox(sidebar)

input_data_button = ctk.CTkButton(sidebar, text='Saisir les valeurs', font=normal_font, hover_color=hover_color, command=define_data_size) 

arrow2 = ctk.CTkLabel(sidebar, text='→ ', font=sub_title_font)

load_data2_display = ctk.CTkTextbox(sidebar)

show_data_button = ctk.CTkButton(sidebar, text='Afficher les données', font=normal_font, hover_color=hover_color, command=onclick_showdata) 

solving_text = ctk.CTkLabel(sidebar, text='Résolution', font=sub_title_font)

solving_random_button = ctk.CTkButton(sidebar, text='Résolution rapide', font=normal_font, hover_color=hover_color, command=random_solve) 
solving_choice_button = ctk.CTkButton(sidebar, text='Résolution par choix', font=normal_font, hover_color=hover_color, command=choose_task) 

display_settings_label = ctk.CTkLabel(sidebar, text='Parametres d\'affichage', font=sub_title_font)

display_settings_button = ctk.CTkButton(sidebar, text='Redimension', font=normal_font, hover_color=hover_color, command=onclick_display_settings) 

help_button = ctk.CTkButton(sidebar, text='Aide', font=normal_font, hover_color=hover_color, command=onclick_help) 
about_button = ctk.CTkButton(sidebar, text='À propos', font=normal_font, hover_color=hover_color, command=onclick_about) 

display_title_text = ctk.CTkLabel(root, text='Affichage', font=title_font)

display_results_frame = ctk.CTkFrame(root)

gantt_button = ctk.CTkButton(root, text='Diagramme de Gantt', font=normal_font, hover_color=hover_color, command=onclick_gantt_frame) 
hamiltonian_button = ctk.CTkButton(root, text='Chemin Hamiltonien', font=normal_font, hover_color=hover_color, command=onclick_hamiltonian_frame) 
details_button = ctk.CTkButton(root, text='Détails', font=normal_font, hover_color=hover_color, command=onclick_details_frame) 
# ------------



# -----------

#widgets config:
logo_container.configure(
    root,
    width=250,
    height=50,
    corner_radius=50,  # This sets the border radius
    fg_color=sidebar_color   # Fill color
)

logo_container.place(x = 5, y = 5)

logo_text.configure(fg_color = sidebar_color)
logo_text.place(x = 47, y = 11)

sub_logo_text.configure(fg_color = sidebar_color)
sub_logo_text.place(x=173, y =20)

sidebar.place(x= 5, y=90)
sidebar.configure(
    fg_color = sidebar_color,
    width = 250,
    height = 500
    )

load_data_text.place(x = 15, y = 5)

load_data1_button.place(x=25, y = 40)
load_data1_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

arrow1.place(x = 30, y = 80)

load_data1_display.place(x = 60, y= 80)
load_data1_display.configure(
    height = 30,
    width = 150,
    state = 'disabled'
)

arrow2.place(x = 30, y = 160)

load_data2_display.place(x = 60, y= 160)
load_data2_display.configure(
    height = 30,
    width = 150,
    state = 'disabled'
)

show_data_button.place(x=25, y = 200)
show_data_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

input_data_button.place(x=25, y = 120)
input_data_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

solving_text.place(x = 15, y = 240)

solving_random_button.place(x=25, y = 280)
solving_random_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

solving_choice_button.place(x=25, y = 325)
solving_choice_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

display_settings_label.place(x = 15, y = 365)

display_settings_button.place(x=25, y = 400)
display_settings_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

help_button.place(x=5, y = 455)
help_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 40,
    corner_radius = 32
)

about_button.place(x=110, y = 455)
about_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 40,
    corner_radius = 32
)

display_title_text.place(x = 290, y = 50)

display_results_frame.place(x= 290, y=90)
display_results_frame.configure(
    width = 900,
    height = 450,
    fg_color = '#DFDFDF'
    )

gantt_button.place(x=350, y = 550)
gantt_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

hamiltonian_button.place(x=600, y = 550)
hamiltonian_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

details_button.place(x=850, y = 550)
details_button.configure(
    fg_color = '#343434',
    height = 35, 
    width = 200,
)

# ----- 

# main loop program
root.mainloop()