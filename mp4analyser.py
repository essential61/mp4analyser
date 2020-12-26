"""
mp4analyser.py

A tkinter application that allows inspection of MP4 files that conform to ISO/IEC 14496-12

This file generates the user interface, and contains the callback functions that respond to user events.


"""

import os
import logging
import json
import binascii
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
# mp4 is the package that actually parses the mp4 file
import mp4.iso

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
        # uncomment desired logging level
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
        #logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING)

        self.mp4file = None
        self.dialog_dir = os.path.expanduser("~")

        # build ui
        self.title("MP4 Analyser")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.geometry('1300x700')

        # create left-right paned window
        self.p = ttk.Panedwindow(self, orient=HORIZONTAL)
        self.p.grid(column=0, row=0, sticky=(N, W, E, S))

        # create top-bottom paned window
        self.p1 = ttk.Panedwindow(self.p, orient=VERTICAL)
        self.p1.grid(column=0, row=0, sticky=(N, W, E, S))

        # first pane shown on left:
        self.f1 = ttk.Labelframe(self.p, text='Box Hierarchy')
        self.f1.grid(column=0, row=0, sticky=(N, W, E, S))
        self.f1.columnconfigure(0, weight=1)
        self.f1.rowconfigure(0, weight=1)

        # box details shown top right
        self.f2 = ttk.Labelframe(self.p1, text='Box Details', width=750, )  # second pane
        self.f2.grid(column=0, row=0, sticky=(N, W, E, S))
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)

        # hex view shown bottom right
        self.f3 = ttk.Labelframe(self.p1, text='Hex View', width=750, )  # second pane
        self.f3.grid(column=0, row=0, sticky=(N, W, E, S))
        self.f3.columnconfigure(0, weight=1)
        self.f3.rowconfigure(0, weight=1)

        # add seems to work left to right, top to bottom
        self.p.add(self.f1)
        self.p.add(self.p1)
        self.p1.add(self.f2)
        self.p1.add(self.f3)

        # tree view showing box hierarchy
        self.tree = ttk.Treeview(self.f1, show="tree")
        self.tree.grid(column=0, row=0, sticky=(N, W, E, S))
        self.tree.column("#0", width=300)

        # Sub-classed auto hiding scroll bar
        self.scroll1 = AutoScrollbar(self.f1, orient=VERTICAL, command=self.tree.yview)
        self.scroll1.grid(column=1, row=0, sticky=(N, S))
        self.tree['yscrollcommand'] = self.scroll1.set
        self.tree.bind('<ButtonRelease-1>', self.select_box)

        # text widget display details of selected box
        self.t = ReadOnlyText(self.f2, state='normal', width=120, height=24, wrap='none')
        self.t.grid(column=0, row=0, sticky=(N, W, E, S))
        self.t.bind('<ButtonRelease-1>', self.check_if_selection)

        # Sub-classed auto hiding scroll bar
        self.scroll2 = AutoScrollbar(self.f2, orient=VERTICAL, command=self.t.yview)
        self.scroll2.grid(column=1, row=0, sticky=(N, S))
        self.t['yscrollcommand'] = self.scroll2.set

        # text widget displaying hex
        self.thex = ReadOnlyText(self.f3, state='normal', width=120, height=15, wrap='none')
        self.thex.grid(column=0, row=0, sticky=(N, W, E, S))
        self.thex.bind('<ButtonRelease-1>', self.check_if_selection)

        # Sub-classed auto hiding scroll bar
        self.scroll3 = AutoScrollbar(self.f3, orient=VERTICAL, command=self.thex.yview)
        self.scroll3.grid(column=1, row=0, sticky=(N, S))
        self.thex['yscrollcommand'] = self.scroll3.set

        # Sub-classed auto hiding scroll bar
        self.scroll4 = AutoScrollbar(self.f3, orient=HORIZONTAL, command=self.thex.xview)
        self.scroll4.grid(column=0, row=1, sticky=(W, E))
        self.thex['xscrollcommand'] = self.scroll4.set

        # build a menu bar
        self.option_add('*tearOff', FALSE)
        self.menubar = Menu(self)

        self.filemenu = Menu(self.menubar)
        self.filemenu.add_command(label="Open...", command=self.open_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.copymenu = Menu(self.menubar)
        self.copymenu.add_command(label="Copy Selection", command=self.copy_selection, state="disabled")
        self.copymenu.add_separator()
        self.copymenu.add_command(label="\"Box Details\" - Select All",
                                  command=lambda: self.select_all(self.t), state="disabled")
        self.copymenu.add_command(label="\"Hex View\" - Select All",
                                  command=lambda: self.select_all(self.thex), state="disabled")
        self.menubar.add_cascade(label="Copy", menu=self.copymenu)

        self.config(menu=self.menubar)

        # status bar
        self.statustext = StringVar()
        self.statustext.set("")
        self.status = Label(self, textvariable=self.statustext, bd=1, anchor=W)
        self.status.grid(column=0, row=1, columnspan=2, sticky=(W, E, S))

    def open_file(self):
        """ Callback on selecting 'Open' from menu """
        filename = filedialog.askopenfilename(filetypes=(("MP4 Files", ".mp4 .m4*"),
                                                         ("All Files", "*.*")), initialdir=self.dialog_dir)
        if not(len(filename)):
            return
        logging.debug("Loading file " + filename)
        self.statustext.set("Loading...")
        self.update_idletasks()
        new_file = mp4.iso.Mp4File(filename)
        logging.debug("Finished loading file " + filename)
        # sanity check that it is an ISO BMFF file
        if (len(new_file.child_boxes) == 0) or (
                len(new_file.child_boxes) == 1 and isinstance(new_file.child_boxes[0], mp4.non_iso.UndefinedBox)):
            logging.error(filename + " does not appear to be a valid ISO BMFF file.")
            messagebox.showerror(message=filename + " does not appear to be a valid ISO BMFF file.")
            return
        self.mp4file = new_file
        self.dialog_dir, filename_base = os.path.split(filename)
        self.title("MP4 Analyser - {0:s}".format(filename_base))
        # Clear tree and text widgets if not empty
        self.tree.delete(*self.tree.get_children())
        self.t.delete(1.0, END)
        self.thex.delete(1.0, END)
        self.copymenu.entryconfig("\"Box Details\" - Select All", state="disabled")
        self.copymenu.entryconfig("\"Hex View\" - Select All", state="disabled")
        # Now fill tree with new contents
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
                                for l6, this_box in enumerate(this_box.child_boxes):
                                    l6_iid = "{0}.{1}.{2}.{3}.{4}.{5}.{6}".format(l0, l1, l2, l3, l4, l5, l6)
                                    self.tree.insert(l5_iid, 'end', l6_iid, text=l6_iid + " " + this_box.type,
                                                     open=TRUE)
                                    for l7, this_box in enumerate(this_box.child_boxes):
                                        l7_iid = "{0}.{1}.{2}.{3}.{4}.{5}.{6}.{7}".format(l0, l1, l2, l3, l4, l5, l6,
                                                                                          l7)
                                        self.tree.insert(l6_iid, 'end', l7_iid, text=l7_iid + " " + this_box.type,
                                                         open=TRUE)
        logging.debug("Summary " + json.dumps(self.mp4file.get_summary(), indent=2))
        logging.debug("Finished populating " + filename)
        self.statustext.set("")
        self.update_idletasks()

    def select_box(self, a):
        """ Callback on selecting an Mp4 box in treeview """
        logging.debug("Box selected " + self.tree.focus())
        self.statustext.set("Loading...")
        self.update_idletasks()
        if self.tree.focus()[0:5] == 'chunk':
            self.select_chunk_details(self.tree.focus())
        elif self.tree.focus()[0:6] == 'sample':
            self.select_sample_details(self.tree.focus())
        else:
            self.select_box_details(self.tree.focus())
        self.statustext.set("")
        self.update_idletasks()

    def select_chunk_details(self, item_id):
        """ if tree item selected is a media chunk (or equivalent 'run' for fragmented mp4) """
        idx_chunk = int(item_id.split('_')[1])
        idx_mdat = int(self.tree.parent(item_id))
        chunk_dict = self.mp4file.child_boxes[idx_mdat].sample_list[idx_chunk]
        self.populate_text_widget(json.dumps(chunk_dict, indent=2))
        if 'chunk_offset' in chunk_dict:
            byte_offset = chunk_dict['chunk_offset']
            last_sample = chunk_dict['chunk_samples'][-1]
        else:
            byte_offset = chunk_dict['run_offset']
            last_sample = chunk_dict['run_samples'][-1]
        num_bytes = (last_sample['offset'] + last_sample['size']) - byte_offset
        self.populate_hex_text_widget(self.mp4file.read_bytes(byte_offset, num_bytes))

    def select_sample_details(self, item_id):
        """ if tree item selected is a media sample """
        idx_sample = int(item_id.split('.')[1])
        parent_id = self.tree.parent(item_id)
        idx_chunk = int(parent_id.split('_')[1])
        idx_mdat = int(self.tree.parent(parent_id))
        if 'chunk_samples' in self.mp4file.child_boxes[idx_mdat].sample_list[idx_chunk]:
            sample_dict = self.mp4file.child_boxes[idx_mdat].sample_list[idx_chunk]['chunk_samples'][idx_sample]
        else:
            sample_dict = self.mp4file.child_boxes[idx_mdat].sample_list[idx_chunk]['run_samples'][idx_sample]
        self.populate_text_widget(json.dumps(sample_dict, indent=2))
        byte_offset = sample_dict['offset']
        num_bytes = sample_dict['size']
        self.populate_hex_text_widget(self.mp4file.read_bytes(byte_offset, num_bytes))

    def select_box_details(self, item_id):
        """ if tree item selected is 'box' or 'atom' """
        # item id is in the form  n.n.n as text
        l = [int(i) for i in item_id.split('.')]
        box_selected = None
        if len(l) == 1:
            box_selected = self.mp4file.child_boxes[l[0]]
            # specific case of mdat box selected and chunks/samples in mdat not yet loaded in tree
            if box_selected.type == 'mdat' and box_selected.sample_list and not self.tree.get_children(item_id):
                self.populate_tree_with_samples_in_mdat(item_id)
        elif len(l) == 2:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]]
        elif len(l) == 3:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]]
        elif len(l) == 4:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]].child_boxes[l[3]]
        elif len(l) == 5:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]].child_boxes[
                l[3]].child_boxes[l[4]]
        elif len(l) == 6:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]].child_boxes[
                l[3]].child_boxes[l[4]].child_boxes[l[5]]
        elif len(l) == 7:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]].child_boxes[
                l[3]].child_boxes[l[4]].child_boxes[l[5]].child_boxes[l[6]]
        elif len(l) == 8:
            box_selected = self.mp4file.child_boxes[l[0]].child_boxes[l[1]].child_boxes[l[2]].child_boxes[
                l[3]].child_boxes[l[4]].child_boxes[l[5]].child_boxes[l[6]].child_boxes[l[7]]
        logging.debug("Populating text widgets")
        self.prepare_string_for_text_widget(box_selected)
        logging.debug("Upper text widget populated")
        self.populate_hex_text_widget(box_selected.get_bytes())
        logging.debug("Hex text widget populated")

    def populate_tree_with_samples_in_mdat(self, mdat_id):
        # for large files may take a few seconds to load
        self.populate_text_widget("Loading Samples...")
        self.update_idletasks()
        mdat = self.mp4file.child_boxes[int(mdat_id)]
        for chunk_idx, chunk in enumerate(mdat.sample_list):
            if 'chunk_ID' in chunk:
                item_text = "track {0}, chunk {1}".format(chunk['track_ID'], chunk['chunk_ID'])
                self.tree.insert(mdat_id, 'end', "chunk_{0}".format(chunk_idx), text=item_text)
                for sample_idx, sample in enumerate(chunk['chunk_samples']):
                    item_text = "sample {0}".format(sample['sample_ID'])
                    self.tree.insert("chunk_{0}".format(chunk_idx), 'end',
                                     "sample_{0}.{1}".format(chunk_idx, sample_idx), text=item_text)
            else:  # fragmented mp4 uses term "run" instead of "chunk" but is otherwise same
                item_text = "track {0}, seq {1}, run {2}".format(chunk['track_ID'], chunk['sequence_number'],
                                                                 chunk['run_ID'])
                self.tree.insert(mdat_id,
                                 'end',
                                 "chunk-{0}_{1}".format(chunk['sequence_number'], chunk_idx),
                                 text=item_text)
                for sample_idx, sample in enumerate(chunk['run_samples']):
                    item_text = "sample {0}".format(sample['sample_ID'])
                    self.tree.insert("chunk-{0}_{1}".format(chunk['sequence_number'], chunk_idx),
                                     'end',
                                     "sample-{0}_{1}.{2}".format(chunk['sequence_number'], chunk_idx, sample_idx),
                                     text=item_text)

    def prepare_string_for_text_widget(self, box_selected):
        my_string = "Box is {0:d} ({0:#x}) bytes from beginning of file.\n\n".format(box_selected.start_of_box)
        my_string += "Has header:\n{0:s}\n\n".format(json.dumps(box_selected.header.get_header()))
        if len(box_selected.box_info) > 0:
            # insertion order is preserved in modern Python
            my_string += "Has values:\n{0:s}\n\n".format(json.dumps(box_selected.box_info, indent=2))
        if len(box_selected.child_boxes) > 0:
            my_string += "Has child boxes:\n" + json.dumps([box.type for box in box_selected.child_boxes])
        self.populate_text_widget(my_string)

    def populate_text_widget(self, the_string):
        self.t.delete(1.0, END)
        self.t.insert(END, the_string)
        self.copymenu.entryconfig("\"Box Details\" - Select All", state="normal")

    def populate_hex_text_widget(self, my_byte_list):
        bytes_per_line = 32  # Num bytes per line
        # trunc_size = arbitrary max. number of bytes to display in hex view to prevent tk text widget barfing.
        # change to suit
        trunc_size = 100000
        self.thex.delete(1.0, END)
        trunc = False
        if len(my_byte_list) > trunc_size:
            my_byte_list = my_byte_list[:trunc_size]
            trunc = True
        hex_string = ''
        for i in range(0, len(my_byte_list), bytes_per_line):
            byte_line = my_byte_list[i:i + bytes_per_line]
            # which is better 256 or 65536? Maybe 65536 for east asian subs
            char_line = "".join([k if k.isprintable() and ord(k) < 65536 else '.'
                                 for k in byte_line.decode('utf-8', "replace")])
            hex_line = binascii.b2a_hex(byte_line).decode('utf-8')
            pretty_hex_line = " ".join([hex_line[j:j + 2] for j in range(0, len(hex_line), 2)])
            pretty_hex_line = pretty_hex_line.ljust(3 * bytes_per_line)
            hex_string += pretty_hex_line + '\t' + char_line + '\n'
        logging.debug("Hex text processed")
        if trunc:
            self.thex.insert(END, 'Hex view, showing first {0:d} bytes: \n{1:s}'.format(trunc_size, hex_string))
        else:
            self.thex.insert(END, 'Hex view: \n{0:s}'.format(hex_string))
        self.copymenu.entryconfig("\"Hex View\" - Select All", state="normal")

    def copy_selection(self):
        self.clipboard_clear()
        if self.t.tag_ranges(SEL):
            self.clipboard_append(self.t.get(*self.t.tag_ranges(SEL)))
        if self.thex.tag_ranges(SEL):
            self.clipboard_append(self.thex.get(*self.thex.tag_ranges(SEL)))

    def check_if_selection(self, a):
        # event occurs for either widget not both, but we want to check both
        if self.t.tag_ranges(SEL) or self.thex.tag_ranges(SEL):
            self.copymenu.entryconfig("Copy Selection", state="normal")
        else:
            self.copymenu.entryconfig("Copy Selection", state="disabled")

    def select_all(self, twidget):
        twidget.tag_add(SEL, "1.0", "end")
        self.copymenu.entryconfig("Copy Selection", state="normal")


if __name__ == '__main__':
    myapp = MyApp()
    myapp.mainloop()
