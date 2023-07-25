import random
import tkinter as tk
from tkinter import *
#from tracker import Tracker

import threading
import time
#from timer import Timer
with open("words.txt") as word_file:
    random_words = [word.split("\n")[0] for word in word_file.readlines()]


class Timer(threading.Thread):

    def __init__(self, widget):
        threading.Thread.__init__(self)
        self.timer = 60
        self.widget = widget
        self.started = False

    def run(self):
        while self.timer > 0:
            time.sleep(1)
            self.timer -= 1
            self.widget.config(text=self.timer)


###the screen class is responsible for all the gui
###it also gives information to the implement tracker object (see description of Tracker Class)
class Screen:
    def __init__(self):
        self.tracker = Tracker(self)
        self.root = tk.Tk()
        self.root.title("Scrollable Box")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        self.frame = tk.Frame(self.root, bg='white', bd=0, highlightthickness=0)
        self.frame.pack()

        self.text_box = tk.Text(self.frame, bd=0, font=("arial", 30), height=3, width=46)
        self.text_box.pack(anchor=tk.CENTER)
        self.text_box.tag_configure("center", justify='center')
        self.text_box.insert("end", self.generate_line(3, random_words))
        self.text_box.tag_add("center", "1.0", "end")
        self.scrollbar = tk.Scrollbar(self.root, command=self.text_box.yview)
        self.text_box['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.time_label = Label(text=60)
        self.time_label.pack()

        self.timer = Timer(self.time_label)
        self.text = tk.StringVar()
        self.text.trace("w", lambda name, index, mode: self.tracker.check_characters(name, index, mode))
        self.entry_field = Entry(self.root, name="entry", textvariable=self.text)
        self.entry_field.pack()

        self.root.bind("<space>", self.tracker.check_word_and_get_new_word)
        self.count_label = Label(text=self.tracker.correct_word_count)
        self.count_label.pack()
        self.tracker.check_word_and_get_new_word(None)

        self.restart_btn = Button(text="Restart", command=self.restart)
        self.restart_btn.pack()


        self.root.mainloop()

    def scroll_down(self):
        scroll_to_index = float(float(self.text_box.index("end")) - 3)
        self.text_box.see(f"{scroll_to_index}")

    def change_char_color(self,color):
        tag_name = "color"
        self.text_box.tag_config(f"{self.tracker.line}.{self.tracker.pos}", foreground=color)
        self.text_box.tag_add(f"{self.tracker.line}.{self.tracker.pos}", f"{self.tracker.line}.{self.tracker.pos}")

    def mark_word(self, color):
        tag_name = f"{self.tracker.line}.{self.tracker.word_start}-{self.tracker.line}.{self.tracker.word_end + 1}"
        self.text_box.tag_config(tag_name, background=color)
        self.text_box.tag_add(tag_name, f"{self.tracker.line}.{self.tracker.word_start}", f"{self.tracker.line}.{self.tracker.word_end + 1}")

    def generate_line(self,num_lines, random_words):
        cur_text = ""
        for line_num in range(num_lines):
            new_line = [random.choice(random_words) for _ in range(6)]
            cur_text += " ".join(new_line) + "\n"

        return cur_text

    def restart(self):
        self.root.destroy()
        self.__init__()


###this class checks if the typed in character or word is correct
###it also detects the coordinates for the beginning and ending of a word
###the class is implemented in the screen class, in order to process the information of the screen
class Tracker():
    def __init__(self, screen_obj):
        self.screen_obj = screen_obj
        self.word_end = -2
        self.end_of_line = False
        self.line = 1
        self.correct_word = ""
        self.word_start = -2
        self.pos = -2
        self.correct_word_count = -1

    def check_characters(self,name, index, mode):
        if not self.screen_obj.timer.started:
            self.screen_obj.timer.started = True
            self.screen_obj.timer.start()

        if self.screen_obj.timer.timer != 0:

            cur_text = self.screen_obj.text.get()
            self.pos = self.word_start

            for char in cur_text:
                if self.screen_obj.text_box.get(f"{self.line}.{self.pos}") == char:
                    self.screen_obj.change_char_color("green")
                else:
                    self.screen_obj.change_char_color("red")

                self.screen_obj.text_box.tag_config(f"{self.line}.{self.pos + 1}", foreground="black")
                self.screen_obj.text_box.tag_add(f"{self.line}.{self.pos + 1}", "end")

                if self.pos <= self.word_end:
                    self.pos += 1
                elif self.end_of_line:
                    self.screen_obj.mark_word("white")

                    self.pos, self.word_end, self.word_start = -2, -2, -2
                    self.line += 1
                    if float(self.line + 3) == float(self.screen_obj.text_box.index("end")):
                        self.screen_obj.text_box.insert("end", self.screen_obj.generate_line(1, random_words))
                        self.screen_obj.scroll_down()

                    self.end_of_line = False
        else:
            self.screen_obj.entry_field["state"] = "disabled"

    def check_word_and_get_new_word(self,_):
        print([*self.correct_word], [*self.screen_obj.text.get()])
        tag_name = f"{self.line}.{self.word_start}-{self.line}.{self.word_end + 1}"
        print(self.word_start, self.word_end)
        if self.correct_word == self.screen_obj.text.get()[:-1]:
            self.correct_word_count += 1
            print("get called")
            self.screen_obj.count_label.config(text=self.correct_word_count)
        else:

            tag_name = f"{self.line}.{self.word_start}-{self.line}.{self.word_end + 1}"
            for index in range(self.word_start, self.word_end + 1):
                self.screen_obj.text_box.tag_config(f"{self.line}.{index}", foreground="red")
                self.screen_obj.text_box.tag_add(f"{self.line}.{index}", f"{self.line}.{index}")

        self.screen_obj.mark_word("white")
        self.screen_obj.entry_field.delete(0, "end")
        self.word_end += 1
        self.word_start = self.word_end + 1
        empty_space = False
        cur_word = ""
        while not empty_space:
            cur_char = self.screen_obj.text_box.get(f"{self.line}.{self.word_end + 1}")
            if cur_char == " ":
                empty_space = True
            elif cur_char == "\n":
                self.end_of_line = True
                empty_space = True
            else:
                cur_word += cur_char
                self.word_end += 1
        self.correct_word = cur_word

        self.screen_obj.mark_word("#add8e6")

        return "break"


screen = Screen()






