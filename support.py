# walk allows you to import from many folders
from os import walk
import pygame

def import_folder(path):
    # stores all of the surfaces
    surface_list = []
    # the path we are getting from the parameters we are passing through
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # in-game pygame surface
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_folder_dict(path):
    surface_dict = {}

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            # create specific key; get index of the list which will give name of file without file ending
            surface_dict[image.split('.')[0]] = image_surf
        
    return surface_dict