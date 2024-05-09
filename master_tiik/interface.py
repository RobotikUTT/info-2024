import tkinter as tk
from threading import Thread
import time
import tkthread


class InterfaceManager(Thread):
    def __init__(self):
        super().__init__()
        self.root = None
        
    def run(self):
        self.root = tk.Tk()
        self.root.mainloop()

    def request_team(self):
        interface = RequestTeamInterface()
        tkthread.call_nosync(lambda: self.create_interface(interface))
        while interface.team is None:
            pass
        tkthread.call_nosync(lambda: self.delete_interface(frame))
        return interface.team

    def create_interface(self, interface):
        frame = tk.Frame(self.root)
        frame.pack()
        interface.pack(frame)

    def delete_interface(self, frame):
        del frame
        


class RequestTeamInterface:
    
    def __init__(self):
        self.team = None

    def pack(self, root):
        tk.Button(root, text="Jaune", command=self.on_yellow_button).pack()
        tk.Button(root, text="Bleu", command=self.on_blue_button).pack()
        
    def on_yellow_button():
        self.team = "yellow"
        
    def on_blue_button():
        self.team = "blue"

if __name__ == "__main__":
    im = InterfaceManager()
    im.start()
    print(im.request_team())
