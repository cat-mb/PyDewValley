import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop):
        # when we pass in group, the object is going to be inside of this group
        super().__init__(group)
        # has to be at top of init method since when we create image, we need animations dictionary
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        # this is what the sprite will look like

        # general setup; key value pair
        # self.status determines what the animation is
        self.image = self.animations[self.status][self.frame_index]
        # rect takes care of the position
        self.rect = self.image.get_rect(center = pos)
        # player has z position; x and y always come from rectangle feature
        self.z = LAYERS['main']

        # movement attributes
        self.direction = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 300

        # collision
        # hitbox for collisions; inflate takes rect and changes dimension while keeping it centered
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        # timers
        self.timers = {
            # tools
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            # seeds
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }

        # tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds; basically the same as setting up tool switching
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # inventory
        self.item_inventory = {
            # we want these numebers to increase once player collects items
            'wood':   0,
            'apple':  0,
            'corn':   0,
            'tomato': 0
        }
        self.seed_inventory = {
            'corn': 5,
            'tomato': 5
        }
        self.money = 200

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        # by default, false
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop

        # watering sound
        self.watering = pygame.mixer.Sound('/Users/cat/Desktop/PyDewValley/audio/water.mp3')
        self.watering.set_volume(0.2)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            # targets method in soil
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            # if selected tool is water, play sound
            self.watering.play()

    def get_target_pos(self):
        self.target_pos = self.rect.center + \
            PLAYER_TOOL_OFFSET[self.status.split('_')[0]]


    def use_seed(self):
        # player can only use seeds if they have at least 1
        if self.seed_inventory[self.selected_seed] > 0:
        # we have to know what target we are hitting and what kind of seed we are using
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def import_assets(self):
        # have to go through list of surfaces
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_hoe': [], 'down_hoe': [],  'left_hoe': [], 'right_hoe': [],
            'up_axe': [], 'down_axe': [],  'left_axe': [], 'right_axe': [],
            'up_water': [], 'down_water': [],  'left_water': [], 'right_water': [],
        }
        
        for animation in self.animations.keys():
            full_path = '/Users/cat/Desktop/PyDewValley/graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self,dt):
        # make sure we are always looping thru index
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        # self.frame index goes thru all frames
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        # returning a list of keys that are all being pressed
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep:
            # directions
            if keys[pygame.K_UP]:
                self.direction.y = -1
            # if player is pressing up, we know the animation will be up
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            # else statement stops from moving in one direction forever
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
                
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            
            # tool use
            if keys[pygame.K_SPACE]:
            # run a timer for tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                # ensures animation begins from the start index
                self.frame_index = 0
            
            # check if player is changing tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                # if tool index > length of tools, then we want to set tool index to 0
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

            # seed use
            if keys[pygame.K_LCTRL]:
            # run a timer for seed use
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                # ensures animation begins from the start index
                self.frame_index = 0

            
            # check if player is changing seed
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                # if seed index > length of seeds, then we want to set seed index to 0
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]

            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self,self.interaction,False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    else:
                        self.status = 'left_idle'
                        # we know player is sleeping, start transition to day from this
                        self.sleep = True
    
    # method that assigns idle animation to when player isn't moving

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_status(self):
        # idle
        if self.direction.magnitude() == 0:
        # add _idle to the status, we will have single idle assigned to status
            self.status = self.status.split('_')[0] + '_idle'
        
        # tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
    
    def collision(self, direction):
        # looks @ every sprite inside of collision sprites
        for sprite in self.collision_sprites.sprites():
            # if sprite has attribute named hitbox
             if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    # check if collision happens on left or right; if collison happens to right, player has to be to the left of obs
                    if direction == 'horizontal':
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.hitbox.right
                        # rectangle player sees
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                # check if collision happens up or down
                    if direction == 'vertical':
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        # rectangle player sees
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery


    def move(self, dt):

        # normalizing a vector; making sure dir of vector is always 1
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # horizontal movement (x dimension)
        self.pos.x += self.direction.x * self.speed * dt
        # moving hitbox; needs to be rounded to proper value, otherwise, bugs will occur
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement (y dimension)
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = round(self.pos.y)
        self.collision('vertical')

    # figures out when to call input method
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt)