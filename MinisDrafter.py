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

#from fontTools.ttLib import TTFont

import sqlite3
from sqlite3 import Error

from fpdf import FPDF
from PyPDF2 import PdfFileReader


class PackFrame(Frame):
    packlist = []
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()

        controller.draftframe = Frame(self, width=width, height=height)
        controller.draftframe.grid(row=0, column=0)

        monofont = font.Font(family='Courier', size=8)

        draftedboxes = LabelFrame(controller.draftframe, text="Drafted Boxes")
        controller.lb2_1 = Listbox(draftedboxes, width=20, height=20)
        controller.lb2_1.configure(font=monofont)
        controller.lb2_1.grid(row=0, column=0)
        controller.lb2_1.bind('<<ListboxSelect>>', lambda x: PackFrame.showpack(self, controller.lb2_1, controller.lb2_2))
        draftedboxes.grid(row=0, column=0)

        boxcontents = LabelFrame(controller.draftframe, text="Pack Contents")
        controller.lb2_2 = Listbox(boxcontents, width=20, height=20)
        controller.lb2_2.configure(font=monofont)
        controller.lb2_2.grid(row=0, column=0)
        controller.lb2_2.bind('<<ListboxSelect>>', lambda x: PackFrame.showpack(self))#,controller.lb2_2.grab_current()))
        boxcontents.grid(row=0, column=1)

    def showpack(self, packnum, packminis):
        char = packnum.get(packnum.index(packnum.curselection()))
        index = int(char.split(" ")[1])
        print ("this is the pack I need to show",index)
        print (self.packlist[0])
        print ("pack contents: ",self.packlist[index-1])
        #packminis.insert()


    def getbox(self):
        answer = simpledialog.askinteger("Input", "Open 1-20 boxes",
                                         parent=self,
                                         minvalue=1, maxvalue=20)
        if answer == None: answer = 1
        self.qty_packs = int(answer)
        self.pack_menubar.entryconfig(8, label=str(self.qty_packs))

    def generate(self, conn, varlist, pack_type):
        setmenu_VarList = varlist
        cur = conn.cursor()
        packtype = pack_type
        cardlist = []
        pdf = FPDF()
        pdf.set_font('Arial', 'B', 10)
        #self.qty_packs = PackFrame.qty_packs
        """Grab the sets that are turned on"""
        setsenabled = []
        for x, i in enumerate(setmenu_VarList):
            if i.get() == 1:
                setsenabled.append(self.SETS[0][x])
        pdfwrite=FALSE
        self.packlist = []
        for p in range(1, self.qty_packs + 1):
            if pdfwrite: pdf.add_page()

            minilist = []
            selected_set = random.choice(setsenabled[:-8])
            print("Pack", p, "of", self.qty_packs,": ", selected_set)
            selected_set_short = self.SETS[1][self.SETS[0].index(selected_set)]
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
                    #commons.remove(mini) # no duplicates
                    minilist.append(mini)
                for x in range(2):
                    mini = random.choice(uncommons)
                    #uncommons.remove(mini)  # no duplicates
                    minilist.append(mini)
                minilist.append(random.choice(rares))

                # CREATES THE CARDS AND RENDERS THEM ON SCREEN
                rw = 0
                for x, i in enumerate(minilist):
                    card = ("./cards/" + selected_set_short + "{:02d}".format(i[0]) + ".jpg")
                    im = Image.open(card)
                    width, height = im.size
                    sizesm = int(width / 6), int(height / 3)
                    imback = im.crop((width / 2, 0, width, height))

                    imbacksm = imback.resize(sizesm, resample=Image.ANTIALIAS)
                    imfront = im.crop((0, 0, width / 2, height))
                    cardlist.append(imback)

                    imback.save("tmp\\" + str(p) + "_" + str(x) + "temp.png")
                    imbacksm.save("tmp\\" + str(p) + "_" + str(x) + "temp_sm.png")
                    #load = Image.open("tmp\\" + str(p) + "_" + str(x) + "temp.png")
                    load_sm = Image.open("tmp\\" + str(p) + "_" + str(x) + "temp_sm.png")
                    #render = ImageTk.PhotoImage(load) #might have to put back in later
                    render_sm = ImageTk.PhotoImage(load_sm)
                    img = Label(self.draftframe, image=render_sm, width=int(width / 6), height=int(height / 3))
                    img.image = render_sm
                    col = x % 4
                    if (x % 4 == 0): rw += 1
                    img.grid(row=rw-1, column=col+2)
                if pdfwrite: #READS THE TEMPORARY PNGS CREATED AND PUTS THEM ON A PDF PAGE
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

            self.packlist.append(minilist)
            self.lb2_1.insert(p,"Pack "+str(p))
        #print("the packlist",self.packlist)
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
        # controller.popup()
        monofont = font.Font(family='Courier', size=8)
        # monofont = 'TkFixedFont'
        topframe = Frame(self, width=width, height=height)
        topframe.grid(row=0, column=0)
        bottomframe = Frame(self, width=width, height=height)  # 550?
        bottomframe.grid(row=1, column=0)
        squadframe = Frame(self, width=width, height=height*0.30)
        squadframe.grid(row=2, column=0)

        controller.colheadVar = []
        controller.headers = ["name", "set", "id", "faction", "rarity", "cost", "size", "hit points", "defense",
                              "attack",
                              "damage", "special abilities", "force points", "force powers", "qty"]
        controller.headers_labels = ["name", "set", "id", "faction", "rarity", "cost", "size", "hp", "df", "at", "dm", "special abilities", "fp", "force powers", "qty"]
        #+3
        columnwidth = [49, 24, 4, 19, 12, 5, 9, 3, 3, 3, 3, 37, 3, 33, 5]
        # columnwidth = [30, 15, 4, 19, 14, 6, 9, 10, 10, 3, 3, 36, 3, 38, 5]

        controller.var_set = StringVar()
        controller.var_player = StringVar()
        controller.var_player.set("None")
        controller.var_sort = StringVar()
        controller.var_sort.set("Name")
        controller.colheadbutton=[]
        controller.ASC = StringVar()
        controller.ASC.set("ASC")

        #LAAAAAAAAAAAAAAAZYYYYYYYYYYYYYYYYY
        offset=-2
        Button(topframe, text="name", width=30, font=monofont, command=lambda: self.sortby("name", controller)).grid(sticky="W", row=0, column=0)
        Button(topframe, text="set", width=columnwidth[1]+offset, font=monofont, command=lambda: self.sortby("set", controller)).grid(sticky="W", row=0, column=1)
        Button(topframe, text="id", width=columnwidth[2]+offset, font=monofont, command=lambda: self.sortby("id", controller)).grid(sticky="W", row=0, column=2)
        Button(topframe, text="faction", width=columnwidth[3]+offset-10, font=monofont, command=lambda: self.sortby("faction", controller)).grid(sticky="W", row=0, column=3)
        Button(topframe, text="rarity", width=columnwidth[4]+offset, font=monofont, command=lambda: self.sortby("rarity", controller)).grid(sticky="W", row=0, column=4)

        Button(topframe, text="cost", width=columnwidth[5]+offset, font=monofont, command=lambda: self.sortby("cost", controller)).grid(sticky="W", row=0, column=5)
        Button(topframe, text="size", width=columnwidth[6]+offset, font=monofont, command=lambda: self.sortby("size", controller)).grid(sticky="W", row=0, column=6)
        Button(topframe, text="hp", width=columnwidth[7]+offset, font=monofont, command=lambda: self.sortby("hit points", controller)).grid(sticky="W", row=0, column=7)
        Button(topframe, text="df", width=columnwidth[8]+offset, font=monofont, command=lambda: self.sortby("defense", controller)).grid(sticky="W", row=0, column=8)
        Button(topframe, text="at", width=columnwidth[9]+offset, font=monofont, command=lambda: self.sortby("attack", controller)).grid(sticky="W", row=0, column=9)
        Button(topframe, text="dmg", width=columnwidth[10]+offset, font=monofont, command=lambda: self.sortby("damage", controller)).grid(sticky="W", row=0, column=10)


        Button(topframe, text="special abilities", width=columnwidth[11]+offset-10, font=monofont, command=lambda: self.sortby("special abilities", controller)).grid(sticky="W", row=0, column=11)
        Button(topframe, text="FP", width=columnwidth[12]+offset, font=monofont, command=lambda: self.sortby("force points", controller)).grid(sticky="W", row=0, column=12)
        Button(topframe, text="Force Powers", width=columnwidth[13]+offset-10, font=monofont, command=lambda: self.sortby("force powers", controller)).grid(sticky="W", row=0, column=13)
        Button(topframe, text="Qty", width=columnwidth[14]+offset, font=monofont, command=lambda: self.sortby("qty", controller)).grid(sticky="W", row=0, column=14)
        tmp=[]
        for x, i in enumerate(controller.headers_labels):
            controller.colheadVar.append(StringVar(self))

            #Button(topframe, text=i, width=len(i), font=monofont,command=lambda: self.sortby(self,controller)).grid(sticky="W", row=0, column=x)

            # Laabel(topframe, text=i, width=len(i), font=monofont).grid(sticky="W", row=0, column=x)
            if i == "set":
                w = OptionMenu(topframe, controller.colheadVar[x], "Alliance and Empire", "Bounty Hunters", "Alliance and Empire",
                               "Champions of the Force", "Clone Strike", "The Clone Wars",
                               "The Force Unleashed", "Galaxy at War", "Imperial Entanglements", "Jedi Academy",
                               "Knights of the Old Republic", "Legacy of the Force",
                               "Masters of the Force", "Revenge of the Sith", "Rebel Storm", "Dark Times", "Universe",
                               "Clone Wars Starter","Battle of Hoth","Clone Wars Battles","The Attack on Teth","Showdown at Teth Palace","The Crystal Caves of Ilum","Affinity")
                controller.colheadVar[x].trace_add('write', lambda x, y, z: DbFrame.refreshfilters(controller))
                w.config(width=columnwidth[x])
                w.grid(sticky="W", row=1, column=x)
                tmp.append("set")

            elif i == "qty":
                p = OptionMenu(topframe, controller.var_player, "None", "matts","tims")
                controller.var_player.trace_add('write', lambda x, y, z: DbFrame.refreshfilters(controller))
                p.config(width=len(i))  # columnwidth[x])
                p.grid(sticky="W", row=1, column=x)
            else:
                tmp.append(Entry(topframe, width=columnwidth[x], textvariable=controller.colheadVar[x]))
                controller.colheadVar[x].trace_add('write', lambda x, y, z: DbFrame.refreshfilters(controller))
                tmp[x].grid(sticky="W", row=1,column=x)



        # make drop downs for set,faction,rarity,size ... maybe abilities/force
        controller.lb1 = Listbox(bottomframe, width=200, height=25)  # ,font=monofont)
        controller.lb1.configure(font=monofont)
        controller.lb1.grid(row=0, column=0)
        controller.lb1.bind('<<ListboxSelect>>', lambda x: controller.preview(controller.lb1))
        # controller.lb1.get(controller.lb1.index(controller.lb1.curselection()))))  # addme
        controller.lb1.bind('<Double-1>', lambda x: controller.sendcharacter(
            controller.lb1.get(controller.lb1.index(controller.lb1.curselection()))))
        datarows = []

        # def loadplayer():
        #     filename = filedialog.askopenfilename(initialdir="./players")
        #     if filename is None:
        #         return
        #     db_menubar.entryconfig(2, label="Custom")
        #     setfilter = True
        #     """do something to mod the count column with the file you get"""
        #     # DbFrame.refreshfilters()
        controller.lb2 = Listbox(squadframe, width=50, height=21)
        controller.lb2.grid(row=0, column=1, rowspan=25)
        controller.lb2.bind('<<ListboxSelect>>',
                            lambda x: controller.preview(
                                controller.lb2))  # .get(controller.lb2.index(controller.lb2.curselection()))))  # addme
        controller.lb2.bind('<Double-1>',
                            lambda x: [controller.lb2.delete(controller.lb2.index(controller.lb2.curselection())),
                                       controller.squadcost()])
        controller.count_label = StringVar()
        controller.count = 0
        controller.count_label.set("Count: " + str(controller.count))
        count_label = Label(squadframe, textvariable=controller.count_label)
        count_label.grid(row=0, column=0)

        controller.cost_label = StringVar()
        controller.cost_label.set("Points: 0")
        cost_label = Label(squadframe, textvariable=controller.cost_label)
        cost_label.grid(row=1, column=0)

        im = Image.open("./cards\\nopreview.png")
        imgwidth, imgheight = im.size
        im = im.resize((int(imgwidth / 3), int(imgheight / 3)), Image.ANTIALIAS)
        #imgwidth, imgheight = im.size
        im = ImageTk.PhotoImage(im)

        controller.preview_lbl = Label(squadframe, image=im)
        controller.preview_lbl.image = im
        controller.preview_lbl.grid(row=0, column=2, rowspan=25)
        controller.compare_lbl = Label(squadframe, image=im)
        controller.compare_lbl.image = im
        controller.compare_lbl.grid(row=0, column=3, rowspan=25)

        xp_pdf = Button(squadframe, width=10, text="Save", command=lambda: Main.exportlb(self, controller.lb2))
        xp_pdf.grid(row=2, column=0)
        imp_list = Button(squadframe, width=10, text="Load", command=lambda: [Main.loadlist(self, controller.lb2), controller.squadcost()])
        imp_list.grid(row=3, column=0)
        clear_list = Button(squadframe, width=10, text="Clear", command=lambda: controller.lb2.delete(0, 1000))
        clear_list.grid(row=5, column=0)
        compare = Button(squadframe, width=10, text="Compare",
                         command=lambda: Main.compare_mini(controller, controller.lb2, controller.lb1))
        compare.grid(row=4, column=0)
        xp_tokens = Button(squadframe, width=10, text="Export Tokens",
                          command=lambda: Main.exporttokens(self, controller.lb2))
        xp_tokens.grid(row=6, column=0)

        imgsize = LabelFrame(squadframe, text="Preview Size")
        Button(imgsize,width=4,text="+",command=lambda : previewsize(1)).grid(row=0,column=1)
        Button(imgsize, width=4, text="-", command=lambda : previewsize(-1)).grid(row=0,column=0)
        imgsize.grid(row=7,column=0)

        glossbox= LabelFrame(squadframe, text="Glossary Lookup")
        controller.lb3 = Listbox(glossbox, width=20, height=20)
        controller.lb3.configure(font=monofont)
        controller.lb3.grid(row=0, column=4, rowspan=21)
        controller.lb3.bind('<<ListboxSelect>>', lambda x: DbFrame.showgloss(controller))

        controller.lb3selected = Text(glossbox, width=30, height=19)
        controller.lb3selected.config(wrap=WORD)
        controller.lb3selected.grid(row=0,column=5,rowspan=21)


        controller.gloss_var = StringVar()
        controller.gloss_var.trace_add('write', lambda x,y,z: DbFrame.refreshgloss(controller))
        controller.glossary_filter = Entry(glossbox, width=65, textvariable=controller.gloss_var)
        controller.glossary_filter.grid(row=23, column=4,columnspan=2)
        glossbox.grid(row=0,column=5,rowspan=21)

        controller.draft_seed = StringVar()
        controller.draft_seed.trace_add('write', lambda x, y, z: print("hi"))#DbFrame.refreshgloss(controller))

    def testtracing (self):
        print ("hit")

    def sortby(self, u,t):
        new = u
        current = t.var_sort.get()
        order = t.ASC.get()
        if new == current:
            if order == "ASC": t.ASC.set("DESC")
            elif order == "DESC": t.ASC.set("ASC")
        else:
            t.var_sort.set(u)
            t.ASC.set("ASC")
        DbFrame.refreshfilters(self.controller)

    def testme(self, one, two, three):
        print(one)
        print(two)
        print(three)

    def refreshgloss(self):
        self.lb3.delete(0, 1000)
        term = self.gloss_var.get()
        for x, i in enumerate(self.glossary):
            if not term == "":
                if term in i[0].lower() or term in i[1].lower():
                    self.lb3.insert(x, str(i[0] + "              " + str(i[1])))
            else:
                self.lb3.insert(x, str(i[0] + "              " + str(i[1])))


    def showgloss(self):
        self.lb3selected.delete(1.0, END)
        stupidvar = self.lb3.get(self.lb3.index(self.lb3.curselection()))
        stupidvar = stupidvar.split("              ")[1]
        self.lb3selected.insert(INSERT, stupidvar)

    def exportscript(self):
        command="SELECT * FROM minis_list ORDER BY minis_list.\"name\" ASC, minis_list.id ASC"
        cur = self.conn.cursor()
        cur.execute(command)
        table = cur.fetchall()

        abilitiesfull = []
        abilitiesdescriptions = []
        file = open("./DB/specialabilities.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            term = i.split("\t")
            # print (term)
            abilitiesfull.append(term[0])
            abilitiesdescriptions.append(term[1])
        file.close

        forcefull = []
        forcedescriptions = []
        file = open("./DB/specialabilities.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            term = i.split("\t")
            # print (term)
            abilitiesfull.append(term[0])
            abilitiesdescriptions.append(term[1])
        file.close

        simple = {"Unique","Droid","Melee Attack","Gungan","Wookie","Commander Effect"}
        character = """"""
        for x, i in enumerate(table):
            #abilities = []
            #abilities.append(str(i[12]).split(";"))

            setshort = self.SETS[1][self.SETS[0].index(i[2])]+"{:02d}".format(i[3])+".jpg"
            character += "{\n"
            character += "     \"name\": \""+i[1]+"\",\n"
            character += "     \"avatar id\": \""+setshort+"\",\n"
            character += "     \"set\": \"" + i[2] + "\",\n"
            character += "     \"id\": " + str(i[3]) + ",\n"
            character += "     \"faction\": \"" + i[4] + "\",\n"
            character += "     \"rarity\": \"" + str(i[5]) + "\",\n"
            character += "     \"cost\": " + str(i[6]) + ",\n"
            character += "     \"size\": \"" + str(i[7]) + "\",\n"
            character += "     \"hit points\": " + str(i[8]) + ",\n"
            character += "     \"defense\": " + str(i[9]) + ",\n"
            character += "     \"attack\": " + str(i[10]) + ",\n"
            character += "     \"damage\": " + str(i[11])

            first = True
            if i[12]:
                character += ",\n     \"abilities\": ["
                for y in str(i[12]).split(";"):
                    if first:
                        first = False
                        character += "\n"
                    else: character += ",\n"

                    is_simple = len(simple.intersection(y))
                    #print(simple.intersection(str(y)))
                    if str(y) in simple:
                        character += "          { \"name\": \"" + str(y) + "\" }"
                    else:
                        pos = abilitiesfull.index(str(y))
                        description = abilitiesdescriptions[pos].strip("\n")
                        character += "          { \"name\": \""+str(y)+"\", \"desc\": \""+description+"\" }"
                character += "\n     ]"

            if i[13] != 0:
                character += ",\n     \"force points\": " + str(i[13])
                if i[14]:
                    character += ",\n     \"force powers\": [\n"
                    first = True
                    for y in str(i[14]).split(";"):
                        if first:
                            first = False
                        else:
                            character += ",\n"
                        character += "          { \"name\": \"" + str(y) + "\" }"
                    character += "\n     ]"
            character += "\n},\n\n"
        f = open("demofile2.txt", "w", encoding="utf-8")
        f.write(character)#"Now the file has more content!")
        f.close()
            # character += "\"abilities": [
            #
            # { "name": """+i[12]+"},\n" """
            # { \"name\": """

    def refreshfilters(self):
        player = self.var_player.get()
        set= self.var_set.get()
        order = self.ASC.get()

        self.lb1.delete(0, 1000)
        statements = [False] * 16
        first = True
        statements[0] = "SELECT * FROM minis_list "
        if not (player == "None"):
            statements[0] = """SELECT uniq_id,name,"set",id,faction,rarity,cost,size,"hit points",defense,attack,damage,"special abilities","force points","force powers",
            CASE 
                WHEN minis_owned_"""+player+""".count IS NULL THEN 0+minis_owned_"""+player+"""."extra minis" WHEN minis_owned_"""+player+"""."extra minis" IS NULL THEN 0+minis_owned_"""+player+""".count
                WHEN minis_owned_"""+player+"""."extra minis" IS NULL THEN 0+minis_owned_"""+player+""".count
                ELSE minis_owned_"""+player+"""."extra minis"+minis_owned_"""+player+""".count
            END AS "qty" 
            FROM minis_list 
            Inner Join minis_owned_"""+player+""" on minis_list.uniq_id = minis_owned_"""+player+"""."mini id"
            WHERE "qty" > 0 """
            first = False
        for x, i in enumerate(self.colheadVar, 1):
            val = i.get()
            #filtered = ""
            if val == "set":
                if first:
                    first = False
                    statements[x] = "WHERE minis_list.set = \""+ set+ "\""
                else:
                    statements[x] = " AND minis_list.set = \""+ set+ "\""
                #statements[x] += no + "LIKE \"%" + val.strip("!") + "%\""

            elif val:
                if first:
                    first = False
                    statements[x] = "WHERE \"" + self.headers[x - 1]+ "\" "

                else:
                    statements[x] = " AND \"" + self.headers[x - 1] + "\" "

                for z in range(val.count(",")):
                    current_val = val.split(",")[z+1]
                    if "!" in current_val: no = "NOT "
                    else: no = ""

                    statements[x] += no + "LIKE \"%" + current_val.strip("!") + "%\" OR \"" + self.headers[x - 1]+ "\" "
                for z in range(val.count("&")):
                    current_val = val.split("&")[z + 1]
                    if "!" in current_val: no = "NOT "
                    else: no = ""
                    statements[x] += no + "LIKE \"%" + current_val.strip("!") + "%\" AND \"" + self.headers[x - 1] + "\" "

                val = val.split(",")[0]
                val = val.split("&")[0]
                tmp = "= "
                try:
                    test = int(val.strip("><"))
                    if "<" in val or ">" in val: tmp = ""
                    statements[x] += tmp + val
                except:
                    if "!" in val: no="NOT "
                    else: no=""
                    statements[x] += no + "LIKE \"%" + val.strip("!") + "%\""
        sortorder = self.var_sort.get().lower()
        print (order)
        statements.append(" ORDER BY minis_list.\""+sortorder+"\" "+order+", minis_list.id ASC")
        command = ""
        for x in statements:
            if x: command += str(x)
        print(command)
        #tempcommand = str("SELECT * FROM minis_list Inner Join minis_owned_matts on minis_list.uniq_id = minis_owned_matts.\"mini id\" WHERE minis_owned_matts.count is NULL and minis_list.faction = \"Rebel\" ORDER BY minis_list.cost ASC")
        #command = tempcommand

        cur = self.conn.cursor()
        cur.execute(command)
        table = cur.fetchall()

        if not (player == "None"):
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
        self.title("SW Minis Companion - v1.6")
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        #self.overrideredirect(1)
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
        #self.db_menubar.add_cascade(label="Refresh Filters", command=lambda: DbFrame.refreshfilters(self))
        # self.db_menubar.add_cascade(label="Load Player File", command=lambda: DbFrame.loadplayer())
        # self.db_menubar.add_command(label="All Minis")
        self.db_menubar.add_command(label="Drafter", command=lambda: self.show_frame("PackFrame"))
        self.db_menubar.add_command(label="DB Browser", command=lambda: self.show_frame("DbFrame"))
        self.db_menubar.add_command(label="Mini Maker", command=lambda: self.minimaker())

        self.db_menubar.add_command(label="- - -")

        self.db_menubar.add_command(label="Preferences", command=lambda: self.preferences())
        self.db_menubar.add_command(label="Clear Filters", command=lambda: self.clearfilters())
        self.db_menubar.add_cascade(label="Close", command=lambda: self.safeclose())
        #self.db_menubar.add_command(label="makeandruslist", command=lambda: DbFrame.exportscript(self))

        self.SETS = ["Alliance and Empire", "Bounty Hunters", "Alliance and Empire", "Champions of the Force",
                     "Clone Strike", "The Clone Wars",
                     "The Force Unleashed", "Galaxy at War", "Imperial Entanglements", "Jedi Academy",
                     "Knights of the Old Republic", "Legacy of the Force",
                     "Masters of the Force", "Revenge of the Sith", "Rebel Storm", "Dark Times", "Universe",
                     "Clone Wars Starter", "Clone Wars Scenario", "Battle of Hoth","Clone Wars Battles",
                     "The Attack on Teth","Showdown at Teth Palace","The Crystal Caves of Ilum","Affinity"], ["ae",
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
                                                                                      "uh",
                                                                                      "cwsp",
                                                                                      "cwmp",
                                                                                      "boh",
                                                                                      "cwbp",
                                                                                      "aot",
                                                                                      "stp",
                                                                                      "cci",
                                                                                      "affinity"]
        self.FACTIONS = ["Rebel", "Imperial", "The Old Republic", "The New Republic", "Sith", "Republic", "Seperatist",
                         "Yuuzhan Vong", "Mandolorian", "Fringe"]

        self.packtypes = ["Standard Pack", "Commons", "Uncommons", "Rares", "Very Rares", "Uniques", "Non-Unique"]
        self.pack_menubar = Menu(self)
        setlist_menu = Menu(self.pack_menubar)
        pack_menu = Menu(self.pack_menubar)
        self.config(menu=self.db_menubar)

        setmenu_VarList = []  # a list containing lists of variables for checkbox states
        packtype = StringVar(self)

        self.pack_menubar.add_command(label="Drafter", command=lambda: self.show_frame("PackFrame"))
        self.pack_menubar.add_command(label="DB Browser", command=lambda: self.show_frame("DbFrame"))
        self.pack_menubar.add_command(label="Mini Maker", command=lambda: self.minimaker())

        self.pack_menubar.add_command(label="- - -")

        self.pack_menubar.add_cascade(label="Sets", underline=0, menu=setlist_menu)
        self.pack_menubar.add_cascade(label="Pack Type", underline=0, menu=pack_menu)
        self.pack_menubar.add_command(label="Change Box Count",
                                      command=lambda: PackFrame.getbox(self))
        self.pack_menubar.add_command(label="1")
        self.qty_packs = 1
        self.pack_menubar.add_command(label="Go", underline=0,
                                      command=lambda: PackFrame.generate(self, self.conn, setmenu_VarList, packtype))
        self.pack_menubar.add_separator()
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

        # Setup the glossary window
        self.glossary = []
        for x in ["specialabilities", "forcepowers", "commandereffects"]:
            file = open("./DB/" + x + ".tsv", encoding="utf8")
            filelist = file.readlines()
            for i in filelist:
                # append a list, the entry name, then its description. when actually searching the glossary search both
                self.glossary.append(i.split("\t"))
            file.close()
        DbFrame.refreshgloss(self)

    def show_frame(self, page_name):  # swaps the left frame from editor to generator controls
        frame = self.frames[page_name]
        frame.tkraise()
        self.program = page_name
        if page_name == "PackFrame":
            self.config(menu=self.pack_menubar)
        elif page_name == "DbFrame":
            self.config(menu=self.db_menubar)

    def preferences(self):
        preferencesWindow = Toplevel(self)
        preferencesWindow.attributes('-topmost', 'true')
        preferencesWindow.geometry("750x525")

        self.paths = []
        file = open("./preferences", encoding="utf8")
        lines = file.readlines()
        for i in lines:
            print("read or write to pref file")

        self.forcepowers = []
        self.forcepowersfull = []
        file = open("./minimaker/forcepowers.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            self.forcepowersfull.append(i.split("\t"))
        file.close()
    def clearfilters(self):
        for x in self.colheadVar:
            x.set("")



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

    def exporttokens(self, lb):
        list = lb
        tokenlist = []
        source=os.getcwd()
        source+="\\tokens\\"

        for x in range(list.size()):
            tokenlist.append(list.get(x).split("_")[1])
            #cardlist.append(list.get(x).split("_")[1])
            #cost += int(list.get(x).split("_")[2])


        destination = filedialog.askdirectory(initialdir="./custom", title='token location')
        if destination is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        destination = destination.replace("/","\\",4)
        files=[]

        for x, i in enumerate(tokenlist):
            for t in os.listdir(source):
                if os.path.isfile(os.path.join(source, t)) and i in t:
                    files.append(t)

        for n in files:
            cmd = "copy "+source+n+" "+destination+"\\"+n
            os.system(cmd)



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
        key=""
        for x in range(list.size()):
            key += str(list.get(x))[1:] + "$"
            #key += str(list.get(x)).split("_")[1]+"_"
        key = key[:-1]
        print ("add keywords: ",key)
        pdf.set_keywords(key)
        pdf.output(file.name)

    def loadlist(self, lb):
        file = filedialog.askopenfile(initialdir="./custom", defaultextension='.sav')
        extension = (str(file.name).split(".")[-1]).lower()
        print (file.name)
        if extension == "pdf":
            pdf_toread = PdfFileReader(open(file.name, "rb"))
            pdf_info = pdf_toread.getDocumentInfo()
            if '/Keywords' in pdf_info:
                print(pdf_info['/Keywords'])
                keyword = str(pdf_info['/Keywords']).split("$")
                for n,x in enumerate(keyword):
                    lb.insert(n, x)
        elif extension == "sav":
            lines = file.readlines()
            lb.delete(0, 'end')
            for n, x in enumerate(lines):
                x = x[:-1]
                lb.insert(n, x)

    # def savelist(self, lb):
    #     list = lb
    #     self.lb3selected.delete(1.0, END)

    def preview(self, list):
        try:
            char = list.get(list.index(list.curselection()))
        except:
            print("changed lists")
        else:
            if len(char) > 100:  # basically are you trying to preview something in the DB view or the squad view
                set = char[43:70].rstrip(" ")  # interprets the line sent and takes the set out of it.
                id = "{:02d}".format(int(char[71:73].strip(" ")))
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

    def compare_mini(self, list, list2):
        try:
            char = list.get(list.index(list.curselection()))
        except:
            print("trying other list")
            char = list2.get(list2.index(list2.curselection()))
        if len(char) > 100:  # basically are you trying to preview something in the DB view or the squad view
            set = char[43:70].rstrip(" ")  # interprets the line sent and takes the set out of it.
            id = "{:02d}".format(int(char[71:73].strip(" ")))
            setshort = self.SETS[1][self.SETS[0].index(set)] + id
        else:
            setshort = char.split("_")[1]
        card = ("./cards/" + setshort + ".jpg")
        im = Image.open(card)
        imgwidth, imgheight = im.size
        imback = im.crop((imgwidth / 2, 0, imgwidth, imgheight))
        imback = imback.resize((int(imgwidth / 6), int(imgheight / 3)), Image.ANTIALIAS)
        imback = ImageTk.PhotoImage(imback)
        self.compare_lbl.configure(image=imback)
        self.compare.image = imback

    def squadcost(self):
        cost = 0
        for x in range(self.lb2.size()):
            cost += int(self.lb2.get(x).split("_")[2])
        self.count_label.set("Count: " + str(self.lb2.size()))
        self.cost_label.set("Points: " + str(cost))

    def sendcharacter(self, char):
        name = char[3:42].rstrip(" ")
        set = char[43:70].rstrip(" ")  # interprets the line sent and takes the set out of it.
        id = "{:02d}".format(int(char[71:73].strip(" ")))
        cost = "{:02d}".format(int(char[103:106].strip(" ")))
        setshort = self.SETS[1][self.SETS[0].index(
            set)] + id  # references the setlist for the shortname of the set the mini is from and rounds the id to two digits.

        self.lb2.insert(0, name + "_" + setshort + "_" + cost)
        self.count = self.lb2.size()
        self.count_label.set("Count: " + str(self.count))
        self.squadcost()

    def minimaker(self):
        makerWindow = Toplevel(self)
        makerWindow.attributes('-topmost', 'true')
        makerWindow.geometry("750x525")
        card = ("./minimaker/templates/02_fringe.png")
        self.portrait = ("./minimaker/blank.png")
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
        self.attacks = StringVar()
        self.attacks.set("")

        self.abilities = []
        self.abilitiesfull = []
        file = open("./minimaker/abilitylist.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            self.abilitiesfull.append(i.split("\t"))

        self.forcepowers = []
        self.forcepowersfull = []
        file = open("./minimaker/forcepowers.tsv", encoding="utf8")
        filelist = file.readlines()
        for i in filelist:
            self.forcepowersfull.append(i.split("\t"))
        file.close()

        self.force = IntVar()
        self.force.set(0)

        self.minicost = IntVar()
        self.minicost.set(5)

        bigfont = ImageFont.truetype('impact', size=20)
        font = ImageFont.truetype('impact', size=16)
        smfont = ImageFont.truetype('verdana', size=11)

        tech_small = ImageFont.truetype(r'.\DB\Tecnica Stencil\\ttf\\TecnicaStencil1Rg.ttf', 14)
        tech_bold = ImageFont.truetype(r'.\DB\Tecnica Stencil\\ttf\\TecnicaStencil1Bd.ttf', 14)
        tech_large = ImageFont.truetype(r'.\DB\Tecnica Stencil\\ttf\\TecnicaStencil1Bd.ttf', 17)
        #tech_small = TTFont(".\DB\Tecnica Stencil\\ttf\\TecnicaStencil1Bd.ttf")




        Label(makerWindow, text="Name: ").grid(row=0, column=2)
        name = StringVar(value='unnamed')
        namefld = Entry(makerWindow, width=20, textvariable=name).grid(row=0, column=3)

        Label(makerWindow, text="Cost: ").grid(row=0, column=4)
        cost = StringVar(value='')
        namefld = Entry(makerWindow, width=5, textvariable=cost).grid(row=0, column=5)

        statframe = LabelFrame(makerWindow, text="Stats")
        statframe.grid(row=1, column=2, rowspan=5, columnspan=2)
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

        traitframe = LabelFrame(makerWindow, text="Attributes")
        traitframe.grid(row=1, column=4, rowspan=5, columnspan=2)

        Checkbutton(traitframe, text="Unique", variable=self.unique, onvalue=20, offvalue=0).grid(row=0, column=0,columnspan=2)
        Checkbutton(traitframe, text="Melee", variable=self.melee, onvalue=1, offvalue=0).grid(row=1, column=0,columnspan=2)

        Label(traitframe, text="Attacks: ").grid(row=2, column=0)
        attackmenu = OptionMenu(traitframe, self.attacks, "", "Double Attack", "Triple Attack", "Quadruple Attack")
        attackmenu.config(width=10)
        attackmenu.grid(row=2, column=1)

        self.unique.trace("w", lambda x,y,m : refresh())
        self.melee.trace("w", lambda x,y,m : refresh())
        self.attacks.trace("w", lambda x,y,m : refresh())

        self.race = StringVar()
        self.race.set("")
        Label(traitframe, text="Race: ").grid(row=3, column=0)
        racemenu = Entry(traitframe, width=10, textvariable=self.race).grid(row=3, column=1)
        #racemenu = OptionMenu(traitframe, self.race, "None", "Droid", "Cyborg","---", "Ewok", "Trandoshan", "Ugnaught", "Wookie", "Gungan","Jawa")
        #racemenu.config(width=10)
        #racemenu.grid(row=3, column=1)

        self.faction = StringVar(value="Fringe")

        Label(traitframe, text="Faction: ").grid(row=4, column=0)
        factionmenu = OptionMenu(traitframe, self.faction, "Fringe", "Rebel", "Old Republic", "Republic",
                                 "New Republic", "Imperial", "Seperatist", "Sith", "Yuuzhan Vong", "Mandalorian")
        factionmenu.config(width=10)
        factionmenu.grid(row=4, column=1)
        self.faction.trace_variable("w", lambda x, y, z: factionchanged(x, y, z))  # DbFrame.refreshfilters(self))

        # OptionMenu(makerWindow,textvariable=)
        Button(makerWindow, text="Export", width=5, command=lambda: tempdef()).grid(row=7, column=2)
        Button(makerWindow, text="Change Avatar", width=5, command=lambda: changeportrait()).grid(row=7, column=3)

        abilitiesframe = LabelFrame(makerWindow, text="Abilities")
        forceframe = LabelFrame(makerWindow, text="Force Powers")
        abilitiesframe.grid(row=6, column=2, columnspan=2)
        forceframe.grid(row=6, column=4, columnspan=2)

        abilitieslb = Listbox(abilitiesframe, width=25, height=10)  # ,font=monofont)
        abilitieslb.grid(row=0, column=0)
        abilitieslb.bind('<Double-1>', lambda x: [
            addability(abilitieslb.get(abilitieslb.index(abilitieslb.curselection())),
                       abilitieslb.index(abilitieslb.curselection())), refresh()])
        for x, i in enumerate(self.abilitiesfull):
            abilitieslb.insert(x, i[0])

        forcelb = Listbox(forceframe, width=25, height=10)  # ,font=monofont)
        forcelb.grid(row=0, column=0)
        forcelb.bind('<Double-1>',
                     lambda x: [addforce(forcelb.get(forcelb.index(forcelb.curselection())),
                                         forcelb.index(forcelb.curselection())), refresh()])


        for x, i in enumerate(self.forcepowersfull):
            forcelb.insert(x, i[0])

        """unique, melee, options box to pick a race..."""

        def tempdef(cmom):
            print(cmom)

        def addability(thing, where):
            print(thing, where)
            self.abilities.append([thing, where])

        def addforce(thing, where):
            self.forcepowers.append([thing, where])

        def factionchanged(ignorea, ignoreb, ignorec):
            self.cardchanged = True
            refresh()

        def modstat(stat, dir):
            ministat = stat
            ministat.set(ministat.get() + dir)
            refresh()

        def changeportrait():
            f = filedialog.askopenfilename()
            self.portrait = f
            refresh()

        def refresh():
            txtoffset = 0

            hitpoints = self.hitpoints.get()
            defense = self.defense.get()
            attack = self.attack.get()
            damage = self.damage.get()
            force = self.force.get()
            # extracost = 0
            #
            # ranks_hp = hitpoints / 10 - 1
            # ranks_def = defense - 13
            # ranks_atk = attack - 4
            # ranks_dmg = damage / 10 - 1
            # dmgtax = 0.25 + float(self.melee.get())
            # cost_hp = ranks_hp ** 2 / 2
            # cost_def = ranks_def ** 2 / 2
            # cost_atk = ranks_atk ** 2 / 2
            # cost_dmg = ranks_dmg ** 2
            # cost_dmgtax = dmgtax * (ranks_hp + ranks_def + ranks_atk + ranks_dmg)

            #minicost = round(cost_hp + cost_def + cost_atk + cost_dmg + cost_dmgtax + force + 5)
            if self.cardchanged:
                card = ("./minimaker/templates/02_" + str(self.faction.get()) + ".png")
                self.cardchange = False
            offsets = []
            #              [name],[cst],[stats,spread]
            offsets.append([20,10,-2,12,18,11,3])


            avatar = Image.open(self.portrait).convert("RGBA")
            imgwidth, imgheight = avatar.size
            sizesm = int(imgwidth / 2.5), int(imgheight / 2.5)
            avatar = avatar.resize(sizesm, resample=Image.ANTIALIAS)

            im = Image.open(card).convert("RGBA")
            imgwidth, imgheight = im.size
            imback = im.crop((imgwidth / 2, 0, imgwidth, imgheight))
            imback.paste(avatar, (25, 625), avatar)
            sizesm = int(imgwidth / 4), int(imgheight / 2)
            imback = imback.resize(sizesm, resample=Image.ANTIALIAS)
            draw = ImageDraw.Draw(imback)

            # # 680x745

            draw.text((60+offsets[0][0], 15+offsets[0][0]), str(name.get()), (255, 255, 255), font=bigfont)
            draw.text((332+offsets[0][2]-(len(cost.get())*4), 25+offsets[0][3]), str(cost.get()), (0, 0, 0), font=font)

            draw.text((102+offsets[0][4]-(len(str(hitpoints))*4), 85+offsets[0][5]), str(hitpoints + self.unique.get()), (0, 0, 0), font=font)
            draw.text((102+offsets[0][4]-(len(str(defense))*4), 138+offsets[0][5]+offsets[0][6]), str(defense), (0, 0, 0), font=font)
            draw.text((102+offsets[0][4]-(len(str(attack))*4), 190+offsets[0][5]+offsets[0][6]*2), str(attack), (0, 0, 0), font=font)
            draw.text((102+offsets[0][4]-(len(str(damage))*4), 243+offsets[0][5]+offsets[0][6]*3), str(damage), (0, 0, 0), font=font)
            styleoffset=10
            draw.text((145 + styleoffset, 95 + txtoffset), "Special Abilities", (0, 0, 0), font=tech_large)
            txtoffset += 20
            offsetmod = 12
            if self.unique.get() > 0:
                draw.text((145+styleoffset, 100 + txtoffset), "Unique", (0, 0, 0), font=tech_small)
                txtoffset += offsetmod
            if not self.race.get() == "":
                draw.text((145+styleoffset, 100 + txtoffset), self.race.get(), (0, 0, 0), font=tech_small)
                txtoffset += offsetmod
            if self.melee.get() == "1":
                extra=str(self.attacks.get())
                if not extra == "0":
                    term = ":"+extra
                else: term = ""
                draw.text((145+styleoffset, 100 + txtoffset), "Melee"+term, (0, 0, 0), font=tech_small)
                txtoffset += offsetmod
            for x in self.abilities:
                read = self.abilitiesfull[x[1]]
                lines = textwrap.wrap(read[0] + ". " + read[1], width=48-styleoffset)
                for line in lines:
                    width, height = tech_small.getsize(line)
                    # draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
                    draw.text((145+styleoffset, 100 + txtoffset), line, (0, 0, 0), font=tech_small)
                    txtoffset += height
                txtoffset += 0
                # draw.text((145, 95 + txtoffset), str(read[0])+". "+str(read[1]),(0, 0, 0), font=smfont)
                #txtoffset += 20
                #extracost += int(read[3][:2])
            if force > 0:
                draw.text((145 + styleoffset, 100 + txtoffset), "Force Powers", (0, 0, 0), font=tech_large)
                draw.text((145 + styleoffset, 125 + txtoffset), "Force " + str(force), (0, 0, 0), font=tech_small)
                txtoffset += 20
            for x in self.forcepowers:
                read = self.forcepowersfull[x[1]]
                lines = textwrap.wrap(read[0] + ". " + read[1], width=48 - styleoffset)
                for line in lines:
                    width, height = tech_small.getsize(line)
                    # draw.text(((w - width) / 2, y_text), line, font=font, fill=FOREGROUND)
                    draw.text((145+styleoffset, 125 + txtoffset), line, (0, 0, 0), font=tech_small)
                    txtoffset += height

            render = ImageTk.PhotoImage(imback)
            img = Label(makerWindow, image=render, width=imgwidth / 4, height=imgheight / 2)
            img.image = render
            img.grid(row=0, column=0, rowspan=12)

        refresh()

if __name__ == "__main__":
    app = Main()
    mainloop()
