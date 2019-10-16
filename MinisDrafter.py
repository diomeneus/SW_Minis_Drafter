from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
#from PIL import Image,ImageTk,ImageDraw
from PIL import Image, ImageDraw, ImageTk, ImageFont,ImageChops
from math import cos, sin, sqrt, radians, floor
import math
import datetime

import random
import os
import ast

import sqlite3
from sqlite3 import Error

from fpdf import FPDF
# class Controls_GearGen(Frame):


class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("SW Minis Drafter")
        self.geometry("1130x2000")
        mainFrame = Frame(self)
        mainFrame.grid(column=0, row=0)

        controlFrame = Frame(mainFrame)
        controlFrame.grid(column=0,row=0)

        displayFrame = Frame(mainFrame)
        displayFrame.grid(column=0, row=1)
        self.SETS = [["ae", "Alliance and Empire"],
                     ["bh", "Bounty Hunters"],
                     ["ae", "Alliance and Empire"],
                     ["cotf", "Champions of the Force"],
                     ["cs", "Clone Strike"],
                     ["cw", "The Clone Wars"],
                     ["fu", "The Force Unleashed"],
                     ["gaw", "Galaxy at War"],
                     ["ie", "Imperial Entanglements"],
                     ["ja", "Jedi Academy"],
                     ["kotor", "Knights of the Old Republic"],
                     ["lotf", "Legacy of the Force"],
                     ["motf", "Masters of the Force"],
                     ["rots", "Revenge of the Sith"],
                     ["rs", "Rebel Storm"],
                     ["tdt", "Dark Times"],
                     ["uh", "Universe"]]
        self.RARITY = ["Common", "Uncommon", "Rare", "Very Rare"]
        self.FACTIONS = ["Rebel", "Imperial", "The Old Republic", "The New Republic", "Sith", "Republic", "Seperatist",
                         "Yuuzhan Vong", "Mandolorian", "Fringe"]

        self.setname = []
        for x in (self.SETS):
            self.setname.append(x[1])
        self.packtypes=["Standard Pack","Commons Only","Non Unique Only"]

        menubar = Menu(self)
        setlist_menu = Menu(menubar)
        pack_menu = Menu(menubar)

        self.config(menu=menubar)

        sm_list = []  # a list of submenus ***MAY BE AN OBSOLETE AND UNNEEDED VARIABLE***
        setmenu_VarList = []  # a list containing lists of variables for checkbox states
        packmenu_VarList = []
        multipleopen = IntVar()

        menubar.add_cascade(label="Sets", underline=0, menu=setlist_menu)
        menubar.add_cascade(label="Pack Type", underline=0, menu=pack_menu)
        menubar.add_checkbutton(label="Additional Boxes",variable=multipleopen)
        menubar.add_command(label="Go", underline=0, command=lambda: generate(self.conn))
        menubar.add_separator()
        menubar.add_command(label="DB Browser",command=lambda : self.popout(self.conn))
        menubar.add_command(label="AB", command=lambda: self.abilitychecker(self.conn, "special abilities"))
        menubar.add_command(label="FC", command=lambda: self.abilitychecker(self.conn, "force powers"))

        for _ in enumerate(self.setname): setmenu_VarList.append(IntVar(self))
        for i in setmenu_VarList:i.set(1)

        setlist_menu.add_command(label="All", command=lambda: modAll(setmenu_VarList, 1))
        setlist_menu.add_command(label="None", command=lambda: modAll(setmenu_VarList, 0))
        setlist_menu.add_separator()
        for index, i in enumerate(self.setname):
            setlist_menu.add_checkbutton(label=i, variable=setmenu_VarList[index], onvalue=1, offvalue=0,
                                command=lambda: refreshState())

        for _ in enumerate(self.packtypes): packmenu_VarList.append(IntVar(self))
        #for i in setmenu_VarList:i.set(1)
        for index,i in enumerate(self.packtypes):
            pack_menu.add_radiobutton(label=i,variable=packmenu_VarList[index], value=1)



        var_rarity = StringVar(self)
        var_rarity.set("Standard Pack")  # default value
        var_faction = StringVar(self)
        var_faction.set("Any")  # default value

        #OptionMenu(controlFrame, var_set, *self.setname).grid(column=0, row=0)

        OptionMenu(controlFrame, var_rarity, *self.RARITY).grid(column=1, row=0)
        OptionMenu(controlFrame, var_faction, *self.FACTIONS).grid(column=2, row=0)

        packtype = StringVar(self)
        packtype.set("Packs")
        Label (controlFrame,textvariable=packtype).grid(column=4, row=0)
        qty_packs = Entry(controlFrame, width=5)
        qty_packs.grid(column=5, row=0)
        qty_packs.insert(END, '1')

        width = 350
        height = 350

        qty_packs.focus_set()



        database = "./DB/SWminis.db"
        self.conn = self.create_connection(database)
        self.rowcounts(self.conn)  # counts the max rowlength for each table.

        def modAll(var, state):
            for index, i in enumerate(var):
                var[index].set(state)

        def open_player():
            self.file_path = filedialog.askopenfilename()

        def save_player():
            # should only invoke the dialog for path and name 1st time.
            if not self.file_path: self.file_path = filedialog.askopenfilename()

        def generate(conn):
            cur = conn.cursor()
            cardlist = []
            pdf = FPDF()
            pdf.set_font('Arial','B',10)

            """Grab the sets that are turned on"""
            setsenabled = []
            for x,i in enumerate(setmenu_VarList):
                if i.get() == 1:
                    setsenabled.append(self.setname[x])


            print (setsenabled)
            for p in range(1,int(qty_packs.get())+1):
                print ("opening pack",p)
                pdf.add_page()

                minilist = []
                selected_set = random.choice(setsenabled)
                #selected_set = "Rebel Storm"
                for x in self.SETS:
                    if x[1] == selected_set: short = x[0] #a crude way to set the short form of your selected set
                print(selected_set,short)

                if var_rarity.get() == "Standard Pack":

                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \"common\"")
                    commons= cur.fetchall()
                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \"uncommon\"")
                    uncommons = cur.fetchall()
                    if random.choice([1,2,3]) == 1: rare="very rare"
                    else: rare = "rare"
                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \""+rare+"\"")
                    rares = cur.fetchall()
                    for x in range (4):
                        mini = random.choice(commons)
                        commons.remove(mini)
                        minilist.append(mini)
                    for x in range (2):
                        mini = random.choice(uncommons)
                        uncommons.remove(mini) # no duplicates
                        minilist.append(mini)
                    minilist.append(random.choice(rares))


                    #CREATES THE CARDS AND RENDERS THEM ON SCREEN
                    rw=0
                    for x,i in enumerate(minilist):
                        card = ("./cards/"+short+"{:02d}".format(i[0])+".jpg")
                        im = Image.open(card)
                        width, height = im.size
                        imback = im.crop((width/2, 0, width, height))

                        #imback = imback.resize((int(width / 6), int(height / 3)))
                        imfront = im.crop((0, 0, width/2, height))
                        cardlist.append(imback)

                        imback.save(str(p)+"_"+str(x)+"temp.png")
                        load = Image.open(str(p)+"_"+str(x)+"temp.png")
                        render = ImageTk.PhotoImage(load)
                        #render_sm = render.subsample(2,2)
                        img = Label(self, image=render,width=int(width / 6),height=int(height / 3))
                        img.image = render
                        col = x % 3
                        if (x % 3 == 0): rw +=1
                        img.grid(row=rw,column=col)

                    #READS THE TEMPORARY PNGS CREATED AND PUTS THEM ON A PDF PAGE
                    rw=0
                    size = 65
                    width=64
                    height=width*1.39
                    pdf.text(x=10, y=5, txt="Pack "+str(p)+" - "+str(selected_set))
                    pdf.rect(x=73, y=191, w=width, h=height)
                    pdf.rect(x=138,y=191, w=width, h=height)
                    for x,i in enumerate(minilist):
                        col = x % 3
                        if (x % 3 == 0): rw += 1
                        pdf.image(str(p)+"_"+str(x)+"temp.png",x=col*size+8,y=rw*size*1.39-80,w=width,h=height)  # , x=10, y=8, w=100)
                        print (i)
                        pdf.text(x=143, y=201+x*4, txt=str(i[2])+"  ["+str(i[0])+"]")



            time = datetime.datetime.now()
            time = (str(time)[-6:])
            pdf.output("./packs/packname"+time+".pdf")





    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

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


    def popout(self,conn):  # makes a popup window with the current settlement and the full description.

        width = 1200
        height = 600
        iheight = height - 100
        iwidth = width - 100

        popup = Toplevel()
        popup.title("DB Browser")
        popup.geometry("1300x600")
        popupbar = Menu(popup)
        popupbar.add_cascade(label="Refresh Filters", command=lambda: refreshfilters())
        popupbar.add_cascade(label="Close", command=popup.destroy)
        popup.config(menu=popupbar)

        topframe = Frame(popup, width=iwidth)
        topframe.grid(row=0,column=0)
        bottomframe = Frame(popup, width=width,height=iheight)
        bottomframe.grid(row=1,column=0)

        colheadVar =[]
        datarows = []
        columnnames = ["uniq_id", "name", "set", "id", "faction", "rarity", "cost", "size", "hit points", "defense", "attack",
                       "damage", "special abilities", "force points", "force powers"]
        for x in range (len(columnnames)):
            colheadVar.append(StringVar(self))


        columnwidth=[1,20,12,3,10,4,3,5,3,3,3,3,20,3,20]
        tableheight = 50
        tablewidth = len(columnnames)
        for j in range (tablewidth):
            Label(bottomframe,text=columnnames[j]).grid(row=0,column=j)
            Entry(bottomframe,text="filter entry",width=columnwidth[j],textvariable=colheadVar[j]).grid(row=1, column=j)

        def refreshfilters():
            for x in datarows: x.destroy()
            datarows.clear()
            print ("am I clean now? ",datarows)

            statements =[False] * 16
            statements[0] = "SELECT * FROM minis_list "
            first = False
            for x,i in enumerate(colheadVar,1):
                val=i.get()
                mod=""
                mod2=""
                if val:
                    if not first:
                        first=True
                        if ">" in val or "<" in val: statements[x] = "WHERE \"" + columnnames[x-1] + "\" "+ val
                        else: statements[x] = "WHERE \"" + columnnames[x-1] + "\" LIKE \"%" + val + "%\""
                    else :
                        if ">" in val or "<" in val: statements[x] = " AND \"" + columnnames[x-1] + "\" "+ val
                        else: statements[x]=" AND \""+columnnames[x-1]+"\" LIKE \"%"+val+"%\""

            command =""
            for x in statements:
                if x: command += str(x)
            print(command)
            cur = conn.cursor()
            cur.execute(command)
            table = cur.fetchall()
            print (table)
            tablelength=len(table)
            #for x in table: print (x)
            if not first:tablelength=50
            print(tablelength,"results found")
            for i in range(tablelength):  # Rows
                for j in range(tablewidth):  # Columns
                    tmp = Label(bottomframe, text=table[i][j])
                    tmp.grid(row=i + 2, column=j)
                    datarows.append(tmp)

        refreshfilters()
        popup.mainloop()

    def rowcounts(self, conn):
        self.count=[0]
        cur = conn.cursor()

        n = 0
        for x in (["Rebel Storm"]):#self.SETS):
            #print (x)
            command = "SELECT COUNT() FROM minis_list WHERE \"SET\" = \"" + x+"\""
            print (command)
            cur.execute(command)
            (self.count[n],) = cur.fetchone()
            n += 1
        n = 0
        print (self.count)

    #pretty confident this is too basic and also not used currently.
    def valuenames(self, conn, table, column, value):
       cur = conn.cursor()
       statement = ("SELECT * FROM " + table + " WHERE " + column + " = " + value)
       cur.execute(statement)
       return cur.fetchone()

# As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()
