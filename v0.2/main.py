#setup
'START BLOCK'
#imports
import pygame
import random
import keyboard
import math

pygame.init()

mainloop = True
clock = pygame.time.Clock()
text = pygame.font.Font(None,32)

hitboxes = False

from map import *
pygame.display.set_icon(bluelaser)
pygame.display.set_caption('Jimmy Simulator')
'END BLOCK'

#player
'START BLOCK'
class player:
    position = (screenwidth/2,screenheight/2)
    #this is different from the rect - the rect will always stay in the middle of the screen
    #this position represents the location on the map
    
    rect = playersprite.get_rect()
    rect.center = (screenwidth/2,screenheight/2)
    sprite = playersprite

    speed = 4

    #this dict of rects is used for directional collisions, ie not walking through rocks and enemies
    #other collisions like taking damage will use the main rect
    '''
    colliderects = {'up':pygame.Rect((590+2,280),(20-4,2)),
                      'left':pygame.Rect((590,285),(2,30)),
                      'down':pygame.Rect((590+2,320-2),(20-4,2)),
                      'right':pygame.Rect((610-2,285),(2,30))
                      }
    ''' #replaced hard coded directional rects with ones that conform to the main rect
    colliderects = {'up':pygame.Rect((rect.topleft[0]+2,rect.topleft[1]),(rect.width-4,2)),
                      'left':pygame.Rect((rect.topleft[0],rect.topleft[1]+2),(2,rect.height-4)),
                      'down':pygame.Rect((rect.bottomleft[0]+2,rect.bottomleft[1]-2),(rect.width-4,2)),
                      'right':pygame.Rect((rect.topright[0]-2,rect.topleft[1]+2),(2,rect.height-4))
                      }
    allowedmovement = {'up':True,'left':True,'down':True,'right':True}

    health = 100

    class bow:
        sprite = bow0
        rect = sprite.get_rect
        position = (0,0)
        draw = 0
        angle = 0
        distance = 30 #distance in terms of sin/cos of angle in radians

        sprites = {0:bow0,1:bow1,2:bow2,3:bow3}

        cooldown = 0
        
player.rect.center = (screenwidth/2,screenheight/2) #redundant but whatever
'END BLOCK'

#arrows
'START BLOCK'
class arrow:

    def __init__(self,position,angle,speed):
        self.sprite = arrowsprite
        self.rect = self.sprite.get_rect()

        self.position = position
        self.angle = angle
        self.speed = speed

        self.timer = 80

arrows = []
'END BLOCK'

#jimmy
'START BLOCK'
class jimmy:

    def __init__(self,position,type):
        self.position = position
        self.knockback = (0,0) #first number is the angle in radians, second number is multiplier
        self.direction = 'left'
        self.attacktimer = 0
        self.type = type
        
        if self.type == 'small':
            self.speed = 2
            self.sprite = small
            self.damage = 5
            self.health = 5
            self.maxhealth = 5

        if self.type == 'blue-laser':
            self.speed = 1.5
            self.sprite = bluelaser
            self.damage = 10
            self.health = 10
            self.maxhealth = 10

        if self.type == 'laser-boss':
            self.speed = 1.25
            self.sprite = bluelaser
            self.damage = 10
            self.health = 30
            self.maxhealth = 30
            self.rings = [{'orig-sprite':pygame.transform.scale(laserring,(60,60)),'sprite':pygame.transform.scale(laserring,(60,60)),
                           'rect':laserring.get_rect(),'angle':0,'turn':10},
                        {'orig-sprite':pygame.transform.scale(laserring,(80,80)),'sprite':pygame.transform.scale(laserring,(80,80)),
                           'rect':laserring.get_rect(),'angle':0,'turn':-8},
                        {'orig-sprite':pygame.transform.scale(laserring,(100,100)),'sprite':pygame.transform.scale(laserring,(100,100)),
                           'rect':laserring.get_rect(),'angle':0,'turn':5}
                          ]

        self.rect = self.sprite.get_rect()

    def checkcollide(self): #makes it so the enemy and player dont overlap
        self.rect.center = (self.position[0]-tempcam[0],self.position[1]-tempcam[1])
        
        if self.rect.colliderect(player.colliderects['up']):
            player.allowedmovement['up'] = False
        if self.rect.colliderect(player.colliderects['left']):
            player.allowedmovement['left'] = False
        if self.rect.colliderect(player.colliderects['down']):
            player.allowedmovement['down'] = False
        if self.rect.colliderect(player.colliderects['right']):
            player.allowedmovement['right'] = False

        collisions = [
            self.rect.colliderect(player.colliderects['up']),
            self.rect.colliderect(player.colliderects['left']),
            self.rect.colliderect(player.colliderects['down']),
            self.rect.colliderect(player.colliderects['right'])]
        
        if True in collisions:
            return True
        else:
            return False

    def render(self):
        
        #back rings for laser boss: have to be blitted before the main sprite
        if enemy.type == 'laser-boss':
            for ring in enemy.rings:
                ring['sprite'] = pygame.transform.rotate(pygame.transform.flip(ring['orig-sprite'],False,True),ring['angle'])
                ring['rect'] = ring['sprite'].get_rect()
                ring['rect'].center = enemy.rect.center
                screen.blit(ring['sprite'],ring['rect'].topleft)
                
        if hitboxes:
            pygame.draw.rect(screen,(0,255,0),self.rect)
        if self.direction == 'left':
            screen.blit(self.sprite,self.rect.topleft)
        if self.direction == 'right':
            screen.blit(pygame.transform.flip(self.sprite,True,False),self.rect.topleft)

        #front rings for laser boss
        if enemy.type == 'laser-boss':
            for ring in enemy.rings:
                ring['sprite'] = pygame.transform.rotate(ring['orig-sprite'],ring['angle'])
                ring['rect'] = ring['sprite'].get_rect()
                ring['rect'].center = enemy.rect.center
                screen.blit(ring['sprite'],ring['rect'].topleft)

                ring['angle'] = ring['angle'] + ring['turn']
                ring['angle'] = ring['angle'] % 360

    def healthbar(self):
        length = self.maxhealth * 4 #length horizontally
        height = 40 #distance from the bar to the sprite
        if self.maxhealth > 10: #how thick the bar is
            width = 7
        else:
            width = 5
        pygame.draw.line(screen,(0,0,0),(self.rect.centerx-length/2-1,self.rect.centery-height),
                         (self.rect.centerx+length/2+1,self.rect.centery-height),width) #black outline
        pygame.draw.line(screen,(100,100,100),(self.rect.centerx-length/2,self.rect.centery-height),
                         (self.rect.centerx+length/2,self.rect.centery-height),width-2) #grey background
        pygame.draw.line(screen,(255,0,0),(self.rect.centerx-length/2,self.rect.centery-height),
                         (self.rect.centerx-length/2+self.health*4,self.rect.centery-height),width-2) #red healthbar

enemies = []
enemytimer = 240
newenemy = None
spawnboss = None
'END BLOCK'

#projectiles
'START BLOCK'
class projectile:

    def __init__(self,sprite,position,direction):
        self.sprite = sprite
        self.rect = sprite.get_rect()
        self.position = position
        self.direction = direction

        if self.sprite == bluelaserprojectile:
            self.speed = 10
            self.damage = 5

projectiles = []
'END BLOCK'

#health pack
'START BLOCK'
class healthpack:

    def __init__(self,position):
        self.position = position
        self.rect = healthsprite.get_rect()
        self.rect.center = self.position

healthdropchances = {'small':0.1,'blue-laser':0.5,'laser-boss':1}

activehealthpacks = [healthpack((200,200)),healthpack((200,300)),healthpack((200,400)),healthpack((200,500))]
healthpacks = 5
healthpackcooldown = 0
'END BLOCK'

###########
#MAIN LOOP#
###########

while mainloop:
    
    #quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainloop = False

    #die
    if player.health == 0 or player.health < 0:
        mainloop = False

    #camera
    tempcam = (player.position[0]-screenwidth/2,player.position[1]-screenheight/2)

    #background/biome
    biome = None
    for color in groundcolors:
        if player.position[1] in color:
            biome = groundcolors[color]['id']
            screen.fill((groundcolors[color]['base'][0]+groundcolors[color]['change'][0]*color.index(player.position[1]),
                         groundcolors[color]['base'][1]+groundcolors[color]['change'][1]*color.index(player.position[1]),
                         groundcolors[color]['base'][2]+groundcolors[color]['change'][2]*color.index(player.position[1]),
                        ))
    if not biome:
        screen.fill((0,0,0)) #fill with black if no biome is found
    
    #rocks
    'START BLOCK'
    for item in rocks:

        if abs(item.position[0]-tempcam[0]) < 1300 and abs(item.position[1]-tempcam[1]) < 700: #dont render if off screen
            
            if not item.rect == None:
                item.rect.topleft = (item.position[0]-tempcam[0],item.position[1]-tempcam[1])

                #makes it so the player cant walk through big rocks
                if item.rect.colliderect(player.colliderects['up']):
                    player.allowedmovement['up'] = False
                    
                if item.rect.colliderect(player.colliderects['left']):
                    player.allowedmovement['left'] = False
                    
                if item.rect.colliderect(player.colliderects['down']):
                    player.allowedmovement['down'] = False
                    
                if item.rect.colliderect(player.colliderects['right']):
                    player.allowedmovement['right'] = False

                if hitboxes:
                    pygame.draw.rect(screen,(255,255,0),item.rect)
            
            if item.direction == 'left':
                screen.blit(item.sprite,(item.position[0]-tempcam[0],item.position[1]-tempcam[1]))
            if item.direction == 'right':
                screen.blit(pygame.transform.flip(item.sprite,True,False),(item.position[0]-tempcam[0],item.position[1]-tempcam[1]))
    'END BLOCK'

    #trees
    'START BlOCK'
    for item in trees:
        
        if abs(item.position[0]-tempcam[0]) < 1300 and abs(item.position[1]-tempcam[1]) < 700: #dont render if off screen
            
            item.rect.topleft = (item.position[0]-tempcam[0],item.position[1]-tempcam[1])

            if item.rect.colliderect(player.colliderects['up']):
                player.allowedmovement['up'] = False
                
            if item.rect.colliderect(player.colliderects['left']):
                player.allowedmovement['left'] = False
                
            if item.rect.colliderect(player.colliderects['down']):
                player.allowedmovement['down'] = False
                
            if item.rect.colliderect(player.colliderects['right']):
                player.allowedmovement['right'] = False

            if hitboxes:
                pygame.draw.rect(screen,(255,255,0),item.rect)
            
            if item.direction == 'left':
                screen.blit(item.trunk,(item.position[0]-tempcam[0],item.position[1]-tempcam[1]))
                screen.blit(item.leaves,(item.position[0]-tempcam[0]-6,item.position[1]-tempcam[1]-6))
            if item.direction == 'right':
                screen.blit(pygame.transform.flip(item.trunk,True,False),(item.position[0]-tempcam[0],item.position[1]-tempcam[1]))
                screen.blit(pygame.transform.flip(item.leaves,True,False),(item.position[0]-tempcam[0]-6,item.position[1]-tempcam[1]-6))
    'END BLOCK'
                
    #player movement
    'START BLOCK'
    if keyboard.is_pressed('w') and player.allowedmovement['up']:
        player.position = (player.position[0],player.position[1]-player.speed)
    if keyboard.is_pressed('a') and player.allowedmovement['left']:
        player.position = (player.position[0]-player.speed,player.position[1])
    if keyboard.is_pressed('s') and player.allowedmovement['down']:
        player.position = (player.position[0],player.position[1]+player.speed)
    if keyboard.is_pressed('d') and player.allowedmovement['right']:
        player.position = (player.position[0]+player.speed,player.position[1])

    player.allowedmovement['up'] = True
    player.allowedmovement['left'] = True
    player.allowedmovement['down'] = True
    player.allowedmovement['right'] = True

    screen.blit(player.sprite,player.rect.topleft)
    
    if hitboxes:
        pygame.draw.rect(screen,(255,0,0),player.colliderects['up'])
        pygame.draw.rect(screen,(255,0,0),player.colliderects['down'])
        pygame.draw.rect(screen,(255,0,0),player.colliderects['left'])
        pygame.draw.rect(screen,(255,0,0),player.colliderects['right'])
    'END BLOCK'

    #bow
    'START BLOCK'
    '''
    this code basically finds the angle to point at the mouse, rotates the bow at it, and moves it so it isnt touching the player,
    and then saves the point, then it gets the rect of the sprite, sets the center of that rect to that point, and then blits
    the rotated sprite using the top left of the rect so it doesnt look weird because .blit() uses the top left of the sprite
    '''
    #get angle
    if player.bow.cooldown > 0:
        player.bow.cooldown = player.bow.cooldown - 1
    player.bow.angle = -math.atan2(player.rect.centery-pygame.mouse.get_pos()[1],player.rect.centerx-pygame.mouse.get_pos()[0])

    #pull the bow back
    if keyboard.is_pressed('space'):
        if player.bow.cooldown == 0:
            if player.bow.draw < 100:
                player.bow.draw = player.bow.draw + 1
    #release
    else:
        if not player.bow.draw == 0:
            #spawn new arrow
            arrows.append(arrow(player.bow.position,player.bow.angle,player.bow.draw/3+5))
            player.bow.cooldown = 10
            #i got player.bow.draw/3+5 experimentally, looked the best
        player.bow.draw = 0
        
    #which sprite to draw
    player.bow.sprite = pygame.transform.rotate(player.bow.sprites[round(player.bow.draw*(3/100))],math.degrees(player.bow.angle))
    #draw arrow in the bow
    '''
    if not round(player.bow.draw*(3/100)) == 0:
        screen.blit(pygame.transform.rotate(arrowsprite,math.degrees(player.bow.angle)),
                    (player.bow.position[0]-tempcam[0],player.bow.position[1]-tempcam[1]))
    ''' #i will do this later

    #find where to draw the bow
    player.bow.rect = player.bow.sprite.get_rect()
    player.bow.position = (player.position[0] - math.cos(player.bow.angle) * player.bow.distance,
                           player.position[1] + math.sin(player.bow.angle) * player.bow.distance)
    player.bow.rect.center = (player.bow.position[0]-tempcam[0],player.bow.position[1]-tempcam[1])

    #draw the bow
    if hitboxes:
        pygame.draw.rect(screen,(255,150,0),player.bow.rect)
        pygame.draw.line(screen,(0,0,255),player.rect.center,player.bow.rect.center,3)
    screen.blit(player.bow.sprite,player.bow.rect.topleft)
    'END BLOCK'

    #arrows
    'START BLOCK'
    for item in arrows:

        item.timer = item.timer - 1
        
        #move arrows
        if item.timer > 0:
            item.position = (item.position[0]-math.cos(item.angle)*item.speed,item.position[1]+math.sin(item.angle)*item.speed)
        item.sprite = pygame.transform.rotate(arrowsprite,math.degrees(item.angle))
        item.rect = item.sprite.get_rect()
        item.rect.center = (item.position[0]-tempcam[0],item.position[1]-tempcam[1])
        
        #old slowdown: changed because it looked weird
        '''
        item.speed = item.speed - .1
        if item.timer < 40:
            item.speed = item.speed - .2
        '''
        #new slowdown: uses exponential decay function
        if not item.speed == 0:
            item.speed = item.speed * 0.99 ** (80 - item.timer)
            if item.speed < 1:
                item.speed = 0
        #despawn timer
        if item.timer < -600: #-20 so the arrow stays on the ground for a moment after stopping
            arrows.remove(item)

        #draw arrows
        if hitboxes:
            pygame.draw.rect(screen,(255,0,255),item.rect)
        screen.blit(item.sprite,item.rect.topleft)
    'END BLOCK'

    #enemies
    'START BLOCK'
    enemytimer = enemytimer - 1
    if enemytimer == 0:

        spawnboss = None
        for boss in bosses:
            if player.position[1] < bosses[boss]['y'] and not bosses[boss]['spawned']:
                spawnboss = boss
                bosses[boss]['spawned'] = True
                break

        if spawnboss:
            newenemy = spawnboss
        else:
            newenemy = random.choice(biomeenemies[biome])
        enemies.append(jimmy(
            position=(random.choice(((player.position[0]-700),(player.position[0]+700))),
                      player.position[1]+random.randint(-400,400)),
            type=newenemy))
        
        enemytimer = random.randint(480,720)
        
    for enemy in enemies:

        if enemy.type == 'small':
            if not enemy.checkcollide():
                #old chase algorithm
                #changed because it made it so the ghoul would only ever move at exact 45 degree angles (only up, down, or diagonal)
                #instead of making a straight line for the player
                '''
                if self.position[0] > player.position[0]:
                    self.position = (self.position[0]-self.speed,self.position[1])
                if self.position[0] < player.position[0]:
                    self.position = (self.position[0]+self.speed,self.position[1])
                if self.position[1] > player.position[1]:
                    self.position = (self.position[0],self.position[1]-self.speed)
                if self.position[1] < player.position[1]:
                    self.position = (self.position[0],self.position[1]+self.speed)
                '''
                
                #new chase algorithm that uses angles instead
                if enemy.knockback == (0,0):
                    if math.dist(enemy.position,player.position) > 10:
                        slope = math.atan2(enemy.rect.centery - player.rect.centery,enemy.rect.centerx - player.rect.centerx)
                        enemy.position = (enemy.position[0]-math.cos(slope)*enemy.speed,enemy.position[1]-math.sin(slope)*enemy.speed)

                #face towards player
                if enemy.position[0] < player.position[0]:
                    enemy.direction = 'left'
                if enemy.position[0] > player.position[0]:
                    enemy.direction = 'right'

            #start attack
            if enemy.rect.colliderect(player.rect):
                if enemy.attacktimer == 0:
                    enemy.attacktimer = 30

            #progress attack
            if not enemy.attacktimer == 0:
                enemy.attacktimer = enemy.attacktimer - 1
                
                if enemy.attacktimer == 10 and enemy.rect.colliderect(player.rect):
                    player.health = player.health - enemy.damage
                
                if enemy.attacktimer < 10:
                    enemy.sprite = smallattack
                    
                if enemy.attacktimer == 0:
                    enemy.sprite = small
                    #enemy.rect.topleft = (enemy.position[0]-tempcam[0],enemy.position[1]-tempcam[1])

        if enemy.type == 'blue-laser':

            enemy.checkcollide() #this is called just to update the position

            if enemy.knockback == (0,0):
                #chase
                if math.dist(enemy.rect.center,player.rect.center) > 100:
                    slope = math.atan2(enemy.position[1] - player.position[1],enemy.position[0] - player.position[0])
                    enemy.position = (enemy.position[0]-math.cos(slope)*enemy.speed,enemy.position[1]-math.sin(slope)*enemy.speed)

                #face towards player
                if enemy.position[0] < player.position[0]:
                    enemy.direction = 'left'
                if enemy.position[0] > player.position[0]:
                    enemy.direction = 'right'

                #attack
                if math.dist(enemy.rect.center,player.rect.center) < 300:
                    
                    if enemy.attacktimer == 0:
                        enemy.attacktimer = 60
                        
                    if enemy.attacktimer > 0:
                        enemy.attacktimer = enemy.attacktimer - 1
                        if enemy.attacktimer == 0:
                            slope = math.atan2(enemy.rect.centery - player.rect.centery+random.randint(-10,10),
                                               enemy.rect.centerx - player.rect.centerx+random.randint(-10,10))
                            projectiles.append(projectile(bluelaserprojectile,
                                                          (enemy.position[0],enemy.position[1]),
                                                           slope))

        if enemy.type == 'laser-boss':

            enemy.checkcollide() #this is called just to update the position

            if enemy.knockback == (0,0):
                #chase
                if math.dist(enemy.rect.center,player.rect.center) > 100:
                    slope = math.atan2(enemy.position[1] - player.position[1],enemy.position[0] - player.position[0])
                    enemy.position = (enemy.position[0]-math.cos(slope)*enemy.speed,enemy.position[1]-math.sin(slope)*enemy.speed)

                #face towards player
                if enemy.position[0] < player.position[0]:
                    enemy.direction = 'left'
                if enemy.position[0] > player.position[0]:
                    enemy.direction = 'right'

                #attack
                if math.dist(enemy.rect.center,player.rect.center) < 600:
                    
                    if enemy.attacktimer == 0:
                        enemy.attacktimer = 480

                        if random.choice((True,True,False)): #special laser attack
                            for coords in [(80,0),(0,80),(-80,0),(0,-80)]:
                                slope = math.atan2(((enemy.rect.centery + coords[1]) - player.rect.centery),
                                                   ((enemy.rect.centerx + coords[0]) - player.rect.centerx))
                                projectiles.append(projectile(bluelaserprojectile,
                                                              (enemy.position[0]+coords[0],enemy.position[1]+coords[1]),
                                                               slope))
                                
                        else: #summon attack
                            enemies.append(jimmy(position=(enemy.position[0],enemy.position[1]+80),type='blue-laser'))
                            enemies.append(jimmy(position=(enemy.position[0]-80,enemy.position[1]-80),type='small'))
                            enemies.append(jimmy(position=(enemy.position[0]+80,enemy.position[1]-80),type='small'))
                        
                    if enemy.attacktimer > 0:
                        enemy.attacktimer = enemy.attacktimer - 1
                        if enemy.attacktimer % 80 == 0: #normal laser attack
                            slope = math.atan2(enemy.rect.centery - player.rect.centery+random.randint(-10,10),
                                               enemy.rect.centerx - player.rect.centerx+random.randint(-10,10))
                            projectiles.append(projectile(bluelaserprojectile,
                                                          (enemy.position[0],enemy.position[1]),
                                                           slope))

        #take damage from arrows
        for item in arrows:
            if enemy.rect.colliderect(item.rect):
                if not item.speed == 0:
                    enemy.health = enemy.health - (item.speed/15+2)
                    enemy.knockback = (item.angle,item.speed/15+2)
                    arrows.remove(item)

        #take knockback
        if not enemy.knockback == (0,0):
            enemy.position = (enemy.position[0]-math.cos(enemy.knockback[0])*enemy.knockback[1],
                              enemy.position[1]+math.sin(enemy.knockback[0])*enemy.knockback[1])
            enemy.knockback = (enemy.knockback[0],enemy.knockback[1]*0.9)
            if enemy.knockback[1] < 1:
                enemy.knockback = (0,0) #reset knockback

        #die
        if enemy.health == 0 or enemy.health < 0:

            if random.uniform(0,1) < healthdropchances[enemy.type]: #drop healthpacks
                activehealthpacks.append(healthpack(enemy.position))
                
            enemies.remove(enemy)
            
        enemy.render()
        enemy.healthbar()
    'END BLOCK'

    #projectiles
    'START BLOCK'
    for item in projectiles:

        #move
        item.position = (item.position[0]-math.cos(item.direction)*item.speed,item.position[1]-math.sin(item.direction)*item.speed)
        item.sprite = pygame.transform.flip(pygame.transform.rotate(bluelaserprojectile,math.degrees(item.direction)),False,True)
        item.rect = item.sprite.get_rect()
        item.rect.center = (item.position[0]-tempcam[0],item.position[1]-tempcam[1])

        #damage
        if item.rect.colliderect(player.rect):
            player.health = player.health - item.damage
            projectiles.remove(item)

        screen.blit(item.sprite,item.rect.topleft)
    'END BLOCK'

    #health packs
    'START BLOCK'
    if healthpackcooldown > 0:
        healthpackcooldown = healthpackcooldown - 1
        
    if keyboard.is_pressed('e'):
        if player.health < 100 and healthpacks > 0 and healthpackcooldown == 0:
            healthpacks = healthpacks - 1
            player.health = player.health + 65
            if player.health > 100:
                player.health = 100
            healthpackcooldown = 60
                
    for pack in activehealthpacks:
        pack.rect.center = (pack.position[0]-tempcam[0],pack.position[1]-tempcam[1])
        if pack.rect.colliderect(player.rect):
            activehealthpacks.remove(pack)
            healthpacks = healthpacks + 1
        screen.blit(healthsprite,pack.rect.topleft)
    'END BLOCK'

    #displays + gui
    'START BLOCK'
    #health
    screen.blit(heart,(50,500))
    pygame.draw.line(screen,(0,0,0),(79,510),(281,510),7)
    pygame.draw.line(screen,(100,100,100),(80,510),(280,510),5)
    pygame.draw.line(screen,(255,0,0),(80,510),(80+player.health*2,510),5)

    #healthpack counter
    healthpackcounter = text.render(str(healthpacks),True,(0,0,0))
    screen.blit(healthsprite,(48,530))
    screen.blit(healthpackcounter,(80,532))

    #toggle hitboxes
    if keyboard.is_pressed('q'):
        hitboxes = True
    else:
        hitboxes = False
    'END BLOCK'
    
    #essential stuff
    pygame.display.update()
    clock.tick(60)

pygame.quit()
