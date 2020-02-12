from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import font

from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageChops
from math import cos, sin, sqrt, radians, floor
import math
import datetime
import textwrap

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
        controller.bottomframe = Frame(self, width=width, height=height)
        controller.bottomframe.grid(row=0, column=0)

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

    def generate(self, conn, varlist, pack_type, packs_qty):
        setmenu_VarList = varlist
        cur = conn.cursor()
        packtype = pack_type
        qty_packs = packs_qty
        cardlist = []
        pdf = FPDF()
        pdf.set_font('Arial', 'B', 10)

        """Grab the sets that are turned on"""
        setsenabled = []
        for x, i in enumerate(setmenu_VarList):
            if i.get() == 1:
                setsenabled.append(self.SETS[0][x])

        for p in range(1, qty_packs + 1):
            print("opening pack", p, "of", qty_packs)
            pdf.add_page()

            minilist = []
            selected_set = random.choice(setsenabled)
            short = self.SETS[1][self.SETS[0].index(selected_set)]
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
                    img = Label(self.bottomframe, image=render_sm, width=int(width / 6), height=int(height / 3))
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
        # style.configure("Courier.TButton", font=("Courier", 12))
        setfilter = False
        filename = ""
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        controller.popup()
        monofont = font.Font(family='Courier', size=8)
        # monofont = 'TkFixedFont'
        topframe = Frame(self, width=width)
        topframe.grid(row=0, column=0)
        bottomframe = Frame(self, width=width, height=height)
        bottomframe.grid(row=2, column=0)

        controller.colheadVar = []
        controller.headers = ["name", "set", "id", "faction", "rarity", "cost", "size", "hit points", "defense", "attack",
                              "damage", "special abilities", "force points", "force powers", "qty"]
        controller.headers_labels = ["name", "set", "id", "faction", "rarity", "cost", "size", "hp", "df",
                              "at",
                              "dm", "special abilities", "fp", "force powers", "qty"]
        +3
        columnwidth = [49, 24, 4, 19, 12, 5, 9, 3, 3, 3, 3, 37, 3, 33, 5]
        #columnwidth = [30, 15, 4, 19, 14, 6, 9, 10, 10, 3, 3, 36, 3, 38, 5]

        var_set = StringVar()
        controller.var_player= StringVar()
        controller.var_player.set("None")
        for x, i in enumerate(controller.headers_labels):
            controller.colheadVar.append(StringVar(self))
            # print (x,i)
            Label(topframe, text=i, width=len(i), font=monofont).grid(sticky="W", row=0, column=x)
            if i == "set":
                w = OptionMenu(topframe, var_set, "Alliance and Empire", "Bounty Hunters", "Alliance and Empire",
                               "Champions of the Force", "Clone Strike", "The Clone Wars",
                               "The Force Unleashed", "Galaxy at War", "Imperial Entanglements", "Jedi Academy",
                               "Knights of the Old Republic", "Legacy of the Force",
                               "Masters of the Force", "Revenge of the Sith", "Rebel Storm", "Dark Times", "Universe")
                w.config(width=columnwidth[x])
                w.grid(sticky="W", row=1, column=x)
                var_set.trace_variable("w", lambda x, y, z: self.testme(x, y, z))  # DbFrame.refreshfilters(self))
            elif i == "qty":
                p = OptionMenu(topframe, controller.var_player, "None", "Matt")
                p.config(width=len(i))#columnwidth[x])
                p.grid(sticky="W", row=1, column=x)
            else:
                Entry(topframe, width=columnwidth[x], textvariable=controller.colheadVar[x]).grid(sticky="W", row=1,
                                                                                                  column=x)
        # make drop downs for set,faction,rarity,size ... maybe abilities/force
        controller.lb1 = Listbox(bottomframe, width=200, height=100)  # ,font=monofont)
        controller.lb1.configure(font=monofont)
        controller.lb1.grid(row=0, column=0)
        controller.lb1.bind('<<ListboxSelect>>', lambda x: controller.preview(
            controller.lb1.get(controller.lb1.index(controller.lb1.curselection()))))  # addme
        controller.lb1.bind('<Double-1>', lambda x: controller.sendcharacter(
            controller.lb1.get(controller.lb1.index(controller.lb1.curselection()))))
        datarows = []
        #columnwidth = [20, 12, 3, 10, 4, 3, 5, 3, 3, 3, 3, 20, 3, 20]

        def loadplayer():
            filename = filedialog.askopenfilename(initialdir="./players")
            if filename is None:
                return
            print(filename)
            db_menubar.entryconfig(2, label="Custom")
            setfilter = True
            """do something to mod the count column with the file you get"""
            # DbFrame.refreshfilters()

    def testme(self, one, two, three):
        print(one)
        print(two)
        print(three)

    def refreshfilters(self):
        self.lb1.delete(0, 1000)
        statements = [False] * 16
        first = False
        if (self.var_player.get()=="Matt"):
            statements[0] = """SELECT uniq_id,name,"set",id,faction,rarity,cost,size,"hit points",defense,attack,damage,"special abilities","force points","force powers",
            CASE 
                WHEN minis_owned_matts.count IS NULL THEN 0+minis_owned_matts."extra minis" WHEN minis_owned_matts."extra minis" IS NULL THEN 0+minis_owned_matts.count
                WHEN minis_owned_matts."extra minis" IS NULL THEN 0+minis_owned_matts.count
                ELSE minis_owned_matts."extra minis"+minis_owned_matts.count
            END AS "qty" 
            FROM minis_list 
            Inner Join minis_owned_matts on minis_list.uniq_id = minis_owned_matts."mini id"
            WHERE "qty" > 0"""
            for x, i in enumerate(self.colheadVar, 1):
                val = i.get()
                filtered = ""
                if val:
                    if ">" in val or "<" in val:
                        statements[x] = " AND \"" + self.headers[x - 1] + "\" " + val
                    else:
                        statements[x] = " AND \"" + self.headers[x - 1] + "\" LIKE \"%" + val + "%\""

        if (self.var_player.get()=="None"):
            statements[0] = "SELECT * FROM minis_list "
            for x, i in enumerate(self.colheadVar, 1):
                val = i.get()
                filtered = ""
                if val:
                    if not first:
                        first = True
                        if "!" in val:
                            statements[x] = "WHERE \"" + self.headers[x - 1] + "\" NOT LIKE \"%" + val.strip("!") + "%\""
                        elif ">" in val or "<" in val:
                            statements[x] = "WHERE \"" + self.headers[x - 1] + "\" " + val
                        else:
                            statements[x] = "WHERE \"" + self.headers[x - 1] + "\" LIKE \"%" + val + "%\""
                    else:
                        if "!" in val:
                            statements[x] = "WHERE \"" + self.headers[x - 1] + "\" NOT LIKE \"%" + val.strip("!") + "%\""
                        elif ">" in val or "<" in val:
                            statements[x] = " AND \"" + self.headers[x - 1] + "\" " + val
                        else:
                            statements[x] = " AND \"" + self.headers[x - 1] + "\" LIKE \"%" + val + "%\""
        command = ""
        for x in statements:
            if x: command += str(x)
        print(command)
        cur = self.conn.cursor()
        cur.execute(command)
        table = cur.fetchall()

        if (self.var_player.get() == "Matt"):
            for x, i in enumerate(table):  # Rows
                extra_a = ""
                extra_b = ""
                extra_c = ""
                if i[1]:
                    if len(i[1])>37: extra_a="..."
                if i[12]:
                    if len(i[12])>25: extra_b="..."
                if i[14]:
                    if len(i[14])>25: extra_c="..."
                # {15:2d}
                self.lb1.insert(x,
                                "{0:3d} {1:39}{2:27} {3:2d} {4:17}{5:10}{6:5d} {7:7}{8:3d}{9:3d}{10:3d}{11:3d}  {12:28}{13:5d} {14:28} {15:2d}".format(
                                    i[0], str(i[1])[0:36]+extra_a, str(i[2]), i[3], str(i[4]), str(i[5]), i[6], str(i[7]), i[8], i[9],
                                    i[10], i[11], str(i[12])[0:25]+extra_b, i[13], str(i[14])[0:25]+extra_c,i[15]))
        else:
            for x, i in enumerate(table):  # Rows
                extra_a = ""
                extra_b = ""
                extra_c = ""
                if i[1]:
                    if len(i[1])>37: extra_a="..."
                if i[12]:
                    if len(i[12])>25: extra_b="..."
                if i[14]:
                    if len(i[14])>25: extra_c="..."
                self.lb1.insert(x,
                                "{0:3d} {1:39}{2:27} {3:2d} {4:17}{5:10}{6:5d} {7:7}{8:3d}{9:3d}{10:3d}{11:3d}  {12:28}{13:5d} {14:28}".format(
                                    i[0], str(i[1])[0:36]+extra_a, str(i[2]), i[3], str(i[4]), str(i[5]), i[6], str(i[7]), i[8], i[9],
                                    i[10], i[11], str(i[12])[0:25]+extra_b, i[13], str(i[14])[0:25]+extra_c))


class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("SW Minis Drafter")
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.overrideredirect(1)
        self.geometry("%dx%d+0+0" % (w, h - 50))
        self.focus_set()  # <-- move focus to this widget
        self.bind("<Escape>", lambda e: e.widget.quit())
        self.bind('<Return>', lambda x: DbFrame.refreshfilters(self))

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
        # self.db_menubar.add_cascade(label="Load Player File", command=lambda: DbFrame.loadplayer())
        # self.db_menubar.add_command(label="All Minis")
        self.db_menubar.add_command(label="Pack Generator", command=lambda: self.show_frame("PackFrame"))
        self.db_menubar.add_command(label="Mini Maker", command=lambda: self.minimaker())
        self.db_menubar.add_cascade(label="Close", command=lambda: self.safeclose())

        self.SETS = ["Alliance and Empire", "Bounty Hunters", "Alliance and Empire", "Champions of the Force",
                     "Clone Strike", "The Clone Wars",
                     "The Force Unleashed", "Galaxy at War", "Imperial Entanglements", "Jedi Academy",
                     "Knights of the Old Republic", "Legacy of the Force",
                     "Masters of the Force", "Revenge of the Sith", "Rebel Storm", "Dark Times", "Universe"], ["ae",
                                                                                                               "bh",
                                                                                                               "ae",
                                                                                                               "cotf",
                                                                                                               "cs",
                                                                                                               "cw",
                                                                                                               "fu",
                                                                                                               "gaw",
                                                                                                               "ie",
                                                                                                               "ja",
                                                                                                               "kotor",
                                                                                                               "lotf",
                                                                                                               "motf",
                                                                                                               "rots",
                                                                                                               "rs",
                                                                                                               "tdt",
                                                                                                               "uh", ]
        self.FACTIONS = ["Rebel", "Imperial", "The Old Republic", "The New Republic", "Sith", "Republic", "Seperatist",
                         "Yuuzhan Vong", "Mandolorian", "Fringe"]

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
                                      command=lambda: PackFrame.getbox(
                                          self)),  # command=lambda : DoSomethingWithInput(a.get))
        self.pack_menubar.add_command(label="1")
        qty_packs = 1
        self.pack_menubar.add_command(label="Go", underline=0,
                                      command=lambda: PackFrame.generate(self, self.conn, setmenu_VarList, packtype,
                                                                         qty_packs))
        self.pack_menubar.add_separator()
        self.pack_menubar.add_command(label="DB Browser", command=lambda: self.show_frame("DbFrame"))

        self.pack_menubar.add_command(label="quit", command=lambda: self.safeclose())

        for _ in enumerate(self.SETS[0]): setmenu_VarList.append(IntVar(self))
        for i in setmenu_VarList: i.set(1)

        setlist_menu.add_command(label="All", command=lambda: modAll(setmenu_VarList, 1))
        setlist_menu.add_command(label="None", command=lambda: modAll(setmenu_VarList, 0))
        setlist_menu.add_separator()
        for index, i in enumerate(self.SETS[0]):
            setlist_menu.add_checkbutton(label=i, variable=setmenu_VarList[index], onvalue=1, offvalue=0)

        for index, i in enumerate(self.packtypes):
            pack_menu.add_radiobutton(label=i, variable=packtype, value=index)
        packtype.set(0)
        DbFrame.refreshfilters(self)

    def show_frame(self, page_name):  # swaps the left frame from editor to generator controls
        frame = self.frames[page_name]
        frame.tkraise()
        self.program = page_name
        if page_name == "PackFrame":
            self.config(menu=self.pack_menubar)
        elif page_name == "DbFrame":
            self.config(menu=self.db_menubar)

    def safeclose(self):
        folder = './tmp/'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        self.destroy()

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    # once DB is validated this is pointless... but could be good to parse out all abilities
    def abilitychecker(self, conn, check):
        abilities = []
        cur = conn.cursor()

        command = "SELECT COUNT() FROM minis_list WHERE minis_list.\"" + check + "\" is not NULL"
        cur.execute(command)
        count = cur.fetchone()[0]

        command = "SELECT minis_list.\"" + check + "\" FROM minis_list WHERE minis_list.\"" + check + "\" is not NULL"
        cur.execute(command)
        for x in range(count):
            ab_tocheck = cur.fetchone()[0].split(";")
            abilities += ab_tocheck
        abilities = list(dict.fromkeys(abilities))  # removes duplicates from the list
        abilities.sort()  # sorts the list alphabetically
        #for x in abilities:
            #print(x)

    def exportlb(self, lb):
        list = lb
        cost = 0
        cardlist = []
        minilist = []
        """you can pass cost and can this"""
        for x in range(list.size()):
            minilist.append(list.get(x).split("_")[0])
            cardlist.append(list.get(x).split("_")[1])
            cost += int(list.get(x).split("_")[2])

        file = filedialog.asksaveasfile(initialdir="./custom", title='Name your cardlist',
                                        defaultextension=str(cost) + '.pdf')
        if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        filename = str(file.name.split("/")[-1:]).split(".")[0][2:]
        pdf = FPDF()
        pdf.set_font('Arial', 'B', 10)

        """get the length of overall minis to print... then structure for loops around that."""
        # saves the temp files
        # print(cardlist)
        pagecount = len(cardlist) // 8 + 1
        page = 0
        width = 63
        height = width * 1.39
        row = 3
        for x, i in enumerate(cardlist):
            card = ("./cards/" + str(i) + ".jpg")
            im = Image.open(card)
            imgwidth, imgheight = im.size
            imback = im.crop((imgwidth / 2, 0, imgwidth, imgheight))
            imback.save("tmp\\" + str(x) + "temp.png")
            if (x // 9 + 1) > page:
                page += 1
                pdf.add_page()
                row += -3
                pdf.text(x=10, y=7, txt=str(filename) + " - " + str(cost) + " Point Squad - Page" + str(page))
            rowf = x // 3 + row
            col = x % 3
            pdf.image("tmp\\" + str(x) + "temp.png", x=col * (width + 2) + 8, y=rowf * (width + 2) * 1.39 + 10, w=width,
                      h=height)
        pdf.output(file.name)

    def popup(self):
        popupWindow = Toplevel(self)
        popupWindow.attributes('-topmost', 'true')
        popupWindow.geometry("550x350")
        self.lb2 = Listbox(popupWindow, width=50, height=20)
        self.lb2.grid(row=0, column=0, columnspan=3)

        self.count_label = StringVar()
        self.count = 0
        self.count_label.set("Count: " + str(self.count))
        count_label = Label(popupWindow, textvariable=self.count_label)
        count_label.grid(row=1, column=0)

        self.cost_label = StringVar()
        self.cost_label.set("Points: 0")
        count_label = Label(popupWindow, textvariable=self.cost_label)
        count_label.grid(row=1, column=1)

        im = Image.open("./cards\\nopreview.png")
        imgwidth, imgheight = im.size
        im = im.resize((int(imgwidth / 3), int(imgheight / 3)), Image.ANTIALIAS)
        imgwidth, imgheight = im.size
        print(im.size)
        im = ImageTk.PhotoImage(im)

        self.preview_lbl = Label(popupWindow, image=im)
        self.preview_lbl.image = im
        self.preview_lbl.grid(row=0, column=4, rowspan=2)

        evoke = Button(popupWindow, text="Export Minis", command=lambda: Main.exportlb(self, self.lb2))
        evoke.grid(row=1, column=2)
        # Button(popupWindow, text="export", command=lambda : Main.exportlb(self,self.lb2)).grid(row=1,column=1)

    def preview(self, char):
        if len(char) > 100: #basically are you trying to preview something in the DB view or the squad view
            name = char[3:42].rstrip(" ")
            set = char[43:70].rstrip(" ")  # interprets the line sent and takes the set out of it.
            id = "{:02d}".format(int(char[71:73].strip(" ")))
            cost = "{:02d}".format(int(char[103:106].strip(" ")))
            setshort = self.SETS[1][self.SETS[0].index(set)] + id
        else:
            setshort = char.split("_")[1]
        card = ("./cards/" + setshort + ".jpg")
        im = Image.open(card)
        imgwidth, imgheight = im.size
        imback = im.crop((imgwidth / 2, 0, imgwidth, imgheight))
        imback = imback.resize((int(imgwidth / 6), int(imgheight / 3)), Image.ANTIALIAS)
        imback = ImageTk.PhotoImage(imback)
        self.preview_lbl.configure(image=imback)
        self.preview_lbl.image = imback

    def squadcost(self):
        cost = 0
        for x in range(self.lb2.size()):
            cost += int(self.lb2.get(x).split("_")[2])
        self.cost_label.set("Points: " + str(cost))

    def sendcharacter(self, char):
        name = char[3:42].rstrip(" ")
        set = char[43:70].rstrip(" ")  # interprets the line sent and takes the set out of it.
        id = "{:02d}".format(int(char[71:73].strip(" ")))
        cost = "{:02d}".format(int(char[103:106].strip(" ")))
        setshort = self.SETS[1][self.SETS[0].index(
            set)] + id  # references the setlist for the shortname of the set the mini is from and rounds the id to two digits.

        # print (name+"_"+setshort+"_"+cost)
        self.lb2.insert(0, name + "_" + setshort + "_" + cost)
        self.lb2.bind('<<ListboxSelect>>',
                      lambda x: self.preview(self.lb2.get(self.lb2.index(self.lb2.curselection()))))  # addme
        self.lb2.bind('<Double-1>', lambda x: [self.lb2.delete(self.lb2.index(self.lb2.curselection())),self.squadcost()])
        self.count = self.lb2.size()
        self.count_label.set("Count: " + str(self.count))
        self.squadcost()


    def minimaker(self):
        makerWindow = Toplevel(self)
        makerWindow.attributes('-topmost', 'true')
        makerWindow.geometry("700x525")
        card = ("./minimaker/templates/01_fringe_template.png")
        self.cardchanged = True

        self.hitpoints = IntVar()
        self.hitpoints.set(10)
        self.defense = IntVar()
        self.defense.set(13)
        self.attack = IntVar()
        self.attack.set(4)
        self.damage = IntVar()
        self.damage.set(10)
        self.unique = IntVar()
        self.unique.set(0)
        self.melee = StringVar()
        self.melee.set("0")

        self.abilities = []
        self.abilitiesfull = []
        file = open("./minimaker/abilitylist.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            print(i)
            self.abilitiesfull.append(i.split("\t"))

        self.forcepowers = []
        self.forcepowersfull = []
        file = open("./minimaker/forcepowers.csv")
        filelist = file.readlines()
        for i in filelist:
            #print(i)
            self.forcepowersfull.append(i)
        file.close()

        self.force = IntVar()
        self.force.set(0)

        self.minicost = IntVar()
        self.minicost.set(5)

        bigfont = ImageFont.truetype('impact', size=20)
        font = ImageFont.truetype('impact', size=16)
        smfont = ImageFont.truetype('verdana', size=11)

        Label(makerWindow, text="Name: ").grid(row=0, column=2)
        name = StringVar(value='unnamed')
        namefld = Entry(makerWindow, width=20, textvariable=name).grid(row=0, column=3)

        statframe = LabelFrame(makerWindow, text="Stats")
        statframe.grid(row=1, column=2, rowspan=4, columnspan=2)
        Label(statframe, text="HP").grid(row=0, column=0)
        Button(statframe, text="↑", width=2, command=lambda: modstat(self.hitpoints, 10)).grid(row=0, column=1)
        Button(statframe, text="↓", width=2, command=lambda: modstat(self.hitpoints, -10)).grid(row=0, column=2)

        Label(statframe, text="Defense").grid(row=1, column=0)
        Button(statframe, text="↑", width=2, command=lambda: modstat(self.defense, 1)).grid(row=1, column=1)
        Button(statframe, text="↓", width=2, command=lambda: modstat(self.defense, -1)).grid(row=1, column=2)

        Label(statframe, text="Attack").grid(row=2, column=0)
        Button(statframe, text="↑", width=2, command=lambda: modstat(self.attack, 1)).grid(row=2, column=1)
        Button(statframe, text="↓", width=2, command=lambda: modstat(self.attack, -1)).grid(row=2, column=2)

        Label(statframe, text="Damage").grid(row=3, column=0)
        Button(statframe, text="↑", width=2, command=lambda: modstat(self.damage, 10)).grid(row=3, column=1)
        Button(statframe, text="↓", width=2, command=lambda: modstat(self.damage, -10)).grid(row=3, column=2)

        Label(statframe, text="Force").grid(row=4, column=0)
        Button(statframe, text="↑", width=2, command=lambda: modstat(self.force, 1)).grid(row=4, column=1)
        Button(statframe, text="↓", width=2, command=lambda: modstat(self.force, -1)).grid(row=4, column=2)

        Checkbutton(makerWindow, text="Unique", variable=self.unique, onvalue=20, offvalue=0).grid(row=1, column=5)
        Checkbutton(makerWindow, text="Melee", variable=self.melee, onvalue=-0.15, offvalue=0).grid(row=2, column=5)
        self.unique.trace("w",lambda : refreshcost())
        self.melee.trace("w", lambda : refreshcost())

        self.race = StringVar()
        self.race.set("None")
        racemenu = OptionMenu(makerWindow, self.race, "None", "Droid", "Cyborg", "Ewok", "Trandoshan", "Ugnaught",
                              "Wookie", "Gungan")
        racemenu.config(width=10)
        racemenu.grid(row=3, column=5)
        Label(makerWindow, text="Race").grid(row=3, column=4)

        self.faction = StringVar(value="Fringe")

        factionmenu = OptionMenu(makerWindow, self.faction, "Fringe", "Rebel", "Old Republic", "Republic",
                                 "New Republic", "Imperial", "Seperatist", "Sith", "Yuuzhan Vong", "Mandalorian")
        factionmenu.config(width=10)
        factionmenu.grid(row=4, column=5)
        Label(makerWindow, text="Faction").grid(row=4, column=4)
        self.faction.trace_variable("w", lambda x, y, z: factionchanged(x, y, z))  # DbFrame.refreshfilters(self))

        # OptionMenu(makerWindow,textvariable=)
        Button(makerWindow, text="Export", width=5, command=lambda: tempdef()).grid(row=7, column=2)
        abilitiesframe = LabelFrame(makerWindow, text="Abilities")
        forceframe = LabelFrame(makerWindow, text="Force Powers")
        abilitiesframe.grid(row=6, column=2, columnspan=2)
        forceframe.grid(row=6, column=4, columnspan=2)

        abilitieslb = Listbox(abilitiesframe, width=25, height=10)  # ,font=monofont)
        abilitieslb.grid(row=0, column=0)
        abilitieslb.bind('<Double-1>', lambda x: [addability(abilitieslb.get(abilitieslb.index(abilitieslb.curselection())),abilitieslb.index(abilitieslb.curselection())),refreshcost()])
        for x, i in enumerate(self.abilitiesfull):
            abilitieslb.insert(x, i[0])

        forcelb = Listbox(forceframe, width=25, height=10)  # ,font=monofont)
        forcelb.grid(row=0, column=0)
        forcelb.bind('<Double-1>', lambda x: [addforce(forcelb.get(forcelb.index(forcelb.curselection()))),refreshcost()])

        for x, i in enumerate(self.forcepowersfull):
            forcelb.insert(x, i)

        """unique, melee, options box to pick a race..."""

        def tempdef(cmom):
            print(cmom)

        def addability(thing,where):
            print (thing, where)
            self.abilities.append([thing,where])

        def addforce(thing):
            self.forcepowers.append(thing)

        def factionchanged(ignorea, ignoreb, ignorec):
            self.cardchanged = True
            print("faction changed")
            refreshcost()

        def modstat(stat, dir):
            ministat = stat
            ministat.set(ministat.get() + dir)
            refreshcost()

        def refreshcost():
            txtoffset = 0

            hitpoints = self.hitpoints.get()
            defense = self.defense.get()
            attack = self.attack.get()
            damage = self.damage.get()
            force = self.force.get()
            extracost=0

            ranks_hp = hitpoints / 10 - 1
            ranks_def = defense - 13
            ranks_atk = attack - 4
            ranks_dmg = damage / 10 - 1
            dmgtax = 0.25 + float(self.melee.get())
            cost_hp = ranks_hp ** 2 / 2
            cost_def = ranks_def ** 2 / 2
            cost_atk = ranks_atk ** 2 / 2
            cost_dmg = ranks_dmg ** 2
            cost_dmgtax = dmgtax * (ranks_hp + ranks_def + ranks_atk + ranks_dmg)
            print(cost_dmgtax)

            minicost = round(cost_hp + cost_def + cost_atk + cost_dmg + cost_dmgtax + force + 5)
            if self.cardchanged:
                card = ("./minimaker/templates/01_" + str(self.faction.get()) + "_template.png")
                self.cardchange = False
            print(card)
            im = Image.open(card)
            imgwidth, imgheight = im.size
            imback = im.crop((imgwidth / 2, 0, imgwidth, imgheight))
            sizesm = int(imgwidth / 4), int(imgheight / 2)
            imback = imback.resize(sizesm, resample=Image.ANTIALIAS)
            draw = ImageDraw.Draw(imback)

            draw.text((60, 15), str(name.get()), (255, 255, 255), font=bigfont)

            draw.text((102, 85), str(hitpoints + self.unique.get()), (0, 0, 0), font=font)
            draw.text((102, 138), str(defense), (0, 0, 0), font=font)
            draw.text((100, 190), "+" + str(attack), (0, 0, 0), font=font)
            draw.text((102, 243), str(damage), (0, 0, 0), font=font)
            if self.unique.get() > 0:
                draw.text((145, 95 + txtoffset), "Unique", (0, 0, 0), font=smfont)
                txtoffset += 20
            if not self.race.get() == "None":
                draw.text((145, 95 + txtoffset), self.race.get(), (0, 0, 0), font=smfont)
                txtoffset += 20
            if not self.melee.get() == "0":
                draw.text((145, 95 + txtoffset), "Melee", (0, 0, 0), font=smfont)
                txtoffset += 20
            for x in self.abilities:
                read = self.abilitiesfull[x[1]]
                lines = textwrap.wrap(read[0]+". "+read[1], width=39)
                print (lines)
                for line in lines:
                    width, height = smfont.getsize(line)
                    #draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
                    draw.text((145, 95 + txtoffset), line, (0, 0, 0), font=smfont)
                    txtoffset += height

                #draw.text((145, 95 + txtoffset), str(read[0])+". "+str(read[1]),(0, 0, 0), font=smfont)
                txtoffset += 20
                extracost += int(read[3][:2])
            if force > 0:
                draw.text((145, 100 + txtoffset), "Force " + str(force), (0, 0, 0), font=smfont)
                txtoffset += 20
            for x in self.forcepowers:
                print(x)
                content = self.forcepowersfull.index(x)
                print (content)
                draw.text((145, 95 + txtoffset), str(x),(0, 0, 0), font=smfont)
                txtoffset += 20
            draw.text((332, 25), str(minicost+extracost), (0, 0, 0), font=font)

            render = ImageTk.PhotoImage(imback)
            img = Label(makerWindow, image=render, width=imgwidth / 4, height=imgheight / 2)
            img.image = render
            img.grid(row=0, column=0, rowspan=12)

        refreshcost()


if __name__ == "__main__":
    app = Main()
    mainloop()
