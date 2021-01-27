import math

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
    return x_rel, y_rel, height

class Contact():x
    #Deze class bevat alle informatie over één contact
    
    def __init__(self, heading, elevation, distance, ground_distance):
        #Initeren van de class. Input zijn de radargegevens en de al berekende informatie
        
        #Current stats
        x,y,z = relativepos(heading, elevation, distance, ground_distance)
        self.relative_position = [x,y,z]
        self.heading = heading
        self.elavation = elavation
        self.distance = distance
        self.ground_distance = ground_distance
        
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
        
    def update(self, heading, elevation, distance, ground_distance, x, y, z):
        #Het updaten van een contact.
        #De input zijn de radargegevens en de al berekende informatie voor het vergelijken.
        
        #Store data
        self.positionOld.insert(0,self.relative_position)
        self.drawPositionOld.insert(0, (self.heading,self.ground_distance))
        if self.speed != list():
            self.speedOld = self.speed
        
        #Save current data
        self.relative_position = [x,y,z]
        self.heading = heading
        self.elevation = elevation
        self.distance = distance
        self.ground_distance = ground_distance
        
        #Calculate information
        self.speed = [ self.relative_position[0] - self.positionOld[0][0] , self.relative_position[1] - self.positionOld[0][1], self.relative_position[2] - self.positionOld[0][2]]
        self.speedTot = self.lengte(self.speed)
        if self.speedOld != list():
            self.acceleration = [ self.speed[0] - self.speedOld[0], self.speed[1] - self.speedOld[1], self.speed[2] - self.speedOld[2]]
            self.accelerationTot = self.lengte(self.acceleration)
        
    def lengte(lijst):
        totaal = 0
        for i in lijst:
            totaal += i**2
        return totaal**0.5
    
    def posToBearing(pos):
        ground_distance = ((pos[0]**2) + (pos[1]**2))**0.5
        heading = math.degrees(math.asin(pos[0] / ground_distance))
        height = pos[2]
        return heading, (ground_distance, height) #heading in degrees, tuple in m
        
    
