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
        self.RARITY = ["Common","Uncommon","Rare","Very Rare"]
        self.FACTIONS = ["Rebel","Imperial","The Old Republic","The New Republic","Sith","Republic","Seperatist","Yuuzhan Vong","Mandolorian","Fringe"]

        self.setname=[]
        for x in (self.SETS):
            self.setname.append(x[1])

        var_set = StringVar(self)
        var_set.set("Sets")  # default value
        var_rarity = StringVar(self)
        var_rarity.set("Standard Pack")  # default value
        var_faction = StringVar(self)
        var_faction.set("Any")  # default value

        OptionMenu(controlFrame, var_set, *self.setname).grid(column=0, row=0)
        OptionMenu(controlFrame, var_rarity, *self.RARITY).grid(column=1, row=0)
        OptionMenu(controlFrame, var_faction, *self.FACTIONS).grid(column=2, row=0)

        packtype = StringVar(self)
        packtype.set("Packs")
        Label (controlFrame,textvariable=packtype).grid(column=4, row=0)
        qty_packs = Entry(controlFrame, width=5)
        qty_packs.grid(column=5, row=0)
        qty_packs.insert(END, '1')
        go = Button(controlFrame, text="Go", command=lambda: generate(self.conn))
        go.grid(column=6, row=0)

        width = 350
        height = 350

        qty_packs.focus_set()



        database = "./DB/SWminis.db"
        self.conn = self.create_connection(database)
        self.rowcounts(self.conn)  # counts the max rowlength for each table.

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

            for p in range(1,int(qty_packs.get())+1):
                print ("opening pack",p)
                pdf.add_page()

                minilist = []
                if var_set.get() == "Sets": selected_set = random.choice(self.setname)
                else: selected_set = var_set.get()
                #selected_set = "Rebel Storm"
                for x in self.SETS:
                    if x[1] == selected_set: short = x[0]
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
                        imback = imback.resize((int(width / 4), int(height / 2)))
                        imfront = im.crop((0, 0, width/2, height))
                        cardlist.append(imback)

                        imback.save(str(p)+"_"+str(x)+"temp.png")
                        load = Image.open(str(p)+"_"+str(x)+"temp.png")
                        render = ImageTk.PhotoImage(load)
                        img = Label(self, image=render)
                        img.image = render
                        col = x % 3
                        if (x % 3 == 0): rw +=1
                        img.grid(row=rw,column=col)

                    #READS THE TEMPORARY PNGS CREATED AND PUTS THEM ON A PDF PAGE
                    rw=0
                    size = 65
                    width=59
                    height=width*1.39
                    pdf.text(x=10, y=5, txt="Pack "+str(p)+" - "+str(selected_set))
                    pdf.rect(x=75, y=191, w=width, h=height)
                    pdf.rect(x=140,y=191, w=width, h=height)
                    for x,i in enumerate(minilist):
                        col = x % 3
                        if (x % 3 == 0): rw += 1
                        pdf.image(str(p)+"_"+str(x)+"temp.png",x=col*size+10,y=rw*size*1.39-80,w=width,h=height)  # , x=10, y=8, w=100)
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

    def popout(self):  # makes a popup window with the current settlement and the full description.
        width = 800
        height = 600
        # self.image = self.trim(self.image)
        popup = Toplevel()
        popup.title("Popup")
        popup.geometry("800x600")
        iheight = 500
        iwidth = 700
        popupbar = Menu(popup)
        popupbar.add_cascade(label="Save", command=lambda: self.save(True))
        popupbar.add_cascade(label="Print", command=lambda: [self.save(False), self.make_print()])
        popupbar.add_cascade(label="Close", command=popup.destroy)
        popup.config(menu=popupbar)
        topframe = Frame(popup, width=width, height=iheight)
        topframe.pack(side=TOP)
        bottomframe = Frame(popup, width=width)
        bottomframe.pack(side=BOTTOM)
        leftframe = Frame(topframe, bd=1, width=iwidth, bg="black")
        leftframe.pack(side=LEFT)
        rightframe = Frame(topframe, width=width - iwidth, height=iheight)  # ,bg="black",bd=1)
        rightframe.pack(side=RIGHT)

        TextArea = Text(rightframe, height=20, width=60)
        TextArea.insert(END, "Words")
        TextArea.pack(expand=YES, fill=BOTH)
        TextArea.config(font="arial", wrap=WORD)  # ('Arial', 10, 'bold', 'italic'))

        TextArea2 = Text(bottomframe, height=20, width=int(width / 9))
        TextArea2.insert(END, "More words")
        TextArea2.pack(expand=YES, fill=BOTH)
        TextArea2.config(font="arial", wrap=WORD)

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
    print ("poop")
