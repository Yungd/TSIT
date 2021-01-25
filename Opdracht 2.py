import Opdracht2func as op2 #alle functies en klassen staan in dit bestand
import math
import networkx as nx
import matplotlib.pyplot as plt

#laad alle tracks in een lijst
combinedTr = op2.readtracks("combined4.tr.txt")
combinedTrL = op2.txtToList(combinedTr)

aantalTracks = 4 #het aantal tracks dat gevolgd gaat worden

#initieer eigen positie
eigenSchip = op2.UFO(0,0,0,0,0,0,"black")
positions = {eigenSchip.naam: (eigenSchip.xNew, eigenSchip.yNew)} #dict waar alle posities in worden opgeslagen
nodes = [0] #lijst met nodes om mee te plotten
colorlist = ["black"] #lijst met kleuren om mee te plotten
#Mogelijke kleuren voor contacten
kleuren= ['black','blue','green', 'red', 'cyan', 'magenta', 'yellow']
spelers = {}#dict waar de spelers in worden opgeslagen
objectNr = 1#counter voor toewijzen kleuren spelers

timer = 0 #verloop van de 'tijd'
updateTime = 100 #om de hoeveel tijd krijgt men een sitrep
plaatje = True #Geplotte update bij sitrep

#initieer de plot
SA = nx.Graph()
nodegrootte = [200,100, 100,100,100]

#counter voor toewijzen namen oude locaties
nodecount = 10

for i in combinedTrL: #Loop stap voor stap door alle tracks heen
    
    #initieer de verschillende contacten
    if timer < 1:
        
        spelers[kleuren[objectNr]] = op2.initieerKlasse(i, objectNr, kleuren[objectNr])
        objectNr +=1
    
    #laat initiele situatie zien
    if timer == 1:
        
        for speler in spelers:
            positions[spelers[speler].naam] = (spelers[speler].xNew,spelers[speler].yNew) #voeg nieuwe posities toe
        
            nodes.append(spelers[speler].naam) #voeg de nieuwe nodenamen toe
            colorlist.append(spelers[speler].kleur) #voeg de kleur van elke speler toe
        
        nx.draw_networkx_nodes(SA,positions,nodelist=nodes,node_size=300,node_color=colorlist, node_shape = 'v')
        plt.show() #plot en show
    
    #eerste update om eerste snelheden te berekenen
    if (timer < 2) and (timer >= 1):
        
        #update de spelers.
        #Er wordt hier van uit gegaan dat de tweede locatie die wordt gedetecteerd
        #kwa bearing genoeg overeenkomt met de eerste locatie om hier geen metingen aan te doen.
        spelers[kleuren[objectNr-aantalTracks]], positions, nodes, colorlist, nodegrootte, nodecount = op2.update_track(i, spelers[kleuren[objectNr-aantalTracks]], positions, nodes, colorlist, nodegrootte, nodecount)
        objectNr+=1
        
    comparedTracks = {} #Er wordt een lege dictionary aangemaakt om de vergelijkingen tussen een track en de spelers in op te slaan. Deze dict wordt per track geleegd.
    if (timer >= 2) :
        for unit in spelers:
            #voeg een dict entry toe met als key de afwijking van de track tov de speler en als data de speler
            comparedTracks[op2.compare(i, spelers[unit])] = spelers[unit]
        # De persoon met de minste afwijking is comparedTracks[min(comparedTracks)]
        comparedTracks[min(comparedTracks)], positions, nodes, colorlist, nodegrootte, nodecount = op2.update_track(i, comparedTracks[min(comparedTracks)], positions, nodes, colorlist, nodegrootte, nodecount)
    
    #Geef een sitrep met eventueel een plotje    
    if ((timer % updateTime) == 0)  and (timer > 1):
        op2.sitrep(timer, spelers)
        nx.draw_networkx_nodes(SA,positions,nodelist=nodes,node_size=nodegrootte,node_color=colorlist, node_shape = 'v')        
        if plaatje == True: plt.show()
         
    #increment timer                    
    timer += (1/aantalTracks)
        
    
plt.show() #laat het eindresultaat zien


