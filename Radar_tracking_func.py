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
    height = distance * math.sin(elevation)
    x_relative = math.sin(heading) * ground_distance
    y_relative = math.cos(heading) * ground_distance
    return x_rel, y_rel, height

class Contact():
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
        self.acceleration = list() #ax,ay,az
        self.cpa = None #Distance to cpa
        self.Tcpa = None #Over hoeveel seconden gebeurt cpa
        self.futurePosition1 = list() #x,y,z over 1 seconde
        self.futurePosition10 = list() #x,y,z over 10 secondes
        
        #Storage old data
        self.positionOld = list() #lijst met oude relatieve posities
        self.drawPositionOld = list() #lijst met de oude (heading,grounddistance) combinaties
        
    def update(self, heading, elevation, distance, ground_distance, x, y, z):
        #Het updaten van een contact.
        #De input zijn de radargegevens en de al berekende informatie voor het vergelijken.
        
        #Store data
        self.positionOld.append(self.relative_position)
        self.drawPositionOld.append((self.heading,self.ground_distance))
        
        
           
    
