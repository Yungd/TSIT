#!/usr/bin/env python3
import tkinter as tk
#from tkinter import *
import tkinter.messagebox as mb
import math, threading, socket
import Radar_tracking_func as tracking

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
        self.systems = set()
        self.updated = False
        self.canons = set()
        self.FO = set()
        self.shotFired = False

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
        self.canvas = tk.Canvas(self, width = SIZE*1.5, height = SIZE, bg='black')
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
        self.connection2 = ConnectionThread(self,self.host.get(),int(self.port.get()))
        self.connection.naam = 1
        self.connection2.naam = 2
        self.host["state"] = tk.DISABLED
        self.port["state"] = tk.DISABLED
        self.user["state"] = tk.DISABLED

        self.connectbutton["text"] = "Disconnect"

        self.connection.start()
        self.connection2.start()

    def disconnect(self):
        if not self.connection is None and self.connection.is_alive():
            self.connection.stop = True
        if not self.connection2 is None and self.connection2.is_alive():
            self.connection2.stop = True

    def emptySystemSelect(self):
        self.systems = set()
        self.systemselect['text'] = 'Select Radar'
        self.systemselect['menu'].delete(0, 'end')

    def updateSystemSelect(self):
        if not self.updated:
            for (name,label) in self.systems:
               self.systemselect['menu'].add_command(label = label, command = lambda value=(name,label): self.onSystemSelect(*value))
               print(app.canonselect['menu'])
            self.systemselect["state"] = tk.NORMAL
            self.updated = True

    def onSystemSelect(self, name, label):
        self.systemselect['text'] = label
        if not self.connection is None:
            self.connection.sendMessage("SYSTEM " + name)
            
    def emptyCanonSelect(self):
        self.canons = set()
        self.canonselect['text'] = 'Select Canon'
        self.canonselect['menu'].delete(0, 'end')

    def updateCanonSelect(self):
        for (name,label) in self.canons:
           self.canonselect['menu'].add_command(label = label, command = lambda value=(name,label): self.onCanonSelect(*value))
        self.canonselect["state"] = tk.NORMAL

    def onCanonSelect(self, name, label):
        self.canonselect['text'] = label
        if not self.connection2 is None:
            self.connection2.sendMessage("SYSTEM " + name)

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
        
        #Draw Sitrep
        textx = 1050
        texty = 250
        sitrep = ''
        if len(self.FO) > 1:
            for contact in self.FO:
                sitrep += f"Contact nr {contact.ID}: \n"
                sitrep += f"Distance: {round(contact.ground_distance)} \n"
                if contact.speedTot != None and contact.speedTot != 0.0:
                    print(contact.speedTot)
                    sitrep += f"Speed: {round(contact.speedTot)} \n"
                if type(contact.cpa) != str and contact.cpa != None:
                    sitrep += f"CPA: {round(contact.cpa)}   TCPA: {round(contact.Tcpa)} \n"
                sitrep += "\n"
            self.canvas.create_text(textx, texty, anchor=tk.W, font="Purisa",
            text=sitrep, fill ='green' )
        
    def onScaleChange(self, *args):
        self.redraw()

    def onLineReceived(self, line):
        if line.startswith('1'):
            
            if line[2:] == 'C2 SCENARIO SIMULATOR':
                self.connection.sendMessage('USER '+ self.user.get())
                
            elif line[2:] == 'USER OK':
                self.connection.sendMessage('SYSTEMS')
                
                self.emptySystemSelect()
                
            elif line[2:] == "SYSTEMS OK":
                self.updateSystemSelect()
                
            elif line[2:] == "SYSTEM OK":
                self.redraw()
            elif line[2:].startswith("SYSTEM"):
                parts = line[2:].split()
                if len(parts) >= 5 and parts[-1] == "RADAR":
                    
                    self.systems.add((" ".join(parts[1:4])," ".join(parts[4:-1])))
                
            elif line[2:].startswith("ERROR"):
                mb.showerror("Simulator error", line)
            else:
                parts = line[2:].split(' ')
                if len(parts) == 4: 
                    t = int(parts[0])
                    heading = float(parts[1])
                    elevation = float(parts[2])
                    distance = float(parts[3])

                    # Compute the distance on the ground plane
                    ground_distance = distance * math.cos(math.radians(elevation))
                    
                    #process data in radar for tracking
                    self.processRadar(heading, elevation, distance, ground_distance, t)

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
    
        if line.startswith('2'):
            
            
            if line[2:] == 'C2 SCENARIO SIMULATOR':
                self.connection2.sendMessage('USER '+ self.user.get())
                
            elif line[2:] == 'USER OK':
                self.connection2.sendMessage('SYSTEMS')
                
                self.emptyCanonSelect()
                
            elif line[2:] == "SYSTEMS OK":
                self.updateCanonSelect()
                
            elif line[2:] == "SYSTEM OK":
                self.redraw()
            elif line[2:].startswith("SYSTEM"):
                parts = line[2:].split()
                if len(parts) >= 5 and parts[-1] == "CANON":
                    print("Dit zijn: "+ str(parts))
                    self.canons.add((" ".join(parts[1:4])," ".join(parts[4:-1])))
    
            elif line[2:].startswith("ERROR"):
                mb.showerror("Simulator error", line)


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
     
#     def ConnectCanon(self):
#         if self.connection is None:
#             return "Connect first"
#         else:
#             self.connection.sendMessage('SYSTEM  tsit-a-testrange 1 3')
                                 
    def FIRE(self):
        if self.connection is None:
            return "Connect first"
        else:
            self.connection2.sendMessage('FIRE')
            self.shotFired = [True , 2]
            
    def processRadar(self, heading, elevation, distance, ground_distance, time):
        
        if self.FO == set():
            self.FO.add(tracking.Contact(heading,elevation,distance,ground_distance, time, 1))
        else:
            a = dict()
            pos = tracking.relativepos(heading, elevation, distance, ground_distance)
            
                     
            for i in self.FO:
                a[i.compare(pos)] = i
            
            if min(a) < 300:
                a[min(a)].update(heading, elevation, distance, ground_distance, pos, time)
                print('Updated', len (self.FO))
            elif self.shotFired == [True, 2]:
                self.FO.add(tracking.Contact(heading,elevation,distance,ground_distance, time, len(self.FO)+1))
                self.shotFired = [True , 1]
            elif self.shotFired == [True, 1]:
                a[min(a)].update(heading, elevation, distance, ground_distance, pos, time)
                self.shotFired = False
            
            else:
                self.FO.add(tracking.Contact(heading,elevation,distance,ground_distance, time, len(self.FO)+1))
                print('New')
                

class ConnectionThread(threading.Thread):

    def __init__(self, app, host, port):
        super().__init__()
        self.app = app
        self.stop = False
        self.socket = None
        self.host = host
        self.port = port
        self.naam = ''
        self.buffer = bytes()
        

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
                            #print(message)
                            #print ( str(self.naam))
                            #print(str(self.naam) + ' '+ message)
                            self.app.onLineReceived(str(self.naam) + ' '+ message)
                            print(str(self.naam) + ' '+ message)
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