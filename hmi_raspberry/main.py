#!/home/droopy/svn/robot_2024/src/venv/bin/python3

import time
import sys
from math import *

import printScore
import stratTable

posX = 100.0
posY = 50.0
posZ = 160.0
start_time = 0
debug = False
debugCV = True
runningMatch = False
lastV = "0"
cote = ""

mainScore = 0

targX = 50.0
targY = 100.0
# parametre de trajectoire
a = 0
b = 0
c = 0
dist = 0

affCoef = 4 # echelle d'affichage
affSize = 20  # taille de la pastille

offsetAngle = 90  # rectification d'angle en °
minX = 0  # en cm
minY = 0  # en cm
alertDist = 50  # en cm

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"

def print_there(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.flush()


def print_there_color(x, y, text, COLOR):
    sys.stdout.write(COLOR)
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.write(RESET)
    sys.stdout.flush()

######################################################################################
#
#       SENDCMD
# envoi des commandes à la carte moteur
#
######################################################################################
def sendCmd(cmd):
    # on enregistre la cible pour l'evitement
    global targX
    global targY
    global lastV
    pos = cmd.split(":")
    if len(pos) > 1:
        if pos[0] in ["G", "T", "S"]:
            targX = float(pos[1])
            targY = float(pos[2])
        if pos[0] == "V":
            lastV = cmd
        print("cmd " + cmd)

######################################################################################
#
#       EXECUTE
# décodage et execution d'une commande
#
######################################################################################
def execute(current):
    global mainScore

    pos = current.split(":")
    # si commande moteur
    if pos[0] == "0" or pos[0].upper() == pos[0]:
        sendCmd(current)

    # si echo
    if pos[0] == "e":
        print(pos[1])

    # si score
    if pos[0] == "s":
        mainScore = mainScore + int(pos[1])
        print(" ==> mainScore " + pos[1] + " => " + str(mainScore))

    # si actionneur
    if pos[0] == "a":
        if debug:
            wait = input("==")
        # serialAct.write(pos[1].encode())
        # serialAct.write("\r\n".encode())

    # si servo
    if pos[0] == "p":
        print("servo " + pos[1] + " pos " + pos[2])
        # kit.servo[int(pos[1])].angle = int(pos[2])

    # si servo
    if pos[0] == "w":
        print("wait " + pos[1])
        # if debug:
        #     chrono_time = time.time()
        #     wait = input("==")
        #     print("chrono: " + str(time.time() - chrono_time))
        # else:
        #     time.sleep(float(pos[1]))

    if pos[0] == "t":
        print("waitTo " + pos[1])
        # if debug:
        #     chrono_time = time.time()
        #     wait = input("==")
        #     print("chrono: " + str(time.time() - chrono_time))
        # else:
        #     while (time.time() - start_time) < float(pos[1]):
        #         time.sleep(0.2)


######################################################################################
#
#       MAIN
#
######################################################################################
if __name__ == '__main__':

    ###################################################################################################
    ###                                                                                            ####
    ###                         MODE AUTOMATIQUE                                                   ####
    ###                                                                                            ####
    ###################################################################################################

    try:
        # l = lidarThread(serialPort, stopEvent, endEvent)  # crée un thread
        # l.start()  # démarre le thread,.

        # tirette = PiButton(22)

        # cmd : on coupe les moteurs
        sendCmd("0")

        targX = 100.0
        targY = 150.0

        stratTable.Paint()
        for item in stratTable.ini_lst:
            print(item)
        for item in stratTable.cmd_lst:
            print(item)
        for item in stratTable.cmd_lst_2:
            print(item)
        for item in stratTable.end_lst:
            print(item)

        print("===== PREPA =====")
        for item in stratTable.ini_lst:
            execute(item)

        print("")
        print("PRET POUR MATCH")
        # on attend la tirette
        runningMatch = True
        # match
        print("===== MATCH =====")
        start_time = time.time()
        for item in stratTable.cmd_lst:
            if (time.time() - start_time) < 85 or debug:
                execute(item)

        # pami
        print("")
        print(str(time.time() - start_time) + "s")
        print("===== PAMI =====")
        start_time = time.time()
        for item in stratTable.cmd_lst_2:
            if (time.time() - start_time) < 95 or debug:
                execute(item)

        # fin
        print("")
        print(str(time.time() - start_time) + "s")
        print("===== FIN =====")
        for item in stratTable.end_lst:
            if (time.time() - start_time) < 100 or debug:
                execute(item)

        print("===== FIN DE MATCH =====")

    except KeyboardInterrupt:
        print('Interruption')
    # cmd : on coupe les moteurs
    finally:
        printScore.printScore(" "+str(mainScore) + "p")
        runningMatch = False
        sendCmd("0")
        sendCmd("0")
        sendCmd("0")



