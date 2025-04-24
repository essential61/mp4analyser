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

import sys
sys.path.append(os.path.dirname(__file__))
# mp4analyser is the package that actually parses the mp4 file
import mp4analyser.iso
# mkvanalyser is the package that parse tje matroska file
import mkvanalyser.mkv
from mkvanalyser.idlookups import id_table

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
        #logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING)

        self.containerfile = None
        self.dialog_dir = os.path.expanduser("~")

        # I don't know if there's a better a way, but this works
        self.popup_focus = None

        # build ui
        self.title("MP4 Analyser")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # This code is to get monitor size as winfo_screenwidth() may not be useful in multi-monitor env.
        # Does cause a flicker though
        t = Tk()  # new temp window
        t.attributes('-fullscreen', True)  # maximize the window
        t.update()
        width = int(t.winfo_width() * 0.75)
        height = int(t.winfo_height() * 0.75)
        t.destroy()
        self.geometry(f'{width}x{height}')

        # create tabbed notebook
        self.nb = ttk.Notebook(self)
        self.nb.grid(column=0, row=0, sticky=N+W+E+S)

        # create left-right paned window and add to tabbed notebook
        self.p = ttk.Panedwindow(self.nb, orient=HORIZONTAL)
        self.nb.add(self.p, text="Box Information", padding=(5, 10, 5, 5))

        # create top-bottom paned window
        self.p1 = ttk.Panedwindow(self.p, orient=VERTICAL)
        self.p1.grid(column=0, row=0, sticky=N+W+E+S)

        # first pane shown on left:
        self.f1 = ttk.Labelframe(self.p, text='Box Hierarchy')
        self.f1.grid(column=0, row=0, sticky=N+W+E+S)
        self.f1.columnconfigure(0, weight=1)
        self.f1.rowconfigure(0, weight=1)

        # box details shown top right
        self.f2 = ttk.Labelframe(self.p1, text='Box Details', width=750, )  # second pane
        self.f2.grid(column=0, row=0, sticky=N+W+E+S)
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)

        # hex view shown bottom right
        self.f3 = ttk.Labelframe(self.p1, text='Hex View', width=750, )  # second pane
        self.f3.grid(column=0, row=0, sticky=N+W+E+S)
        self.f3.columnconfigure(0, weight=1)
        self.f3.rowconfigure(0, weight=1)

        # add seems to work left to right, top to bottom
        self.p.add(self.f1)
        self.p.add(self.p1)
        self.p1.add(self.f2)
        self.p1.add(self.f3)

        # tree view showing box hierarchy
        self.tree = ttk.Treeview(self.f1, show="tree")
        self.tree.grid(column=0, row=0, sticky=N+W+E+S)
        self.tree.column("#0", width=300)

        # Sub-classed auto hiding scroll bar
        self.scroll1 = AutoScrollbar(self.f1, orient=VERTICAL, command=self.tree.yview)
        self.scroll1.grid(column=1, row=0, sticky=N+S)
        self.tree['yscrollcommand'] = self.scroll1.set
        self.tree.bind('<ButtonRelease-1>', self.select_box)

        # text widget display details of selected box
        self.t = ReadOnlyText(self.f2, state='normal', width=120, height=24, wrap='none')
        self.t.grid(column=0, row=0, sticky=N+W+E+S)
        self.t.bind('<ButtonRelease-1>', self.check_if_selection)
        self.t.bind("<Button-3>", self.popup_sel)

        # Sub-classed auto hiding scroll bar
        self.scroll2 = AutoScrollbar(self.f2, orient=VERTICAL, command=self.t.yview)
        self.scroll2.grid(column=1, row=0, sticky=N+S)
        self.t['yscrollcommand'] = self.scroll2.set

        # Sub-classed auto hiding scroll bar
        self.scroll3 = AutoScrollbar(self.f2, orient=HORIZONTAL, command=self.t.xview)
        self.scroll3.grid(column=0, row=1, sticky=W+E)
        self.t['xscrollcommand'] = self.scroll3.set

        # text widget displaying hex
        self.thex = ReadOnlyText(self.f3, state='normal', width=120, height=15, wrap='none')
        self.thex.grid(column=0, row=0, sticky=N+W+E+S)
        self.thex.bind('<ButtonRelease-1>', self.check_if_selection)
        self.thex.bind("<Button-3>", self.popup_sel)

        # Sub-classed auto hiding scroll bar
        self.scroll4 = AutoScrollbar(self.f3, orient=VERTICAL, command=self.thex.yview)
        self.scroll4.grid(column=1, row=0, sticky=N+S)
        self.thex['yscrollcommand'] = self.scroll4.set

        # Sub-classed auto hiding scroll bar
        self.scroll5 = AutoScrollbar(self.f3, orient=HORIZONTAL, command=self.thex.xview)
        self.scroll5.grid(column=0, row=1, sticky=W+E)
        self.thex['xscrollcommand'] = self.scroll5.set

        # create a frame and as second tab to notebook
        self.f4 = ttk.Frame(self.nb)
        self.nb.add(self.f4, text="File Summary")

        # text widget display summary
        self.tsum = ReadOnlyText(self.f4, state='normal')
        self.tsum.pack(expand=True, fill='both')
        self.tsum.bind('<ButtonRelease-1>', self.check_if_selection)
        self.tsum.bind("<Button-3>", self.popup_sel)

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
        self.menubar.add_cascade(label="Copy", menu=self.copymenu)
        self.config(menu=self.menubar)

        # pop-up menu
        self.rclickmenu = Menu(self.tsum)
        self.rclickmenu.add_command(label="Copy Selection", command=self.copy_selection, state="disabled")
        self.rclickmenu.add_command(label="Select All", command=self.select_all)

        # status bar
        self.statustext = StringVar()
        self.statustext.set("")
        self.status = Label(self, textvariable=self.statustext, bd=1, anchor=W)
        self.status.grid(column=0, row=1, columnspan=2, sticky=W+E+S)

        # set ratios of panes
        self.update_idletasks()
        self.p.sashpos(0, int(self.p.winfo_width() / 4))
        self.p1.sashpos(0, int(3 * self.p1.winfo_height() / 4))

    def open_file(self):
        """ Callback on selecting 'Open' from menu """
        filename = filedialog.askopenfilename(filetypes=(("All Files", "*.*"), ("MP4 Files", ".mp4 .m4s .m4a .m4v"),
                                                         ("MKV Files", ".mkv .webm")), initialdir=self.dialog_dir)
        if not(len(filename)):
            return
        logging.debug("Loading file " + filename)
        self.statustext.set("Loading...")
        self.update_idletasks()
        matroska = False
        with open(filename, 'rb') as f:
            if f.read(4) in (b'\x1a\x45\xdf\xa3', b'\x1f\x43\xb6\x75'):
                matroska = True
        if matroska:
            self.populate_ui(mkvanalyser.mkv.MkvFile(filename))
        else:
            self.populate_ui(mp4analyser.iso.Mp4File(filename))
        logging.debug("Finished loading file " + filename)

        self.statustext.set("")
        self.update_idletasks()

    def item_string(self, container):
        '''  item_string returns appropriate container type depending on whether file is mp4 or matroska '''
        if type(self.containerfile) == mp4analyser.iso.Mp4File:
            return container.type
        else:
            if container.elementid in id_table:
                return id_table[container.elementid]['name']
            else:
                return 'Unknown'

    def populate_ui(self, new_file):
        # sanity check that it is a valid file
        if (len(new_file.children) == 0) or (
                len(new_file.children) == 1 and isinstance(new_file.children[0], mp4analyser.non_iso.UndefinedBox)):
            logging.error(new_file.filename + " does not appear to be a valid Container file.")
            messagebox.showerror(message=new_file.filename + " does not appear to be a valid Container file.")
            return
        self.containerfile = new_file
        self.dialog_dir, filename_base = os.path.split(self.containerfile.filename)
        self.title("MP4 Analyser - {0:s}".format(filename_base))
        # Clear tree and text widgets if not empty
        self.tree.delete(*self.tree.get_children())
        self.t.delete(1.0, END)
        self.thex.delete(1.0, END)
        self.tsum.delete(1.0, END)
        self.tsum.insert(END, json.dumps(self.containerfile.get_summary(), indent=2))

        # Now fill tree with new contents
        for l0, this_box in enumerate(self.containerfile.children):
            self.tree.insert('', 'end', str(l0), text=str(l0) + " " + self.item_string(this_box), open=TRUE)
            self.walk_the_boxes(this_box, [l0])
        logging.debug("Summary " + json.dumps(self.containerfile.get_summary(), indent=2))
        logging.debug("Finished populating " + self.containerfile.filename)

    def walk_the_boxes(self, parent_box, parent_tree_index):
        ''' populate the tree view widget using recursion '''
        parent_item = '.'.join([str(indice) for indice in parent_tree_index])
        for i, this_box in enumerate(parent_box.children):
            this_item = parent_item + '.' + str(i)
            self.tree.insert(parent_item, 'end', this_item, text=this_item + " " + self.item_string(this_box), open=TRUE)
            tree_index = parent_tree_index + [i]
            self.walk_the_boxes(this_box, tree_index)

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
        idx_chunk = int((item_id.split('_')[1]).split('_')[0])
        idx_mdat = int(self.tree.parent(item_id))
        chunk_dict = self.containerfile.children[idx_mdat].sample_list[idx_chunk]
        self.populate_text_widget(json.dumps(chunk_dict, indent=2))
        if 'chunk_offset' in chunk_dict:
            byte_offset = chunk_dict['chunk_offset']
            last_sample = chunk_dict['chunk_samples'][-1]
        else:
            byte_offset = chunk_dict['run_offset']
            last_sample = chunk_dict['run_samples'][-1]
        num_bytes = (last_sample['offset'] + last_sample['size']) - byte_offset
        self.populate_hex_text_widget(self.containerfile.read_bytes(byte_offset, num_bytes))

    def select_sample_details(self, item_id):
        """ if tree item selected is a media sample """
        idx_sample = int((item_id.split('.')[1]).split('_')[0])
        parent_id = self.tree.parent(item_id)
        idx_chunk = int((parent_id.split('_')[1]).split('_')[0])
        idx_mdat = int(self.tree.parent(parent_id))
        if 'chunk_samples' in self.containerfile.children[idx_mdat].sample_list[idx_chunk]:
            sample_dict = self.containerfile.children[idx_mdat].sample_list[idx_chunk]['chunk_samples'][idx_sample]
        else:
            sample_dict = self.containerfile.children[idx_mdat].sample_list[idx_chunk]['run_samples'][idx_sample]
        self.populate_text_widget(json.dumps(sample_dict, indent=2))
        byte_offset = sample_dict['offset']
        num_bytes = sample_dict['size']
        self.populate_hex_text_widget(self.containerfile.read_bytes(byte_offset, num_bytes))

    def get_descendant(self, parent_box, tree_index):
        """ walk down the tree to get selected box """
        if len(tree_index) > 1:
            new_parent_box = parent_box.children[tree_index.pop(0)]
            return self.get_descendant(new_parent_box, tree_index)
        else:
            return parent_box.children[tree_index[0]]

    def select_box_details(self, item_id):
        """ if tree item selected is 'box' or 'atom' """
        # item id is in the form  n.n.n as text
        l = [int(i) for i in item_id.split('.')]
        box_selected = None
        if len(l) == 1:
            box_selected = self.containerfile.children[l[0]]
            # specific case of mdat box selected and chunks/samples in mdat not yet loaded in tree
            if box_selected.type == 'mdat' and box_selected.sample_list and not self.tree.get_children(item_id):
                self.populate_tree_with_samples_in_mdat(item_id)
        elif len(l) > 1:
            box_selected = self.get_descendant(self.containerfile.children[l.pop(0)], l)
        else:
            logging.debug("This shouldn't happen")
        logging.debug("Populating text widgets")
        self.prepare_string_for_text_widget(box_selected)
        logging.debug("Upper text widget populated")
        self.populate_hex_text_widget(box_selected.get_bytes())
        logging.debug("Hex text widget populated")

    def populate_tree_with_samples_in_mdat(self, mdat_id):
        # for large files may take a few seconds to load
        self.populate_text_widget("Loading Samples...")
        self.update_idletasks()
        mdat = self.containerfile.children[int(mdat_id)]
        for chunk_idx, chunk in enumerate(mdat.sample_list):
            if 'chunk_ID' in chunk:
                item_text = "track {0}, chunk {1}".format(chunk['track_ID'], chunk['chunk_ID'])
                self.tree.insert(mdat_id, 'end', "chunk_{0}_mdat_{1}".format(chunk_idx, mdat_id), text=item_text)
                for sample_idx, sample in enumerate(chunk['chunk_samples']):
                    item_text = "sample {0}".format(sample['sample_ID'])
                    self.tree.insert("chunk_{0}_mdat_{1}".format(chunk_idx, mdat_id), 'end',
                                     "sample_{0}.{1}_mdat_{2}".format(chunk_idx, sample_idx, mdat_id), text=item_text)
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
        if type(self.containerfile) == mp4analyser.iso.Mp4File:
            my_string = "Box is {0:d} ({0:#x}) bytes from beginning of file.\n\n".format(box_selected.start_of_box)
            my_string += "Has header:\n{0:s}\n\n".format(json.dumps(box_selected.header.get_header()))
            my_string += "Has version: {0:d}\n".format(box_selected.version) if hasattr(box_selected, 'version') else ""
            my_string += "Has flags: {0:#08x}\n\n".format(box_selected.flags) if hasattr(box_selected, 'flags') else ""
            if len(box_selected.box_info) > 0:
                # insertion order is preserved in modern Python
                my_string += "Has values:\n{0:s}\n\n".format(json.dumps(box_selected.box_info, indent=2))
            if len(box_selected.children) > 0:
                my_string += "Has child boxes:\n" + json.dumps([box.type for box in box_selected.children])
        else:
            name = id_table[box_selected.elementid]['name'] if box_selected.elementid in id_table else 'unknown'
            my_string = "Element {0:s} ({1:#x}) is {2:d} ({2:#x}) bytes from beginning of file.\n\n".format(
                name, box_selected.elementid,
                box_selected.element_position)
            my_string += "Data Type: {0:s}\n".format(box_selected.type)
            if box_selected.unknown_datasize:
                my_string += "Data Length: Unknown\n"
            else:
                my_string += "Data Length: {0:d} bytes\n".format(box_selected.datasize)
            if box_selected.elementid in [0xA1, 0xA3]:
                my_string += "Has values:\n{0:s}\n\n".format(json.dumps(box_selected.datavalue, indent=2))
            else:
                my_string += "Data Value: " + f'{box_selected.datavalue}' + "\n\n"
            my_string += id_table[box_selected.elementid]['documentation'] if box_selected.elementid in id_table else ""
            if box_selected.elementid in id_table and 'enum' in id_table[box_selected.elementid]:
                my_string += "\nEnumeration:\n"
                for k, v in id_table[box_selected.elementid]['enum'].items():
                    my_string += "{0:d}, {1:s}\n".format(k, v)
        self.populate_text_widget(my_string)

    def populate_text_widget(self, the_string):
        self.t.delete(1.0, END)
        self.t.insert(END, the_string)

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

    def popup_sel(self, e):
        self.popup_focus = e.widget
        self.check_if_selection(e)
        self.rclickmenu.tk_popup(e.x_root, e.y_root)

    def copy_selection(self):
        self.clipboard_clear()
        if self.popup_focus.tag_ranges(SEL):
            self.clipboard_append(self.popup_focus.get(*self.popup_focus.tag_ranges(SEL)))

    def check_if_selection(self, a):
        self.popup_focus = a.widget
        # event occurs for any text widget
        if self.popup_focus.tag_ranges(SEL):
            self.copymenu.entryconfig("Copy Selection", state="normal")
            self.rclickmenu.entryconfig("Copy Selection", state="normal")
        else:
            self.copymenu.entryconfig("Copy Selection", state="disabled")
            self.rclickmenu.entryconfig("Copy Selection", state="disabled")

    def select_all(self):
        self.popup_focus.tag_add(SEL, "1.0", "end")
        self.copymenu.entryconfig("Copy Selection", state="normal")
        self.rclickmenu.entryconfig("Copy Selection", state="normal")


if __name__ == '__main__':
    myapp = MyApp()
    myapp.mainloop()
