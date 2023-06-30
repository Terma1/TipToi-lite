from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import os
from miner import PDFMiner
from tkinter import simpledialog

class PDFViewer:
    def __init__(self, master):
        self.path = None
        self.fileisopen = None
        self.name = None
        self.current_page = 0
        self.numPages = None
        self.master = master
        self.master.title('PDF Viewer')
        self.master.geometry('580x520+440+180')
        self.master.resizable(width=0, height=0)
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)
        self.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open File", command=self.open_file)
        self.filemenu.add_command(label="Exit", command=self.master.destroy)
        self.top_frame = ttk.Frame(self.master, width=580, height=460)
        self.top_frame.grid(row=0, column=0)
        self.top_frame.grid_propagate(False)
        self.bottom_frame = ttk.Frame(self.master, width=580, height=50)
        self.bottom_frame.grid(row=1, column=0)
        self.bottom_frame.grid_propagate(False)
        self.scrolly = Scrollbar(self.top_frame, orient=VERTICAL)
        self.scrolly.grid(row=0, column=1, sticky=(N, S))
        self.scrollx = Scrollbar(self.top_frame, orient=HORIZONTAL)
        self.scrollx.grid(row=1, column=0, sticky=(W, E))
        self.output = Canvas(self.top_frame, bg='#ECE8F3', width=560, height=435)
        self.output.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        self.output.grid(row=0, column=0)
        self.scrolly.configure(command=self.output.yview)
        self.scrollx.configure(command=self.output.xview)
        self.upbutton = ttk.Button(self.bottom_frame, text="Previous", command=self.previous_page)
        self.upbutton.grid(row=0, column=1, padx=(270, 5), pady=8)
        self.downbutton = ttk.Button(self.bottom_frame, text="Next", command=self.next_page)
        self.downbutton.grid(row=0, column=3, pady=8)
        self.page_label = ttk.Label(self.bottom_frame, text='page')
        self.page_label.grid(row=0, column=4, padx=5)
        self.add_text_button = ttk.Button(self.bottom_frame, text="Add Text", command=self.add_text)
        self.add_text_button.grid(row=0, column=5, padx=5)
        self.save_button = ttk.Button(self.bottom_frame, text="Save", command=self.save_file)
        self.save_button.grid(row=0, column=6, padx=5)

        self.circle_radius = 1.5
        self.circle_ids = []  # список идентификаторов кружков

    def open_file(self):
        filepath = fd.askopenfilename(title='Select a PDF file', initialdir=os.getcwd(), filetypes=(('PDF', '*.pdf'),))
        if filepath:
            self.path = filepath
            filename = os.path.basename(self.path)
            self.miner = PDFMiner(self.path)
            data, numPages = self.miner.get_metadata()
            self.current_page = 0
            if numPages:
                self.name = data.get('title', filename[:-4])
                self.numPages = numPages
                self.fileisopen = True
                self.display_page()
                self.master.title(self.name)

    def display_page(self):
        if 0 <= self.current_page < self.numPages:
            self.img_file = self.miner.get_page(self.current_page)
            self.output.create_image(0, 0, anchor='nw', image=self.img_file)
            self.stringified_current_page = self.current_page + 1
            self.page_label['text'] = str(self.stringified_current_page) + ' of ' + str(self.numPages)
            region = self.output.bbox(ALL)
            self.output.configure(scrollregion=region)

    def next_page(self):
        if self.fileisopen:
            if self.current_page <= self.numPages - 1:
                self.current_page += 1
                self.display_page()

    def previous_page(self):
        if self.fileisopen:
            if self.current_page >= 1:
                self.current_page -= 1
                self.display_page()

    def add_text(self):
        if self.fileisopen:
            text = simpledialog.askstring("Add Text", "Enter text to add:")
            if text:
                self.output.bind("<Button-1>", lambda event: self.place_circle(event.x, event.y, text))

    def place_circle(self, x, y, text):
        dpi = 50
        radius = self.cm_to_pixels(self.circle_radius, dpi)
        x1 = x - radius
        y1 = y - radius
        x2 = x + radius
        y2 = y + radius
        # Удаление предыдущих кружков
        for circle_id in self.circle_ids:
            self.output.delete(circle_id)
        self.circle_ids = []
        # Создание нового кружка
        circle_id = self.output.create_oval(x1, y1, x2, y2, fill="white")
        self.output.tag_bind(circle_id, "<Button-1>", lambda event: self.start_dragging(event, circle_id))
        self.output.tag_bind(circle_id, "<B1-Motion>", self.move_circle)
        self.output.tag_bind(circle_id, "<ButtonRelease-1>", self.stop_dragging)
        self.circle_ids.append(circle_id)

    def start_dragging(self, event, circle_id):
        self.circle_id = circle_id
        self.start_x = event.x
        self.start_y = event.y

    def move_circle(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.output.move(self.circle_id, delta_x, delta_y)
        self.start_x = event.x
        self.start_y = event.y

    def stop_dragging(self, event):
        pass

    def save_file(self):
        if self.fileisopen:
            filepath = fd.asksaveasfilename(title='Save PDF file', defaultextension='.pdf',
                                            filetypes=(('PDF', '*.pdf'),))
            if filepath:
                self.miner.save(filepath)

    @staticmethod
    def cm_to_pixels(cm, dpi):
        return int(cm * dpi / 2.54)


root = Tk()
pdf = PDFViewer(root)
root.mainloop()
