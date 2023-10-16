#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice, randint

import pygame
import ujson

from scripts.utility import event_text_adjust, scale, ACC_DISPLAY, process_text, chunks

from .Screens import Screens

from scripts.utility import get_text_box_theme, scale_dimentions, shorten_text_to_fit, generate_sprite
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE


from scripts.game_structure.game_essentials import game, screen

class CustomizeScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.your_cat = None
        self.elements = {}
        self.name="SingleColour"
        self.length="short"
        self.colour="WHITE"
        self.white_patches=None
        self.eye_color="BLUE"
        self.eye_colour2=None
        self.tortiebase=None
        self.tortiecolour=None
        self.pattern=None
        self.tortiepattern=None
        self.vitiligo=None
        self.points=None
        self.accessory=None
        self.paralyzed=False
        self.opacity=100
        self.scars=None
        self.tint="none"
        self.skin="BLACK"
        self.white_patches_tint="none"
        self.kitten_sprite=None
        self.adol_sprite=None
        self.adult_sprite=None
        self.senior_sprite=None
        self.para_adult_sprite=None
        self.reverse=False
        self.accessories=[]
        
    def screen_switches(self):
        # handle screen switch
        pelt2 = Pelt(
            name=self.name,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        self.your_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        self.your_cat.sprite = generate_sprite(self.your_cat)
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((700,100), (200, 200))),
                                   self.your_cat.sprite,
                                   self.your_cat.ID,
                                   starting_height=0, manager=MANAGER)
        
        column1_x = 200  # x-coordinate for column 1
        column2_x = 700  # x-coordinate for column 2
        column3_x = 1200  # x-coordinate for column 3
        y_pos = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300]
        
        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']
        
        self.elements['pelt dropdown'] = pygame_gui.elements.UIDropDownMenu(pelts, "SingleColour", scale(pygame.Rect((column1_x, y_pos[0]),(250,70))), manager=MANAGER)
        self.elements['pelt color'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "WHITE", scale(pygame.Rect((column1_x, y_pos[1]),(250,70))), manager=MANAGER)
        self.elements['eye color'] = pygame_gui.elements.UIDropDownMenu(Pelt.eye_colours, "BLUE", scale(pygame.Rect((column1_x, y_pos[2]),(250,70))), manager=MANAGER)
        self.elements['eye color2'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.eye_colours, "None", scale(pygame.Rect((column1_x, y_pos[3]),(250,70))), manager=MANAGER)
        self.elements['white patches'] = pygame_gui.elements.UIDropDownMenu(["None", "FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white, "None", scale(pygame.Rect((column1_x, y_pos[4]),(250,70))), manager=MANAGER)
        self.elements['pelt length'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_length, "short", scale(pygame.Rect((column1_x, y_pos[5]), (250, 70))), manager=MANAGER)
        
        self.elements['paralyzed'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column2_x, y_pos[0]), (250, 70))), manager=MANAGER)
        self.elements['reverse'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column2_x, y_pos[1]), (250, 70))), manager=MANAGER)
        self.elements['scars'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3, "None", scale(pygame.Rect((column2_x, y_pos[2]), (250, 70))), manager=MANAGER)
        self.elements['vitiligo'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.vit, "None", scale(pygame.Rect((column2_x, y_pos[3]), (250, 70))), manager=MANAGER)
        self.elements['points'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.point_markings, "None", scale(pygame.Rect((column2_x, y_pos[4]), (250, 70))), manager=MANAGER)
        self.elements['tint'] = pygame_gui.elements.UIDropDownMenu(["pink", "gray", "red", "orange", "None"], "None", scale(pygame.Rect((column2_x, y_pos[5]), (250, 70))), manager=MANAGER)
        
        self.elements['skin'] = pygame_gui.elements.UIDropDownMenu(Pelt.skin_sprites, "BLACK", scale(pygame.Rect((column3_x, y_pos[0]), (250, 70))), manager=MANAGER)
        self.elements['white_patches_tint'] = pygame_gui.elements.UIDropDownMenu(["None"] + ["none", "offwhite", "offwhite"], "None", scale(pygame.Rect((column3_x, y_pos[1]), (250, 70))), manager=MANAGER)
        
        self.elements['tortie'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column3_x, y_pos[2]), (250, 70))), manager=MANAGER)
        self.elements['pattern'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiepatterns, "ONE", scale(pygame.Rect((column3_x, y_pos[3]), (250, 70))), manager=MANAGER)
        self.elements['tortiebase'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiebases, "single", scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)
        self.elements['tortiecolor'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "GINGER", scale(pygame.Rect((column3_x, y_pos[5]), (250, 70))), manager=MANAGER)
        self.elements['tortiepattern'] = pygame_gui.elements.UIDropDownMenu(pelts, "Bengal", scale(pygame.Rect((column3_x, y_pos[6]), (250, 70))), manager=MANAGER)

        self.elements['permanent conditions'] = pygame_gui.elements.UIDropDownMenu(["None"] + permanent_conditions, "None", scale(pygame.Rect((column3_x, y_pos[7]), (250, 70))), manager=MANAGER)
        
        # tortie_pattern + cat.pelt.tortiecolour + cat_sprite
        self.elements['pattern'].disable()
        self.elements['tortiebase'].disable()
        self.elements['tortiecolor'].disable()
        self.elements['tortiepattern'].disable()
        
        self.elements['done'] = pygame_gui.elements.UIButton(scale(pygame.Rect((700, 1400),(100,50))), "Done", manager=MANAGER)

    def handle_event(self, event):
        
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.elements['pelt dropdown']:
                self.name = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pelt color']:
                self.colour = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['eye color']:
                self.eye_color = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['eye color2']:
                if event.text == "None":
                    self.eye_colour2 = None
                else:
                    self.eye_colour2 = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['white patches']:
                if event.text == "None":
                    self.white_patches = None
                else:
                    self.white_patches = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pelt length']:
                self.length = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['scars']:
                if event.text == "None":
                    self.scars = None
                else:
                    self.scars = [event.text]
                self.update_sprite()
            elif event.ui_element == self.elements['tortie']:
                if event.text == "Yes":
                    self.name = "Tortie"
                    self.elements['pelt dropdown'].disable()
                    self.elements['pattern'].enable()
                    self.elements['tortiebase'].enable()
                    self.elements['tortiecolor'].enable()
                    self.elements['tortiepattern'].enable()
                    
                    self.pattern = "ONE"
                    self.tortiepattern = "bengal"
                    self.tortiebase = "single"
                    self.tortiecolour = "GINGER"
                else:
                    self.name = "SingleColour"
                    self.elements['pelt dropdown'].enable()
                    self.elements['pattern'].disable()
                    self.elements['tortiebase'].disable()
                    self.elements['tortiecolor'].disable()
                    self.elements['tortiepattern'].disable()
                    self.pattern = None
                    self.tortiebase = None
                    self.tortiepattern = None
                    self.tortiecolour = None
                self.update_sprite()
                
            elif event.ui_element == self.elements['tortiecolor']:
                self.tortiecolour = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pattern']:
                self.pattern = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['tortiepattern']:
                self.tortiepattern = event.text.lower()
                self.update_sprite()
            elif event.ui_element == self.elements['tortiebase']:
                self.tortiebase = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['vitiligo']:
                if event.text == "None":
                    self.vitiligo = None
                else:
                    self.vitiligo = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['points']:
                if event.text == "None":
                    self.points = None
                else:
                    self.points = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['paralyzed']:
                self.paralyzed = (event.text == "Yes")
                self.update_sprite()
            elif event.ui_element == self.elements['tint']:
                if event.text == "None":
                    self.tint = None
                else:
                    self.tint = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['skin']:
                self.skin = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['white_patches_tint']:
                if event.text == "None":
                    self.white_patches_tint = None
                else:
                    self.white_patches_tint = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['reverse']:
                self.reverse = (event.text == "Yes")
                self.update_sprite()
            elif event.ui_element == self.elements['permanent conditions']:
                chosen_condition = event.text
                self.your_cat.get_permanent_condition(chosen_condition, True)
                # assign scars
                if chosen_condition in ['lost a leg', 'born without a leg']:
                    self.your_cat.pelt.scars.append('NOPAW')
                elif chosen_condition in ['lost their tail', 'born without a tail']:
                    self.your_cat.pelt.scars.append("NOTAIL")
                self.update_sprite()
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements['done']:
                game.switches['custom_cat'] = self.your_cat
                self.change_screen("make clan screen")
            
    def update_sprite(self):
        pelt2 = Pelt(
            name=self.name,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        self.your_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        self.your_cat.sprite = generate_sprite(self.your_cat)
        self.elements['sprite'].kill()
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((700,100), (200, 200))),
                                   self.your_cat.sprite,
                                   self.your_cat.ID,
                                   starting_height=0, manager=MANAGER)
        

        