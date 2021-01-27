import math
import copy



#Gegeven informatie vanuit radar
# t = int(parts[0])
# heading = float(parts[1])
# elevation = float(parts[2])
# distance = float(parts[3])
# 
# # Compute the distance on the ground plane
# ground_distance = distance * math.cos(math.radians(elevation))

def relativepos(heading, elevation, distance, ground_distance):
    #Input zijn de gegevens uit de radar, output is relative position
    height = distance * math.sin(math.radians(elevation))
    x_relative = math.sin(math.radians(heading)) * ground_distance
    y_relative = math.cos(math.radians(heading)) * ground_distance
    return [x_relative, y_relative, height]

#Het inproduct.   
def dot(x, y):
    return sum(x_i*y_i for x_i, y_i in zip(x, y))



class Contact():
    #Deze class bevat alle informatie over één contact
    
    def __init__(self, heading, elevation, distance, ground_distance, t, ID):
        #Initeren van de class. Input zijn de radargegevens en de al berekende informatie
        
        #Current stats
        self.ID = ID
        self.relative_position = relativepos(heading, elevation, distance, ground_distance)
        self.heading = heading
        self.elevation = elevation
        self.distance = distance
        self.ground_distance = ground_distance
        self.lastUpdate = t
        
        
        #To be calculated
        self.speed=list() #vx,vy,vz
        self.speedTot = None #totale snelheid
        self.acceleration = list() #ax,ay,az
        self.accelerationTot = None #totale versnelling
        self.cpa = None #Distance to cpa
        self.Tcpa = None #Over hoeveel seconden gebeurt cpa
        self.futurePosition1 = list() #x,y,z over 1 seconde
        self.futurePosition10 = list() #x,y,z over 10 secondes
        
        #Storage old data
        self.positionOld = list() #lijst met oude relatieve posities
        self.drawPositionOld = list() #lijst met de oude (heading,grounddistance) combinaties
        self.speedOld = list()
        
    def update(self, heading, elevation, distance, ground_distance, pos, t):
        #Het updaten van een contact.
        #De input zijn de radargegevens en de al berekende informatie voor het vergelijken.
        
        #Store data
        self.positionOld.insert(0,self.relative_position)
        self.drawPositionOld.insert(0, (self.heading,self.ground_distance))
        if self.speed != list():
            self.speedOld = self.speed
        
        #Save current data
        self.relative_position = pos #[x,y,z]
        self.heading = heading
        self.elevation = elevation
        self.distance = distance
        self.ground_distance = ground_distance
        self.lastUpdate = t
        
        #Calculate information
        self.speed = [ self.relative_position[0] - self.positionOld[0][0] , self.relative_position[1] - self.positionOld[0][1], self.relative_position[2] - self.positionOld[0][2]]
        self.speedTot = self.lengte(self.speed)
        if self.speedOld != list():
            self.acceleration = [ self.speed[0] - self.speedOld[0], self.speed[1] - self.speedOld[1], self.speed[2] - self.speedOld[2]]
            self.accelerationTot = self.lengte(self.acceleration)
        self.cpa, self.Tcpa = self.cpa_calc()
        self.futurePosition1 = self.futurePosition(1)
        self.futurePosition10 = self.futurePosition(10)
        
    def lengte(self, lijst):
        totaal = 0
        for i in lijst:
            totaal += i**2
        return totaal**0.5
    
    def posToBearing(self, pos):
        ground_distance = ((pos[0]**2) + (pos[1]**2))**0.5
        heading = math.degrees(math.asin(pos[0] / ground_distance))
        height = pos[2]
        return heading, (ground_distance, height) #heading in degrees, tuple in m

    def cpa_calc(self):
        a = self.relative_position
        v = self.speed
        if self.speed == [0,0,0]:
            return 'n/a', 'n/a'
        else:
            time = -dot(a,v)/ dot(v,v)
            px,py,pz = self.cpa_pos(a,v,time)
            distance = ((px**2 ) + (py **2) + (pz **2))**0.5
            return distance, time
    
    #berekenen van de positie van de closest point of advance    
    def cpa_pos(self,a,v,time):
        #p= a+ v*t
        px = a[0] + v[0] * time
        py = a[1] + v[1] * time
        pz = a[2] + v[2] * time
        return px,py,pz
    
    def futurePosition(self, time):
        pos = self.relative_position
        speed = self.speed
        futpos = [pos[0] + speed[0] * time , pos[1] + speed[1] * time , pos[2] + speed[2] * time]
        return futpos
    
    def compare(self, pos):
        totDev = 0
        if self.futurePosition1 != list():
            for i in [0,1,2]:
                totDev += (pos[i] - self.futurePosition1[i])**2 #afstand van de posities
            return totDev ** 0.5
        else:
            for i in [0,1,2]:
                totDev += (pos[i] - self.relative_position[i])**2 #afstand van de posities
            return totDev ** 0.5
        
     


#def __init__(self, heading, elevation, distance, ground_distance, t)
# 
# a = Contact(174.525857226826, 7.29180391166557, 3774.99103205393, 3774.99103205393 * math.cos(math.radians(7.29180391166557)), 9000)
# 
# # 10000 175.190206882535 8.17267984890556 3705.36757074263
# #def update(self, heading, elevation, distance, ground_distance, pos, t)
# 
# x,y,z = relativepos(175.190206882535, 8.17267984890556, 3705.36757074263, 3705.36757074263 * math.cos(math.radians(8.17267984890556)))
# pos = [x,y,z]
# a.update(175.190206882535, 8.17267984890556 , 3705.36757074263, 3705.36757074263 * math.cos(math.radians(8.17267984890556)), pos , 10000 )
# 
# #1 11000 175.864192391421 8.96806696301345 3630.61836729314
# bearing = 175.864192391421
# elevation = 8.96806696301345
# distance = 3630.61836729314
# ground_distance = 3630.61836729314 * math.cos(math.radians(8.96806696301345))
# x,y,z = relativepos(175.864192391421, 8.96806696301345, 3630.61836729314, 3630.61836729314 * math.cos(math.radians(8.96806696301345)))
# pos = [x,y,z]
# b = a.compare(pos)