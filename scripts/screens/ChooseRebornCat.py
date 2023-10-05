import os
import shutil
import threading
import time
from re import search as re_search
import platform

import pygame
import pygame_gui
from sys import exit
from re import sub
from platform import system
from random import choice
import logging
import subprocess
import random


from scripts.cat.history import History
from scripts.cat.names import Name
from pygame_gui.elements import UIWindow

from scripts.housekeeping.datadir import get_save_dir, get_cache_dir, get_saved_images_dir, get_data_dir
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, screen_x, screen_y
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.housekeeping.progress_bar_updater import UIUpdateProgressBar
from scripts.housekeeping.update import self_update, UpdateChannel, get_latest_version_number
from scripts.event_class import Single_Event
from scripts.utility import scale, quit, update_sprite, scale_dimentions, logger, process_text
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.housekeeping.version import get_version_info

class ChooseRebornCat(UIWindow):
    def __init__(self, last_screen):
        super().__init__(scale(pygame.Rect((500, 400), (750, 500))),
                         window_display_title='You have died',
                         object_id='#game_over_window',
                         resizable=False)
        self.set_blocking(True)
        game.switches['window_open'] = True
        if game.clan:
            self.clan_name = str(game.clan.name + 'Clan')
        else:
            self.clan_name = None
        self.last_screen = last_screen
        self.pick_path_message = UITextBoxTweaked(
            f"What will you do now?",
            scale(pygame.Rect((40, 40), (670, -1))),
            line_spacing=1,
            object_id="text_box_30_horizcenter",
            container=self
        )

        self.begin_anew_button = UIImageButton(
            scale(pygame.Rect((130, 190), (150, 150))),
            "",
            object_id="#random_dice_button",
            container=self,
            tool_tip_text='Start anew'
        )
        
        self.mediator_button = UIImageButton(
            scale(pygame.Rect((310, 190), (150, 150))),
            "",
            object_id="#unknown_residence_button",
            container=self,
            tool_tip_text='Be reborn'

        )
        
        self.mediator_button2 = UIImageButton(
            scale(pygame.Rect((490, 190), (150, 150))),
            "",
            object_id="#leader_ceremony_button",
            container=self,
            tool_tip_text='Revive'

        )
        

        self.begin_anew_button.enable()
        self.mediator_button.enable()
        if game.clan:
            if game.clan.your_cat.revives < 5:
                self.mediator_button2.enable()


    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.begin_anew_button:
                game.last_screen_forupdate = None
                game.switches['window_open'] = False
                game.switches['cur_screen'] = 'start screen'
                self.begin_anew_button.kill()
                self.pick_path_message.kill()
                self.mediator_button.kill()
                self.mediator_button2.kill()
                self.kill()
                game.all_screens['events screen'].exit_screen()
            elif event.ui_element == self.mediator_button:
                game.last_screen_forupdate = None
                game.switches['window_open'] = False
                game.switches['cur_screen'] = "choose reborn screen"
                self.begin_anew_button.kill()
                self.pick_path_message.kill()
                self.mediator_button.kill()
                self.mediator_button2.kill()
                self.kill()
                game.all_screens['events screen'].exit_screen()
            elif event.ui_element == self.mediator_button2:
                game.clan.your_cat.revives +=1
                game.clan.your_cat.dead = False
                game.clan.your_cat.df = False
                game.clan.your_cat.dead_for = 0
                game.clan.your_cat.moons+=1
                game.clan.add_to_clan(game.clan.your_cat)
                game.clan.your_cat.update_mentor()
                game.clan.your_cat.thought = "Is surprised to find themselves back in the Clan"
                game.last_screen_forupdate = None
                game.switches['window_open'] = False
                self.begin_anew_button.kill()
                self.pick_path_message.kill()
                self.mediator_button.kill()
                self.mediator_button2.kill()
                self.kill()