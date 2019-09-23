import mp4box
import os

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
try:
    from idlelib.redirector import WidgetRedirector
except ImportError:
    raise Exception("Python > 3.6 needed. Also idle3 needs to be installed on your system")


# From http://effbot.org/zone/tkinter-autoscrollbar.htm
# a scrollbar that hides itself if it's not needed.  only
# works if you use the grid geometry manager.
class AutoScrollbar(ttk.Scrollbar):

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)


# See https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
# note idle3 dependency
class ReadOnlyText(Text):

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


class MyApp(Tk):

    def __init__(self):
        super().__init__()
        self.mp4file = None
        # build ui
        self.title("MP4 Analyser")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.geometry('900x600')
        self.option_add('*tearOff', FALSE)
        self.menubar = Menu(self)

        self.filemenu = Menu(self.menubar)
        self.filemenu.add_command(label="Open...", command=self.open_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.config(menu=self.menubar)

        self.p = ttk.Panedwindow(self, orient=HORIZONTAL)
        self.p.grid(column=0, row=0, sticky=(N, W, E, S))

        # first pane, which would get widgets gridded into it:
        self.f1 = ttk.Labelframe(self.p, text='Pane1')
        self.f1.grid(column=0, row=0, sticky=(N, W, E, S))
        self.f1.columnconfigure(0, weight=1)
        self.f1.rowconfigure(0, weight=1)

        self.f2 = ttk.Labelframe(self.p, text='Pane2')  # second pane
        self.f2.grid(column=0, row=0, sticky=(N, W, E, S))
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)
        self.p.add(self.f1)
        self.p.add(self.f2)

        self.tree = ttk.Treeview(self.f1, show="tree")
        self.tree.grid(column=0, row=0, sticky=(N, W, E, S))
        self.tree.column("#0", width=250)
        # Sub-classed auto hiding scroll bar
        self.scroll = AutoScrollbar(self.f1, orient=VERTICAL, command=self.tree.yview)
        self.scroll.grid(column=1, row=0, sticky=(N, S))
        self.tree['yscrollcommand'] = self.scroll.set
        self.tree.bind('<ButtonRelease-1>', self.select_box)

        self.t = Text(self.f2, state='disabled', width=80, height=24, wrap='none')
        self.t.grid(column=0, row=0, sticky=(N, W, E, S))

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*")),
                                              initialdir=os.path.expanduser("~"))
        self.mp4file = mp4box.Mp4File(filename)
        self.title("MP4 Analyser" + " - " + os.path.basename(filename))
        # Clear tree if not empty
        self.tree.delete(*self.tree.get_children())
        # Now fill it with new contents
        for l0, this_box in enumerate(self.mp4file.child_boxes):
            self.tree.insert('', 'end', str(l0), text=str(l0) + " " + this_box.type, open=TRUE)
            for l1, this_box in enumerate(this_box.child_boxes):
                l1_iid = "{0}.{1}".format(l0, l1)
                self.tree.insert(str(l0), 'end', l1_iid, text=l1_iid + " " + this_box.type, open=TRUE)
                for l2, this_box in enumerate(this_box.child_boxes):
                    l2_iid = "{0}.{1}.{2}".format(l0, l1, l2)
                    self.tree.insert(l1_iid, 'end', l2_iid, text=l2_iid + " " + this_box.type, open=TRUE)
                    for l3, this_box in enumerate(this_box.child_boxes):
                        l3_iid = "{0}.{1}.{2}.{3}".format(l0, l1, l2, l3)
                        self.tree.insert(l2_iid, 'end', l3_iid, text=l3_iid + " " + this_box.type, open=TRUE)
                        for l4, this_box in enumerate(this_box.child_boxes):
                            l4_iid = "{0}.{1}.{2}.{3}.{4}".format(l0, l1, l2, l3, l4)
                            self.tree.insert(l3_iid, 'end', l4_iid, text=l4_iid + " " + this_box.type, open=TRUE)
                            for l5, this_box in enumerate(this_box.child_boxes):
                                l5_iid = "{0}.{1}.{2}.{3}.{4}.{5}".format(l0, l1, l2, l3, l4, l5)
                                self.tree.insert(l4_iid, 'end', l5_iid, text=l5_iid + " " + this_box.type, open=TRUE)

    def select_box(self, a):
        my_id = self.tree.focus()
        if len(my_id) == 1:
            box_selected = self.mp4file.child_boxes[int(my_id[0])]
        elif len(my_id) == 3:
            box_selected = self.mp4file.child_boxes[int(my_id[0])].child_boxes[int(my_id[2])]
        elif len(my_id) == 5:
            box_selected = self.mp4file.child_boxes[int(my_id[0])].child_boxes[int(my_id[2])].child_boxes[int(my_id[4])]
        elif len(my_id) == 7:
            box_selected = \
                self.mp4file.child_boxes[int(my_id[0])].child_boxes[int(my_id[2])].child_boxes[
                    int(my_id[4])].child_boxes[
                    int(my_id[6])]
        elif len(my_id) == 9:
            box_selected = \
                self.mp4file.child_boxes[int(my_id[0])].child_boxes[int(my_id[2])].child_boxes[
                    int(my_id[4])].child_boxes[
                    int(my_id[6])].child_boxes[int(my_id[8])]
        elif len(my_id) == 11:
            box_selected = \
                self.mp4file.child_boxes[int(my_id[0])].child_boxes[int(my_id[2])].child_boxes[
                    int(my_id[4])].child_boxes[
                    int(my_id[6])].child_boxes[int(my_id[8])].child_boxes[int(my_id[10])]
        self.populate_text_widget(box_selected)

    def populate_text_widget(self, box_selected):
        self.t['state'] = 'normal'
        self.t.delete(1.0, END)
        self.t.insert(END, "Box is located at position " + "{0:#x}".format(box_selected.start_of_box) +
                      " from start of from file\n\n")
        self.t.insert(END, "Has header " + box_selected.header.get_header() + "\n\n")
        if len(box_selected.box_info) > 0:
            self.t.insert(END, "Has values " + box_selected.get_box_data() + "\n\n")
        if len(box_selected.get_children()) > 0:
            self.t.insert(END, "Has child boxes " + box_selected.get_children() + "\n\n")
        self.t['state'] = 'disabled'


if __name__ == '__main__':
    myapp = MyApp()
    myapp.mainloop()
