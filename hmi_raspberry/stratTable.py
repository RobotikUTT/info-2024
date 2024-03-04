######################################################################################
#
#       PAINT
# gestion de l'écran de strat
#
######################################################################################

from tkinter import *
from math import *

affCoef = 4 # echelle d'affichage
affSize = 20  # taille de la pastille

servo_pos = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 164, 25], [5, 160, 15], [6, 10, 155],
             [7, 0, 180], [8, 30, 160], [9, 180, 0], [10, 40, 140]]

zone_depart = [[0, 45, 0, 45, 0, '#005b8c'], [0, 45, 78, 122, 0, '#f7b500'], [0, 45, 155, 200, 0, '#005b8c'],
               [255, 300, 0, 45, 180, '#f7b500'], [255, 300, 78, 122, 180, '#005b8c'], [255, 300, 155, 200, 180, '#f7b500']]


zone_recal = [[0, 12, 0, 95, 0], [0, 12, 105, 200, 0],
              [0, 300, 0, 12, 90], [0, 300, 188, 200, -90],
              [288, 300, 0, 95, 180], [288, 300, 105, 200, 180]]

zone_depose = [[0, 20, 50, 72, 180, False, True,  '#f7b500'], [0, 20, 127, 150, 180, False, True, '#005b8c'],
               [280, 300, 50, 72, 0, False, True,  '#005b8c'], [280, 300, 127, 150, 0, False, True, '#f7b500'],
               [60, 92.5, 180, 200, 90, False, True , '#005b8c'], [207.5, 240, 180, 200, 90, False, True, '#f7b500'],
               [0, 45, 0, 45, 180, False, False,  '#005b8c'], [0, 45, 78, 122, 180, False, False, '#f7b500'], [0, 45, 155, 200, 180, False, False, '#005b8c'],
               [255, 300, 0, 45, 0, False, False , '#f7b500'], [255, 300, 78, 122, 0, False, False, '#005b8c'], [255, 300, 155, 200, 0, False, False, '#f7b500']]

zone_panneau = [[ 27.5, 5, True,  '#005b8c'],[ 50, 5, True,  '#005b8c'],[ 72.5, 5, True,  '#005b8c'],
                [ 127.5, 5, True, '#ffffff'],[ 150, 5, True, '#ffffff'],[ 172.5, 5, True, '#ffffff'],
                [ 227.5, 5, True, '#f7b500'],[ 250, 5, True, '#f7b500'],[ 272.5, 5, True, '#f7b500']]

zone_capture = [[ 5, 61.25, True, True, 180],[5 , 138.75, True, True,180],
                [ 295, 61.25, True, True, 0],[295, 138.75, True, True, 0],
                [90, 70, True, False, 0], [90, 130, True, False, 0], [140, 50, True, False, 0], [140, 150, True, False, 0], [190, 70, True, False, 0], [190, 130, True, False, 0],
                [110, 70, True, False, 180], [110, 130, True, False, 180], [160, 50, True, False, 180], [160, 150, True, False, 180], [210, 70, True, False, 180], [210, 130, True, False, 180],
                [100, 5, True, True, -90],[ 200, 5, True, True, -90]]

zone_pami = [[106, 149, 186, 200, 90,  '#005b8c'], [151, 194, 186, 200, 90, '#f7b500']]

ini_lst = []
cmd_lst = []
cmd_lst_2 = []
end_lst = []

class Paint(object):
    DEFAULT_PEN_SIZE = 10.0

    def __init__(self):
        self.action = None
        self.start_x = None
        self.start_y = None
        self.temp_x = None
        self.temp_y = None
        self.temp_z = None
        self.root = Tk()
        self.pot = False
        self.plante = False

        self.clear_button = Button(self.root, text='Reset', height=1, width=10, command=self.use_clear, bg='red')
        self.clear_button.grid(row=0, column=1)

        self.recal_button = Button(self.root, text='Recallage', height=1, width=10, command=self.use_recal)
        self.recal_button.grid(row=1, column=1)

        self.capture_button = Button(self.root, text='Capture', height=1, width=10, command=self.use_capture)
        self.capture_button.grid(row=2, column=1)

        self.depose_button = Button(self.root, text='Dépose', height=1, width=10, command=self.use_depose)
        self.depose_button.grid(row=3, column=1)

        self.panneau_button = Button(self.root, text='PS', height=1, width=10, command=self.use_panneau)
        self.panneau_button.grid(row=4, column=1)

        self.pami_button = Button(self.root, text='PAMI', height=1, width=10, command=self.use_pami)
        self.pami_button.grid(row=5, column=1)

        self.end_button = Button(self.root, text='Arrive', height=1, width=10, command=self.use_end)
        self.end_button.grid(row=6, column=1)

        self.domatch_button = Button(self.root, text='GO', height=2, width=10, command=self.use_domatch, bg='green')
        self.domatch_button.grid(row=7, column=1)

        self.active_button = self.recal_button

        self.c = Canvas(self.root, bg='white', width=300 * affCoef, height=200 * affCoef)  #
        self.c.grid(row=0, column=0, rowspan=8)

        myImage = PhotoImage(file="fond" + str(affCoef) + ".png")
        self.c.create_image(0, 0, anchor=NW, image=myImage)
        self.setup()
        self.root.mainloop()

    def setup(self):
        self.start_x = None
        self.start_y = None
        self.line_width = self.DEFAULT_PEN_SIZE  # self.choose_size_button.get()
        self.color = "black"
        self.action = "start"
        self.desactivate_button()
        self.active_button = self.recal_button
        # self.c.bind('<Button-1>', self.press)
        self.c.bind('<ButtonRelease-1>', self.release)
        self.c.delete("zones")
        self.c.delete("trajectory")
        self.c.delete("robot")

        ini_lst.clear()
        cmd_lst.clear()
        cmd_lst_2.clear()
        end_lst.clear()
        self.root.configure(bg='white')

        for i in range(len(zone_capture)):
            zone_capture[i][2] = True

        self.pot = False
        self.plante = False

        for i in range(len(zone_depose)):
            zone_depose[i][5] = True

        for i in range(len(zone_depart)):
            self.c.create_rectangle(zone_depart[i][0] * affCoef, (200 - zone_depart[i][2]) * affCoef,
                                    zone_depart[i][1] * affCoef, (200 - zone_depart[i][3]) * affCoef,
                                    width=3 * affCoef, outline=zone_depart[i][5], tags="zones")

    def use_recal(self):
        self.c.delete("zones")
        if self.action != "recal":
            self.activate_button(self.recal_button)
            for i in range(len(zone_recal)):
                self.c.create_rectangle(zone_recal[i][0] * affCoef, (200 - zone_recal[i][2]) * affCoef,
                                        zone_recal[i][1] * affCoef, (200 - zone_recal[i][3]) * affCoef,
                                        width=0, outline='red', fill='red', tags="zones")
            self.action = "recal"
        else:
            self.desactivate_button()
            self.action = "goto"

    def use_capture(self):
        self.c.delete("zones")
        if not (self.plante and self.pot):
            self.activate_button(self.capture_button)
            for i in range(len(zone_capture)):
                if zone_capture[i][2] and not self.plante and not zone_capture[i][3]:
                    self.c.create_oval((zone_capture[i][0] - 6) * affCoef, (200 - zone_capture[i][1] - 6) * affCoef,
                                       (zone_capture[i][0] + 6) * affCoef, (200 - zone_capture[i][1] + 6) * affCoef,
                                       width=0, outline='red', fill='red', tags="zones")

                if zone_capture[i][2] and not self.pot and zone_capture[i][3]:
                    self.c.create_oval((zone_capture[i][0] - 6) * affCoef, (200 - zone_capture[i][1] - 6) * affCoef,
                                       (zone_capture[i][0] + 6) * affCoef, (200 - zone_capture[i][1] + 6) * affCoef,
                                       width=0, outline='red', fill='red', tags="zones")
            self.action = "capture"
        else:
            self.desactivate_button()
            self.action = "goto"

    def use_panneau(self):
        self.c.delete("zones")
        self.activate_button(self.panneau_button)
        for i in range(len(zone_panneau)):
            self.c.create_oval((zone_panneau[i][0] - 6) * affCoef, (200 - zone_panneau[i][1] - 6) * affCoef,
                               (zone_panneau[i][0] + 6) * affCoef, (200 - zone_panneau[i][1] + 6) * affCoef,
                               width=0, outline=zone_panneau[i][3], fill=zone_panneau[i][3], tags="zones")
        self.action = "panneau"

    def use_pami(self):
        self.c.delete("zones")
        self.activate_button(self.pami_button)
        for i in range(len(zone_pami)):
            if zone_pami[i][2]:
                self.c.create_rectangle(zone_pami[i][0] * affCoef, (200 - zone_pami[i][2]) * affCoef,
                                        zone_pami[i][1] * affCoef, (200 - zone_pami[i][3]) * affCoef,
                                        width=0, outline=zone_pami[i][5], fill=zone_pami[i][5], tags="zones")
        self.action = "pami"

    def use_depose(self):
        self.c.delete("zones")
        if self.action != "depose":
            self.activate_button(self.depose_button)
            for i in range(len(zone_depose)):

                # zone libre et (zone en bas ou zone non occupe)
                if zone_depose[i][5] and (i > 3 or not zone_capture[i][2]):
                    self.c.create_rectangle(zone_depose[i][0] * affCoef, (200 - zone_depose[i][2]) * affCoef,
                                            zone_depose[i][1] * affCoef, (200 - zone_depose[i][3]) * affCoef,
                                            width=3 * affCoef, outline=zone_depose[i][7], fill=zone_depose[i][7],
                                            tags="zones")
                else:
                    self.c.create_rectangle(zone_depose[i][0] * affCoef, (200 - zone_depose[i][2]) * affCoef,
                                            zone_depose[i][1] * affCoef, (200 - zone_depose[i][3]) * affCoef,
                                            width=3 * affCoef, outline=zone_depose[i][7], fill='red', tags="zones")
            self.action = "depose"
        else:
            self.desactivate_button()
            self.action = "goto"

    def use_domatch(self):
        self.root.destroy()

    def use_end(self):
        self.c.delete("zones")

        for i in range(len(zone_depart)):
            self.c.create_rectangle(zone_depart[i][0] * affCoef, (200 - zone_depart[i][2]) * affCoef,
                                    zone_depart[i][1] * affCoef, (200 - zone_depart[i][3]) * affCoef,
                                    width=3 * affCoef, outline=zone_depart[i][5], tags="zones")
        if self.action != "end":
            self.activate_button(self.end_button)
            self.action = "end"
        else:
            self.desactivate_button()
            self.action = "goto"

    def use_clear(self):
        self.setup()

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button

    def desactivate_button(self, eraser_mode=False):
        self.active_button.config(relief=RAISED)

    # def press(self, event):

    def release(self, event):

        self.line_width = self.DEFAULT_PEN_SIZE  # self.choose_size_button.get()

        if self.action == "start":
            for i in range(len(zone_depart)):
                if zone_depart[i][0] * affCoef < event.x < zone_depart[i][1] * affCoef and (
                        200 - zone_depart[i][3]) * affCoef < event.y < (200 - zone_depart[i][2]) * affCoef:
                    self.temp_x = (zone_depart[i][0] + zone_depart[i][1]) / 2
                    self.temp_y = (zone_depart[i][2] + zone_depart[i][3]) / 2
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    ini_lst.append("C:-")
                    ini_lst.append("V:50")
                    ini_lst.append("S:" + str(int(self.temp_x - 12 * cos(zone_depart[i][4] * pi / 180.0))) + ":" + str(
                        int(self.temp_y - 12 * sin(zone_depart[i][4] * pi / 180.0))) + ":" + str(
                        int(zone_depart[i][4])))
                    ini_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    ini_lst.append("V:70")
                    ini_lst.append("R:" + str(int(zone_depart[i][4])))
                    # point panier
                    ini_lst.append("s:0")

                    self.c.create_oval((self.start_x - 5) * affCoef, (200 - self.start_y - 5) * affCoef,
                                       (self.start_x + 5) * affCoef, (200 - self.start_y + 5) * affCoef,
                                       width=self.line_width,
                                       outline='red', fill='red', tags="trajectory")
                    self.c.delete("zones")
                    self.action = "goto"
                    self.root.configure(bg=zone_depart[i][5])

        elif self.action == "recal":
            for i in range(len(zone_recal)):
                if zone_recal[i][0] * affCoef < event.x < zone_recal[i][1] * affCoef and (
                        200 - zone_recal[i][3]) * affCoef < event.y < (200 - zone_recal[i][2]) * affCoef:
                    cmd_lst.append("R:" + str(int(zone_recal[i][4])))
                    cmd_lst.append("C:-")

                    if zone_recal[i][4] == 0:
                        self.temp_x = zone_recal[i][1]
                        self.temp_y = self.start_y
                        cmd_lst.append("X:" + str(int(self.temp_x)))

                    if zone_recal[i][4] == 180:
                        self.temp_x = zone_recal[i][0]
                        self.temp_y = self.start_y
                        cmd_lst.append("X:" + str(int(self.temp_x)))

                    if zone_recal[i][4] == 90:
                        self.temp_x = self.start_x
                        self.temp_y = zone_recal[i][3]
                        cmd_lst.append("Y:" + str(int(self.temp_y)))

                    if zone_recal[i][4] == -90:
                        self.temp_x = self.start_x
                        self.temp_y = zone_recal[i][2]
                        cmd_lst.append("Y:" + str(int(self.temp_y)))

                    cmd_lst.append("Z:" + str(int(zone_recal[i][4])))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.c.delete("zones")
                    self.action = "goto"
                    self.desactivate_button()

        elif self.action == "capture":
            for i in range(len(zone_capture)):
                # [112.5, 72.5, 1]
                if (zone_capture[i][0] - 6) * affCoef < event.x < (zone_capture[i][0] + 6) * affCoef and (
                        200 - zone_capture[i][1] - 6) * affCoef < event.y < (200 - zone_capture[i][1] + 6) * affCoef:
                    zone_capture[i][2] = False
                    self.c.delete("zones")
                    self.action = "goto"

                    # si zone pot
                    if zone_capture[i][3] == True:
                        self.temp_x = zone_capture[i][0] - 27 * cos(zone_capture[i][4] * pi / 180)
                        self.temp_y = zone_capture[i][1] - 27 * sin(zone_capture[i][4] * pi / 180)
                        # approche
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                        event.x = self.temp_x * affCoef
                        event.y = (200 - self.temp_y) * affCoef
                        self.drawLine(event)
                        self.start_x = self.temp_x
                        self.start_y = self.temp_y

                        # mise en position
                        self.temp_x = zone_capture[i][0] - 15 * cos(zone_capture[i][4] * pi / 180)
                        self.temp_y = zone_capture[i][1] - 15 * sin(zone_capture[i][4] * pi / 180)
                        cmd_lst.append("R:" + str(int(zone_capture[i][4] * 180 / pi)))
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                        self.pot = True
                        cmd_lst.append("e:CAPTURE POT")
                        cmd_lst.append("p:6:" + str(servo_pos[6][2]))
                        cmd_lst.append("w:0.5")
                        cmd_lst.append("p:7:" + str(servo_pos[7][2]))
                    else:
                        # capture plante
                        # avec angle d'approche calculé
                        self.desactivate_button()
                        if self.start_y > zone_capture[i][1]:
                            signe = -1
                        else:
                            signe = 1
                        # approche direct
                        # self.temp_z = signe * acos((zone_capture[i][0] - self.start_x) /
                        #                            sqrt((zone_capture[i][0] - self.start_x) * (zone_capture[i][0] - self.start_x) +
                        #                                 (zone_capture[i][1] - self.start_y) * (zone_capture[i][1] - self.start_y)))
                        # self.temp_x = zone_capture[i][0] - 27 * cos(self.temp_z)
                        # self.temp_y = zone_capture[i][1] - 27 * sin(self.temp_z)
                        # print (self.temp_z * 180 / pi)

                        # approche inverse
                        self.temp_x = zone_capture[i][0] + 27 * cos(zone_capture[i][4] * pi / 180)
                        self.temp_y = zone_capture[i][1] + 27 * sin(zone_capture[i][4] * pi / 180)
                        self.temp_z = -zone_capture[i][4] * pi / 180

                        canReverse = False
                        # si la distance est plus petit que le trajet jusque la cible
                        if sqrt((zone_capture[i][0] - self.start_x) * (zone_capture[i][0] - self.start_x) + (
                                zone_capture[i][1] - self.start_y) * (zone_capture[i][1] - self.start_y)) > sqrt(
                                (self.temp_x - self.start_x) * (self.temp_x - self.start_x) + (
                                        self.temp_y - self.start_y) * (self.temp_y - self.start_y)):
                            canReverse = True
                            # on regarde si la zone est dispo
                            for j in range(len(zone_capture)):
                                if (zone_capture[j][0] - 15) < self.temp_x < (zone_capture[j][0] + 15) and (
                                        zone_capture[j][1] - 15) < self.temp_y < (zone_capture[j][1] + 15) and \
                                        zone_capture[j][2] == True:
                                    print(zone_capture[j][0])
                                    print(zone_capture[j][1])
                                    canReverse = False
                            if not canReverse:
                                # avec angle d'approche piloté
                                self.temp_x = zone_capture[i][0] - 27 * cos(zone_capture[i][4] * pi / 180)
                                self.temp_y = zone_capture[i][1] - 27 * sin(zone_capture[i][4] * pi / 180)
                        else:
                            # avec angle d'approche piloté
                            self.temp_x = zone_capture[i][0] - 27 * cos(zone_capture[i][4] * pi / 180)
                            self.temp_y = zone_capture[i][1] - 27 * sin(zone_capture[i][4] * pi / 180)
                        # approche
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                        event.x = self.temp_x * affCoef
                        event.y = (200 - self.temp_y) * affCoef
                        self.drawLine(event)
                        self.start_x = self.temp_x
                        self.start_y = self.temp_y

                        # mise en position

                        if canReverse:
                            # avec angle d'approche calculé
                            self.temp_x = zone_capture[i][0] + 15 * cos(zone_capture[i][4] * pi / 180)
                            self.temp_y = zone_capture[i][1] + 15 * sin(zone_capture[i][4] * pi / 180)
                        else:
                            # avec angle d'approche piloté
                            self.temp_x = zone_capture[i][0] - 15 * cos(zone_capture[i][4] * pi / 180)
                            self.temp_y = zone_capture[i][1] - 15 * sin(zone_capture[i][4] * pi / 180)

                        cmd_lst.append("R:" + str(int(zone_capture[i][4] * 180 / pi)))
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                        self.plante = True
                        cmd_lst.append("e:CAPTURE PLANTE")
                        cmd_lst.append("p:6:" + str(servo_pos[6][2]))
                        cmd_lst.append("w:0.5")
                        cmd_lst.append("p:7:" + str(servo_pos[7][2]))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.action = "goto"
                    self.desactivate_button()

        elif self.action == "depose":
            for i in range(len(zone_depose)):
                if zone_depose[i][0] * affCoef < event.x < zone_depose[i][1] * affCoef and (
                        200 - zone_depose[i][3]) * affCoef < event.y < (200 - zone_depose[i][2]) * affCoef:
                    zone_depose[i][5] = False
                    self.temp_x = (zone_depose[i][0] + zone_depose[i][1]) / 2 - 15 * cos(zone_depose[i][4] * pi / 180)
                    self.temp_y = (zone_depose[i][2] + zone_depose[i][3]) / 2 - 15 * sin(zone_depose[i][4] * pi / 180)
                    # approche
                    cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    cmd_lst.append("R:" + str(int(zone_depose[i][4])))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    # zone sureleve
                    if zone_depose[i][6] == True:
                        # on rabaisse
                        cmd_lst.append("p:8:" + str(servo_pos[8][1]))
                        cmd_lst.append("C:+")

                        self.temp_x = (zone_depose[i][0] + zone_depose[i][1]) / 2 + 2 * cos(
                            zone_depose[i][4] * pi / 180.0)
                        self.temp_y = (zone_depose[i][2] + zone_depose[i][3]) / 2 + 2 * sin(
                            zone_depose[i][4] * pi / 180.0)
                        cmd_lst.append("S:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                        event.x = self.temp_x * affCoef
                        event.y = (200 - self.temp_y) * affCoef
                        self.drawLine(event)
                        self.start_x = self.temp_x
                        self.start_y = self.temp_y

                    cmd_lst.append("e:RELACHE")
                    cmd_lst.append("p:4:" + str(servo_pos[4][1]))
                    cmd_lst.append("p:5:" + str(servo_pos[5][1]))
                    cmd_lst.append("p:6:" + str(servo_pos[6][1]))
                    cmd_lst.append("p:7:" + str(servo_pos[7][1]))
                    cmd_lst.append("p:8:" + str(servo_pos[8][1]))
                    cmd_lst.append("w:0.5")

                    # zone sureleve
                    if zone_depose[i][6] == True:
                        # on rabaisse
                        cmd_lst.append("p:8:" + str(servo_pos[8][1]))
                        self.temp_x = (zone_depose[i][0] + zone_depose[i][1]) / 2 - 15 * cos(
                            zone_depose[i][4] * pi / 180.0)
                        self.temp_y = (zone_depose[i][2] + zone_depose[i][3]) / 2 - 15 * sin(
                            zone_depose[i][4] * pi / 180.0)
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                    else:
                        self.temp_x = (zone_depose[i][0] + zone_depose[i][1]) / 2 - 30 * cos(
                            zone_depose[i][4] * pi / 180.0)
                        self.temp_y = (zone_depose[i][2] + zone_depose[i][3]) / 2 - 30 * sin(
                            zone_depose[i][4] * pi / 180.0)
                        cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.c.delete("zones")
                    self.action = "goto"

                    self.desactivate_button()
                    if self.plante:
                        cmd_lst.append("s:9")
                        self.plante = False
                        if self.pot:
                            cmd_lst.append("s:3")
                            self.pot = False
                        if zone_depose[i][6]:
                            cmd_lst.append("s:3")

        elif self.action == "panneau":
            for i in range(len(zone_panneau)):
                if (zone_panneau[i][0] - 6) * affCoef < event.x < (zone_panneau[i][0] + 6) * affCoef and (
                        200 - zone_panneau[i][1] - 6) * affCoef < event.y < (200 - zone_panneau[i][1] + 6) * affCoef:
                    self.temp_x = zone_panneau[i][0]
                    self.temp_y = zone_panneau[i][1] + 30
                    # approche
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    cmd_lst_2.append("R:-90")

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.temp_x = zone_panneau[i][0]
                    self.temp_y = zone_panneau[i][1] + 15
                    # position
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    cmd_lst_2.append("R:-90")

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    cmd_lst_2.append("e:PANNEAU")
                    cmd_lst_2.append("p:4:" + str(servo_pos[4][1]))
                    cmd_lst_2.append("w:0.5")
                    cmd_lst_2.append("s:5")

                    self.temp_x = zone_panneau[i][0]
                    self.temp_y = zone_panneau[i][1] + 30
                    # recule
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    cmd_lst_2.append("R:-90")

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.c.delete("zones")
                    self.action = "goto"
                    self.desactivate_button()

        elif self.action == "pami":
            for i in range(len(zone_pami)):
                if zone_pami[i][0] * affCoef < event.x < zone_pami[i][1] * affCoef and (
                        200 - zone_pami[i][3]) * affCoef < event.y < (200 - zone_pami[i][2]) * affCoef:
                    self.temp_x = (zone_pami[i][0] + zone_pami[i][1]) / 2 - 30 * cos(zone_pami[i][4] * pi / 180)
                    self.temp_y = (zone_pami[i][2] + zone_pami[i][3]) / 2 - 30 * sin(zone_pami[i][4] * pi / 180)
                    # approche
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    cmd_lst_2.append("R:" + str(int(zone_pami[i][4])))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    # position
                    self.temp_x = (zone_pami[i][0] + zone_pami[i][1]) / 2 - 15 * cos(zone_pami[i][4] * pi / 180)
                    self.temp_y = (zone_pami[i][2] + zone_pami[i][3]) / 2 - 15 * sin(zone_pami[i][4] * pi / 180)
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    cmd_lst_2.append("t:90")
                    cmd_lst_2.append("e:RELACHE")
                    cmd_lst_2.append("p:4:" + str(servo_pos[4][1]))
                    cmd_lst_2.append("w:0.5")
                    cmd_lst_2.append("p:5:" + str(servo_pos[5][1]))

                    self.temp_x = (zone_pami[i][0] + zone_pami[i][1]) / 2 - 100 * cos(zone_pami[i][4] * pi / 180)
                    self.temp_y = (zone_pami[i][2] + zone_pami[i][3]) / 2 - 100 * sin(zone_pami[i][4] * pi / 180)
                    cmd_lst_2.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y

                    self.c.delete("zones")
                    self.action = "goto"
                    self.desactivate_button()

        elif self.action == "goto":
            if self.action == "goto":
                cmd_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))

                self.temp_x = event.x / affCoef
                self.temp_y = 200 - event.y / affCoef
                self.drawLine(event)
                self.start_x = self.temp_x
                self.start_y = self.temp_y

        elif self.action == "end":

            for i in range(len(zone_depart)):
                if zone_depart[i][0] * affCoef < event.x < zone_depart[i][1] * affCoef and (
                        200 - zone_depart[i][3]) * affCoef < event.y < (200 - zone_depart[i][2]) * affCoef:
                    self.c.delete("robot")

                    self.temp_x = (zone_depart[i][0] + zone_depart[i][1]) / 2
                    self.temp_y = (zone_depart[i][2] + zone_depart[i][3]) / 2

                    if not (zone_depart[i][0] < self.start_x < zone_depart[i][1] and
                            zone_depart[i][3] < self.start_y < zone_depart[i][2]):
                        end_lst.append("G:" + str(int(self.temp_x)) + ":" + str(int(self.temp_y)))
                    end_lst.append("s:10")
                    end_lst.append("R:" + str(int(zone_depart[i][4])))
                    self.c.delete("zones")
                    self.action = ""

                    event.x = self.temp_x * affCoef
                    event.y = (200 - self.temp_y) * affCoef
                    self.drawLine(event)
                    self.start_x = self.temp_x
                    self.start_y = self.temp_y
                    self.desactivate_button()

    def drawLine(self, event):
        self.c.create_line(self.start_x * affCoef, (200 - self.start_y) * affCoef, event.x, event.y,
                           width=self.line_width, fill="black",
                           capstyle=ROUND, smooth=TRUE, splinesteps=36, tags="trajectory")
        self.c.delete("robot")
        self.c.create_oval(event.x - 5 * affCoef, event.y - 5 * affCoef, event.x + 5 * affCoef, event.y + 5 * affCoef,
                           width=self.line_width,
                           outline='green', fill='green', tags="trajectory")
        self.c.create_oval(event.x - 5 * affCoef, event.y - 5 * affCoef, event.x + 5 * affCoef, event.y + 5 * affCoef,
                           width=self.line_width,
                           outline='yellow', fill='yellow', tags="robot")

