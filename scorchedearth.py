import pygame
import random
import math


#############
# Constants #
#############
# game data
winner = False
running = True
maxdt = 0.5

# screen data
resy = 1080
resx = int(resy * (16/9))
reso = (resx, resy)

# tank data
playersize = (60, 30)
players = []
turn_speed = 25 # rad/s
charge_speed = 25 # power/s

# color data
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
black = (0, 0, 0)

# missile data
flying = False
trajectory = [(0, 0)]
speed = (0, 0)
rho = 1.225
surface = 0.005
Cd = 0.7
mass = 1.0
Cext = 20 # a constant to determine the exit velocity
g = 9.81 #m/s^2


#########################
# Classes and functions #
#########################
# class to store player data
class Players:
    # function to initialize a new player
    def __init__(self, name):
        self.name = name

        self.pos = (random.randint(0+playersize[0], reso[0]-playersize[0]),int(reso[1]*0.9))
        succes = False
        # Function to make sure that the players are not located to close to each other
        while succes == False:
            succes = True
            for player in players:
                seperation = 0.05 * reso[0]
                if (player.pos[0] + seperation) > self.pos[0] and (player.pos[0] - seperation) < self.pos[0]:
                    self.pos = (random.randint(0+playersize[0], reso[0]-playersize[0]),int(reso[1]*0.9))
                    succes = False


        # assign a color to the new player and make sure that its blue value is not to close to the background color
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while self.color[2] > 204.8:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # set initial barrel angle
        self.angle = 20
        self.power = 1

        self.center = (self.pos[0],int(self.pos[1]-0.5*playersize[1]))

    # function to make the tank set the missile to the first position with the initial speed after being fired
    def fire(self):
        trajectory = [self.barrelend]
        speedx = self.power*math.cos(self.theta)*Cext
        speedy = self.power*math.sin(self.theta)*Cext
        speed = (speedx, -speedy)

        return trajectory, speed

    # function to draw the tank
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.pos[0] - playersize[0] * 0.5), int(self.pos[1] - 0.5 * playersize[1]), playersize[0], int(0.5 * playersize[1])))
        self.turretcenter = (self.pos[0],int(self.pos[1]-0.5*playersize[1]))
        self.theta = self.angle * math.pi/180
        self.barrelend = (int(self.turretcenter[0]+math.cos(self.theta)*playersize[0]*0.67), int(self.turretcenter[1]-math.sin(self.theta)*playersize[0]*0.67))

        pygame.draw.circle(screen, self.color, self.turretcenter, int(0.4*playersize[1]))
        pygame.draw.line(screen, self.color, self.turretcenter, self.barrelend,5)


# function to draw the background of the game
def drawbackground(screen):
    screen.fill(blue)
    pygame.draw.rect(screen, green, (0, int(reso[1] * 0.9), int(reso[0]), int(0.1 * reso[1])))


# function to draw the text on the screen
def drawtext(screen, q):
    battlemenu = font.render('Player '+players[q].name+': power = '+str(round(players[q].power, 1))+' angle = '+str(round(players[q].angle, 1)), False, black)
    screen.blit(battlemenu, (int(0.02 * reso[0]), int(reso[1] * 0.02)))


# function to draw the missile and its trajectory
def drawmissile(screen):

    x = len(trajectory)
    if x > 1:
        for y in range(x - 1):
            pygame.draw.line(screen, red, (int(trajectory[y][0]),int(trajectory[y][1])), (int(trajectory[y+1][0]),int(trajectory[y+1][1])), 2)

    pygame.draw.circle(screen, black, (int(trajectory[-1][0]),int(trajectory[-1][1])), 4)


# function for the control inputs
def controls(keys):
    if keys[pygame.K_UP]:
        players[currentplayer].power = min(players[currentplayer].power+charge_speed*dt,100)
    if keys[pygame.K_DOWN]:
        players[currentplayer].power = max(players[currentplayer].power-charge_speed*dt,1)
    if keys[pygame.K_LEFT]:
        players[currentplayer].angle = min(players[currentplayer].angle+turn_speed*dt,170)
    if keys[pygame.K_RIGHT]:
        players[currentplayer].angle = max(players[currentplayer].angle-turn_speed*dt,10)
            

#################
# MAIN FUNCTION #
#################
try: 
    numplay = int(input('Start game with how many players?: '))
except:
    print('Please enter a valid number!')
if 2 < numplay < 9:
    print('You need to have between 2 and 8 players to play!')

for n in range(numplay):
    players.append(Players(input('Enter name for player '+str(n)+': ')))

pygame.init()

ft = pygame.font.match_font('impact')
font = pygame.font.SysFont(None, reso[1] // 30)
screen = pygame.display.set_mode(reso)
t0 = 0.001 * pygame.time.get_ticks()
pygame.event.pump()

currentplayer = 0

while running:
    t = 0.001 * pygame.time.get_ticks()
    dt = min(t - t0, maxdt)

    if dt > 0.:
        t0 = t
    keys = pygame.key.get_pressed()

    # listen for two events in which case the game exits
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if keys[pygame.K_ESCAPE]:
        running = False
    
    # if there is no missile currently flying the player has controls
    if flying == False:
        controls(keys)

    # draw the background
    drawbackground(screen)

    # draw all players
    for player in players:
        player.draw(screen)

    # listen for the control to fire the missile
    if flying == False:
        if keys[pygame.K_SPACE]:
            trajectory, speed = players[currentplayer].fire()
            flying = True

    # all stuff to make the missile fly
    if flying:
        # calculate drag values for x and y in the right direction
        if speed[0] > 0:
            adragx = -(0.5*rho*speed[0]**2*Cd*surface)/mass
        elif speed[0] < 0:
            adragx = (0.5*rho*speed[0]**2*Cd*surface)/mass
        else:
            adragx = 0

        if speed[1] > 0:
            adragy = -(0.5*rho*speed[1]**2*Cd*surface)/mass
        elif speed[1] < 0:
            adragy = (0.5*rho*speed[0]**2*Cd*surface)/mass
        else:
            adragy = 0

        # update the speed with the previously calculated acceleration values
        speed = (speed[0]+adragx*dt, speed[1]+(g+adragy)*dt)

        # add an entry to the trajectory using the last entry and the speed vector
        trajectory.append((trajectory[-1][0]+speed[0]*dt,trajectory[-1][1]+speed[1]*dt))

        # if the missile comes near to one of the tanks it will destroy this player
        hitt = -1
        for n in range(len(players)):
            player = players[n]
            # use the pythagoras theorem to find the distance from the missile to the center of a tank
            distance = ((player.center[0]-trajectory[-1][0])**2+(player.center[1]-trajectory[-1][1])**2)**0.5
            if distance < playersize[0]*0.4:
                flying = False
                hitt = n

        if hitt != -1:
            del players[hitt]
            hitt = -1
        # if the missile leaves the boundaries of the map it will hit
        if trajectory[-1][1] > (0.9 * reso[1]) or trajectory[-1][1] < 0 or trajectory[-1][0] < 0 or trajectory[-1][0] > reso[0]:
            flying = False

        # draw the missile
        drawmissile(screen)

        # if the missile hit something switch to the next player and enable controls
        if flying == False:
            currentplayer += 1
            if currentplayer >= len(players):
                currentplayer = 0

    # draw some text indicating the current player and his/her turret settings
    drawtext(screen, currentplayer)

    # draw new frame
    pygame.display.flip()

    if len(players) == 1:
        running = False
        winner = True
pygame.quit()
if winner == True:
    dummy = input("\nPlayer "+players[0].name+" won the game!")
