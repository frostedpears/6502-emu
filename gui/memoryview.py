"""module level docstring"""
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font

APPNAME = 'Hex View'
BLOCK_WIDTH = 16
BLOCK_HEIGHT = 32
BLOCK_SIZE = BLOCK_WIDTH * BLOCK_HEIGHT
BLOCK_CHAR_WIDTH = (BLOCK_WIDTH * 3) - 1
UPPERCASE = False
ROM_START = 0x0
ROM_END = 0x6000
LINE_START = 0x0


def main():
    """function level docstring"""
    app = tk.Tk()
    p1 = tk.PhotoImage(file='./gui/icon.png')
    app.iconphoto(False, p1)
    style = ttk.Style(app)
    app.call('source', './gui/style/theme.tcl')
    style.theme_use('theme-dark')
    style.configure(
            'Vertical.TScrollbar', background=DC.backgroundAlt,
            arrowcolor='white', relief=tk.SOLID)

    app.title(APPNAME)
    window = MainWindow(app)
    app.protocol('WM_DELETE_WINDOW', window.quit)
    app.resizable(width=False, height=False)

    app.mainloop()


class MainWindow:

    def __init__(self, parent):
        # e = emu.emu6502()
        # e.writeAsm(dd63, 0xdd63)
        # sampleList = e.getRange(0xd000, 0xddc0)
        self.file_contents = None
        self.file_name = None

        self.parent = parent
        # self.show_block(sampleList, 0xd000)

    # ------------------------- widgets -------------------------

        self.window_frame = tk.Frame(
                self.parent, border=0, padx=4, pady=4,)

        self.toolbar_frame = tk.Frame(
                self.window_frame, border=0, padx=4, pady=4,)
        self.open_button = ttk.Button(
                self.toolbar_frame, text='Open', underline=0,
                command=self.open)
        self.quit_button = ttk.Button(
                self.toolbar_frame, text='Quit', underline=0,
                command=self.quit)
        self.paste_button = ttk.Button(
                self.toolbar_frame, text='Paste', command=self.paste)
        self.view_frame = tk.Frame(
                self.window_frame, border=0, padx=4, pady=4,)

        # create text boxes
        border_options = {'border': 0, 'padx': 4, 'pady': 0}
        self.header_text = tk.Text(
                self.view_frame, border_options,
                background=DC.backgroundAlt,
                height=1, width=BLOCK_CHAR_WIDTH + 24,)
        self.left_text = tk.Text(
                self.view_frame, border_options,
                background=DC.backgroundAlt,
                height=BLOCK_HEIGHT, width=4)
        self.view_text = tk.Text(
                self.view_frame, border_options,
                height=BLOCK_HEIGHT, width=BLOCK_CHAR_WIDTH)
        self.right_text = tk.Text(
                self.view_frame, border_options,
                background=DC.backgroundAlt,
                height=BLOCK_HEIGHT, width=16)

        # add styles and tags
        self.addTextStyle(self.header_text)
        self.addTextStyle(self.left_text)
        self.addTextStyle(self.view_text)
        self.addTextStyle(self.right_text)

        # insert values
        header_string = '     '
        header_string += '00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f'
        header_string += ' 0123456789abcdef  '
        self.header_text.insert('end', header_string, 'address')
        self.header_text['state'] = 'disabled'

        # create scrollbar
        self.uniscrollbar = ttk.Scrollbar(self.view_frame)

        self.uniscrollbar.config(command=self.scroll_all)
        self.left_text.config(yscrollcommand=self.update_scroll)
        self.view_text.config(yscrollcommand=self.update_scroll)
        self.right_text.config(yscrollcommand=self.update_scroll)

    # ------------------------- layout -------------------------
        # top level
        self.window_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # window frame
        self.toolbar_frame.grid(row=0, column=0, sticky=tk.NW)
        self.view_frame.grid(row=1, column=0, sticky=tk.NW)

        # toolbar
        self.open_button.grid(row=0, column=0, sticky=tk.W)
        # paste function in progress
        # self.paste_button.grid(row=0, column=1, sticky=tk.W)
        self.quit_button.grid(row=0, column=2, sticky=tk.W)

        # viewframe
        self.header_text.grid(
                row=1, column=0, columnspan=4, sticky=tk.NW)
        self.left_text.grid(row=2, column=0, sticky=tk.NW)
        self.view_text.grid(row=2, column=1, sticky=tk.NW)
        self.right_text.grid(row=2, column=2, sticky=tk.NW)
        self.uniscrollbar.grid(row=2, column=3, sticky=tk.NS)

    # ------------------------- styling -------------------------

    def addTextStyle(self, textBox):
        textBox.tag_configure('address', background=DC.backgroundAlt)
        textBox.tag_configure('ascii', foreground=DC.green1)
        textBox.tag_configure('highlight', background=DC.highlight)
        textBox.tag_configure('highlightAlt', background=DC.highlightAlt)

        bold = tk.font.Font(
                family='consolas', weight='bold', size=12)
        textBox.tag_configure('bold', font=bold)

        underline = tk.font.Font(
                family='consolas', underline=True, size=12)
        textBox.tag_configure('underline', font=underline)
        textBox.tag_raise('sel')
        return

    def toHex(self, number, places=2):
        case = 'X' if UPPERCASE else 'x'
        hexFormat = '{:0' + str(places) + case + '}'
        return hexFormat.format(number)

    # ------------------------- viewer -------------------------
    def show_block(self, byteList, addressStart):
        lineAddress = addressStart
        self.view_text['state'] = 'normal'
        self.left_text['state'] = 'normal'

        rows = [byteList[i:i + BLOCK_WIDTH]
                for i in range(0, len(byteList), BLOCK_WIDTH)]
        for row in rows:
            self.show_bytes(row, lineAddress)
            self.show_line(row)
            lineAddress += BLOCK_WIDTH
        self.view_text['state'] = 'disabled'
        self.left_text['state'] = 'disabled'
        self.right_text['state'] = 'disabled'

    def show_bytes(self, row, line_address):
        tags = ()
        self.left_text.insert(
                'end', self.toHex(line_address, 4), ('address'))
        self.left_text.insert('end', '\n')
        for i in range(0, len(row)):
            byte = row[i]
            if byte == 0x60:
                tags = ('highlight')
            else:
                tags = ()
            self.view_text.insert('end', self.toHex(byte), tags)
            if i < len(row) - 1:
                self.view_text.insert('end', ' ')
        if len(row) < BLOCK_WIDTH:
            self.view_text.insert('end', ' ' * (BLOCK_CHAR_WIDTH - len(row)))
        self.view_text.insert('end', '\n')

    def show_line(self, row):
        string = bytes(row).decode('ASCII', 'replace')
        tags = ()
        for char in string:
            if char in '\u2028\u2029\t\n\r\v\f\uFFFD':
                char = '.'
            elif 0x20 < ord(char) < 0x7F:
                tags = ('ascii')
            elif not 0x20 <= ord(char) <= 0xFFFF:  # Tcl/Tk limit
                char = '?'
            self.right_text.insert('end', char, tags)
        self.right_text.insert('end', '\n')

    # ------------------- file -------------------
    def open(self):
        self.left_text.delete("1.0", "end")
        self.view_text.delete("1.0", "end")
        self.right_text.delete("1.0", "end")
        name = filedialog.askopenfilename(title="Open — {}".format(APPNAME))
        self._open(name)

    def _open(self, name):
        if name and os.path.exists(name):
            self.parent.title("{} — {}".format(name, APPNAME))
            size = os.path.getsize(name)
            size = (size - BLOCK_SIZE if size > BLOCK_SIZE else
                    size - BLOCK_WIDTH)
            self.file_name = name
        if not self.file_name:
            return
        with open(self.file_name, "rb") as file:
            try:
                file.seek(ROM_START, os.SEEK_SET)
                self.file_contents = file.read(ROM_END - ROM_START)
            except Exception as e:
                print('error reading file')
                return
        self.show_block(self.file_contents, LINE_START)

    # ------------------------ scrollbar ------------------------
    def scroll_all(self, position):
        self.left_text.yview_moveto(position)
        self.view_text.yview_moveto(position)
        self.right_text.yview_moveto(position)

    def update_scroll(self, first, last):
        self.uniscrollbar.set(first, last)
        self.left_text.yview_moveto(first)
        self.view_text.yview_moveto(first)
        self.right_text.yview_moveto(first)

    # ------------------------- toolbar -------------------------
    def paste(self, event=None):
        clipString = ''
        try:
            clipString = self.parent.clipboard_get()
            # self.parent.clipboard_append(clipString)
            top = tk.Toplevel()
            top.geometry("600x400")
            top.title("Child Window")
            clipLabel = tk.Label(top, text=clipString, justify='left')
            clipLabel.place(x=0, y=0)
        except:
            print('clipboard empty')

    def quit(self, event=None):
        self.parent.destroy()


# ----------------------- style variables -----------------------
class DC(object):
    background = "#1E1E1E"
    backgroundAlt = "#cecece"
    backgroundAlt2 = "#d6d6d6"
    foreground = "#e4e4e4"
    highlight = "#76bce6"
    highlightAlt = "#bce6bc"

    lightGray = "#808080"
    gray84 = "#D4D4D4"
    coolGray46 = "#646695"
    red51 = "#f44747"
    red59 = "#ce7878"
    orange70 = "#d7ba7d"
    green1 = "#077707"
    green46 = "#6A9955"
    green73 = "#b5cea8"
    blue43 = "#007ACC"
    blue60 = "#569cd6"
    blue64 = "#6796e6"
    blue83 = "#9cdcfe"


if __name__ == '__main__':
    main()
