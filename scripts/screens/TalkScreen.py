from random import choice, choices, randint
import pygame
import ujson

from scripts.utility import scale

from .Screens import Screens

from scripts.utility import generate_sprite, get_cluster, get_alive_kits, get_alive_cats, get_alive_apps, get_alive_meds, get_alive_mediators, get_alive_queens, get_alive_elders, get_alive_warriors
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
import pygame_gui
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER, screen
from enum import Enum  # pylint: disable=no-name-in-module

class RelationType(Enum):
    """An enum representing the possible age groups of a cat"""

    BLOOD = ''                      # direct blood related - do not need a special print
    ADOPTIVE = 'adoptive'       	# not blood related but close (parents, kits, siblings)
    HALF_BLOOD = 'half sibling'   	# only one blood parent is the same (siblings only)
    NOT_BLOOD = 'not blood related'	# not blood related for parent siblings
    RELATED = 'blood related'   	# related by blood (different mates only)

BLOOD_RELATIVE_TYPES = [RelationType.BLOOD, RelationType.HALF_BLOOD, RelationType.RELATED]

class TalkScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None
        self.possible_texts = {}
        self.chosen_text_key = ""
        self.choice_buttons = {}
        self.text_choices = {}
        self.option_bgs = {}
        self.current_scene = ""
        self.created_choice_buttons = False
        self.choicepanel = False
        self.textbox_graphic = None



    def screen_switches(self):
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.choicepanel = False
        self.created_choice_buttons = False
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((230, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                       scale(pygame.Rect((300, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)

        self.text_type = ""
        self.texts = self.load_texts(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )

        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("",
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container,
                                                manager=MANAGER)

        self.textbox_graphic = pygame_gui.elements.UIImage(
                scale(pygame.Rect((170, 942), (346, 302))),
                image_cache.load_image("resources/images/textbox_graphic.png").convert_alpha()
            )
        # self.textbox_graphic.hide()

        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),
                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.textbox_graphic.kill()
        del self.textbox_graphic
        self.paw.kill()
        del self.paw
        for button in self.choice_buttons:
            self.choice_buttons[button].kill()
        self.choice_buttons = {}
        for option in self.text_choices:
            self.text_choices[option].kill()
        self.text_choices = {}
        for option_bg in self.option_bgs:
            self.option_bgs[option_bg].kill()
        self.option_bgs = {}

    def update_camp_bg(self):
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        camp_bg_base_dir = 'resources/images/camp_bg/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = 'camp1'
            game.clan.camp_bg = camp_nr

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:

            platform_dir = ""
            if self.the_cat.dead and not self.the_cat.df:
                platform_dir = "resources/images/starclanbg.png"
            elif self.the_cat.dead and self.the_cat.df:
                platform_dir = "resources/images/darkforestbg.png"
            else:
                platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))

    def on_use(self):
        if game.clan.clan_settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))
        now = pygame.time.get_ticks()
        if self.texts:
            if self.texts[self.text_index][0] == "[" and self.texts[self.text_index][-1] == "]":
                self.profile_elements["cat_image"].hide()
                # self.textbox_graphic.show()
            else:
                self.profile_elements["cat_image"].show()
                # self.textbox_graphic.hide()

        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay
        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                if self.text_type != "choices":
                    self.paw.visible = True
                if not self.created_choice_buttons and self.text_type == "choices":
                    self.create_choice_buttons()
                    self.created_choice_buttons = True


        # Always render the current frame
        if self.text_frames:
            self.text.html_text = self.text_frames[self.text_index][self.frame_index]

        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
            else:
                for key, button in self.choice_buttons.items():
                    if event.ui_element == button and self.chosen_text_key:
                        self.current_scene = self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"][key]["next_scene"]
                        self.handle_choice(self.the_cat)
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_frames:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
            
        return

    def get_cluster_list(self):
        return ["assertive", "brooding", "cool", "upstanding", "introspective", "neurotic", "silly", "stable", "sweet", "unabashed", "unlawful"]

    def get_cluster_list_you(self):
        return ["you_assertive", "you_brooding", "you_cool", "you_upstanding", "you_introspective", "you_neurotic", "you_silly", "you_stable", "you_sweet", "you_unabashed", "you_unlawful"]


    def relationship_check(self, talk, cat_relationship):
        relationship_conditions = {
            'hate': 50,
            'romantic_like': 30,
            'platonic_like': 30,
            'jealousy': 30,
            'dislike': 30,
            'comfort': 30,
            'respect': 30,
            'trust': 30
        }
        tags = talk["intro"] if "intro" in talk else talk[0]
        for key, value in relationship_conditions.items():
            if key in tags and cat_relationship < value:
                return True
        return False

    def handle_random_cat(self, cat):
        random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        counter = 0
        while random_cat.outside or random_cat.dead or random_cat.ID in [game.clan.your_cat.ID, cat.ID]:
            counter += 1
            if counter == 15:
                break
            random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        return random_cat

    def display_intro(self, cat, texts_list, texts_chosen_key):
        chosen_text_intro = texts_list[texts_chosen_key]["intro"]
        chosen_text_intro = self.get_adjusted_txt(chosen_text_intro, cat)
        self.current_scene = "intro"
        self.possible_texts = texts_list
        self.chosen_text_key = texts_chosen_key
        return chosen_text_intro

    def create_choice_buttons(self):


        y_pos = 0
        if f"{self.current_scene}_choices" not in self.possible_texts[self.chosen_text_key]:
            self.paw.visible = True

            return
        for c in self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"]:
            text = self.possible_texts[self.chosen_text_key][f"{self.current_scene}_choices"][c]['text']
            text = self.get_adjusted_txt([text], self.the_cat)
            text = text[0]

            #the background image for the text
            option_bg = pygame_gui.elements.UIImage(scale(pygame.Rect((860, 855 + y_pos), (540, 70))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/option_bg.png").convert_alpha(),
                                                                (540, 60)), manager=MANAGER)
            self.option_bgs[c] = option_bg

            #the button for dialogue choices
            button = UIImageButton(scale(pygame.Rect((780, 855 + y_pos), (68, 68))),
                                        text = "",
                                        object_id="#dialogue_choice_button", manager=MANAGER)
            self.choice_buttons[c] = button


            #the text for dialogue choices
            option = pygame_gui.elements.UITextBox(str(text),
                                                            scale(pygame.Rect((870, 860 + y_pos), (540, 60))),
                                                            object_id="#text_box_30_horizleft",
                                                            manager=MANAGER)
            self.text_choices[c] = option

            y_pos -= 80

    def handle_choice(self, cat):
        for b in self.choice_buttons:
            self.choice_buttons[b].kill()
        for b in self.text_choices:
            self.text_choices[b].kill()
        for b in self.option_bgs:
            self.option_bgs[b].kill()

        self.choice_buttons = {}
        chosen_text = self.possible_texts[self.chosen_text_key][self.current_scene]
        chosen_text2 = self.get_adjusted_txt(chosen_text, cat)
        self.texts = chosen_text2
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in chosen_text2]
        self.text_index = 0
        self.frame_index = 0
        self.created_choice_buttons = False


    def load_texts(self, cat):
        you = game.clan.your_cat
        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = {}

        if cat.status not in ['loner', 'rogue', 'former Clancat', 'kittypet', 'exiled']:
            with open(f"{resource_dir}{cat.status}.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())

        with open(f"{resource_dir}choice_dialogue.json", 'r') as read_file:
            possible_texts.update(ujson.loads(read_file.read()))

        if cat.status not in ['kitten', "newborn"] and you.status not in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_no_kit.json", 'r') as read_file:
                possible_texts2 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts2)

        if cat.status not in ['kitten', "newborn"] and you.status in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_you_kit.json", 'r') as read_file:
                possible_texts3 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts3)

        if cat.status not in ['kitten', 'newborn'] and you.status not in ['kitten', 'newborn'] and randint(1,3)==1:
            with open(f"{resource_dir}crush.json", 'r') as read_file:
                possible_texts3 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts3)

        return self.filter_texts(cat, possible_texts)


    def filter_texts(self, cat, possible_texts):
        text = ""
        texts_list = {}
        you = game.clan.your_cat

        cluster1, cluster2 = get_cluster(cat.personality.trait)
        cluster3, cluster4 = get_cluster(you.personality.trait)

        their_trait_list = ['troublesome', 'fierce', 'bold', 'daring', 'confident', 'adventurous', 'arrogant', 'competitive', 'rebellious', 'bloodthirsty', 'cold', 'strict', 'vengeful', 'grumpy', 'charismatic', 'sneaky', 'cunning', 'arrogant', 'righteous', 'ambitious', 'strict', 'competitive', 'responsible', 'lonesome', 'righteous', 'calm', 'gloomy', 'wise', 'thoughtful', 'nervous', 'insecure', 'lonesome', 'troublesome', 'childish', 'playful', 'strange', 'loyal', 'responsible', 'wise', 'faithful', 'compassionate', 'faithful', 'loving', 'oblivious', 'sincere', 'childish', 'confident', 'bold', 'shameless', 'strange', 'oblivious', 'flamboyant', 'troublesome', 'bloodthirsty', 'sneaky', 'rebellious']
        you_trait_list = ['you_troublesome', 'you_fierce', 'you_bold', 'you_daring', 'you_confident', 'you_adventurous', 'you_arrogant', 'you_competitive', 'you_rebellious', 'you_bloodthirsty', 'you_cold', 'you_strict', 'you_vengeful', 'you_grumpy', 'you_charismatic', 'you_sneaky', 'you_cunning', 'you_arrogant', 'you_righteous', 'you_ambitious', 'you_strict', 'you_competitive', 'you_responsible', 'you_lonesome', 'you_righteous', 'you_calm', 'you_gloomy', 'you_wise', 'you_thoughtful', 'you_nervous', 'you_insecure', 'you_lonesome', 'you_troublesome', 'you_childish', 'you_playful', 'you_strange', 'you_loyal', 'you_responsible', 'you_wise', 'you_faithful', 'you_compassionate', 'you_faithful', 'you_loving', 'you_oblivious', 'you_sincere', 'you_childish', 'you_confident', 'you_bold', 'you_shameless', 'you_strange', 'you_oblivious', 'you_flamboyant', 'you_troublesome', 'you_bloodthirsty', 'you_sneaky', 'you_rebellious']
        you_backstory_list = [
            "you_clanfounder",
            "you_clanborn",
            "you_outsiderroots",
            "you_half-Clan",
            "you_formerlyloner",
            "you_formerlyrogue",
            "you_formerlykittypet",
            "you_formerlyoutsider",
            "you_originallyanotherclan",
            "you_orphaned",
            "you_abandoned"
        ]
        they_backstory_list = ["they_clanfounder",
            "they_clanborn",
            "they_outsiderroots",
            "they_half-Clan",
            "they_formerlyloner",
            "they_formerlyrogue",
            "they_formerlykittypet",
            "they_formerlyoutsider",
            "they_originallyanotherclan",
            "they_orphaned",
            "they_abandoned"
        ]
        skill_list = ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator1', 'clever', 'insightful', 'sense', 'kit', 'story', 'lore', 'camp', 'healer', 'star', 'omen', 'dream', 'clairvoyant', 'prophet', 'ghost', 'explorer', 'tracker', 'artistan', 'guardian', 'tunneler', 'navigator', 'song', 'grace', 'clean', 'innovator', 'comforter', 'matchmaker', 'thinker', 'cooperative', 'scholar', 'time', 'treasure', 'fisher', 'language', 'sleeper']
        you_skill_list = ['you_teacher', 'you_hunter', 'you_fighter', 'you_runner', 'you_climber', 'you_swimmer', 'you_speaker', 'you_mediator1', 'you_clever', 'you_insightful', 'you_sense', 'you_kit', 'you_story', 'you_lore', 'you_camp', 'you_healer', 'you_star', 'you_omen', 'you_dream', 'you_clairvoyant', 'you_prophet', 'you_ghost', 'you_explorer', 'you_tracker', 'you_artistan', 'you_guardian', 'you_tunneler', 'you_navigator', 'you_song', 'you_grace', 'you_clean', 'you_innovator', 'you_comforter', 'you_matchmaker', 'you_thinker', 'you_cooperative', 'you_scholar', 'you_time', 'you_treasure', 'you_fisher', 'you_language', 'you_sleeper']
        for talk_key, talk in possible_texts.items():
            tags = talk["tags"] if "tags" in talk else talk[0]
            for i in range(len(tags)):
                tags[i] = tags[i].lower()

            if "insult" in tags:
                continue

            if "notyet" in tags:
                continue

            # bc i dont wanna remove my deaf dialogue rn lol

            if you.moons == 0 and "newborn" not in tags:
                continue

            # if "deaf" in cat.permanent_condition and "they_deaf" not in tags:
            #     continue

            # if "blind" in cat.permanent_condition and "they_blind" not in tags:
            #     continue

            # if "deaf" in you.permanent_condition and "you_deaf" not in tags:
            #     continue

            # if "blind" in you.permanent_condition and "you_blind" not in tags:
            #     continue

            # Status tags
            if you.status not in tags and "any" not in tags and "young elder" not in tags and "no_kit" not in tags and "newborn" not in tags:
                continue
            elif "young elder" in tags and cat.status == 'elder' and cat.moons >= 100:
                continue
            elif "no_kit" in tags and (you.status in ['kitten', 'newborn'] or cat.status in ['kitten', 'newborn']):
                continue
            elif "newborn" in tags and "kitten" not in tags and you.moons != 0:
                continue

            if "they_adult" in tags and cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice", "kitten", "newborn"]:
                continue
            if "they_app" in tags and cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                continue
            
            if not any(t in tags for t in ["they_sc", "they_df"]) and cat.dead:
                continue
            if not any(t in tags for t in ["you_sc", "you_df"]) and you.dead:
                continue

            if any(t in tags for t in ["they_sc", "they_df"]) and not cat.dead:
                continue
            if any(t in tags for t in ["you_sc", "you_df"]) and not you.dead:
                continue

            if "they_df" in tags and not cat.df:
                continue
            if "you_df" in tags and not you.df:
                continue
            if "they_sc" in tags and cat.df:
                continue
            if "you_sc" in tags and you.df:
                continue

            if "grief stricken" in cat.illnesses:
                dead_cat = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                if "grievingyou" in tags:
                    if dead_cat.name != game.clan.your_cat.name:
                        continue
                else:
                    if dead_cat.name == game.clan.your_cat.name:
                        continue

            if "grief stricken" in you.illnesses:
                dead_cat = Cat.all_cats.get(you.illnesses['grief stricken'].get("grief_cat"))
                if "grievingthem" in tags:
                    if dead_cat.name == cat.name:
                        print ('You are grieving the death of this cat.')
                        
                    if dead_cat.name != cat.name:
                        continue
                else:
                    if dead_cat.name == cat.name:
                        continue

            roles = ["they_kitten", "they_apprentice", "they_medicine_cat_apprentice", "they_mediator_apprentice", "they_queen's_apprentice", "they_warrior", "they_mediator", "they_medicine_cat", "they_queen", "they_deputy", "they_leader", "they_elder", "they_newborn"]
            if any(r in roles for r in tags):
                has_role = False
                if "they_kitten" in tags and cat.status == "kitten":
                    has_role = True
                elif "they_apprentice" in tags and cat.status == "apprentice":
                    has_role = True
                elif "they_medicine_cat_apprentice" in tags and cat.status == "medicine cat apprentice":
                    has_role = True
                elif "they_mediator_apprentice" in tags and cat.status == "mediator apprentice":
                    has_role = True
                elif "they_queen's_apprentice" in tags and cat.status == "queen's apprentice":
                    has_role = True
                elif "they_warrior" in tags and cat.status == "warrior":
                    has_role = True
                elif "they_mediator" in tags and cat.status == "mediator":
                    has_role = True
                elif "they_medicine_cat" in tags and cat.status == "medicine cat":
                    has_role = True
                elif "they_queen" in tags and cat.status == "queen":
                    has_role = True
                elif "they_deputy" in tags and cat.status == "deputy":
                    has_role = True
                elif "they_leader" in tags and cat.status == "leader":
                    has_role = True
                elif "they_elder" in tags and cat.status == "elder":
                    has_role = True
                elif "they_newborn" in tags and cat.status == "newborn":
                    has_role = True
                if not has_role:
                    continue

            if "they_grieving" not in tags and "grief stricken" in cat.illnesses and not cat.dead:
                continue
            if "they_grieving" in tags and "grief stricken" not in cat.illnesses and not cat.dead:
                continue

            # Cluster tags
            if any(i in self.get_cluster_list() for i in tags):
                if cluster1 not in tags and cluster2 not in tags:
                    continue
            if any(i in self.get_cluster_list_you() for i in tags):
                if ("you_"+cluster3) not in tags and ("you_"+cluster4) not in tags:
                    continue

            # Trait tags
            if any(i in you_trait_list for i in tags):
                ts = you_trait_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.personality.trait not in ts:
                    continue
            if any(i in their_trait_list for i in tags):
                if cat.personality.trait not in tags:
                    continue

            # Backstory tags
            if any(i in you_backstory_list for i in tags):
                ts = you_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.backstory not in ts:
                    continue
            if any(i in they_backstory_list for i in tags):
                ts = they_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][4:]
                if cat.backstory not in ts:
                    continue

            # Skill tags
            if any(i in you_skill_list for i in tags):
                ts = you_skill_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (you.skills.primary.path not in ts) or (you.skills.secondary.path not in ts):
                    continue
            if any(i in skill_list for i in tags):
                ts = skill_list
                for j in range(len(ts)):
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (cat.skills.primary.path not in ts) or (cat.skills.secondary.path not in ts):
                    continue

            # Season tags
            if ('leafbare' in tags and game.clan.current_season != 'Leaf-bare') or ('newleaf' in tags and game.clan.current_season != 'Newleaf') or ('leaffall' in tags and game.clan.current_season != 'Leaf-fall') or ('greenleaf' in tags and game.clan.current_season != 'Greenleaf'):
                continue

            # Biome tags
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands', 'desert'] for i in tags):
                if game.clan.biome.lower() not in tags:
                    continue

            # Injuries, grieving and illnesses tags

            if "you_pregnant" in tags and "pregnant" not in you.injuries:
                continue
            if "they_pregnant" in tags and "pregnant" not in cat.injuries:
                continue

            if "grief stricken" not in you.illnesses and "you_grieving" in tags and not you.dead:
                continue

            if "starving" not in you.illnesses and "you_starving" in tags:
                continue
            if "starving" not in cat.illnesses and "they_starving" in tags:
                continue


            if any(i in ["you_ill", "you_injured"] for i in tags):
                ill_injured = False

                if you.is_ill() and "you_ill" in tags and "grief stricken" not in you.illnesses:
                    for illness in you.illnesses:
                        if you.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if you.is_injured() and "you_injured" in tags and "pregnant" not in you.injuries and "recovering from birth" not in you.injuries and "sprain" not in you.injuries:
                    for injury in you.injuries:
                        if you.injuries[injury]['severity'] != 'minor':
                            ill_injured = True

                if not ill_injured:
                    continue

            if any(i in ["they_ill", "they_injured"] for i in tags):
                ill_injured = False

                if cat.is_ill() and "they_ill" in tags and "grief stricken" not in cat.illnesses and "guilty" not in cat.illnesses:
                    for illness in cat.illnesses:
                        if cat.illnesses[illness]['severity'] != 'minor':
                            ill_injured = True
                if cat.is_injured() and "they_injured" in tags and "pregnant" not in cat.injuries and "recovering from birth" not in cat.injuries and "sprain" not in cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury]['severity'] != 'minor':
                            ill_injured = True

                if not ill_injured:
                    continue


            # Relationships
            # Family tags:
            if any(i in ["from_your_parent", "from_adopted_parent", "adopted_parent", "half sibling", "littermate", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_kit", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling", "from_adopted_kit"] for i in tags):

                fam = False
                if "from_mentor" in tags:
                    if you.mentor == cat.ID:
                        fam = True
                if "from_your_apprentice" in tags:
                    if cat.mentor == you.ID:
                        fam = True
                if "from_mate" in tags:
                    if cat.ID in you.mate:
                        fam = True
                if "from_parent" in tags or "from_your_parent" in tags:
                    if you.parent1:
                        if you.parent1 == cat.ID:
                            fam = True
                    if you.parent2:
                        if you.parent2 == cat.ID:
                            fam = True
                if "adopted_parent" in tags or "from adopted_parent" in tags or "from_adopted_parent" in tags:
                    if cat.ID in you.inheritance.get_no_blood_parents():
                        fam = True
                if "from_kit" in tags or "from_your_kit" in tags:
                    if cat.ID in you.inheritance.get_blood_kits():
                        fam = True
                if "from_adopted_kit" in tags:
                    if cat.ID in you.inheritance.get_not_blood_kits():
                        fam = True
                if "littermate" in tags:
                    if cat.ID in you.inheritance.get_siblings() and cat.moons == you.moons:
                        fam = True
                if "sibling" in tags:
                    if cat.ID in you.inheritance.get_siblings():
                        fam = True
                if "half sibling" in tags:
                    c_p1 = cat.parent1
                    if not c_p1:
                        c_p1 = "no_parent1_cat"
                    c_p2 = cat.parent2
                    if not c_p2:
                        c_p2 = "no_parent2_cat"
                    y_p1 = you.parent1
                    if not y_p1:
                        y_p1 = "no_parent1_you"
                    y_p2 = you.parent2
                    if not y_p2:
                        y_p2 = "no_parent2_you"
                    if ((c_p1 == y_p1 or c_p1 == y_p2) or (c_p2 == y_p1 or c_p2 == y_p2)) and not (c_p1 == y_p1 and c_p2 == y_p2) and not (c_p2 == y_p1 and c_p1 == y_p2) and not (c_p1 == y_p2 and c_p2 == y_p1):
                        fam = True
                if "adopted_sibling" in tags:
                    if cat.ID in you.inheritance.get_no_blood_siblings():
                        fam = True
                if "parents_siblings" in tags:
                    if cat.ID in you.inheritance.get_parents_siblings():
                        fam = True
                if "cousin" in tags:
                    if cat.ID in you.inheritance.get_cousins():
                        fam = True
                if "siblings_mate" in tags:
                    if cat.ID in you.inheritance.get_siblings_mates():
                        fam = True
                if not fam:
                    continue


            if "non-related" in tags:
                if you.inheritance.get_exact_rel_type(cat.ID) == RelationType.RELATED:
                    continue

            # If you have murdered someone and have been revealed
            if "murder" in tags and you.shunned == 1:
                if game.clan.your_cat.revealed:
                    if game.clan.your_cat.history:
                        if "is_murderer" in game.clan.your_cat.history.murder:
                            if len(game.clan.your_cat.history.murder["is_murderer"]) == 0:
                                continue
                            if 'accomplices' in game.switches:
                                if cat.ID in game.switches['accomplices']:
                                    continue
                        else:
                            continue
                    else:
                        continue
                else:
                    continue

            if "war" in tags:
                if game.clan.war.get("at_war", False):
                    continue

            if "non-mates" in tags:
                if you.ID in cat.mate:
                    continue

            if "clan_has_kits" in tags:
                clan_has_kits = False
                for c in Cat.all_cats_list:
                    if c.status == "kitten" and not c.dead and not c.outside:
                        clan_has_kits = True
                if not clan_has_kits:
                    continue

            if "they_older" in tags:
                if you.age == cat.age or cat.moons < you.moons:
                    continue

            if "they_sameage" in tags:
                if you.age != cat.age:
                    continue

            if "they_younger" in tags:
                if you.age == cat.age or cat.moons > you.moons:
                    continue

            if "they_shunned" in tags:
                if cat.shunned == 0:
                    continue

            if "you_shunned" in tags:
                if you.shunned == 0:
                    continue
            
            if "both_shunned" in tags:
                if cat.shunned == 0 or you.shunned == 0:
                    continue

            if cat.shunned > 0 and you.shunned == 0 and "they_shunned" not in tags:
                continue

            if you.shunned > 0 and cat.shunned == 0 and "you_shunned" not in tags:
                continue

            if you.shunned > 0 and cat.shunned > 0 and "both_shunned" not in tags:
                continue

            if "guilty" in tags and "guilt" not in cat.illnesses:
                continue

            # PERMANENT CONDITIONS
            # to be un-commented with the actual permacondition dialogue implementation

            # if "deaf" in cat.illnesses and "they_deaf" not in tags:
            #     continue
            # if "blind" in cat.illnesses and "they_blind" not in tags:
            #     continue
            # if "deaf" in you.illnesses and "you_deaf" not in tags:
            #     continue
            # if "blind" in you.illnesses and "you_blind" not in tags:
            #     continue

            # if "only_they_deaf" in tags and "deaf" not in cat.illnesses:
            #     continue
            # if "only_they_blind" in tags and "blind" not in cat.illnesses:
            #     continue
            # if "only_you_deaf" in tags and "deaf" not in cat.illnesses:
            #     continue
            # if "only_you_blind" in tags and "blind" not in cat.illnesses:
            #     continue
            
            # Relationship conditions
            if you.ID in cat.relationships:
                if cat.relationships[you.ID].dislike < 30 and 'hate' in tags:
                    continue
                if cat.relationships[you.ID].romantic_love < 15 and 'romantic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 15 and 'platonic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 40 and 'platonic_love' in tags:
                    continue
                if cat.relationships[you.ID].jealousy < 5 and 'jealousy' in tags:
                    continue
                if cat.relationships[you.ID].dislike < 20 and 'dislike' in tags:
                    continue
                if cat.relationships[you.ID].comfortable < 5 and 'comfort' in tags:
                    continue
                if cat.relationships[you.ID].admiration < 5 and 'respect' in tags:
                    continue
                if cat.relationships[you.ID].trust < 5 and 'trust' in tags:
                    continue
                if (cat.relationships[you.ID].platonic_like > 10 or cat.relationships[you.ID].dislike > 10) and "neutral" in tags:
                    continue
            else:
                if any(i in ["hate","romantic_like","platonic_like","jealousy","dislike","comfort","respect","trust"] for i in tags):
                    continue

            texts_list[talk_key] = talk

        return self.choose_text(cat, texts_list)


    def choose_text(self, cat, texts_list):
        you = game.clan.your_cat
        resource_dir = "resources/dicts/lifegen_talk/"
        if not texts_list:
            cluster1, cluster2 = get_cluster(cat.personality.trait)
            cluster3, cluster4 = get_cluster(you.personality.trait)
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
                clusters_1 = f"{cluster1} "
                if cluster2:
                    clusters_1 += f"and {cluster2}"
                clusters_2 = f"{cluster3} "
                if cluster4:
                    clusters_2 += f"and {cluster4}"
                try:
                    add_on = ""
                    add_on2 = ""
                    if you.dead and you.df:
                        add_on = " df"
                    elif you.dead and not you.df:
                        add_on = " sc"
                    if "grief stricken" in you.illnesses:
                        add_on += " g"
                    if you.shunned > 0:
                        add_on += " sh"
                    if cat.dead and cat.df:
                        add_on2 = " df"
                    elif cat.dead and not cat.df:
                        add_on2 = " sc"
                    if "grief stricken" in cat.illnesses:
                        add_on2 += " g"
                    if cat.shunned > 0:
                        add_on2 += " sh"
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_1", clusters_1)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("c_2", clusters_2)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_1", you.status + add_on)
                    possible_texts['general'][1][0] = possible_texts['general'][1][0].replace("r_2", cat.status + add_on2)
                except Exception as e:
                    print(e)
            texts_list['general'] = possible_texts['general']

        max_retries = 30
        counter = 0
        if len(game.clan.talks) > 50:
            game.clan.talks.clear()

        weights2 = []
        weighted_tags = ["you_pregnant", "they_pregnant", "from_mentor", "from_your_parent", "from_adopted_parent", "adopted_parent", "half sibling", "littermate", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_kit", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling", "from_adopted_kit", "they_injured", "they_ill", "you_injured", "you_ill", "you_grieving"]
        for item in texts_list.values():
            tags = item["tags"] if "tags" in item else item[0]
            num_fam_mentor_tags = 1
            if any(i in weighted_tags for i in tags):
                num_fam_mentor_tags+=3
            weights2.append(num_fam_mentor_tags)

        if "debug_ensure_dialogue" in game.config and game.config["debug_ensure_dialogue"]:
            if game.config["debug_ensure_dialogue"] in list(texts_list.keys()):
                text_chosen_key = game.config["debug_ensure_dialogue"]
                text = texts_list[text_chosen_key]["intro"] if "intro" in texts_list[text_chosen_key] else texts_list[text_chosen_key][1]
                new_text = self.get_adjusted_txt(text, cat)
                if new_text:
                    if "intro" in texts_list[text_chosen_key]:
                        self.text_type = "choices"
                        self.display_intro(cat, texts_list, text_chosen_key)
                    return new_text
            else:
                print("something's wrong")

        while counter < max_retries:
            text_chosen_key = choices(list(texts_list.keys()), weights=weights2, k=1)[0]
            text = texts_list[text_chosen_key]["intro"] if "intro" in texts_list[text_chosen_key] else texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)

            if "intro" in texts_list[text_chosen_key]:
                for choice_key in texts_list[text_chosen_key].keys():
                    choice_text = texts_list[text_chosen_key][choice_key]
                    if isinstance(choice_text, list) and choice_key != "tags":
                        choice_text = self.get_adjusted_txt(choice_text, cat)
                        if not choice_text:
                            new_text = ""
                            break


            if text_chosen_key not in game.clan.talks and new_text:
                game.clan.talks.append(text_chosen_key)
                if "intro" in texts_list[text_chosen_key]:
                    self.text_type = "choices"
                    self.display_intro(cat, texts_list, text_chosen_key)
                return new_text

            counter += 1

        weights = []
        for item in texts_list.values():
            tags = item["tags"] if "tags" in item else item[0]
            weights.append(len(tags))
        text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
        while text_chosen_key not in texts_list.keys():
            text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
        try:
            text = texts_list[text_chosen_key][1]
        except:
            possible_texts = None
            cluster1, cluster2 = get_cluster(cat.personality.trait)
            cluster3, cluster4 = get_cluster(you.personality.trait)
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
                clusters_1 = f"{cluster1} "
                if cluster2:
                    clusters_1 += f"and {cluster2}"
                clusters_2 = f"{cluster3} "
                if cluster4:
                    clusters_2 += f"and {cluster4}"
                try:
                    possible_texts['general'][1][0].replace("c_1", clusters_1)
                    possible_texts['general'][1][0].replace("c_2", clusters_2)
                    possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                    possible_texts['general'][1][0].replace("r_2", cat.status)
                except Exception as e:
                    print(e)

            return possible_texts['general'][1]
        new_text = self.get_adjusted_txt(text, cat)
        counter = 0
        while not new_text:
            text_chosen_key = choices(list(texts_list.keys()), weights=weights, k=1)[0]
            text = texts_list[text_chosen_key][1]
            new_text = self.get_adjusted_txt(text, cat)
            counter +=1
            if counter == 30:
                possible_texts = None
                cluster1, cluster2 = get_cluster(cat.personality.trait)
                cluster3, cluster4 = get_cluster(you.personality.trait)
                with open(f"{resource_dir}general.json", 'r') as read_file:
                    possible_texts = ujson.loads(read_file.read())
                    clusters_1 = f"{cluster1} "
                    if cluster2:
                        clusters_1 += f"and {cluster2}"
                    clusters_2 = f"{cluster3} "
                    if cluster4:
                        clusters_2 += f"and {cluster4}"
                    try:
                        possible_texts['general'][1][0].replace("c_1", clusters_1)
                        possible_texts['general'][1][0].replace("c_2", clusters_2)
                        possible_texts['general'][1][0].replace("r_1", game.clan.your_cat.status)
                        possible_texts['general'][1][0].replace("r_2", cat.status)
                    except Exception as e:
                        print(e)

                return possible_texts['general'][1]
        return new_text

    def get_adjusted_txt(self, text, cat):
        you = game.clan.your_cat

        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(you.name)) for t1 in text]
        text = [t1.replace("t_c", str(cat.name)) for t1 in text]

        for i in range(len(text)):
            text[i] = self.adjust_txt(text[i], cat)
            if text[i] == "":
                return ""

        r_c_found = False
        for i in range(len(text)):
            if "r_c" in text[i]:
                r_c_found = True
        if r_c_found:
            alive_cats = self.get_living_cats()
            alive_cat = choice(alive_cats)
            while alive_cat.ID == game.clan.your_cat.ID or alive_cat.ID == cat.ID:
                alive_cat = choice(alive_cats)
            text = [t1.replace("r_c", str(alive_cat.name)) for t1 in text]

        t_l_found = False
        for i in range(len(text)):
            if "t_l" in text[i]:
                t_l_found = True
        if t_l_found:
            if len(cat.inheritance.get_siblings()) == 0:
                    return ""
            sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
            counter = 0
            while sibling.moons != cat.moons or sibling.outside or sibling.dead or sibling.ID == game.clan.your_cat.ID:
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                counter+=1
                if counter == 15:
                    return ""
            text = [t1.replace("t_l", str(sibling.name)) for t1 in text]

        t_s_found = False
        for i in range(len(text)):
            if "t_s" in text[i]:
                t_s_found = True
        if t_s_found:
            if len(cat.inheritance.get_siblings()) == 0:
                    return ""
            sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
            counter = 0
            while sibling.outside or sibling.dead or sibling.ID == game.clan.your_cat.ID:
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                counter+=1
                if counter == 15:
                    return ""
            text = [t1.replace("t_s", str(sibling.name)) for t1 in text]

        


        if "grief stricken" in cat.illnesses:
            try:
                dead_cat = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]


            except:
                return ""
        elif "grief stricken" in you.illnesses:
            try:
                dead_cat = Cat.all_cats.get(you.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]
            except:
                return ""
        d_c_found = False
        for t in text:
            if "d_c" in t:
                d_c_found = True
        if d_c_found:
            dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
            text = [t1.replace("d_c", dead_cat) for t1 in text]
        return text

    def get_living_cats(self):
        living_cats = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside:
                living_cats.append(the_cat)
        return living_cats

    def adjust_txt(self, text, cat):
        try:
            if "your_crush" in text:
                if len(game.clan.your_cat.mate) > 0 or game.clan.your_cat.no_mates:
                    return ""
                crush = None
                for c in self.get_living_cats():
                    if c.ID == game.clan.your_cat.ID or c.ID == cat.ID or c.ID in cat.mate or c.ID in game.clan.your_cat.mate or c.age != game.clan.your_cat.age:
                        continue
                    relations = game.clan.your_cat.relationships.get(c.ID)
                    if not relations:
                        continue
                    if relations.romantic_love > 10:
                        crush = c
                        break
                if crush:
                    text = text.replace("your_crush", str(crush.name))
                else:
                    return ""
            if "their_crush" in text:
                if len(cat.mate) > 0 or cat.no_mates:
                    return ""
                crush = None
                for c in self.get_living_cats():
                    if c.ID == game.clan.your_cat.ID or c.ID == cat.ID or c.ID in cat.mate or c.ID in game.clan.your_cat.mate or c.age != cat.age:
                        continue
                    relations = cat.relationships.get(c.ID)
                    if not relations:
                        continue
                    if relations.romantic_love > 10:
                        crush = c
                        break
                if crush:
                    text = text.replace("their_crush", str(crush.name))
                else:
                    return ""


            if "r_c1" in text:
                alive_apps = self.get_living_cats()
                if len(alive_apps) <= 2:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter==30:
                        return ""
                    alive_app = choice(alive_apps)
                alive_apps.remove(alive_app)
                text = text.replace("r_c1", str(alive_app.name))
                if "r_c2" in text:
                    alive_app2 = choice(alive_apps)
                    counter = 0
                    while alive_app2.ID == game.clan.your_cat.ID or alive_app2.ID == cat.ID:
                        alive_app2 = choice(alive_apps)
                        counter+=1
                        if counter==30:
                            return ""
                    text = text.replace("r_c2", str(alive_app2.name))
                if "r_c3" in text:
                    alive_app3 = choice(alive_apps)
                    counter = 0
                    while alive_app3.ID == game.clan.your_cat.ID or alive_app3.ID == cat.ID:
                        alive_app3 = choice(alive_apps)
                        counter+=1
                        if counter==30:
                            return ""
                    text = text.replace("r_c3", str(alive_app3.name))
            if "r_k" in text:
                alive_kits = get_alive_kits(Cat)
                if len(alive_kits) <= 1:
                    return ""
                alive_kit = choice(alive_kits)
                counter = 0
                while alive_kit.ID == game.clan.your_cat.ID or alive_kit.ID == cat.ID:
                    counter+=1
                    if counter==30:
                        return ""
                    alive_kit = choice(alive_kits)
                text = text.replace("r_k", str(alive_kit.name))
            if "r_a" in text:
                alive_apps = get_alive_apps(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("r_a", str(alive_app.name))
            if "r_w1" in text:
                alive_apps = get_alive_warriors(Cat)
                if len(alive_apps) <= 2:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                alive_apps.remove(alive_app)
                text = text.replace("r_w1", str(alive_app.name))
                if "r_w2" in text:
                    alive_app2 = choice(alive_apps)
                    counter = 0
                    while alive_app2.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                        alive_app2 = choice(alive_apps)
                        counter+=1
                        if counter == 30:
                            return ""
                    text = text.replace("r_w2", str(alive_app2.name))
                if "r_w3" in text:
                    alive_app3 = choice(alive_apps)
                    counter = 0
                    while alive_app3.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                        counter+=1
                        if counter == 30:
                            return ""
                        alive_app3 = choice(alive_apps)
                    text = text.replace("r_w3", str(alive_app3.name))
            if "r_w" in text:
                alive_apps = get_alive_warriors(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("r_w", str(alive_app.name))
            if "r_m" in text:
                alive_apps = get_alive_meds(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("r_m", str(alive_app.name))
            if "r_d" in text:
                alive_apps = get_alive_mediators(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("r_d", str(alive_app.name))
            if "r_q" in text:
                alive_apps = get_alive_queens(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("r_q", str(alive_app.name))
            if "r_e" in text:
                alive_apps = get_alive_elders(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID:
                    alive_app = choice(alive_apps)
                    counter+=1
                    if counter==30:
                        return ""
                text = text.replace("r_e", str(alive_app.name))
            if "r_s" in text:
                alive_apps = get_alive_cats(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.is_ill():
                    alive_app = choice(alive_apps)
                    counter+=1
                    if counter == 30:
                        return ""
                text = text.replace("r_s", str(alive_app.name))
            if "r_i" in text:
                alive_apps = get_alive_cats(Cat)
                if len(alive_apps) <= 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.is_injured():
                    alive_app = choice(alive_apps)
                    counter+=1
                    if counter == 30:
                        return ""
                text = text.replace("r_i", str(alive_app.name))
            if "l_n" in text:
                if game.clan.leader is None:
                    return ""
                if game.clan.leader.dead or game.clan.leader.outside or game.clan.leader.ID == game.clan.your_cat.ID or game.clan.leader.ID == cat.ID:
                    return ""
                text = text.replace("l_n", str(game.clan.leader.name))
            if "d_n" in text:
                if game.clan.deputy is None:
                    return ""
                if game.clan.deputy.dead or game.clan.deputy.outside or game.clan.deputy.ID == game.clan.your_cat.ID or game.clan.deputy.ID == cat.ID:
                    return ""
                text = text.replace("d_n", str(game.clan.deputy.name))

            if "rsh_c" in text:
                random_cat = choice(self.get_living_cats())
                counter = 0
                while random_cat.ID == game.clan.your_cat.ID or random_cat.ID == cat.ID or not random_cat.shunned:
                    if counter == 30:
                        return ""
                    random_cat = choice(self.get_living_cats())
                    counter +=1
                text = text.replace("rsh_c", str(random_cat.name))
            if "rsh_k" in text:
                alive_kits = get_alive_kits(Cat)
                if len(alive_kits) < 1:
                    return ""
                alive_kit = choice(alive_kits)
                counter = 0
                while alive_kit.ID == game.clan.your_cat.ID or alive_kit.ID == cat.ID or not alive_kit.shunned:
                    alive_kit = choice(alive_kits)
                    counter+=1
                    if counter == 30:
                        return ""
                text = text.replace("rsh_k", str(alive_kit.name))
            if "rsh_a" in text:
                alive_apps = get_alive_apps(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("rsh_a", str(alive_app.name))
            if "rsh_w" in text:
                alive_apps = get_alive_warriors(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("rsh_w", str(alive_app.name))
            if "rsh_m" in text:
                alive_apps = get_alive_meds(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("rsh_m", str(alive_app.name))
            if "rsh_d" in text:
                alive_apps = get_alive_mediators(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("rsh_d", str(alive_app.name))
            if "rsh_q" in text:
                alive_apps = get_alive_queens(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    counter+=1
                    if counter == 30:
                        return ""
                    alive_app = choice(alive_apps)
                text = text.replace("rsh_q", str(alive_app.name))
            if "rsh_e" in text:
                alive_apps = get_alive_elders(Cat)
                if len(alive_apps) < 1:
                    return ""
                alive_app = choice(alive_apps)
                counter = 0
                while alive_app.ID == game.clan.your_cat.ID or alive_app.ID == cat.ID or not alive_app.shunned:
                    alive_app = choice(alive_apps)
                    counter+=1
                    if counter==30:
                        return ""
                text = text.replace("rsh_e", str(alive_app.name))
            if "sh_d" in text:
                random_cat = choice(self.get_living_cats())
                counter = 0
                while random_cat.ID == game.clan.your_cat.ID or random_cat.ID == cat.ID or random_cat.status != "deputy" or not random_cat.shunned >0:
                    if counter == 30:
                        return ""
                    random_cat = choice(self.get_living_cats())
                    counter +=1
                text = text.replace("sh_d", str(random_cat.name))
            if "sh_l" in text:
                random_cat = choice(self.get_living_cats())
                counter = 0
                while random_cat.ID == game.clan.your_cat.ID or random_cat.ID == cat.ID or random_cat.status != "leader" or not random_cat.shunned >0:
                    if counter == 30:
                        return ""
                    random_cat = choice(self.get_living_cats())
                    counter +=1
                text = text.replace("sh_l", str(random_cat.name))

            if "y_s" in text:
                if len(game.clan.your_cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                if sibling.outside or sibling.dead or sibling.ID == cat.ID:
                    return ""
                text = text.replace("y_s", str(sibling.name))
            if "t_s" in text:
                if len(cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                if sibling.outside or sibling.dead or sibling.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_s", str(sibling.name))
            if "y_a" in text:
                if len(game.clan.your_cat.apprentice) == 0:
                    return ""
                text = text.replace("y_a", str(Cat.fetch_cat(choice(game.clan.your_cat.apprentice)).name))
            if "t_a" in text:
                if len(cat.apprentice) == 0:
                    return ""
                their_app = Cat.fetch_cat(choice(cat.apprentice))
                if their_app.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_a", str(Cat.fetch_cat(choice(cat.apprentice)).name))
            if "y_l" in text:
                if len(game.clan.your_cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                counter = 0
                while sibling.moons != game.clan.your_cat.moons or sibling.outside or sibling.dead:
                    sibling = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_siblings()))
                    counter+=1
                    if counter == 15:
                        return ""
                text = text.replace("y_l", str(sibling.name))

            if "t_l" in text:
                if len(cat.inheritance.get_siblings()) == 0:
                    return ""
                sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                counter = 0
                while sibling.moons != cat.moons or sibling.outside or sibling.dead or sibling.ID == game.clan.your_cat.ID:
                    sibling = Cat.fetch_cat(choice(cat.inheritance.get_siblings()))
                    counter+=1
                    if counter == 15:
                        return ""
                text = text.replace("t_l", str(sibling.name))

            if "y_p" in text:
                parent = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_parents()))
                if len(game.clan.your_cat.inheritance.get_parents()) == 0:
                    return ""

                if parent.outside or parent.dead or parent.ID==cat.ID:
                    return ""
                text = text.replace("y_p", str(parent.name))


            if "t_p_positive" in text:
                if len(cat.inheritance.get_parents()) == 0:
                    return ""
                parent = Cat.fetch_cat(choice(cat.inheritance.get_parents()))
                if parent.outside or parent.dead or parent.ID==game.clan.your_cat.ID:
                    return ""
                relations = cat.relationships.get(parent.ID)
                if not relations:
                    return ""
                if relations.platonic_like < 10:
                    return ""
                text = text.replace("t_p_positive", str(parent.name))
            if "t_p_negative" in text:
                if len(cat.inheritance.get_parents()) == 0:
                    return ""
                parent = Cat.fetch_cat(choice(cat.inheritance.get_parents()))
                if parent.outside or parent.dead or parent.ID==game.clan.your_cat.ID:
                    return ""
                relations = cat.relationships.get(parent.ID)
                if not relations:
                    return ""
                if relations.dislike < 20:
                    return ""
                text = text.replace("t_p_negative", str(parent.name))
            if "t_p" in text:
                if len(cat.inheritance.get_parents()) == 0:
                    return ""
                parent = Cat.fetch_cat(choice(cat.inheritance.get_parents()))
                if parent.outside or parent.dead or parent.ID==game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_p", str(parent.name))
            if "y_m" in text:
                if game.clan.your_cat.mate is None or len(game.clan.your_cat.mate) == 0 or cat.ID in game.clan.your_cat.mate:
                    return ""
                mate = Cat.fetch_cat(choice(game.clan.your_cat.mate))
                if mate.dead or mate.outside:
                    return ""
                text = text.replace("y_m", str(mate.name))
            if "t_mn" in text:
                if cat.mentor is None:
                    return ""
                text = text.replace("t_mn", str(Cat.fetch_cat(cat.mentor).name))
            if "tm_n" in text:
                if cat.mentor is None or cat.mentor == game.clan.your_cat.ID:
                    return ""
                text = text.replace("tm_n", str(Cat.fetch_cat(cat.mentor).name))
            if "m_n" in text:
                if game.clan.your_cat.mentor is None or game.clan.your_cat.mentor == cat.ID:
                    return ""
                text = text.replace("m_n", str(Cat.fetch_cat(game.clan.your_cat.mentor).name))
            if "o_c" in text:
                other_clan = choice(game.clan.all_clans)
                if not other_clan:
                    return ""
                text = text.replace("o_c", str(other_clan.name))

            #their mate
            if "t_m" in text:
                if cat.mate is None or len(cat.mate) == 0 or cat.ID in game.clan.your_cat.mate:
                    return ""
                mate1 = Cat.fetch_cat(choice(cat.mate))
                if mate1.outside or mate1.dead:
                    return ""
                text = text.replace("t_m", str(mate1.name))
            #their kit


            #their kit-- apprentice
            if "t_ka" in text:
                if cat.inheritance.get_children() is None or len(cat.inheritance.get_children()) == 0:
                    return ""
                kit = Cat.fetch_cat(choice(cat.inheritance.get_children()))
                if kit.moons < 12 or kit.outside or kit.dead or kit.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_ka", str(kit.name))

            #their kit-- kit aged
            if "t_kk" in text:
                if cat.inheritance.get_children() is None or len(cat.inheritance.get_children()) == 0:
                    return ""
                kit = Cat.fetch_cat(choice(cat.inheritance.get_children()))
                if kit.moons >= 6 or kit.outside or kit.dead or kit.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_kk", str(kit.name))

            if "t_k" in text:
                if cat.inheritance.get_children() is None or len(cat.inheritance.get_children()) == 0:
                    return ""
                kit = Cat.fetch_cat(choice(cat.inheritance.get_children()))
                if kit.outside or kit.dead or kit.ID == game.clan.your_cat.ID:
                    return ""
                text = text.replace("t_k", str(kit.name))

            if "y_k" in text:
                if game.clan.your_cat.inheritance.get_children() is None or len(game.clan.your_cat.inheritance.get_children()) == 0:
                    return ""
                kit = Cat.fetch_cat(choice(game.clan.your_cat.inheritance.get_children()))
                if kit.outside or kit.dead or kit.ID == cat.ID:
                    return ""

                text = text.replace("y_k", str(kit.name))


            #random cats 1 and 2
            if "n_r1" in text:
                if "n_r2" not in text:
                    return ""
                random_cat1 = choice(self.get_living_cats())
                random_cat2 = choice(self.get_living_cats())
                counter = 0
                while not random_cat1.is_potential_mate(random_cat2) or random_cat2.age != random_cat1.age:
                    random_cat1 = choice(self.get_living_cats())
                    random_cat2 = choice(self.get_living_cats())
                    counter +=1
                    if counter > 40:
                        return ""
                if random_cat1.ID == game.clan.your_cat.ID or random_cat1.ID == cat.ID or random_cat2.ID == game.clan.your_cat.ID or random_cat2.ID == cat.ID:
                    return ""
                text = text.replace("n_r1", str(random_cat1.name))
                text = text.replace("n_r2", str(random_cat2.name))

                #random cat
                #this does not work in any other location or indent level. i dont know.
                #just dont move it unless youve got a better way
                if "r_c" in text:

                    random_cat = choice(self.get_living_cats())
                    counter = 0
                    while random_cat.ID == game.clan.your_cat.ID or random_cat.ID == cat.ID:
                        if counter == 30:
                            return ""
                        random_cat = choice(self.get_living_cats())
                        counter +=1
                    text = text.replace("r_c", str(random_cat.name))


        except Exception as e:
            print(e)
            print("ERROR: could not replace abbrv.")
            return ""


        return text
