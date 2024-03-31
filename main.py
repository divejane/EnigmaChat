import tkinter as tk


class Gui:

    def __init__(self) -> None:
        self.window = tk.Tk()

        self.window.geometry(
            f"{int(self.window.winfo_screenwidth()/1.5)}x{int(self.window.winfo_screenheight()/1.5)}"
        )

        self.window.config(bg="#222222")

        self.window.title("Discreet Dial")

        self.entry = tk.Text(self.window, bg="#222222", fg="#FFFFFF", width=int(self.window.winfo_screenwidth()/1.5), font=("Courier", 30), height=5)
        self.entry.pack(side="bottom")

    def loop(self) -> None:
        self.window.mainloop()


root = Gui()

root.loop()
