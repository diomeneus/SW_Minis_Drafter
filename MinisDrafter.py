from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
from PIL import Image,ImageTk,ImageDraw

from math import cos, sin, sqrt, radians, floor
import math

import random
import os
import ast

import sqlite3
from sqlite3 import Error
# class Controls_GearGen(Frame):


class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("SW Minis Drafter")
        self.geometry("1500x650")
        """OK, here is the plan... I'm going to injest
        This quality gear generator with...
        Magic Item Generator...
        Crafting tracker...

        Player version that tracks crafting progress?
        DM version for generating gear

        you need a system for how the 'minor quirks' are adjusted based on YOU making the item.
        """
        mainFrame = Frame(self)
        mainFrame.grid(column=0, row=0)

        controlFrame = Frame(mainFrame)
        controlFrame.grid(column=0,row=0)

        displayFrame = Frame(mainFrame)
        displayFrame.grid(column=0, row=1)

        self.SETS = [["ae", "Alliance and Empire"],
                ["bh", "Bounty Hunters"],
                ["boh", "The Battle of Hoth"],
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

        # setting up our frames

        # self.frames = {}
        # for F in (Controls_Editor, Controls_Generator):
        #     page_name = F.__name__
        #     frame = F(parent=mainFrame, controller=self)
        #     self.frames[page_name] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")
        # self.show_frame("Controls_Generator")
        # controlFrame = Frame(self)
        # controlFrame.grid(column=0,row=0)

        width = 350
        height = 350

        #self.can = Canvas(displayFrame, width=width, height=height, bg="#fffafa")
        #self.can.grid(row=0, column=0)  # .pack()
        qty_packs.focus_set()

        #vbar = Scrollbar(mainFrame, orient=VERTICAL)
        #vbar.grid()
        #vbar.config(command=self.can.yview)
        #self.can.config(yscrollcommand=vbar.set)


        database = "./SWminis.db"
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
            for p in range(1,int(qty_packs.get())+1):
                print ("opening pack",p)
                minilist = []
                #if all sets selected_set = random.choice(self.setname)
                selected_set = "Rebel Storm"
                for x in self.SETS:
                    if x[1] == selected_set: short = x[0]
                print(short)
                if var_rarity.get() == "Standard Pack":

                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \"common\"")
                    commons= cur.fetchall()
                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \"uncommon\"")
                    uncommons = cur.fetchall()
                    cur.execute(
                        "SELECT \"id\", \"set\", \"name\" FROM minis_list WHERE \"SET\" = \""+selected_set+"\" AND \"rarity\" = \"rare\" OR \"rarity\" = \"very rare\"")
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
                    # print (minilist)


                    for x,i in enumerate(minilist):
                        card = ("./cards/"+short+"{:02d}".format(i[0])+".jpg")
                        im = Image.open(card)
                        width, height = im.size
                        imback = im.crop((width/2, 0, width, height))
                        imback = imback.resize((int(width / 4), int(height / 2)))

                        imfront = im.crop((0, 0, width/2, height))
                        cardlist.append(imback)

                        imback.save("temp.png")

                        load = Image.open("temp.png")
                        render = ImageTk.PhotoImage(load)

                        img = Label(self, image=render)
                        img.image = render
                        img.grid(row=1,column=0)#img.place(x=0, y=0)

                    print(cardlist)
                        # Shows the image in image viewer

                    preview = ImageTk.PhotoImage(Image.open("temp.png"))
                    #ImageDraw.ImageDraw(imback)
                    #imfront.show()

                    #back = ImageTk.PhotoImage(imback)
                    #self.can.create_image(10, 50, image=back, anchor=NW)





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
        # for x in (
        # "layout_basic", "layout_coastal", "layout_rivers", "layout_confluence", "layout_estuary", "layout_wetland"):
        #     cur.execute("SELECT COUNT(1) from " + x)
        #     (self.layoutcount[n],) = cur.fetchone()
        #     n += 1
        # n = 0
        # for x in ("generic", "good", "evil", "magical", "dwarven", "elven", "halfling", "orc"):
        #     cur.execute("SELECT COUNT(1) from name_" + x + "_prefix")
        #     (self.namecount[n],) = cur.fetchone()
        #     cur.execute("SELECT COUNT(1) from name_" + x + "_center")
        #     (self.namecount[n + 1],) = cur.fetchone()
        #     cur.execute("SELECT COUNT(1) from name_" + x + "_suffix")
        #     (self.namecount[n + 2],) = cur.fetchone()
        #     n += 3

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
