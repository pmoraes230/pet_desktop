import customtkinter as ctk

class Modal(ctk.CTkToplevel):

    def __init__(self, master, title, message):
        super().__init__(master)
        self.title(title)
        self.geometry("350x200")
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text=message).pack(pady=20)
        ctk.CTkButton(self, text="OK", command=self.destroy).pack()
