import pygame_gui

from .Screens import Screens
import pygame
from scripts.events import events_class
from scripts.utility import get_living_clan_cat_count, get_text_box_theme, scale, shorten_text_to_fit
from scripts.game_structure.image_button import IDImageButton, UIImageButton, UISpriteButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from ..cat.cats import Cat
from ..game_structure import image_cache
from scripts.event_class import Single_Event
from scripts.game_structure.windows import GameOver, PickPath, DeathScreen, EventLoading
import ujson
import random
from scripts.game_structure.propagating_thread import PropagatingThread


class EventsScreen(Screens):
    event_display_type = "all events"
    all_events = ""
    ceremony_events = ""
    birth_death_events = ""
    relation_events = ""
    health_events = ""
    other_clans_events = ""
    misc_events = ""
    display_text = ""
    display_events = ""
    
    def __init__(self, name=None):
        super().__init__(name)
        self.misc_alert = None
        self.other_clans_alert = None
        self.health_alert = None
        self.relation_alert = None
        self.birth_death_alert = None
        self.ceremony_alert = None
        self.misc_events_button = None
        self.other_clans_events_button = None
        self.health_events_button = None
        self.birth_death_events_button = None
        self.ceremonies_events_button = None
        self.all_events_button = None
        self.relationship_events_button = None
        self.events_list_box = None
        self.toggle_borders_button = None
        self.timeskip_button = None
        self.death_button = None
        self.freshkill_pile_button = None
        self.events_frame = None
        self.clan_age = None
        self.season = None
        self.heading = None
        self.display_events_elements = {}
        self.involved_cat_buttons = []
        self.cat_profile_buttons = {}
        self.scroll_height = {}
        self.CEREMONY_TXT = None
        self.start = 0
        self.loading_window = None
        self.done_moon = False
        self.events_thread = None
        self.you = None

        # Stores the involved cat button that currently has its cat profile buttons open
        self.open_involved_cat_button = None

        self.first_opened = False

    def handle_event(self, event):
        if game.switches['window_open']:
            return
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            try:
                if event.ui_element == self.ceremonies_events_button and self.ceremony_alert:
                    self.ceremony_alert.kill()
                elif event.ui_element == self.birth_death_events_button and self.birth_death_alert:
                    self.birth_death_alert.kill()
                elif event.ui_element == self.relationship_events_button and self.relation_alert:
                    self.relation_alert.kill()
                elif event.ui_element == self.health_events_button and self.health_alert:
                    self.health_alert.kill()
                elif event.ui_element == self.other_clans_events_button and self.other_clans_alert:
                    self.other_clans_alert.kill()
                elif event.ui_element == self.misc_events_button and self.misc_alert:
                    self.misc_alert.kill()
            except:
                print("too much button pressing!")
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.timeskip_button and game.clan.your_cat.dead_for >= 1 and not game.switches['continue_after_death']:
                DeathScreen('events screen')
                return
            elif self.death_button and event.ui_element == self.death_button:
                DeathScreen('events screen')
                return
            if event.ui_element == self.timeskip_button and game.clan.your_cat.moons == 5 and game.clan.your_cat.status == 'kitten' and not game.clan.your_cat.outside and not game.clan.your_cat.dead:
                PickPath('events screen')
            elif event.ui_element == self.you or ("you" in self.display_events_elements and event.ui_element == self.display_events_elements["you"]):
                game.switches['cat'] = game.clan.your_cat.ID
                self.change_screen("profile screen")
            elif event.ui_element == self.timeskip_button:
                # Save the start time, so the loading animation can be
                # set to only show up if timeskip is taking a good amount of time. 
                self.events_thread = self.loading_screen_start_work(events_class.one_moon)
            
            elif game.clan.game_mode != "classic" and event.ui_element == self.freshkill_pile_button:
                self.change_screen('clearing screen')

            # Change the type of events displayed
            elif event.ui_element == self.all_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "all events"
                self.cat_icon.hide()
                # Update Display
                self.update_list_buttons(self.all_events_button)
                self.display_events = self.all_events
                self.update_events_display()
            elif event.ui_element == self.ceremonies_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "ceremony events"
                self.ceremonies_events_button.disable()
                self.cat_icon.hide()

                # Update Display
                self.update_list_buttons(self.ceremonies_events_button, self.ceremony_alert)
                self.display_events = self.ceremony_events
                self.update_events_display()
            elif event.ui_element == self.birth_death_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "birth death events"
                self.birth_death_events_button.enable()
                self.cat_icon.hide()

                # Update Display
                self.update_list_buttons(self.birth_death_events_button, self.birth_death_alert)
                self.display_events = self.birth_death_events
                self.update_events_display()
            elif event.ui_element == self.relationship_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "relationship events"
                self.relationship_events_button.enable()
                self.cat_icon.show()
                # Update Display
                self.update_list_buttons(self.relationship_events_button, self.relation_alert)
                self.display_events = self.relation_events
                self.update_events_display()
            elif event.ui_element == self.health_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "health events"
                self.health_events_button.disable()
                self.cat_icon.hide()
                # Update Display
                self.update_list_buttons(self.health_events_button, self.health_alert)
                self.display_events = self.health_events
                self.update_events_display()
            elif event.ui_element == self.other_clans_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "other clans events"
                self.other_clans_events_button.disable()
                self.cat_icon.hide()
                # Update Display
                self.update_list_buttons(self.other_clans_events_button, self.other_clans_alert)
                self.display_events = self.other_clans_events
                self.update_events_display()
            elif event.ui_element == self.misc_events_button:
                if self.event_container.vert_scroll_bar:
                    self.scroll_height[self.event_display_type] = self.event_container.vert_scroll_bar.scroll_position / self.event_container.vert_scroll_bar.scrollable_height
                self.event_display_type = "misc events"
                self.misc_events_button.disable()
                self.cat_icon.hide()
                # Update Display
                self.update_list_buttons(self.misc_events_button, self.misc_alert)
                self.display_events = self.misc_events
                self.update_events_display()
            elif event.ui_element == self.cat_icon:
                if self.yc_pressed:
                    self.relation_events = [x for x in (game.other_events_list + game.cur_events_list) if "relation" in x.types]
                    self.display_events = self.relation_events
                    self.update_events_display()
                    self.yc_pressed = False
                else:
                    self.relation_events = [x for x in (game.cur_events_list) if "relation" in x.types]
                    for i in game.other_events_list:
                        for c in game.clan.clan_cats:
                            if Cat.all_cats.get(c).favourite:
                                if str(Cat.all_cats.get(c).name) in i.text:
                                    self.relation_events.append(i)
                                    break
                                  
                    self.display_events = self.relation_events
                    self.update_events_display()
                    self.yc_pressed = True
                
            elif event.ui_element in self.involved_cat_buttons:
                self.make_cat_buttons(event.ui_element)
            elif event.ui_element in self.cat_profile_buttons:
                game.switches['cat'] = event.ui_element.ids
                self.change_screen('profile screen')
            else:
                self.menu_button_pressed(event)
            
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_RIGHT:
                self.change_screen('camp screen')
            elif event.key == pygame.K_UP:
                if self.event_display_type == 'ceremony events':
                    self.event_display_type = "all events"
                    # Update Display
                    self.update_list_buttons(self.all_events_button)
                    self.display_events = self.all_events
                    self.update_events_display()
                elif self.event_display_type == 'birth death events':
                    self.event_display_type = "ceremony events"
                    # Update Display
                    self.update_list_buttons(self.ceremonies_events_button, self.ceremony_alert)
                    self.display_events = self.ceremony_events
                    self.update_events_display()
                elif self.event_display_type == 'relationship events':
                    self.event_display_type = "birth death events"
                    # Update Display
                    self.update_list_buttons(self.birth_death_events_button, self.birth_death_alert)
                    self.display_events = self.birth_death_events
                    self.update_events_display()
                elif self.event_display_type == 'health events':
                    self.event_display_type = "relationship events"
                    # Update Display
                    self.update_list_buttons(self.relationship_events_button, self.relation_alert)
                    self.display_events = self.relation_events
                    self.update_events_display()
                elif self.event_display_type == 'other clans events':
                    self.event_display_type = "health events"
                    # Update Display
                    self.update_list_buttons(self.health_events_button, self.health_alert)
                    self.display_events = self.health_events
                    self.update_events_display()
                elif self.event_display_type == 'misc events':
                    self.event_display_type = "other clans events"
                    # Update Display
                    self.update_list_buttons(self.other_clans_events_button, self.other_clans_alert)
                    self.display_events = self.other_clans_events
                    self.update_events_display()
            elif event.key == pygame.K_DOWN:
                if self.event_display_type == 'all events':
                    self.event_display_type = "ceremony events"
                    # Update Display
                    self.update_list_buttons(self.ceremonies_events_button, self.ceremony_alert)
                    self.display_events = self.ceremony_events
                    self.update_events_display()
                elif self.event_display_type == 'ceremony events':
                    self.event_display_type = "birth death events"
                    # Update Display
                    self.update_list_buttons(self.birth_death_events_button, self.birth_death_alert)
                    self.display_events = self.birth_death_events
                    self.update_events_display()
                elif self.event_display_type == 'birth death events':
                    self.event_display_type = "relationship events"
                    # Update Display
                    self.update_list_buttons(self.relationship_events_button, self.relation_alert)
                    self.display_events = self.relation_events
                    self.update_events_display()
                elif self.event_display_type == 'relationship events':
                    self.event_display_type = "health events"
                    # Update Display
                    self.update_list_buttons(self.health_events_button, self.health_alert)
                    self.display_events = self.health_events
                    self.update_events_display()
                elif self.event_display_type == 'health events':
                    self.event_display_type = "other clans events"
                    # Update Display
                    self.update_list_buttons(self.other_clans_events_button, self.other_clans_alert)
                    self.display_events = self.other_clans_events
                    self.update_events_display()
                elif self.event_display_type == 'other clans events':
                    self.event_display_type = "misc events"
                    # Update Display
                    self.update_list_buttons(self.misc_events_button, self.misc_alert)
                    self.display_events = self.misc_events
                    self.update_events_display()
            elif event.key == pygame.K_SPACE:
                if game.clan.your_cat.moons == 5 and game.clan.your_cat.status == 'kitten' and not game.clan.your_cat.outside and not game.clan.your_cat.dead:
                    PickPath('events screen')
                elif (game.clan.your_cat.dead_for == 1 or game.clan.your_cat.exiled):
                    DeathScreen('events screen')
                    return
                self.events_thread = self.loading_screen_start_work(events_class.one_moon)

    def screen_switches(self):
        # On first open, update display events list
        self.update_display_events_lists()

        if game.clan.game_mode != "classic":
            self.freshkill_pile_button =  UIImageButton(scale(pygame.Rect((1270, 210), (282, 60))), "", object_id="#freshkill_pile_button"
                                             , manager=MANAGER)

        self.season = pygame_gui.elements.UITextBox(f'Season: {game.clan.current_season} - Clan Age: {game.clan.age} moons',
                                                    scale(pygame.Rect((600, 220), (400, 80))),
                                                    object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                    manager=MANAGER)
        self.clan_age = pygame_gui.elements.UITextBox("",
                                                      scale(pygame.Rect((600, 280), (400, 80))),
                                                      object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                      manager=MANAGER)
        self.leaf = pygame_gui.elements.UITextBox("leafbare",
                                                      scale(pygame.Rect((400, 340), (800, 80))),
                                                      object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                      manager=MANAGER)
 
        self.events_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((412, 532), (1068, 740))),
                                                        image_cache.load_image(
                                                            "resources/images/event_page_frame.png").convert_alpha()
                                                        , manager=MANAGER)
        self.events_frame.disable()
        self.yc_pressed = True
        if not game.clan.your_cat:
            print("Are you playing a normal ClanGen save? Switch to a LifeGen save or create a new cat!")
            print("Choosing random cat to play...")
            game.clan.your_cat = Cat.all_cats[random.choice(game.clan.clan_cats)]
            counter = 0
            while game.clan.your_cat.dead or game.clan.your_cat.outside:
                if counter == 25:
                    break
                game.clan.your_cat = Cat.all_cats[random.choice(game.clan.clan_cats)]
                counter+=1
                
            print("Chose " + str(game.clan.your_cat.name))
        # Set text for clan age
        if game.clan.your_cat.moons == -1:
            self.clan_age.set_text(f'Your age: Unborn')
        elif game.clan.your_cat.moons != 1:
            self.clan_age.set_text(f'Your age: {game.clan.your_cat.moons} moons')
        elif game.clan.your_cat.moons == 1:
            self.clan_age.set_text(f'Your age: {game.clan.your_cat.moons} moon')


        self.timeskip_button = UIImageButton(scale(pygame.Rect((620, 436), (360, 60))), "", object_id="#timeskip_button"
                                             , manager=MANAGER)

        self.death_button = UIImageButton(scale(pygame.Rect((1020, 430), (68, 68))), "", object_id="#warrior", tool_tip_text="Revive"
                                             , manager=MANAGER)
        self.death_button.hide()

        if game.switches['continue_after_death']:
            self.death_button.show()

        # Sets up the buttons to switch between the event types.
        self.all_events_button = UIImageButton(
            scale(pygame.Rect((120, 570), (300, 60))),
            "",
            object_id="#all_events_button", manager=MANAGER)
        self.ceremonies_events_button = UIImageButton(
            scale(pygame.Rect((120, 672), (300, 60))),
            "",
            object_id="#ceremony_events_button", manager=MANAGER)
        self.birth_death_events_button = UIImageButton(
            scale(pygame.Rect((120, 772), (300, 60))),
            "",
            object_id="#birth_death_events_button", manager=MANAGER)
        self.relationship_events_button = UIImageButton(
            scale(pygame.Rect((120, 872), (300, 60))),
            "",
            object_id="#relationship_events_button")
        self.cat_icon = UIImageButton(
            scale(pygame.Rect((75, 875), (50, 50))),
            "",
            tool_tip_text="Show your cat/favorited cat relationship events",
            object_id="#events_cat_button")
        self.cat_icon.hide()
        self.health_events_button = UIImageButton(
            scale(pygame.Rect((120, 972), (300, 60))),
            "",
            object_id="#health_events_button", manager=MANAGER)
        self.other_clans_events_button = UIImageButton(
            scale(pygame.Rect((120, 1072), (300, 60))),
            "",
            object_id="#other_clans_events_button", manager=MANAGER)
        self.misc_events_button = UIImageButton(
            scale(pygame.Rect((120, 1172), (300, 60))),
            "",
            object_id="#misc_events_button", manager=MANAGER)

        if self.event_display_type == "all events":
            self.all_events_button.disable()
        elif self.event_display_type == "ceremony events":
            self.ceremonies_events_button.disable()
        elif self.event_display_type == "birth death events":
            self.birth_death_events_button.disable()
        elif self.event_display_type == "relationship events":
            self.relationship_events_button.disable()
            self.cat_icon.show()
        elif self.event_display_type == "health events":
            self.health_events_button.disable()
        elif self.event_display_type == "other clans events":
            self.other_clans_events_button.disable()
        elif self.event_display_type == "misc events":
            self.misc_events_button.disable()

        self.misc_alert = None
        self.other_clans_alert = None
        self.health_alert = None
        self.relation_alert = None
        self.birth_death_alert = None
        self.ceremony_alert = None

        self.open_involved_cat_button = None
        self.make_events_container()
        self.events_container_y = self.event_container.get_relative_rect()[3]

        # Display text
        # self.explain_text = pygame_gui.elements.UITextBox(self.display_text, scale(pygame.Rect((25,110),(750,40))))

        # Draw and disable the correct menu buttons.
        self.set_disabled_menu_buttons(["events_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()
        self.update_events_display()

    def exit_screen(self):
        self.open_involved_cat_button = None

        self.timeskip_button.kill()
        del self.timeskip_button
        if self.death_button:
            self.death_button.kill()
        if game.clan.game_mode != "classic":
            self.freshkill_pile_button.kill()
            del self.freshkill_pile_button
        self.all_events_button.kill()
        del self.all_events_button
        self.ceremonies_events_button.kill()
        del self.ceremonies_events_button
        if self.ceremony_alert:
            self.ceremony_alert.kill()
            del self.ceremony_alert
        self.birth_death_events_button.kill()
        del self.birth_death_events_button
        if self.birth_death_alert:
            self.birth_death_alert.kill()
            del self.birth_death_alert
        self.relationship_events_button.kill()
        del self.relationship_events_button
        if self.relation_alert:
            self.relation_alert.kill()
            del self.relation_alert
        self.health_events_button.kill()
        del self.health_events_button
        if self.health_alert:
            self.health_alert.kill()
            del self.health_alert
        self.other_clans_events_button.kill()
        del self.other_clans_events_button
        if self.other_clans_alert:
            self.other_clans_alert.kill()
            del self.other_clans_alert
        self.misc_events_button.kill()
        del self.misc_events_button
        if self.misc_alert:
            self.misc_alert.kill()
            del self.misc_alert
        self.events_frame.kill()
        del self.events_frame
        self.clan_age.kill()
        del self.clan_age
        self.season.kill()
        del self.season
        self.leaf.kill()
        del self.leaf
        self.event_container.kill()
        self.cat_icon.kill()
        del self.cat_icon
        if self.you:
            self.you.kill()
        for ele in self.display_events_elements:
            self.display_events_elements[ele].kill()
        self.display_events_elements = {}

        for ele in self.involved_cat_buttons:
            ele.kill()
        self.involved_cat_buttons = []

        for ele in self.cat_profile_buttons:
            ele.kill()
        self.cat_profile_buttons = []

        # self.hide_menu_buttons()

    def on_use(self):
        
        self.loading_screen_on_use(self.events_thread, self.timeskip_done)
            
    def timeskip_done(self):
        """Various sorting and other tasks that must be done with the timeskip is over. """
        
        self.scroll_height = {}
        if get_living_clan_cat_count(Cat) == 0:
            GameOver('events screen')
        
        if self.event_display_type != 'relationship events':
            self.cat_icon.hide()

        self.update_display_events_lists()

        self.ceremonies_events_button.enable()
        if self.ceremony_alert:
            self.ceremony_alert.kill()
        if self.ceremony_events:
            self.ceremony_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 680), (8, 44))),
                                                                pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/alert_mark.png"
                                                                ), (8, 44)), manager=MANAGER)

        if self.birth_death_alert:
            self.birth_death_alert.kill()
        self.birth_death_events_button.enable()
        if self.birth_death_events:
            self.birth_death_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 780), (8, 44))),
                                                                    pygame.transform.scale(
                                                                    image_cache.load_image(
                                                                        "resources/images/alert_mark.png"
                                                                    ), (8, 44)), manager=MANAGER)

        if self.relation_alert:
            self.relation_alert.kill()
        self.relationship_events_button.enable()
        if self.relation_events:
            self.relation_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 880), (8, 44))),
                                                                pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/alert_mark.png"
                                                                ), (8, 44)), manager=MANAGER)

        if self.health_alert:
            self.health_alert.kill()
        self.health_events_button.enable()
        self.health_events = [x for x in game.other_events_list if "health" in x.types]
        if self.health_events:
            self.health_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 980), (8, 44))),
                                                            pygame.transform.scale(
                                                            image_cache.load_image(
                                                                "resources/images/alert_mark.png"
                                                            ), (8, 44)), manager=MANAGER)

        if self.other_clans_alert:
            self.other_clans_alert.kill()
        self.other_clans_events_button.enable()
        if self.other_clans_events:
            self.other_clans_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 1080), (8, 44))),
                                                                    pygame.transform.scale(
                                                                    image_cache.load_image(
                                                                        "resources/images/alert_mark.png"
                                                                    ), (8, 44)), manager=MANAGER)

        if self.misc_alert:
            self.misc_alert.kill()
        self.misc_events_button.enable()
        if self.misc_events:
            self.misc_alert = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 1180), (8, 44))),
                                                            pygame.transform.scale(
                                                            image_cache.load_image(
                                                                "resources/images/alert_mark.png"
                                                            ), (8, 44)), manager=MANAGER)

        if self.event_display_type == "all events":
            # if events list is empty, add a single message the says nothing interesting happened
            if not self.all_events:
                self.all_events.append(Single_Event("Nothing interesting happened this moon."))
            self.display_events = self.all_events
            self.update_list_buttons(self.all_events_button)
        elif self.event_display_type == "ceremony events":
            self.display_events = self.ceremony_events
            self.update_list_buttons(self.ceremonies_events_button)
        elif self.event_display_type == "birth death events":
            self.display_events = self.birth_death_events
            self.update_list_buttons(self.birth_death_events_button)
        elif self.event_display_type == "relationship events":
            self.display_events = self.relation_events
            self.update_list_buttons(self.relationship_events_button)
        elif self.event_display_type == "health events":
            self.display_events = self.health_events
            self.update_list_buttons(self.health_events_button)
        elif self.event_display_type == "other clans events":
            self.display_events = self.other_clans_events
            self.update_list_buttons(self.other_clans_events_button)
        elif self.event_display_type == "misc events":
            self.display_events = self.misc_events
            self.update_list_buttons(self.misc_events_button)

        self.update_events_display()
        self.show_menu_buttons()
        
    def update_list_buttons(self, current_list, current_alert=None):
        """ handles the disabling and enabling of the list buttons """

        # enable all the buttons
        self.all_events_button.enable()
        self.ceremonies_events_button.enable()
        self.birth_death_events_button.enable()
        self.relationship_events_button.enable()
        self.health_events_button.enable()
        self.other_clans_events_button.enable()
        self.misc_events_button.enable()

        # disable the current button
        current_list.disable()
        if current_alert:
            current_alert.kill()

    def update_events_display(self):
        
        self.leaf.set_text(f'Season: {game.clan.current_season} - Clan Age: {game.clan.age}')
        self.season.set_text(str(game.clan.your_cat.name))
        if game.clan.your_cat.moons == -1:
            self.clan_age.set_text(f'Your age: Unborn')
        elif game.clan.your_cat.moons != 1:
            self.clan_age.set_text(f'Your age: {game.clan.your_cat.moons} moons')
        elif game.clan.your_cat.moons == 1:
            self.clan_age.set_text(f'Your age: {game.clan.your_cat.moons} moon')

        for ele in self.display_events_elements:
            self.display_events_elements[ele].kill()
        if self.you:
            self.you.kill()
    
        for ele in self.involved_cat_buttons:
            ele.kill()
        self.involved_cat_buttons = []

        for ele in self.cat_profile_buttons:
            ele.kill()
        self.cat_profile_buttons = []

        if game.switches['continue_after_death'] and game.clan.your_cat.moons >= 0:
            self.death_button.show()
        else:
            self.death_button.hide()

        # In order to set-set the scroll-bar postion, we have to remake the scrolling container
        self.event_container.kill()
        self.make_events_container()

        # Stop if Clan is new, so that events from previously loaded Clan don't show up
        if game.clan.age == 0:
            return

        # Make display, with buttons and all that.
        box_length = self.event_container.get_relative_rect()[2]
        i = 0
        y = 0
        padding = 70/1400 * screen_y
        button_size = 68/1600 * screen_x
        button_padding = 80/1400 * screen_x
        for ev in self.display_events:
            if isinstance(ev.text, str):  # Check to make sure text is a string.
                self.display_events_elements["event" + str(i)] = pygame_gui.elements.UITextBox(ev.text,
                                                                                               pygame.Rect((0, y), (box_length - 20, -1)),
                                                                                               object_id=get_text_box_theme("#text_box_30_horizleft"),
                                                                                               container=self.event_container,
                                                                                               starting_height=2,
                                                                                               manager=MANAGER)
                self.display_events_elements["event" + str(i)].disable()
                # Find the next y-height by finding the height of the text box, and adding 35 for the cats button

                if i % 2 == 0:
                    if game.settings["dark mode"]:
                        self.display_events_elements["shading" + str(i)] = pygame_gui.elements.UIImage(
                            pygame.Rect((0, y), (box_length + 100, self.display_events_elements["event" + str(i)].get_relative_rect()[3] + padding)),
                            image_cache.load_image("resources/images/shading_dark.png"), container=self.event_container,
                            manager=MANAGER)
                    else:
                        self.display_events_elements["shading" + str(i)] = pygame_gui.elements.UIImage(
                            pygame.Rect((0, y),
                                        (box_length + 100,
                                         self.display_events_elements["event" + str(i)].get_relative_rect()[3] + padding)),
                            image_cache.load_image("resources/images/shading.png"), container=self.event_container
                            , manager=MANAGER)

                    self.display_events_elements["shading" + str(i)].disable()

                y += self.display_events_elements["event" + str(i)].get_relative_rect()[3]

                self.involved_cat_buttons.append(IDImageButton(pygame.Rect(
                    (self.event_container.get_relative_rect()[2] - button_padding, y - 10), (button_size, button_size)),
                    ids=ev.cats_involved, container=self.event_container, layer_starting_height=2,
                    object_id="#events_cat_button", manager=MANAGER))

                y += 68/1600 * screen_y
                i += 1
            else:
                print("Incorrectly formatted event:", ev.text, type(ev))

        # Set scrolling container length
        # This is a hack-y solution, but it was the easiest way to have the shading go all the way across the box
        self.event_container.set_scrollable_area_dimensions((box_length, y + 15))

        if self.event_container.vert_scroll_bar:
            for ele in self.involved_cat_buttons:
                ele.set_relative_position((ele.get_relative_rect()[0] - 20, ele.get_relative_rect()[1]))

        if self.event_container.horiz_scroll_bar:
            self.event_container.set_dimensions((box_length, self.events_container_y + 20))
            self.event_container.horiz_scroll_bar.hide()
        else:
            self.event_container.set_dimensions((box_length, self.events_container_y))
        # Set the scroll bar to the last position it was at
        if self.event_container.vert_scroll_bar and self.scroll_height.get(self.event_display_type):
            self.event_container.vert_scroll_bar.set_scroll_from_start_percentage(self.scroll_height[self.event_display_type])
        if self.you:
            self.you.kill()
        if game.clan.your_cat.moons != -1:
            self.you = UISpriteButton(scale(pygame.Rect((1050, 200), (200, 200))),
                                   game.clan.your_cat.sprite,
                                   cat_object=game.clan.your_cat,
                                   manager=MANAGER)
            
    def make_cat_buttons(self, button_pressed):
        """ Makes the buttons that take you to the profile. """

        # Check if the button you pressed doesn't have it cat profile buttons currently displayed.
        # If it doesn't have it's buttons displayed, set the current open involved_cat_button to the pressed button,
        # clear all other buttons, and open the cat profile buttons.
        if self.open_involved_cat_button != button_pressed:
            self.open_involved_cat_button = button_pressed
            for ele in self.cat_profile_buttons:
                ele.kill()
            self.cat_profile_buttons = []

            pressed_button_pos = (button_pressed.get_relative_rect()[0], button_pressed.get_relative_rect()[1])

            i = 1
            for ev in button_pressed.ids:
                cat_ob = Cat.fetch_cat(ev)
                if cat_ob:
                    # Shorten name if needed
                    name = str(cat_ob.name)
                    short_name = shorten_text_to_fit(name, 195, 26)

                    self.cat_profile_buttons.append(
                        IDImageButton(pygame.Rect((pressed_button_pos[0] - (240/1600 * screen_x * i) - 1,
                                                   pressed_button_pos[1] + 4),
                                                   (232/1600 * screen_x, 60/1400 * screen_y)),
                                      text=short_name, ids=ev, container=self.event_container,
                                      object_id="#events_cat_profile_button", layer_starting_height=2, 
                                      manager=MANAGER))
                    # There is only room for about four buttons.
                    if i > 3:
                        break
                    i += 1

        # If the button pressed does have its cat profile buttons open, just close the buttons.
        else:
            self.open_involved_cat_button = None
            for ele in self.cat_profile_buttons:
                ele.kill()
            self.cat_profile_buttons = []

    def update_display_events_lists(self):
        """
        Categorize events from game.cur_events_list into display categories for screen
        """
        
        self.all_events = [x for x in game.cur_events_list if "interaction" not in x.types]
        self.ceremony_events = [x for x in (game.other_events_list + game.cur_events_list) if "ceremony" in x.types]
        self.birth_death_events = [x for x in (game.other_events_list + game.cur_events_list) if "birth_death" in x.types]
        self.relation_events = [x for x in (game.other_events_list + game.cur_events_list) if "relation" in x.types]
        self.health_events = [x for x in (game.other_events_list + game.cur_events_list) if "health" in x.types]
        self.other_clans_events = [x for x in (game.other_events_list + game.cur_events_list) if "other_clans" in x.types]
        self.misc_events = [x for x in (game.other_events_list + game.cur_events_list) if "misc" in x.types]

        if self.event_display_type == "all events":
            self.display_events = self.all_events
        elif self.event_display_type == "ceremony events":
            self.display_events = self.ceremony_events
        elif self.event_display_type == "birth death events":
            self.display_events = self.birth_death_events
        elif self.event_display_type == "relationship events":
            self.display_events = self.relation_events
        elif self.event_display_type == "health events":
            self.display_events = self.health_events
        elif self.event_display_type == "other clans events":
            self.display_events = self.other_clans_events
        elif self.event_display_type == "misc events":
            self.display_events = self.misc_events


    def make_events_container(self):
        """ In its own function so that there is only one place the box size is set"""
        self.event_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((432, 552), (1028, 700)))
                                                                        , manager=MANAGER)
