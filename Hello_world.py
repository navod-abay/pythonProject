import model
import view
import controller
import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        self.model = model.Model()
        self.view = view.View(self)
        self.controller = controller.Controller(self.model, self.view)
        self.mainloop()

if __name__ == '__main__':
    App()