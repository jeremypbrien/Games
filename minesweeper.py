import threading
from tkinter import *
from random import randint

ROWS = 24
COLS = 30
MINES = 50
COLORS = {"0": "#cad7e8",
          "1": "blue",
          "2": "green",
          "3": "red",
          "4": "#000c51",
          "5": "#5c110b",
          "6": "#0d7c83",
          "7": "white",
          "8": "white",
          "X": "black"}
TIMER_ENABLED = True


class Level:
    def __init__(self, row, col, mines):
        self.row = row
        self.col = col
        self.mines = mines
        self.coordinates_of_mines = []
        self.checked_coordinates = []
        self.flagged_coordinates = []
        self.grid = [["" for _ in range(self.col)] for _ in range(self.row)]
        self.shuffle()

    def reset(self):
        self.coordinates_of_mines = []
        self.checked_coordinates = []
        self.flagged_coordinates = []
        self.grid = [["" for _ in range(self.col)] for _ in range(self.row)]
        self.shuffle()

    def shuffle(self):
        """ Creates Board """
        mines_placed = 0
        while mines_placed < self.mines:
            x, y = randint(0, self.row - 1), randint(0, self.col - 1)
            while self.grid[x][y] == "X":
                x, y = randint(0, self.row - 1), randint(0, self.col - 1)
            self.grid[x][y] = "X"
            self.coordinates_of_mines.append((x, y))
            mines_placed += 1

        for i in range(self.row):
            for j in range(self.col):
                if self.grid[i][j] != "X":
                    adjacent_tiles = [
                        self.grid[i - 1][j - 1] if i - 1 >= 0 and j - 1 >= 0 else None,
                        self.grid[i - 1][j] if i - 1 >= 0 else None,
                        self.grid[i - 1][j + 1] if i - 1 >= 0 and j + 1 < self.col else None,
                        self.grid[i][j - 1] if j - 1 >= 0 else None,
                        self.grid[i][j + 1] if j + 1 < self.col else None,
                        self.grid[i + 1][j - 1] if i + 1 < self.row and j - 1 >= 0 else None,
                        self.grid[i + 1][j] if i + 1 < self.row else None,
                        self.grid[i + 1][j + 1] if i + 1 < self.row and j + 1 < self.col else None
                    ]
                    self.grid[i][j] = str(len([x for x in adjacent_tiles if x == "X"]))

    def get_zero_chain(self, x, y):
        """ Returns a list of coordinates for block of zeros """
        list_of_coordinates = [
            (x, y),
            (x - 1, y - 1) if x - 1 >= 0 and y - 1 >= 0 else None,
            (x - 1, y) if x - 1 >= 0 else None,
            (x - 1, y + 1) if x - 1 >= 0 and y + 1 < self.col else None,
            (x, y - 1) if y - 1 >= 0 else None,
            (x, y + 1) if y + 1 < self.col else None,
            (x + 1, y - 1) if x + 1 < self.row and y - 1 >= 0 else None,
            (x + 1, y) if x + 1 < self.row else None,
            (x + 1, y + 1) if x + 1 < self.row and y + 1 < self.col else None
        ]
        coordinates = [(x, y)]
        for coordinate in list_of_coordinates:
            if coordinate is not None and coordinate not in self.checked_coordinates:
                if self.grid[coordinate[0]][coordinate[1]] == "0" and coordinate != (x, y):
                    self.checked_coordinates.append(coordinate)
                    coordinates += self.get_zero_chain(coordinate[0], coordinate[1])
                else:
                    self.checked_coordinates.append(coordinate)
                    coordinates.append(coordinate)
        return coordinates


class Tile:
    def __init__(self, label, row, column, value):
        self.label = label
        self.row = row
        self.column = column
        self.value = value
        self.is_revealed = False
        self.is_flagged = False


class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.root = None
        self.canvas = None
        self.info_canvas = None
        self.tiles = []
        self.level = Level(ROWS, COLS, MINES)
        self.timer = None
        self.timer_is_running = False
        self.mine_counter = None
        self.game_over = False

        self.start()

    def callback(self):
        """ Called when window is closed to close thread """
        self.root.quit()

    def run(self):
        """ Runs thread """
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.wm_minsize(width=900, height=900)
        self.root.configure(bg="grey")
        self.root.bind("<Button-1>", self.on_left_click)
        self.root.bind("<Button-3>", self.on_right_click)

        self.canvas = Canvas(self.root, bg="white", bd=0, highlightthickness=0)
        self.info_canvas = Canvas(self.root, bg="grey", width=20, height=75, highlightthickness=0)
        self.info_canvas.pack(fill=X, pady=10)
        self.canvas.pack(pady=10)

        self.timer = Label(self.info_canvas, bg="black", fg="red", font=("Digital-7", 45), width=3, height=1)
        self.timer.pack(side=RIGHT, padx=50)
        self.mine_counter = Label(self.info_canvas, bg="black", fg="red", font=("Digital-7", 45), width=3, height=1)
        self.mine_counter.pack(side=LEFT, padx=50)

        self.reset()
        self.timer_tick()

        self.root.mainloop()

    def reset(self):
        """ Resets view, model, and timer """
        self.tiles = []
        self.level.reset()
        self.game_over = False
        for row in range(self.level.row):
            current_row = []
            for col in range(self.level.col):
                tile = Tile(
                    label=Label(self.canvas, bg="#6270d1", font=("Cambria", 15), width=2, height=1, relief=RAISED),
                    row=row, column=col, value=self.level.grid[row][col])
                tile.label.grid(row=row, column=col, padx=0, pady=0)
                current_row.append(tile)
            self.tiles.append(current_row)
        self.reset_timer()
        self.reset_mine_counter()

    @staticmethod
    def reveal_tile(tile):
        """ Reveals tile """
        if not tile.is_revealed:
            tile.label.configure(text=tile.value, bg="#cad7e8", fg=COLORS.get(tile.value))
            tile.is_revealed = True

    def get_tile(self, label):
        """ Finds tile associated with widget """
        for row in self.tiles:
            for tile in row:
                if tile.label == label:
                    return tile
        return None

    def on_left_click(self, event):
        """ Called when user left-clicks """
        if self.game_over:
            self.reset()
            return

        tile = self.get_tile(event.widget)
        if tile is None or tile.is_revealed:
            return

        if not self.timer_is_running:
            self.timer_is_running = True

        if tile.value == "X":
            self.on_mine_reveal()
            return
        elif tile.value == "0":
            for coordinate in self.level.get_zero_chain(tile.row, tile.column):
                self.reveal_tile(self.tiles[coordinate[0]][coordinate[1]])
        else:
            self.level.checked_coordinates.append((tile.row, tile.column))
            self.reveal_tile(tile)

        self.check_win()

    def on_right_click(self, event):
        """ Called when user right-clicks """

        if self.game_over:
            return
        tile = self.get_tile(event.widget)
        if tile is None or tile.is_revealed:
            return

        if tile.is_flagged:
            tile.label.configure(text="")
            self.update_mine_counter(1)
            tile.is_flagged = False
            self.level.flagged_coordinates.remove((tile.row, tile.column))
        else:
            tile.label.configure(text="#", fg="red")
            self.update_mine_counter(-1)
            tile.is_flagged = True
            self.level.flagged_coordinates.append((tile.row, tile.column))

    def on_mine_reveal(self):
        """ Called when user hits mine """
        for coordinate in self.level.coordinates_of_mines:
            tile = self.tiles[coordinate[0]][coordinate[1]]
            self.reveal_tile(tile)
        for coordinate in self.level.flagged_coordinates:
            tile = self.tiles[coordinate[0]][coordinate[1]]
            if coordinate in self.level.coordinates_of_mines:
                tile.label.configure(fg="#23b709")
            else:
                tile.label.configure(fg="#d12b2b", bg="#cad7e8", text="X")
        self.game_over = True
        self.pause_timer()

    def check_win(self):
        """ Determines if user has won. (all tiles but mines revealed) """
        if ((self.level.row * self.level.col) - self.level.mines) == len(self.level.checked_coordinates):
            print("WINNER")
            self.game_over = True
            self.pause_timer()

    def timer_tick(self):
        """ Updates timer every second """
        if not TIMER_ENABLED:
            return

        if self.timer_is_running:
            current_time = int(self.timer.cget("text"))
            new_time = str(current_time + 1) if current_time + 1 < 999 else "999"
            while len(new_time) < 3:
                new_time = "0" + new_time
            self.timer.configure(text=new_time)
        self.root.after(1000, self.timer_tick)

    def reset_timer(self):
        """ Resets timer """
        self.timer.configure(text="000")
        self.timer_is_running = False

    def update_mine_counter(self, value):
        """ Updates mine counter by value """
        count = int(self.mine_counter.cget("text"))
        new_count = str(count + value) if count + value > 0 else "0"
        while len(new_count) < 3:
            new_count = "0" + new_count
        self.mine_counter.configure(text=new_count)

    def reset_mine_counter(self):
        """ Resets mine counter """
        amount = str(self.level.mines)
        while len(amount) < 3:
            amount = "0" + amount
        self.mine_counter.configure(text=amount)

    def pause_timer(self):
        """ Used to pause timer at end of game """
        self.timer_is_running = False


if __name__ == "__main__":
    App()
