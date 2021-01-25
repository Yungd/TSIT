#in dit bestand staan alle functies en klassen die worden gebruikt in opdracht 2
import math
import networkx as nx
import matplotlib.pyplot as plt

#in deze class wordt de informatie over de spelers opgeslagen
class UFO:
    #initiele functie voor registreren nieuwe contacten
    def __init__(self, name, x_rel, y_rel, height, distance_ground, distance_tot, kleur="blue"):
        self.naam = name #een integer om de nodes mee te identificeren
        self.xNew = x_rel
        self.yNew = y_rel
        self.heightNew = height
        self.distancetotNew=distance_tot
        self.distanceNew = distance_ground
        self.xOld = []
        self.yOld = []
        self.heightOld = []
        self.distanceOld = []
        self.distancetotOld = []
        self.kleur = kleur
        self.vxNew = 0
        self.vyNew = 0
        self.vzNew = 0
        self.vtotNew = 0
        self.vxOld = []
        self.vyOld = []
        self.vzOld = []
        self.vtotOld = []
        self.axNew = 0
        self.ayNew = 0
        self.azNew = 0
        self.atotNew = 0
        self.axOld = []
        self.ayOld = []
        self.azOld = []
        self.atotOld = []
        self.posfut= [] #[x,y,height]
        self.vfut = [] #[x,y,z]
    
    #het updaten van de speler als er nieuwe informatie wordt toegevoegd
    def update(self,x_rel, y_rel, height, distance_ground, distance_tot):
        #sla de oude waardes van een contact op
        self.xOld.insert(0,self.xNew)
        self.yOld.insert(0,self.yNew)
        self.heightOld.insert(0,self.heightNew)
        self.distanceOld.insert(0,self.distanceNew)
        self.distancetotOld.insert(0,self.distancetotNew)
        self.vxOld.insert(0,self.vxNew)
        self.vyOld.insert(0,self.vyNew)
        self.vzOld.insert(0,self.vzNew)
        self.vtotOld.insert(0,self.vtotNew)
        self.axOld.insert(0,self.axNew)
        self.ayOld.insert(0,self.ayNew)
        self.azOld.insert(0,self.azNew)
        self.atotOld.insert(0,self.atotNew)
        #voer nieuwe gegevens in
        self.xNew = x_rel
        self.yNew = y_rel
        self.heightNew = height
        self.distanceNew = distance_ground
        self.distancetotNew = distance_tot
        self.vxNew = self.xNew - self.xOld[0]
        self.vyNew = self.yNew - self.yOld[0]
        self.vzNew = self.heightNew - self.heightOld[0]
        self.vtotNew = ((self.vxNew ** 2 )+(self.vyNew ** 2 )+(self.vzNew ** 2 ))**0.5
        self.axNew = self.vxNew - self.vxOld[0]
        self.ayNew = self.vyNew - self.vyOld[0]
        self.azNew = self.vzNew - self.vzOld[0]
        self.atotNew = ((self.axNew ** 2 )+(self.ayNew ** 2 )+(self.azNew ** 2 ))**0.5
        self.cpa = cpa(self)
        self.posfut,self.vfut = future(self)
        
#functie voor het inlezen van  files  
def readtracks(filename):
    f = open(filename, "r")
    return f

#berekenen van relatieve posities
def relativepos(track):
    a = track.split(" ")
    distance_tot = float(a[3].rstrip("\n"))
    bearing_z = math.radians(float(a[2]))
    bearing_xy = math.radians(float(a[1]))
    track_id = a[0]
    height = distance_tot * math.sin(bearing_z)
    distance_ground = distance_tot * math.cos(bearing_z)
    x_rel = math.sin(bearing_xy) * distance_ground
    y_rel = math.cos(bearing_xy) * distance_ground
    return x_rel, y_rel, height, distance_ground, distance_tot

#Deze functie berekent de relatieve positie, update de speler klasse
#en update de lijsten die nodig zijn voor het plotten van de situatie
def update_track(track, ufo, positions, nodes, colorlist, nodegrootte, nodecount):
    a,b,c,d,e=relativepos(track)
    ufo.update(a,b,c,d,e)
    
    #update de posities voor de graph
    positions[ufo.naam] = (ufo.xNew, ufo.yNew)
    
    #voeg de geschiedenis toe aan de graph
    nodes = nodes+[nodecount]
    colorlist = colorlist + ["grey"]
    nodegrootte = nodegrootte + [1]
    positions[nodecount] = (ufo.xOld[0] , ufo.yOld[0])
            
    nodecount+=1
        
    return ufo, positions, nodes, colorlist, nodegrootte, nodecount

#Deze functie geeft een situational report van de situatie
def sitrep(timer, spelers):
    print('\033[1m'+ "Time:" + str(timer)+ '\033[0m')
    for i in spelers:
        sitrep_klasse(spelers[i])

#Zelfde als sitrep() maar dan per klasse
def sitrep_klasse(klasse):
    print ("Object: " , klasse.kleur)
    print("Distance: ", str(round(klasse.distanceNew))+ "m (over ground), ", str(round(klasse.distancetotNew)) + "m (total)")
    print("Speed: ", str(round(klasse.vtotNew))+ "m/s , Acceleration: ", "{:.3f}".format(klasse.atotNew)+ "m/s^2")
    #Voorbeeld van een warning system. Als cpa kleiner is dan 2000 m wordt de text rood in de sitrep.
    if round(klasse.cpa[0]) > 2000:
        print("CPA: ", str(round(klasse.cpa[0])) + "m , TCPA: ", str("{:.3f}".format(klasse.cpa[1]) + "s"))
    else :
        print('\033[91m' + "CPA: ", str(round(klasse.cpa[0])) + "m , TCPA: ", str("{:.3f}".format(klasse.cpa[1]) + "s" + '\033[0m'))
    
        
#berekenen van de cpa distance en time
def cpa(klasse):
    a = [klasse.xNew, klasse.yNew, klasse.heightNew]
    v = [klasse.vxNew, klasse.vyNew, klasse.vzNew]
    time = -dot(a,v)/ dot(v,v)
    px,py,pz = cpa_pos(a,v,time)
    distance = ((px**2 ) + (py **2) + (pz **2))**0.5
    return distance, time
#berekenen van de positie van de closest point of advance    
def cpa_pos(a,v,time):
    #p= a+ v*t
    px = a[0] + v[0] * time
    py = a[1] + v[1] * time
    pz = a[2] + v[2] * time
    return px,py,pz
#Het inproduct.   
def dot(x, y):
    return sum(x_i*y_i for x_i, y_i in zip(x, y))

#initieer een nieuwe speler door een nummer, kleur en track te combineren.
def initieerKlasse(track, nummer, kleur):
    a,b,c,d,e=relativepos(track)
    klasse = UFO(nummer,a,b,c,d,e,kleur)
    return klasse

#Zet een geheel txt bestand om naar een lijst met alle regels
def txtToList(f):
    a=[]
    for i in f:
        a.append(i)
    return a

#voorspel de positie en snelheid van een klasse over 1 seconde
def future(klasse):
    #voorspel positie
    xf = klasse.xNew + klasse.vxNew
    yf = klasse.yNew + klasse.vyNew
    zf = klasse.heightNew + klasse.vzNew
    posfut = [xf,yf,zf]
    #voorspel snelheid
    vxf = klasse.vxNew + klasse.axNew
    vyf = klasse.vyNew + klasse.ayNew
    vzf = klasse.vzNew + klasse.azNew
    vfut = [vxf,vyf,vzf]
    return posfut, vfut
  
#Vergelijk de nieuwe meting met de voorspelling en kwantificeer de afwijking.
#Doordat de verschillen in snelheid klein zijn, heeft positie meer invloed op de afwijking.
def compare(track, klasse):
    #bereken relatieve positie nieuwe ping
    x,y,height,disG,disTot = relativepos(track)
    #vergelijk positie met voorspelde positie
    xDev = abs((x - klasse.posfut[0]) )
    yDev = abs((y - klasse.posfut[1]) )
    zDev = abs((height - klasse.posfut[2]) )
    #bereken snelheid toz positie klasse
    vx = x - klasse.xNew
    vy = y - klasse.yNew
    vz = height - klasse.heightNew
    #vergelijk met voorspelde snelheid
    vxDev = abs((vx - klasse.vfut[0])-1)
    vyDev = abs((vy - klasse.vfut[1])-1)
    vzDev = abs((vz - klasse.vfut[2])-1)
    #kwantificeer afwijking. Hoe kleiner hoe beter
    totDev = xDev + yDev + zDev + vxDev + vyDev + vzDev
    return totDev
    
        
        