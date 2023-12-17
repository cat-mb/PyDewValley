import os
import pygame
from settings import *
from support import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu



class Level:
   
   def __init__(self):
    # this display surface is the same as self.screen in Game class, allows level to draw straight on the main display 
    # get the display surface
      self.display_surface = pygame.display.get_surface()

    # sprite groups; groups help us draw and update any sprite in the game
      self.all_sprites = CameraGroup()
      # keep track of what player can collide w
      self.collision_sprites = pygame.sprite.Group()
      self.tree_sprites = pygame.sprite.Group()
      self.interaction_sprites = pygame.sprite.Group()

      self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
      self.setup()
      self.overlay = Overlay(self.player)
      # day to nighttime
      self.transition = Transition(self.reset, self.player)

      # sky
      self.rain = Rain(self.all_sprites)
      self.raining = randint(0,10) > 3
      self.soil_layer.raining = self.raining
      self.sky = Sky()

      # shop
      self.menu = Menu(self.player, self.toggle_shop)
      self.shop_active = False

      # item obtained sound
      self.success = pygame.mixer.Sound('/Users/cat/Desktop/PyDewValley/audio/success.wav')
      self.success.set_volume(0.3)

      # music
      self.music = pygame.mixer.Sound('/Users/cat/Desktop/PyDewValley/audio/music.mp3')
      # loop plays music continously
      self.music.play(loops = -1)


   def setup(self):
      tmx_data = load_pygame('/Users/cat/Desktop/PyDewValley/data/map.tmx')

      # house floor has to come before house furniture bottom since its drawn on top of house furniture
      for layer in ['HouseFloor', 'HouseFurnitureBottom']:
      # build house; for loop that places each tile using x val, y val, and surf type
         for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE, y*TILE_SIZE), surf,
                        self.all_sprites, LAYERS['house bottom'])

      # same idea as building the house floor
      for layer in ['HouseWalls', 'HouseFurnitureTop']:
         for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites)

      # fence tiles
      for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
         Generic((x*TILE_SIZE, y*TILE_SIZE), surf,
                    [self.all_sprites, self.collision_sprites]) # omitted LAYERS['main'] since it shows up as default

      # water; classes created inside sprite
      water_frames = import_folder('/Users/cat/Desktop/PyDewValley/graphics/water')
      for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)


      # trees
      for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites,
                        self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add)

      # wildflowers
      for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [
                       self.all_sprites, self.collision_sprites])

      #collision tiles
      for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
         # collision sprites is one sprite that will not exist in all sprites
        Generic((x*TILE_SIZE, y*TILE_SIZE),
                    pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

      # Player
      for obj in tmx_data.get_layer_by_name('Player'):
         if obj.name == 'Start':
            self.player = Player(
               pos = (obj.x, obj.y), 
               group = self.all_sprites, 
               collision_sprites = self.collision_sprites,
               tree_sprites = self.tree_sprites,
               interaction = self.interaction_sprites,
               soil_layer = self.soil_layer,
               toggle_shop = self.toggle_shop
               )
         # bed interaction 
         if obj.name == 'Bed':
             Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
         # trader interaction
         if obj.name == 'Trader':
             Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
             
      Generic(
         pos = (0,0), 
         surf = pygame.image.load('/Users/cat/Desktop/PyDewValley/graphics/world/ground.png').convert_alpha(), 
         groups = self.all_sprites,
         z = LAYERS['ground'])
   
   def player_add(self, item):

      self.player.item_inventory[item] += 1
      self.success.play()

   def toggle_shop(self):
       # when we are running method, we are switching method on or off
       self.shop_active = not self.shop_active

   def plant_collision(self):
       if self.soil_layer.plant_sprites:
           # if there are no plants, this will not trigger
           for plant in self.soil_layer.plant_sprites.sprites():
               if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                   self.player_add(plant.plant_type)
                   plant.kill()
                   Particle(
                       pos = plant.rect.topleft,
                       surf = plant.image,
                       groups = self.all_sprites,
                       z = LAYERS['main']
                   )
                   self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')


   def reset(self):
       #plants; has to be called before everything since we might end up watering all plants w rain
       self.soil_layer.update_plants()

       # soil
       self.soil_layer.remove_water()

       # apples on the trees
       for tree in self.tree_sprites.sprites():
           for apple in tree.apple_sprites.sprites():
               apple.kill()
           tree.create_fruit()

       # sky
       self.sky.start_color = [255,255,255]
   # need delta time to make framerate independent
   def run(self, dt):
      # so we dont accidentally see the prev frame
      # drawing logic
      self.display_surface.fill('black')
      self.all_sprites.custom_draw(self.player)
      # updates
      if self.shop_active:
            self.menu.update()
      else:
            self.all_sprites.update(dt)
            self.plant_collision()
      # weather
      self.overlay.display()
      if self.raining and not self.shop_active:
          # calls update method in rain
          self.rain.update()
      # daytime
      self.sky.display(dt)
      
      # transition overlay
      if self.player.sleep:
          self.transition.play()
      

class CameraGroup(pygame.sprite.Group):
   def __init__(self):
      super().__init__()
      self.display_surface = pygame.display.get_surface()
      # if player if moving right, shift entire map to the left
      self.offset = pygame.math.Vector2()

   def custom_draw(self, player):
      # make relative to the player; gets position of player; offset is going to be by how much we shift sprite relative to player
      self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
      self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

      # cycle thru layers list, that way we get 3D effect
      for layer in LAYERS.values():
      # implementing player being shown in front or behind an object via y coordinate
         for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
      # if sprite.z is same as layer, draw display surface
            if sprite.z == layer:
               offset_rect = sprite.rect.copy()
               offset_rect.center -= self.offset
               # if we are calling blit, it draws sprite in certain position
               self.display_surface.blit(sprite.image, offset_rect)

   