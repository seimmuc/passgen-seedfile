import base64
import hashlib
from pathlib import Path
from tkinter import ttk, Tk, StringVar, filedialog, W, E

import pyperclip


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, height=500, width=500)

        self.columnconfigure(0, weight=3, pad=10)
        self.columnconfigure(1, weight=1, pad=1)
        self.rowconfigure(1, pad=10)

        self.seed_file_str = StringVar(master=self)
        self.seed_file_input = ttk.Entry(master=self, textvariable=self.seed_file_str, width=40)
        self.seed_file_input.grid(column=0, row=0, sticky=W)

        self.seed_file_picker = ttk.Button(master=self, text='Open seed file', command=self.pick_file)
        self.seed_file_picker.grid(column=1, row=0, sticky=E)

        self.gen_pass_button = ttk.Button(master=self, text="Generate", command=self.action_generate)
        self.gen_pass_button.grid(column=0, columnspan=2, row=1)
        self.seed_file_input.bind('<Key-Return>', self.action_generate)

        self.result_str = StringVar(master=self, value='ready')
        self.result_label = ttk.Label(master=self, relief='ridge', width=40, textvariable=self.result_str)
        self.result_label.grid(column=0, row=2)

        self.copy_btn = ttk.Button(master=self, text='Copy', command=self.action_copy)
        self.copy_btn.grid(column=1, row=2)

        self.password: str | None = None
        self._copied_id: int | None = None
        self._next_id = 0

    def pick_file(self):
        fh = filedialog.askopenfile(mode='r', parent=self, title='Select seed file')
        if fh is None:
            return
        file_path = Path(fh.name).resolve()
        if file_path.is_file():
            self.seed_file_str.set(str(file_path))

    def action_generate(self, event=None):
        fp_str = self.seed_file_str.get()
        file_path = Path(fp_str)
        if not file_path.is_file():
            self.password = None
            self.result_str.set('not a file')
            return
        with file_path.open('rb') as f:
            self.password = base64.b64encode(hashlib.sha512(f.read(4096)).digest()).decode('ascii')[:32]
            self.result_str.set(f'Password: {self.password[:5]}...')

    def action_copy(self):
        if self.password is None:
            self.result_str.set('No password to copy')
            return
        password = self.password
        cid = self._next_id
        self._copied_id = cid
        self._next_id = cid + 1
        pyperclip.copy(password)
        self.after(3 * 1000, lambda: self.clear_clipboard(copy_id=cid, content=password))
        self.result_str.set(f'Copied password: {password[:5]}...')

    def clear_clipboard(self, copy_id: int = None, content: str = None):
        if copy_id is not None and copy_id != self._copied_id:
            return
        if content is not None:
            cc: str = pyperclip.paste()
            if cc.strip() != content.strip():
                return
        pyperclip.copy('.')
        pyperclip.copy('')
        self._copied_id = None
        self.result_str.set('Cleared clipboard')

    def on_close(self):
        print('closing window')
        if self._copied_id:
            self.clear_clipboard(copy_id=self._copied_id, content=self.password)


def create_window() -> Tk:
    root = Tk()
    # root.geometry("500x500")
    app = App(root)
    app.pack()

    def close():
        app.on_close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)

    return root


if __name__ == '__main__':
    win = create_window()
    win.mainloop()
