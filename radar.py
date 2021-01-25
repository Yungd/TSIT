#!/usr/bin/env python3
import tkinter as tk
#from tkinter import *
import tkinter.messagebox as mb
import math, threading, socket

DEFAULT_HOST = 'multiverse.cloud.c2lab.nl'
DEFAULT_PORT = 9800
DEFAULT_SCALE = 25 #Km
DEFAULT_USER = 'tsit-a'

SIZE = 1000

class RadarDisplay(tk.Frame):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Radar Console")
        super().__init__(self.master)
        self.pack()

        self.connection = None
        self.stopped = False
        self.systems = list()
        self.canons = list()

        # Create toolbar
        connectbar = tk.Frame(self)
        connectbar.pack()

        self.host = tk.Entry(connectbar)
        self.host.insert(0,DEFAULT_HOST)
        self.host.pack(side=tk.LEFT)
        self.port= tk.Entry(connectbar)
        self.port.insert(0,str(DEFAULT_PORT))
        self.port.pack(side=tk.LEFT)
        self.user = tk.Entry(connectbar)
        self.user.insert(0,DEFAULT_USER)
        self.user.pack(side=tk.LEFT)
        self.system = tk.StringVar(connectbar)
        self.systemselect = tk.OptionMenu(connectbar,None,'Select')
        self.systemselect["text"] = 'Select Radar'

        self.systemselect["state"] = tk.DISABLED
        self.systemselect.pack(side=tk.LEFT)

        self.connectbutton = tk.Button(connectbar, text="Connect",command=self.onConnectClick)
        self.connectbutton.pack(side="right")

        self.scalevalue = tk.StringVar(self)
        self.scalevalue.set(DEFAULT_SCALE)
        self.scalevalue.trace('w', self.onScaleChange)

        self.scale = tk.OptionMenu(connectbar,self.scalevalue, 10,25,50,100,200)
        self.scale.pack(side="right")
        
        #Create firebar
        firebar = tk.Frame(self)
        firebar.pack()
        
        self.canon = tk.StringVar(firebar)
        self.canonselect = tk.OptionMenu(firebar,None,'Select')
        self.canonselect["text"] = 'Select Canon'

        self.canonselect["state"] = tk.DISABLED
        self.canonselect.pack(side=tk.LEFT)
#         self.Canonbutton = tk.Button(firebar, text="Connect to Canon",command=self.ConnectCanon)
#         self.Canonbutton.pack(side="left")

        self.target = tk.StringVar(firebar)
        self.targetselect = tk.OptionMenu(firebar,None,'Select Target')
        self.targetselect["text"] = 'Select Target'

        self.targetselect["state"] = tk.DISABLED
        self.targetselect.pack(side=tk.LEFT,)


        

        
        self.FIREbutton = tk.Button(firebar, text="FIRE",command=self.FIRE, bg='red')
        self.FIREbutton.pack(side="left")
        
#         self.connectCanon = tk.Button(firebar, text="Connect to Canon",command=self.FIRE)
#         self.ConnectCanon.pack(side="right")
        

        chkValue = tk.BooleanVar() 
        chkValue.set(True)
        
        self.Auto_defense = tk.Checkbutton(firebar, text='Auto', var=chkValue)
        self.Auto_defense.pack(side='right')

        self.scalevalue = tk.StringVar(self)
        self.scalevalue.set(DEFAULT_SCALE)
        self.scalevalue.trace('w', self.onScaleChange)


        

        # Create canvas
        self.canvas = tk.Canvas(self, width = SIZE, height = SIZE, bg='black')
        self.canvas.pack()

        self.time = 0
        self.contacts = []

        self.redraw()

    def onConnectClick(self):
        if self.connection is None:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        # Start connection
        self.connection = ConnectionThread(self,self.host.get(),int(self.port.get()))

        self.host["state"] = tk.DISABLED
        self.port["state"] = tk.DISABLED
        self.user["state"] = tk.DISABLED

        self.connectbutton["text"] = "Disconnect"

        self.connection.start()

    def disconnect(self):
        if not self.connection is None and self.connection.is_alive():
            self.connection.stop = True

    def emptySystemSelect(self):
        self.systems = list()
        self.systemselect['text'] = 'Select Radar'
        self.systemselect['menu'].delete(0, 'end')

    def updateSystemSelect(self):
        for (name,label) in self.systems:
           self.systemselect['menu'].add_command(label = label, command = lambda value=(name,label): self.onSystemSelect(*value))
        self.systemselect["state"] = tk.NORMAL

    def onSystemSelect(self, name, label):
        self.systemselect['text'] = label
        if not self.connection is None:
            self.connection.sendMessage("SYSTEM " + name)
            
    def emptyCanonSelect(self):
        self.canons = list()
        self.canonselect['text'] = 'Select Canon'
        self.canonselect['menu'].delete(0, 'end')

    def updateCanonSelect(self):
        for (name,label) in self.canons:
           self.canonselect['menu'].add_command(label = label, command = lambda value=(name,label): self.onCanonSelect(*value))
        self.canonselect["state"] = tk.NORMAL

    def onCanonSelect(self, name, label):
        self.canonselect['text'] = label
        if not self.connection is None:
            self.connection.sendMessage("SYSTEM " + name)

    def stop(self):
        self.stopped = True
        if not self.connection is None:
            self.connection.stop = True
            self.connection.join()

    def redraw(self):
        self.canvas.delete(tk.ALL)

        center_x = SIZE / 2
        center_y = SIZE / 2

        #Draw grid
        num_circles = 4
        circle_width = 100
        circle_km = int(self.scalevalue.get()) / num_circles

        for step in range(1, num_circles + 1):
            radius = step * circle_width
            self.canvas.create_oval( center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline='green')

        for angle in range(0,360,30):
            line_length = num_circles * circle_width
            self.canvas.create_line(center_x, center_y
                , center_x + math.cos(math.radians(angle)) * line_length
                , center_y + math.sin(math.radians(angle)) * line_length, fill='green')

        #Draw contacts
        for (angle,distance) in self.contacts:
            
            scaled_distance = (distance / (circle_km * 1000)) * circle_width
            contact_x = center_x + math.cos(math.radians(angle - 90)) * scaled_distance
            contact_y = center_y + math.sin(math.radians(angle - 90)) * scaled_distance
            radius = 5 
            self.canvas.create_oval(contact_x - radius, contact_y - radius, contact_x + radius, contact_y + radius, fill='green')

    def onScaleChange(self, *args):
        self.redraw()

    def onLineReceived(self, line):
        if line == 'C2 SCENARIO SIMULATOR':
            self.connection.sendMessage('USER '+ self.user.get())
        elif line == 'USER OK':
            self.connection.sendMessage('SYSTEMS')
            self.emptySystemSelect()
            self.emptyCanonSelect()
        elif line == "SYSTEMS OK":
            self.updateSystemSelect()
            self.updateCanonSelect()
        elif line == "SYSTEM OK":
            self.redraw()
        elif line.startswith("SYSTEM"):
            parts = line.split()
            if len(parts) >= 5 and parts[-1] == "RADAR":
                self.systems.append((" ".join(parts[1:4])," ".join(parts[4:-1])))
            if len(parts) >= 5 and parts[-1] == "CANON":
                self.canons.append((" ".join(parts[1:4])," ".join(parts[4:-1])))
        elif line.startswith("ERROR"):
            mb.showerror("Simulator error", line)
        else:
            parts = line.split(' ')
            if len(parts) == 4: 
                t = int(parts[0])
                heading = float(parts[1])
                elevation = float(parts[2])
                distance = float(parts[3])

                # Compute the distance on the ground plane
                ground_distance = distance * math.cos(math.radians(elevation)) 

                # Reset contacts when the virtual clock increases
                if t != self.time:
                    self.contacts = []
                    self.time = t

                # Add to contact list and redraw
                self.contacts.append((heading,ground_distance))
                self.redraw()        
            else:
                self.contacts = []
                self.redraw()        

    def onDisconnected(self, message = None):
        if self.stopped:
            return
        if not message is None:
            mb.showerror("Disconnected", message)

        self.emptySystemSelect()
        self.host["state"] = tk.NORMAL
        self.port["state"] = tk.NORMAL
        self.user["state"] = tk.NORMAL
        self.systemselect["state"] = tk.DISABLED
        self.connectbutton["text"] = "Connect"

        self.connection = None
     
    def ConnectCanon(self):
        if self.connection is None:
            return "Connect first"
        else:
            self.connection.sendMessage('SYSTEM  tsit-a-testrange 1 3')
                                 
    def FIRE(self):
        if self.connection is None:
            return "Connect first"
        else:
            self.connection.sendMessage('FIRE')

class ConnectionThread(threading.Thread):

    def __init__(self, app, host, port):
        self.app = app
        self.stop = False
        self.socket = None
        self.host = host
        self.port = port
        self.buffer = bytes()
        super().__init__()

    def run(self):
        try:
            with socket.socket() as s:

                s.connect((self.host,self.port))

                self.socket = s
                # Make sure we check at least every second if we need to stop
                s.settimeout(1)
                while not self.stop:
                    try:
                        data = s.recv(1024)
                        if not data:
                            break

                        self.buffer += data
                        line_end = self.buffer.find(b"\r\n")
                        while line_end >= 0:
                            #Take message from buffer
                            message = str(self.buffer[:line_end],'utf-8')
                            self.buffer = self.buffer[line_end + 2:]
                            line_end = self.buffer.find(b"\r\n")
                            #Process the line
                            self.app.onLineReceived(message)
                            print(message)
                            #label = Label(app,foreground="red",text= 'hoi')
                            #this creates a new label to the GUI
                            #label.pack()

                    # By allowing timeouts to happen we can check the stop flag
                    except socket.timeout:
                        pass

                if self.stop:
                    self.socket.close()

                self.app.onDisconnected()
        except Exception as e:
            self.app.onDisconnected("Error: " + str(e))

    def sendMessage(self,message):
        if not self.socket is None:
            self.socket.sendall(bytes(message + "\r\n",'utf-8'))

app = RadarDisplay()
app.mainloop()
app.stop()

