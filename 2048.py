from tkinter import *
from random import choice

COLORS = {
    "": "#cdc0b4",
    "2": "#eee4da",
    "4": "#ede0c8",
    "8": "#f2b179",
    "16": "#f59565",
    "32": "#f67c5f",
    "64": "#f65d3b",
    "128": "#edce71",
    "256": "#edcc63",
    "512": "#edc750",
    "1024": "#edc440",
    "2048": "#eec22e"
}


class App:

    def __init__(self):

        self.root = Tk()
        self.root.wm_minsize(width=900, height=900)
        self.root.config(bg="white")
        self.canvas = Canvas(self.root, bg="#bbada0", bd=0, highlightthickness=0)
        self.score_label = Label(self.root, bg="white", width=20, height=2, text="0", font=("Arial ", 50))

        self.score_label.pack()
        self.canvas.pack()

        self.tiles = None
        self.reset()

        self.root.bind("<Left>", lambda event, direction="left": self.swipe(direction))
        self.root.bind("<Right>", lambda event, direction="right": self.swipe(direction))
        self.root.bind("<Up>", lambda event, direction="up": self.swipe(direction))
        self.root.bind("<Down>", lambda event, direction="down": self.swipe(direction))
        # self.root.bind("<space>", lambda event: self.simulate())

    def reset(self):
        self.score_label.config(text="0")
        self.tiles = []

        for row in range(4):
            current_row = []
            for col in range(4):
                tile = Label(self.canvas, bg="#cdc0b4", text="", font=("Arial", 50), width=4, height=2)
                tile.grid(row=row, column=col, padx=7, pady=7)
                current_row.append(tile)
            self.tiles.append(current_row)
        self.add_random_tile()

    def swipe(self, direction):
        old_values = [[z.cget("text") for z in y] for y in [x for x in self.tiles]]

        if direction == "left":
            for row in self.tiles:
                values = [x.cget("text") for x in row if x.cget("text") != ""]

                # Combine pairs into one from left to right
                for i in range(1, len(values)):
                    if values[i] == values[i - 1]:
                        values[i - 1] = str(int(values[i - 1]) * 2)
                        values[i] = ""
                        self.update_score_by(values[i-1])

                # Refill row with empty slots to fill board again
                values = [x for x in values if x != ""]
                while len(values) < 4:
                    values.append("")
                for i in range(4):
                    row[i].config(text=values[i])

        elif direction == "right":
            for row in self.tiles:
                values = [x.cget("text") for x in row if x.cget("text") != ""]

                # Combine pairs into one from right to left
                for i in reversed(range(len(values) - 1)):
                    if values[i] == values[i + 1]:
                        values[i + 1] = str(int(values[i + 1]) * 2)
                        values[i] = ""
                        self.update_score_by(values[i + 1])
                values = [x for x in values if x != ""]

                # Refill row from start with empty slots to fill board again
                while len(values) < 4:
                    values.insert(0, "")
                for i in range(4):
                    row[i].config(text=values[i])

        elif direction == "up":
            for index in range(4):
                values = [row[index].cget("text") for row in self.tiles if row[index].cget("text") != ""]

                # Combine pairs into one from top to bottom
                for i in range(1, len(values)):
                    if values[i] == values[i - 1]:
                        values[i - 1] = str(int(values[i - 1]) * 2)
                        values[i] = ""
                        self.update_score_by(values[i-1])
                values = [x for x in values if x != ""]

                # Refill column from bottom with empty slots to fill board again
                while len(values) < 4:
                    values.append("")
                for row in range(4):
                    self.tiles[row][index].config(text=values[row])

        elif direction == "down":
            for index in range(4):
                values = [row[index].cget("text") for row in self.tiles if row[index].cget("text") != ""]

                # Combine pairs into one from bottom to top
                for i in reversed(range(len(values) - 1)):
                    if values[i] == values[i + 1]:
                        values[i + 1] = str(int(values[i + 1]) * 2)
                        values[i] = ""
                        self.update_score_by(values[i + 1])
                values = [x for x in values if x != ""]

                # Refill column from top with empty slots to fill board again
                while len(values) < 4:
                    values.insert(0, "")
                for row in range(4):
                    self.tiles[row][index].config(text=values[row])

        # Add new tile for next turn and check if moves are available
        if old_values != [[z.cget("text") for z in y] for y in [x for x in self.tiles]]:
            self.add_random_tile()
            if self.detected_loss():
                self.reset()

    def add_random_tile(self):
        empty_tiles = []
        options = ["2", "4"]
        for row in range(4):
            for col in range(4):
                if self.tiles[row][col].cget("text") == "":
                    empty_tiles.append(self.tiles[row][col])
        choice(empty_tiles).config(text=choice(options))
        self.update_color()

    def update_score_by(self, value):
        score = int(self.score_label.cget("text"))
        score += int(value)
        self.score_label.config(text=str(score))

    def update_color(self):
        for row in range(4):
            for col in range(4):
                tile = self.tiles[row][col]
                tile_text = self.tiles[row][col].cget("text")
                color = COLORS.get(tile_text)
                if color is not None:
                    tile.config(bg=color)
                else:
                    tile.config(bg="red")

    def detected_loss(self):
        values = [[z.cget("text") for z in y] for y in [x for x in self.tiles]]
        for row in range(4):
            for col in range(4):
                if values[row][col] == "":
                    return False
                a = values[row + 1][col] if row + 1 < 4 else None
                b = values[row - 1][col] if row - 1 > 0 else None
                c = values[row][col + 1] if col + 1 < 4 else None
                d = values[row][col - 1] if col - 1 > 0 else None
                for i in [a, b, c, d]:
                    if i == values[row][col]:
                        return False
        return True


if __name__ == "__main__":
    app = App()
    app.root.mainloop()
