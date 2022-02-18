import random
import pygame
pygame.init()

screenwidth = 1200
screenheight = 600
screen = pygame.display.set_mode((screenwidth,screenheight))

#########
#SPRITES#
#########

playersprite = pygame.image.load('assets//player.png')
playersprite.convert()

small = pygame.image.load('assets//small.png')
smallattack = pygame.image.load('assets//small-attack.png')
bluelaser = pygame.image.load('assets//blue-laser.png')
laserring = pygame.image.load('assets//laser-ring.png')
small.convert()
smallattack.convert()
bluelaser.convert()
laserring.convert()
laserringback = pygame.transform.flip(laserring,True,False)

bluelaserprojectile = pygame.image.load('assets//blue-laser-projectile.png')
bluelaserprojectile.convert()

rocksmall1 = pygame.image.load('assets//rock-small-1.png')
rocksmall2 = pygame.image.load('assets//rock-small-2.png')
rocksmall1.convert()
rocksmall2.convert()

rockbig1 = pygame.image.load('assets//rock-big-1.png')
rockbig2 = pygame.image.load('assets//rock-big-2.png')
rockbig1.convert()
rockbig2.convert()

trunk1 = pygame.image.load('assets//trunk-1.png')
trunk1.convert()

leaf1 = pygame.image.load('assets//leaf-1.png')
leaf1.convert()

heart = pygame.image.load('assets//heart.png')
heart.convert()

bow0 = pygame.image.load('assets//bow-0.png')
bow1 = pygame.image.load('assets//bow-1.png')
bow2 = pygame.image.load('assets//bow-2.png')
bow3 = pygame.image.load('assets//bow-3.png')
bow0.convert()
bow1.convert()
bow2.convert()
bow3.convert()

arrowsprite = pygame.image.load('assets//arrow.png')
arrowsprite.convert()

healthsprite = pygame.image.load('assets//health.png')
healthsprite.convert()

#####
#MAP#
#####

#ground colors
'''
range: range of player y values
id: biome id
base: the base color of the biome in rgb
change: the change in color per pixel y in rgb
'''
groundcolors = { #ids start at 1 cry about it
    range(2000,0,-1):{'id':1,'base':(80,250,100),'change':(0,0,0)}, #green grass biome
    range(0,-3000,-1):{'id':2,'base':(80,250,100),'change':(0,-0.02,0)}, #darkening green
    range(-3000,-6000,-1):{'id':3,'base':(80,190,100),'change':(0,0,0.02)} ,#increasingly blue
    range(-6000,-10000,-1):{'id':4,'base':(80,190,160),'change':(0,0,0)} #blue snow biome
}

biomeenemies = { #i am too lazy to do numbers
    1:['small'],
    2:['small'],
    3:['small','blue-laser'],
    4:['small','blue-laser','blue-laser'] #higher chance of spawning laser enemies
}

bosses = {
    'laser-boss':{'y':-8000,'spawned':False}
}

#rocks
class rock:

    def __init__(self,position,sprite,direction,rect):
        self.position = position
        self.sprite = sprite
        self.direction = direction
        self.rect = rect

rocks = []

#randomly generated rocks
for x in range(-4000,4000,300):
    for y in range(-10000,1000,300):
        if random.choice((True,False)):
            for i in range(random.randint(1,3)):
                newrock = rock(
                    position = (x+random.randint(-50,50),y+random.randint(-50,50)),
                    #higher chance of getting small rocks than large rocks
                    sprite = random.choice((rocksmall1,rocksmall1,rocksmall2,rockbig1,rockbig2)),
                    direction = random.choice(('left','right')),
                    rect = None
                    )
                
                if newrock.sprite == rockbig1:
                    newrock.rect = rockbig1.get_rect()
                if newrock.sprite == rockbig2:
                    newrock.rect = rockbig2.get_rect()
                rocks.append(newrock)

#border rocks   
for x in range(-4100,4100,30):
    #bottom border
    newrock = rock(
        position = (x,1100),
        sprite = rockbig1,
        direction = random.choice(('left','right')),
        rect = rockbig1.get_rect()
        )
    rocks.append(newrock)

for y in range(-10000,1100,30):
    #left border
    newrock = rock(
        position = (-4100,y),
        sprite = rockbig1,
        direction = random.choice(('left','right')),
        rect = rockbig1.get_rect()
        )
    rocks.append(newrock)
    #right border
    newrock = rock(
        position = (4100,y),
        sprite = rockbig1,
        direction = random.choice(('left','right')),
        rect = rockbig1.get_rect()
        )
    rocks.append(newrock)

#trees
class tree:

    def __init__(self,position,direction,trunk,leaves):
        self.position = position
        self.direction = direction
        self.trunk = trunk
        self.leaves = leaves
        self.offset = (random.randint(-4,4),random.randint(-4,4))
        self.rect = trunk.get_rect()

trees = [tree((0,0),'left',trunk1,leaf1)]


#randomly generated trees
for x in range(-4000,4000,500):
    for y in range(-10000,1000,500):
        if random.choice((True,True,False,False,False)):
            for i in range(random.randint(1,3)):
                newtree = tree(
                    position = (x+random.randint(-50,50),y+random.randint(-50,50)),
                    direction = random.choice(('left','right')),
                    trunk = trunk1,
                    leaves = leaf1
                    )
                trees.append(newtree)
