'''
code file: aimgui.py (AI Image GUI)
Modified: 7/4/2026
'''
import os
import sys
import base64
import time
import subprocess
from pathlib import Path
from time import localtime, strftime
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font
import configparser
from ttkbootstrap import *
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToolTip
from openai import OpenAI

class Application(Frame):
    ''' main class docstring '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=True, padx=4, pady=4)

        config = configparser.ConfigParser()
        config.read('aimgui.ini')
        self.MyModel = config['Main']['model']
        self.MyTheme = config['Main']['theme']
        self.MyFMgr = config['Main']['filemgr']
        self.MyPath = config['Main']['imgpath']

        # establish path for image files
        if self.MyPath != ".":
            self.images_path = self.MyPath
        else:
            self.images_path = str(Path.cwd() / "images")

        self.create_widgets()


    def create_widgets(self):
        ''' creates GUI for app '''

        self.vlbl3 = StringVar()
        lbl = Label(self, textvariable=self.vlbl3)
        lbl.grid(row=3, column=1, sticky='e')
        self.vlbl3.set('Number of Images')

        self.vlbl4 = StringVar()
        lbl = Label(self, textvariable=self.vlbl4)
        lbl.grid(row=4, column=1, sticky='e')
        self.vlbl4.set('Image Size')

        self.vlbl5 = StringVar()
        lbl5 = Label(self, textvariable=self.vlbl5)
        lbl5.grid(row=5, column=1, sticky='e')
        self.vlbl5.set('Input Image for Variation')
        ToolTip(lbl5, "Image must be png, square,\n256x256, 512x512, or 1024x1024")

        self.vlbl6 = StringVar()
        lbl6 = Label(self, textvariable=self.vlbl6)
        lbl6.grid(row=6, column=1, sticky='e')
        self.vlbl6.set('Quality')

        self.vlbl7 = StringVar()
        lbl7 = Label(self, textvariable=self.vlbl7)
        lbl7.grid(row=7, column=1, sticky='e')
        self.vlbl7.set('Background')

        self.vlbl8 = StringVar()
        lbl = Label(self, textvariable=self.vlbl8)
        lbl.grid(row=8, column=1, sticky='e')
        self.vlbl8.set('Text Prompt for Image Creation')

        self.vstatus = StringVar()
        lbl = Label(self, textvariable=self.vstatus)
        lbl.grid(row=11, column=1, columnspan=3)
        self.vstatus.set('Ready')

        # right side

        self.vspn = IntVar(value=0)
        spn = Spinbox(self, textvariable=self.vspn, from_=0, to=10, width=4)
        spn.grid(row=3, column=2, sticky='w', padx=4, pady=4)
        self.vspn.set(1)  # from aimgui.ini

        optionlist = ('', '1024x1024', '1024x1536', '1536x1024')
        self.vopt_size = StringVar()
        self.vopt_size.set(optionlist[1])  # from aimgui.ini
        opt_size = OptionMenu(self, self.vopt_size, *optionlist, bootstyle='outline')
        opt_size.grid(row=4, column=2, sticky='w', padx=4, pady=4)

        self.vvar_file = StringVar()
        # self.vvar_file.trace("w", self.eventHandler)
        self.var_file = Entry(self, textvariable=self.vvar_file)
        self.var_file.grid(row=5, column=2, sticky='w', padx=4, pady=4)

        btn_var_file = Button(self, text='Open',
                              command=self.btn_out_var_click, bootstyle='outline')
        btn_var_file.grid(row=5, column=3, sticky='w', padx=4, pady=4)
        ToolTip(btn_var_file,
                text="Image to modify",
                bootstyle=(INVERSE),
                wraplength=80)


        optionlist = ('', "low", "medium", "high", "auto")
        self.vopt_qual = StringVar()
        self.vopt_qual.set(optionlist[3])  # from aimgui.ini
        opt_qual = OptionMenu(self, self.vopt_qual, *optionlist, bootstyle='outline')
        opt_qual.grid(row=6, column=2, sticky='w', padx=4, pady=4)

        optionlist = ('', "transparent", "opaque", "auto")
        self.vopt_bkgd = StringVar()
        self.vopt_bkgd.set(optionlist[3])  # from aimgui.ini
        opt_qual = OptionMenu(self, self.vopt_bkgd, *optionlist, bootstyle='outline')
        opt_qual.grid(row=7, column=2, sticky='w', padx=4, pady=4)

        btn_var_file = Button(self, text='Images',
                              command=self.btn_images_click, bootstyle='outline')
        btn_var_file.grid(row=7, column=3, sticky='w', padx=4, pady=4)
        ToolTip(btn_var_file,
                text="View images directory",
                bootstyle=(INVERSE),
                wraplength=80)


        self.prompt = Text(self)
        self.prompt.grid(row=9, column=1, columnspan=3, sticky='ew', padx=4, pady=4)
        efont = Font(family="Arial", size=14)
        self.prompt.configure(font=efont)
        self.prompt.config(wrap="word", # wrap=NONE
                           undo=True, # Tk 8.4
                           width=30,
                           height=5,
                           padx=5, # inner margin
                           insertbackground='#fff',   # cursor color
                           tabs=(efont.measure(' ' * 4),))

        btn_create = Button(self, text='Create', command=self.btn_create_click)
        btn_create.grid(row=10, column=1, columnspan=2, sticky='ew', padx=4, pady=4)

        btn_close = Button(self, text='Close',
                           command=self.btn_close_click, bootstyle='outline')
        btn_close.grid(row=10, column=3, sticky='ew', padx=4, pady=4)

    #    _   _                 _ _
    #   | | | | __ _ _ __   __| | | ___ _ __ ___
    #   | |_| |/ _` | '_ \ / _` | |/ _ \ '__/ __|
    #   |  _  | (_| | | | | (_| | |  __/ |  \__ \
    #   |_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
    #

    def btn_images_click(self):
        ''' Opens the images directory with user's file manager '''
        subprocess.Popen([self.MyFMgr, self.images_path])


    def btn_out_var_click(self):
        ''' Select an image file to generate a variation on.
        "images" is a subdirectory of the application directory '''
        filename =  filedialog.askopenfilename(initialdir=self.images_path,
                    title = "Open Image File for Variation",
                    filetypes = (("png files", "*.png"),("all files", "*.*")))
        if filename is not None:
            self.vvar_file.set(filename)
            self.var_file.xview_moveto(1)  # scrolls to end of text in Entry

    def make_filename(self) -> str:
        ''' create a unique file name for image file '''
        timenow = strftime('%Y-%m-%d_%H-%M-%S', localtime())
        img_filename = "image_" + timenow + ".png"
        fpath = str(Path(self.images_path, img_filename))
        return fpath

    def btn_create_click(self):
        ''' Generate the Prompted Image or Image Variation '''
        # self.vspn         number of images SPINBOX
        # self.vopt_size    Image File Size OPTIONMENU
        # self.vvar_file    Image file name ENTRY (input image)
        # self.vopt_qual    Quality
        # self.vopt_bkgd    background
        # self.prompt       Prompt TEXT

        try:
            client = OpenAI(
            api_key = os.getenv("GPTKEY")  # openai API
            )
        except Exception as e:
            messagebox.showerror("Could Not Read Key file",
                       "Did you enter your Gpt Key?")
            return

        prompt_text = self.prompt.get("1.0", END)
        if len(prompt_text) < 4:
            messagebox.showerror("AimGUI", "Missing Text Prompt")
            return

        self.vstatus.set('Processing . . .')
        root.update_idletasks()

        try:  # VARIATION WITH PROMPT

            if self.vvar_file.get() != "":  # generate variation of an image

                filein = self.vvar_file.get()

                # Open your source image file
                with open(filein, "rb") as image_file:
                    response = client.images.edit(
                        model=self.MyModel,
                        image=image_file,
                        # Provide targeted instruction to guide the variation
                        prompt=prompt_text,
                        n=self.vspn.get(),
                        size=self.vopt_size.get(),
                        quality=self.vopt_qual.get()
                    )

            else:  # CREATE NEW FROM PROMPT

                response = client.images.generate(
                    model=self.MyModel,
                    prompt=prompt_text,
                    size=self.vopt_size.get(),
                    quality=self.vopt_qual.get(),        # Options: low, medium, high, auto
                    background=self.vopt_bkgd.get(),     # Options: transparent, opaque, auto
                    n=self.vspn.get()
                )

            # Extract and save the base64 image
            for x in range(0, self.vspn.get()):
                image_base64 = response.data[x].b64_json
                with open(self.make_filename(), "wb") as f:
                    f.write(base64.b64decode(image_base64))
                    time.sleep(1.5)  # wait 1.5 seconds

        except Exception as e:
            messagebox.showerror("Image Creation Problems", e)

        self.vstatus.set('Ready')


    def btn_close_click(self):
        ''' Close the Application '''
        save_location()


# change working directory to path for this file
p = os.path.realpath(__file__)
os.chdir(os.path.dirname(p))

# get options that go into the window creation and title
config = configparser.ConfigParser()
config.read('aimgui.ini')
MyTheme = config['Main']['theme']

root = Window("AI Image Generator 4.0", MyTheme)

def save_location(e=None):
    ''' executes at WM_DELETE_WINDOW event - see below '''
    with open("winfi", "w") as fout:
        fout.write(root.geometry())
    root.destroy()

if os.path.isfile("winfi"):
    with open("winfi") as f:
        lcoor = f.read()
    root.geometry(lcoor.strip())
else:
    root.geometry("475x435") # WxH+left+top

try:
    icon_img = PhotoImage(file="AIcon.png")
    root.iconphoto(True, icon_img)
except Exception:
    pass

root.protocol("WM_DELETE_WINDOW", save_location)  # UNCOMMENT TO SAVE GEOMETRY INFO
root.resizable(0, 0) # no resize & removes maximize button
Application(root)
root.mainloop()
