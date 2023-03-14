from csv import reader
from os import walk
import pygame

def import_csv_layout(path):
    terrain_map = []

    with open(path) as level_map:
        layout = reader(level_map, delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))

        return terrain_map
        
def import_folder(path):
    surface_list = []

    # Walk returns folder path(path), an array of sub folders, and an array of files
    # We do not care about path and subfolder, so we will label them _ and __ just to indicate we don't care about those
    # But we do want the file names, which we know will image file names
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list
