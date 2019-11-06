from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
from tkinter import simpledialog

from PIL import Image, ImageDraw, ImageTk, ImageFont,ImageChops
from math import cos, sin, sqrt, radians, floor
import math
import datetime

import random
import os
import ast
import ctypes

import sqlite3
from sqlite3 import Error

from fpdf import FPDF

class PackFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        controller.bottomframe = Frame(self, width=width,height=height)
        controller.bottomframe.grid(row=0,column=0)

        """pretty confident this has gotta move"""
        def modAll(var, state):
            for index, i in enumerate(var):
                var[index].set(state)

    def getbox(self):
        answer = simpledialog.askinteger("Input", "Open 1-20 boxes",
                                         parent=self,
                                         minvalue=1, maxvalue=20)
        if answer == None: answer = 1
        self.pack_menubar.entryconfig(4, label=str(answer))

    def generate(self,conn,varlist,pack_type,packs_qty):
        setmenu_VarList = varlist
        cur = conn.cursor()
        packtype=pack_type
        qty_packs=packs_qty
        cardlist = []
        pdf = FPDF()
        pdf.set_font('Arial', 'B', 10)

        """Grab the sets that are turned on"""
        setsenabled = []
        for x, i in enumerate(setmenu_VarList):
            if i.get() == 1:
                setsenabled.append(self.setname[x])

        for p in range(1, qty_packs + 1):
            print("opening pack", p, "of", qty_packs)
            pdf.add_page()

            minilist = []
            selected_set = random.choice(setsenabled)
            for x in self.SETS:
                if x[1] == selected_set: short = x[0]  # a crude way to set the short form of your selected set
            if packtype.get() == str(0):  # 0 is standard pack
                cur.execute(
                    "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \"" + selected_set + "\" AND \"rarity\" = \"common\"")
                commons = cur.fetchall()
                cur.execute(
                    "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \"" + selected_set + "\" AND \"rarity\" = \"uncommon\"")
                uncommons = cur.fetchall()
                if random.choice([1, 2, 3]) == 1:
                    rare = "very rare"
                else:
                    rare = "rare"
                cur.execute(
                    "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \"" + selected_set + "\" AND \"rarity\" = \"" + rare + "\"")
                rares = cur.fetchall()
                for x in range(4):
                    mini = random.choice(commons)
                    commons.remove(mini)
                    minilist.append(mini)
                for x in range(2):
                    mini = random.choice(uncommons)
                    uncommons.remove(mini)  # no duplicates
                    minilist.append(mini)
                minilist.append(random.choice(rares))

                # CREATES THE CARDS AND RENDERS THEM ON SCREEN
                rw = 0
                for x, i in enumerate(minilist):
                    card = ("./cards/" + short + "{:02d}".format(i[0]) + ".jpg")
                    im = Image.open(card)
                    width, height = im.size
                    sizesm = int(width / 6), int(height / 3)
                    imback = im.crop((width / 2, 0, width, height))

                    imbacksm = imback.resize(sizesm, resample=Image.ANTIALIAS)
                    imfront = im.crop((0, 0, width / 2, height))
                    cardlist.append(imback)

                    imback.save("tmp\\" + str(p) + "_" + str(x) + "temp.png")
                    imbacksm.save("tmp\\" + str(p) + "_" + str(x) + "temp_sm.png")
                    load = Image.open("tmp\\" + str(p) + "_" + str(x) + "temp.png")
                    load_sm = Image.open("tmp\\" + str(p) + "_" + str(x) + "temp_sm.png")
                    render = ImageTk.PhotoImage(load)
                    render_sm = ImageTk.PhotoImage(load_sm)
                    img = Label(self.bottomframe,image=render_sm, width=int(width / 6), height=int(height / 3))
                    img.image = render_sm
                    col = x % 4
                    if (x % 4 == 0): rw += 1
                    img.grid(row=rw, column=col)

                # READS THE TEMPORARY PNGS CREATED AND PUTS THEM ON A PDF PAGE
                rw = 0
                size = 65
                width = 64
                height = width * 1.39
                pdf.text(x=10, y=5, txt="Pack " + str(p) + " - " + str(selected_set))
                pdf.rect(x=73, y=191, w=width, h=height)
                pdf.rect(x=138, y=191, w=width, h=height)
                offset = 0
                for x, i in enumerate(minilist):
                    col = x % 3
                    if (x % 3 == 0): rw += 1
                    pdf.image("tmp\\" + str(p) + "_" + str(x) + "temp.png", x=col * size + 8,
                              y=rw * size * 1.39 - 80, w=width, h=height)  # , x=10, y=8, w=100)
                    if x == 4 or x == 6: offset += 4
                    pdf.text(x=143, y=201 + x * 4 + offset, txt=str(i[2]) + "  [" + str(i[0]) + "]")

        time = datetime.datetime.now()
        time = (str(time)[-6:])
        pdf.output("./packs/packname" + time + ".pdf")

class DbFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        setfilter = False
        filename=""
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        controller.popup()

        topframe = Frame(self, width=width)
        topframe.grid(row=0,column=0)
        bottomframe = Frame(self, width=width,height=height)
        bottomframe.grid(row=2,column=0)

        controller.colheadVar = []
        controller.headers = ["name", "set", "id", "faction", "rarity", "cost", "size", "hit points", "defense", "attack",
                   "damage", "special abilities", "force points", "force powers", "count"]
        for x, i in enumerate(controller.headers):
             controller.colheadVar.append(StringVar(self))
             print (x,i)
             Label (topframe,text=i,width=len(i)).grid(row=0, column=x)
             Entry (topframe,width=len(i),textvariable=controller.colheadVar[x]).grid(row=1, column=x)
        controller.lb1 = Listbox(bottomframe,width=200,height=100)#,selectmode=EXTENDED)
        controller.lb1.grid(row=0,column=0)
        controller.lb1.bind('<Double-1>', lambda x: controller.sendcharacter(controller.lb1.get(controller.lb1.index(controller.lb1.curselection()))))
        datarows = []
        #columnwidth=[20,12,3,10,4,3,5,3,3,3,3,20,3,20]
        #tableheight = 50
        #tablewidth = len(columnnames)



        def loadplayer():
            filename = filedialog.askopenfilename(initialdir = "./players")
            if filename is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            print (filename)
            db_menubar.entryconfig(2,label="Custom")
            setfilter = True
            """do something to mod the count column with the file you get"""
            #DbFrame.refreshfilters()

    def refreshfilters(self):#conn,varlist,pack_type,packs_qty):):
        columnwidth = [20, 12, 3, 10, 4, 3, 5, 3, 3, 3, 3, 20, 3, 20]
        row_format = "{:<20}  {:>12}  {:<3}  {:10}  {:4}  {:3}  {:5}  {:3}  {:3}  {:3}  {:3}  {:20}  {:3}  {:20}  {:5}"  # left or right align, with an arbitrary '8' column width
        self.lb1.delete(1,1000)
        statements =[False] * 16
        statements[0] = "SELECT * FROM minis_list "
        #if setfilter: statements[0]+
        first = False
        for x,i in enumerate(self.colheadVar,1):
            val=i.get()
            filtered=""
            if val:
                if not first:
                    first=True
                    if ">" in val or "<" in val: statements[x] = "WHERE \"" + self.headers[x-1] + "\" "+ val
                    else: statements[x] = "WHERE \"" + self.headers[x-1] + "\" LIKE \"%" + val + "%\""
                else :
                    if ">" in val or "<" in val: statements[x] = " AND \"" + self.headers[x-1] + "\" "+ val
                    else: statements[x]=" AND \""+self.headers[x-1]+"\" LIKE \"%"+val+"%\""
        command =""
        for x in statements:
            if x: command += str(x)
        print(command)
        cur = self.conn.cursor()
        cur.execute(command)
        table = cur.fetchall()
        for x,i in enumerate(table):  # Rows
            temp = i[1:]
            self.lb1.insert(x,i[1:])

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("SW Minis Drafter")
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.overrideredirect(1)
        self.geometry("%dx%d+0+0" % (w, h))
        self.focus_set()  # <-- move focus to this widget
        self.bind("<Escape>", lambda e: e.widget.quit())

        database = "./DB/SWminis.db"
        self.conn = self.create_connection(database)

        mainFrame = Frame(self)
        mainFrame.grid(column=0, row=0)

        self.frames = {}
        for F in (PackFrame, DbFrame):
            page_name = F.__name__
            frame = F(parent=mainFrame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.db_menubar = Menu(self)
        self.db_menubar.add_cascade(label="Refresh Filters", command=lambda: DbFrame.refreshfilters(self))
        self.db_menubar.add_cascade(label="Load Player File", command=lambda: DbFrame.loadplayer())
        self.db_menubar.add_command(label="All Minis")
        self.db_menubar.add_command(label="Pack Generator", command=lambda: self.show_frame("PackFrame"))
        self.db_menubar.add_cascade(label="Close", command=lambda: self.safeclose())

        """----------------------------------------------------------------------------------------------------------"""
        self.SETS = [["ae", "Alliance and Empire"],
                     ["bh", "Booty Hunters"],
                     ["ae", "Alliance and Penis"],
                     ["cotf", "Champions of the Force"],
                     ["cs", "Clone Strike"],
                     ["cw", "The Clone Porn"],
                     ["fu", "The Force Unleashed"],
                     ["gaw", "Galaxy at War"],
                     ["ie", "Imperial Entanglements"],
                     ["ja", "Jedi Academy"],
                     ["kotor", "Knights of the Old Republic"],
                     ["lotf", "Legacy of the Farts"],
                     ["motf", "Masters of the Force"],
                     ["rots", "Revenge of the Sluts"],
                     ["rs", "Rebel Storm"],
                     ["tdt", "High Times"],
                     ["uh", "Universe"]]
        self.FACTIONS = ["Rebel", "Imperial", "The Old Republic", "The New Republic", "Sith", "Republic", "Seperatist",
                         "Yuuzhan Vong", "Mandolorian", "Fringe"]

        self.setname = []
        for x in (self.SETS):
            self.setname.append(x[1])
        self.packtypes = ["Standard Pack", "Commons", "Uncommons", "Rares", "Very Rares", "Uniques", "Non-Unique"]
        self.pack_menubar = Menu(self)
        setlist_menu = Menu(self.pack_menubar)
        pack_menu = Menu(self.pack_menubar)
        self.config(menu=self.db_menubar)

        setmenu_VarList = []  # a list containing lists of variables for checkbox states
        packtype = StringVar(self)

        self.pack_menubar.add_cascade(label="Sets", underline=0, menu=setlist_menu)
        self.pack_menubar.add_cascade(label="Pack Type", underline=0, menu=pack_menu)
        self.pack_menubar.add_command(label="Change Box Count",
                                 command=lambda: PackFrame.getbox(self)),  # command=lambda : DoSomethingWithInput(a.get))
        self.pack_menubar.add_command(label="1")
        qty_packs = 1
        self.pack_menubar.add_command(label="Go", underline=0, command=lambda: PackFrame.generate(self,self.conn,setmenu_VarList,packtype,qty_packs))
        self.pack_menubar.add_separator()
        self.pack_menubar.add_command(label="DB Browser", command=lambda: self.show_frame("DbFrame"))

        self.pack_menubar.add_command(label="quit", command=lambda: self.safeclose())

        for _ in enumerate(self.setname): setmenu_VarList.append(IntVar(self))
        for i in setmenu_VarList: i.set(1)

        setlist_menu.add_command(label="All", command=lambda: modAll(setmenu_VarList, 1))
        setlist_menu.add_command(label="None", command=lambda: modAll(setmenu_VarList, 0))
        setlist_menu.add_separator()
        for index, i in enumerate(self.setname):
            setlist_menu.add_checkbutton(label=i, variable=setmenu_VarList[index], onvalue=1, offvalue=0)

        for index, i in enumerate(self.packtypes):
            pack_menu.add_radiobutton(label=i, variable=packtype, value=index)
        packtype.set(0)
        DbFrame.refreshfilters(self)

    def show_frame(self, page_name): #swaps the left frame from editor to generator controls
        frame = self.frames[page_name]
        frame.tkraise()
        self.program = page_name
        if page_name == "PackFrame":
            self.config(menu=self.pack_menubar)
        elif page_name == "DbFrame":
            self.config(menu=self.db_menubar)

    def safeclose(self):
        print("do stuff before closing, like closing open files/db connections?")
        self.destroy()

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    #once DB is validated this is pointless... but could be good to parse out all abilities
    def abilitychecker(self,conn,check):
        abilities =[]
        cur = conn.cursor()

        command =  "SELECT COUNT() FROM minis_list WHERE minis_list.\""+check+"\" is not NULL"
        cur.execute(command)
        count = cur.fetchone()[0]
        print (count)

        command = "SELECT minis_list.\""+check+"\" FROM minis_list WHERE minis_list.\""+check+"\" is not NULL"
        cur.execute(command)
        for x in range(count):
                ab_tocheck = cur.fetchone()[0].split(";")
                abilities += ab_tocheck
        abilities = list(dict.fromkeys(abilities)) #removes duplicates from the list
        abilities.sort() #sorts the list alphabetically
        for x in abilities:
            print (x)

    def popup(self):
        popupWindow = Toplevel(self)
        popupWindow.attributes('-topmost', 'true')
        popupWindow.geometry("300x100")
        self.lb2 = Listbox(popupWindow, width=50, height=50, selectmode=EXTENDED)
        self.lb2.grid(row=0, column=0)

    def sendcharacter(self,char):
        self.lb2.insert(0,str(char[0])+" - "+str(char[5]))
        self.lb2.bind('<Double-1>', lambda x: self.lb2.delete(self.lb2.index(self.lb2.curselection())))
        print (char)

if __name__ == "__main__":
    app = Main()
    mainloop()
