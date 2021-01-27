from math import *
import numpy as np
import matplotlib.pyplot as plt

# Parameters of projectile 
g       = 9.81         # Acceleration due to gravity (m/s^2)
rho_air = 1.29         # Air density (kg/m^3)
v0      = 1050         # Initial velocity (m/s)
m       = 0.125        # Mass of projectile (kg)
cD      = 0.25         # Drag coefficient (for bullet-grenade)
r       = 0.01         # Radius of projectile (m)
mu = 0.5 * cD * (pi * r ** 2) * rho_air / m

deltaT  = 0.01

# update projectile position linearly starting at: pv = (x,y,vx,vy)
# with gravity g and drag mu over delta time dt
def updatePos(g,mu,pv,dt):
    (x,y,vx,vy) = pv
    v = sqrt(vx**2 + vy**2)
    return (x + dt*vx,
            y + dt*vy,
            vx - mu*v*vx*dt,
            vy - (g + mu*v*vy) * dt)
    
# calculate position (distance, height) and speed (vx,vy) of
# projectile launched with elevation: elev and initial speed: v0
def grenadePosSpeed(elev,v0,t):
    x, y = 0.0, 0.0
    alpha0  = radians(elev)
    vx, vy = v0 * cos(alpha0), v0 * sin(alpha0)
    steps = floor(t / deltaT)
    for k in range(steps):
        x,y,vx,vy = updatePos(g,mu,(x,y,vx,vy),deltaT)
    x,y,vx,vy = updatePos(g,mu,(x,y,vx,vy),t - steps * deltaT)
    return (x,y,vx,vy)

# generate array of (x,y,vx,vy) spaced at dt
def pointsTrajectory(elev,v0,dt):
    x, y = 0.0, 0.0
    alpha0  = radians(elev)
    vx, vy = v0 * cos(alpha0), v0 * sin(alpha0)
    tpeak   = newton(lambda t: grenadePosSpeed(elev,v0,t)[3],0)
    tground = newton(lambda t: grenadePosSpeed(elev,v0,t)[1],tpeak + 2)
    maxheight = grenadePosSpeed(elev,v0,tpeak)[1]
    dist = grenadePosSpeed(elev,v0,tground)[0]
    pinterval = round(dt / deltaT)
    points = []
    for k in range(floor(tground/deltaT)):
        if k % pinterval == 0:
            points.append((x,y,vx,vy))
        x,y,vx,vy = updatePos(g,mu,(x,y,vx,vy),deltaT)
    res = np.array(points)
    return res


# calculate minimum distance of trajectory to point p (px,py)
# for projectile launched with elevation elev and initial speed v0
def mindist2point(elev,v0,p):
    px,py = p
    x, y = 0.0, 0.0
    mindist = sqrt(px**2+py**2)
    kmin = 0
    alpha0  = radians(elev)
    vx, vy = v0 * cos(alpha0), v0 * sin(alpha0)
    tpeak   = newton(lambda t: grenadePosSpeed(elev,v0,t)[3],0)
    tground = newton(lambda t: grenadePosSpeed(elev,v0,t)[1],tpeak + 2)
    maxheight = grenadePosSpeed(elev,v0,tpeak)[1]
    for k in range(floor(tground/deltaT)):
        x,y,vx,vy = updatePos(g,mu,(x,y,vx,vy),deltaT)
        dist = sqrt((px-x)**2 + (py-y)**2)
        if dist < mindist:
            mindist = dist
            kmin = k
    return mindist,kmin*deltaT

# generate graphs of trajectories for elevations: start to end spaced at interval 
# for projectile launched with initial speed v0
def graphs(start,end,interval,v0 = 1050):
    fig, ax = plt.subplots()
    for e in range(start,end+interval,interval):
        ps = pointsTrajectory(e,v0,1)
        ax.plot(ps[:,0],ps[:,1],label="Elevation: " + str(e))
    ax.grid(b=True)
    ax.legend()
    ax.set_xlabel("$x$ (m)")
    ax.set_ylabel("$y$ (m)")
    plt.show()
    
# speed vs time for elevation elev
def speedgraph(elev,v0 = 1050):
    tpeak   = newton(lambda t: grenadePosSpeed(elev,v0,t)[3],0)
    tground = newton(lambda t: grenadePosSpeed(elev,v0,t)[1],tpeak + 2)
    ps = pointsTrajectory(elev,v0,1)
    fig, ax = plt.subplots()
    ts = [t for t in range(floor(tground) + 1)]
    ax.grid(b=True)
    ax.plot(ts,[sqrt(vx**2+vy**2) for vx, vy in zip(ps[:,2],ps[:,3])])
    ax.set_xlabel("$t$ (s)")
    ax.set_ylabel("$speed$ (m/s)")
    plt.show()
  
# extra functions  
def deriv(f,x):
    return (f(x+0.0001) - f(x)) / 0.0001

def improve(f,a):
    return a - f(a)/ deriv(f,a)

def newton(f,a):
    while abs(f(a)) > 0.0001:
        a = improve(f,a)
    return a

def rounding(i):
    i_r = round(i/100)
    return int(i_r *100)
    
d = {}
xlist = list(range(0,2600,100))
ylist = list(range(0,2100,100))
for x in xlist:
    for y in ylist:
        d[(x,y)] = 0
x_min = 0
y_min = 0
y_max = 2000
x_max = 2500
elev = list(range(1,90,1))
for e in elev:
    print("Elevatie: " + str(e))
    points = pointsTrajectory(e,1050,0.01)
    for p in points:
        if p[0] >= x_min and p[0] <= x_max and round(p[0]%100) < 75:
            #print(p[0],p[1])
            if p[1] >= y_min and p[1] <= y_max and round(p[1]%100) < 75:
                #print(rounding(p[0]),rounding(p[1]))
                if d[(rounding(p[0]), rounding(p[1]))] == 0:
                    #print(f'Nu gaan we {e} invullen')
                    d[(rounding(p[0]),rounding(p[1]))] = e
count = 0                    
for i in d:
    if d[i] != 0:
        #print ( i, d[i])
        count += 1
print(count/len(d))