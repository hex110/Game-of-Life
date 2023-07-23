import random
import tkinter as tk
from tkinter import ttk
import copy

# Create a new board in a dead state (all cells are 0)
def dead_state():
    board_state = [[0] * width for _ in range(height)]

    # Add all cells to the changed_cells set initially to display them in gui at the start
    for x in range(width):
        for y in range(height):
            changed_cells.add((x, y))

    return board_state

# Create a new board in a random state (cells are randomly set to 0 or 1)
def random_state():
    random_board = dead_state()
    for i in range(width):
        for j in range(height):
            random_board[i][j] = random.randint(0, 1) # Generate random number
            if random_board[i][j] < 0.5: # Set the state as 0 or 1 based on the random number
                random_board[i][j] = 0
            else:
                random_board[i][j] = 1
    return random_board

# Draw the red borders
def draw_borders():

    length = size / min(width, height)

    x1 = 0
    x2 = x1 + length
    for i in range(width):
        y1 = i * length
        y2 = y1 + length
        canvas.create_rectangle(x1, y1, x2, y2, fill="red")
    
    y1 = 0
    y2 = y1 + length
    for i in range(width):
        x1 = i * length
        x2 = x1 + length
        canvas.create_rectangle(x1, y1, x2, y2, fill="red")

    x1 = (width-1) * length
    x2 = x1 + length
    for i in range(width):
        y1 = i * length
        y2 = y1 + length
        canvas.create_rectangle(x1, y1, x2, y2, fill="red")
    
    y1 = (width-1) * length
    y2 = y1 + length
    for i in range(width):
        x1 = i * length
        x2 = x1 + length
        canvas.create_rectangle(x1, y1, x2, y2, fill="red")

# Update the GUI by drawing the current state of the board on the canvas
def update_gui():
    global changed_cells

    length = size / min(width, height)

    for x, y in changed_cells: # Walk through all changed cells and display them
        x1 = x * length
        y1 = y * length
        x2 = x1 + length
        y2 = y1 + length

        if board[x][y] == 0:
            fill_color = "white"
        else:
            fill_color = "black"
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)

    changed_cells.clear()  # Clear the set of changed cells

def update_gui_all():

    length = size/min(width,height)

    print("hey")
    for i in range(width):
        for j in range(height):
            x1 = i * length
            y1 = j * length
            x2 = x1 + length
            y2 = y1 + length
            if i == 0 or j == 0 or i == width - 1 or j == height - 1:
                fill_color = "red"
            elif board[i][j] == 1:
                fill_color = "black"
            else:
                fill_color = "white"
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)

# Get the next state of the board based on the rules of the game of life
def next_board_state():
    global board, changed_cells
    new_board = [[0] * width for _ in range(height)]
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            # Get the sum of neighbours
            near = (
                board[i - 1][j - 1] + board[i - 1][j] + board[i - 1][j + 1]
                + board[i][j - 1] + board[i][j + 1]
                + board[i + 1][j - 1] + board[i + 1][j] + board[i + 1][j + 1]
            )

            # Apply the rules of game of life
            if board[i][j] == 0 and near == 3:
                new_board[i][j] = 1
            elif board[i][j] == 1 and (near == 2 or near == 3):
                new_board[i][j] = 1
            else:
                new_board[i][j] = 0 

            # Check if the cell state has changed and add it to the set of changed cells to know which ones to update on the gui
            if new_board[i][j] != board[i][j]:
                changed_cells.add((i, j))

    return new_board

# Update the board, this is the looping function that happens every x seconds
def game_of_life():
    global running, update_id, board, placing_state
    if running:
        new_board = next_board_state()

        # Check if the board has changed since the last update
        if new_board != board:
            board = new_board
            update_gui()

        #chatgpt optimization
        if update_id is not None:
            canvas.after_cancel(update_id)  # Cancel the previous update
        update_id = canvas.after(int(time_to_change * 1000), game_of_life)

# Toggle start/stop
def toggle_flow():
    global running, update_id, placing_state
    running = not running
    if running:
        running = True
        game_of_life()

        # Disables both place and erase buttons, to not interfere with the game once it started
        place_button.config(state=tk.DISABLED)
        erase_button.config(state=tk.DISABLED)

    else:
        running = False

        # Same as above, but it returns them to what they were
        place_button.config(state=tk.DISABLED if placing_state else tk.NORMAL)
        erase_button.config(state=tk.NORMAL if placing_state else tk.DISABLED)


    global toggle_button
    toggle_button.config(text="Stop" if running else "Start")  

# Place/erase on mouse click/drag
def on_canvas_click_drag(event):
    global is_dragging,prev_x, prev_y, modified_cells
    x = int(event.x / (size / width))
    y = int(event.y / (size / height))
    if 0 <= x < width and 0 <= y < height and (x, y) != (prev_x, prev_y) and running == False:
        prev_x, prev_y = x, y
        if placing_state and (x, y) not in modified_cells:
                board[x][y] = 1
                changed_cells.add((x,y))
                modified_cells.add((x, y))
        elif (x, y) not in modified_cells:
                board[x][y] = 0
                changed_cells.add((x,y))
                modified_cells.add((x, y))
    update_gui()

# Stop dragging
def on_canvas_release(event):
    global is_dragging, modified_cells
    is_dragging = False
    modified_cells.clear()  # Clear the set of modified cells when the dragging stops

# Toggle between place/erase based on the buttons
def toggle_mode(placing):
        global placing_state
        placing_state = placing
        place_button.config(state=tk.DISABLED if placing else tk.NORMAL)
        erase_button.config(state=tk.NORMAL if placing else tk.DISABLED)

# Reset the board to all 0s
def reset_board():
    global board, changed_cells
    board = dead_state()
    update_gui()
    draw_borders()

def save_board():
    global saved_boards, pattern_options, pattern_menu, execute_on_pattern_selected

    # Disable on_pattern_selected function execution while saving
    execute_on_pattern_selected = False

    saved_boards.append(board)
    new_pattern = entry.get()
    pattern_options.append(new_pattern)

    # Update the OptionMenu with the new options
    pattern_menu['menu'].add_command(label=new_pattern, command=lambda p=new_pattern: selected_pattern.set(p))

    # Update the selected pattern to the new pattern
    selected_pattern.set(new_pattern)

    # Clear the Entry widget
    entry.delete(0, 'end')

    # Re-enable on_pattern_selected function
    execute_on_pattern_selected = True

def load_pattern(name):
    if name in pattern_options:
        global board
        index = pattern_options.index(name)
        board = copy.deepcopy(saved_boards[index])
        update_gui_all()
    else:
        print("Invalid board name.")

# Pattern selection function
def on_pattern_selected(*args):
    if execute_on_pattern_selected:
        selected_pattern_name = selected_pattern.get()
        load_pattern(selected_pattern_name)

# Main function
def main(w, h):
    global width
    width = w
    global height
    height = h

    global window
    window = tk.Tk()
    global size
    size = width * size_of_cell
    global canvas
    canvas = tk.Canvas(window, width=size, height=size * 1.4)
    canvas.pack()

    global changed_cells
    changed_cells = set()  

    global board
    board = dead_state()

    update_gui()
    draw_borders()

    global update_id
    update_id = canvas.after(int(time_to_change * 1000), game_of_life)

    global is_dragging
    is_dragging = False
    global prev_x, prev_y
    prev_x = 0
    prev_y = 0
    global modified_cells
    modified_cells = set()  # Initialize the set to keep track of modified cells in the current drag

    # Button-1 is click, B1-Motion is drag, ButtonRelease-1 is drag release
    canvas.bind("<Button-1>", on_canvas_click_drag)
    canvas.bind("<B1-Motion>", on_canvas_click_drag)
    canvas.bind("<ButtonRelease-1>", on_canvas_release)

    global running, placing_state, saved_boards, pattern_options
    running = False
    placing_state = True  # Initial state: placing cells
    saved_boards = []

    global toggle_button, place_button, erase_button, reset_button, save_button, pattern_menu, selected_pattern, entry, entry_text, execute_on_pattern_selected
    execute_on_pattern_selected = True


    # Create a custom style for the button
    style = ttk.Style()
    style.configure(
        "Custom.TButton",
        foreground="black",
        padding=10,
        font=("Helvetica", 12, "bold"),
        borderwidth=0,  # Remove border
        highlightthickness=0,  # Remove highlight thickness (additional border on click)
        relief="flat",  # Remove any 3D-like effect
    )



    toggle_button = ttk.Button(window, text="Start", command=toggle_flow, style="Custom.TButton")
    toggle_button.place(x=50, y=size * 1.05)
    toggle_button.configure(takefocus=False) # Remove the dotted lines border when the button is clicked

    place_button = ttk.Button(window, text="Place", command=lambda: toggle_mode(True), style="Custom.TButton")
    place_button.place(x=250, y=size * 1.05)
    place_button.config(state=tk.DISABLED)

    erase_button = ttk.Button(window, text="Erase", command=lambda: toggle_mode(False), style="Custom.TButton")
    erase_button.place(x=400, y=size * 1.05)

    reset_button = ttk.Button(window, text="Reset", command=reset_board, style="Custom.TButton")
    reset_button.place(x=550, y=size * 1.05)

    entry = tk.Entry(window, width = 15, font=("Helvetica", 24, "normal"))
    entry.place(x=400, y=size * 1.15)
    entry_text=entry.get()

    save_button = ttk.Button(window, text="Save board", command=save_board, style="Custom.TButton")
    save_button.place(x=250, y=size * 1.15)

    # Patterns
    pattern_options = [
        "Pattern 1",
    ]

    selected_pattern = tk.StringVar()
    selected_pattern.set(pattern_options[0])  # Set the initial selection

    pattern_menu = tk.OptionMenu(window, selected_pattern, *pattern_options)
    pattern_menu.config(font=("Helvetica", 12, "bold"), width=10)
    pattern_menu.place(x=50, y=size * 1.15)

    # Set the trace for selected_pattern to call on_pattern_selected when the selection changes
    selected_pattern.trace("w", on_pattern_selected)


    window.mainloop()

# Modifiable variables
time_to_change = 0.3
size_of_cell = 15
number_of_cells = 50

if __name__ == "__main__":
    main(number_of_cells,number_of_cells)