import keyboard
import random
import time

import colors
import sounds
from colors import *
from controller import MultiSegment
from rule import Rule, Mode

# TODO: Review iosoft.blog
# https://iosoft.blog/2020/09/29/raspberry-pi-multi-channel-ws2812/

# Keys
KEY_START = 'f'

# Segment numbers
BOXES = ((2, 22, 4, 23),
         (3, 24, 5, 25),
         (6, 26, 8, 27),
         (7, 28, 9, 29),
         (10, 30, 12, 31),
         (11, 32, 13, 33),
         (14, 34, 16, 35),
         (15, 36, 17, 37),
         (18, 38, 20, 39),
         (19, 40, 21, 41))
RAILS = (0, 1)
GRID = tuple(i for i in range(2, 42))
ALL_SEGS = tuple(i for i in range(42))


class Game:
    """
    Control all game logic for Glass Stepping Stones. There are multiple 'modes' which
    govern how rules are generated for lights and how input is handled.
    Mode 100 - attract
    Mode 200 - startup
    Mode 300 - gameplay
    Mode 400 - win
    """

    def __init__(self, control, grid):
        """
        Initialize Game.
        :param control: LED controller.
        :param grid: Segment container class.
        """
        self.controller = control
        self.grid = grid
        self.sound_player = sounds.SoundPlayer()
        self.mode = 100
        self.mode_initialized = False
        self.start_time = time.time()

        # Variables used by update()
        self.row = 0
        self.undertale_count = 0
        self.started_scream = False

    def update(self):
        """
        Called every frame - update the game state, LEDs, etc. based on input and timing.
        """
        time_elapsed = time.time() - self.start_time
        self.new_mode = False

        # Mode 0-99 - testing purposes only
        if self.mode <= 99:
            # MultiSegment(self.grid, 12, 15, 18, 21, 24, 10, 11).set_rule(Rule().hue(60, 310, 0.1))
            # MultiSegment(self.grid, 12, 15, 18, 21, 24, 10, 11).set_rule(Rule().fill(RED).crop(40, 990))
            #MultiSegment(self.grid, *ALL_SEGS).set_rule(
            #    Rule().fill(WHITE)
            #)
            # MultiSegment(self.grid, *ALL_SEGS).set_rule(Rule().fill(WHITE))
            if not self.mode_initialized:
                self.grid.get_seg(0).set_rule(
                    Rule().stripes((RED, YELLOW), 5).animate(10)
                )

        # Mode 100-199 - attract sequence
        elif self.mode <= 199:
            self.sound_player.update()

            # On space press, move to stage 2 - start the game.
            if keyboard.is_pressed(KEY_START):
                self.set_mode(random.randint(200, 201), clear_all=True)
                self.sound_player.stop()
                self.undertale_count = 0

            elif self.mode == 100:
                if not self.mode_initialized:
                    # Play attract music
                    self.sound_player.set_mode(sounds.SoundPlayer.Mode.ATTRACT)

                    # Railings are red/orange moving stripes in intro
                    self.grid.get_seg(0).set_rule(Rule().stripes((GREEN, PURPLE), width=8).animate(10).fade_in(2, 1))
                    self.grid.get_seg(1).set_rule(Rule().stripes((GREEN, PURPLE), width=8).animate(10).fade_in(2, 1))
                if time_elapsed > 4:
                    self.set_mode(101)

            elif self.mode == 101:
                if not self.mode_initialized:
                    # Have 5 boxes fade in and out in an orange color
                    box_ids = 0, 3, 4, 7, 8  # [BOX0, BOX3, BOX4, BOX7, BOX8]
                    for i, box_id in enumerate(box_ids):
                        box_rule = Rule().fill(ORANGE).fade_in(0.25, 0.75 * i).fade_out(0.25, 0.5 + 0.75 * i)
                        for seg_id in BOXES[box_id]:
                            self.grid.get_seg(seg_id).set_rule(box_rule)
                if time_elapsed > 5:
                    self.set_mode(102)

            elif self.mode == 102:
                if not self.mode_initialized:
                    # Have a white light zoom around the strip
                    multi_seg = MultiSegment(self.grid, 22, 4, 27, 8, 30, 34, 38, 20, 21, 41,
                                             17, 36, 13, 33, 29, 25, 3, 2,
                                             flipped_segs=(8, 41, 17, 36, 33, 29, 25, 3, 2))
                    multi_seg.set_rule(Rule().fill(WHITE, -15, 0).animate(60))
                if time_elapsed > 5:
                    self.set_mode(103)

            elif self.mode == 103:
                if not self.mode_initialized:
                    multi_segs = []
                    multi_segs.append(MultiSegment(self.grid, 22, 26, 30, 34, 38, 20, 21))

                    multi_segs.append(MultiSegment(self.grid, 18, 39))
                    multi_segs.append(MultiSegment(self.grid, 16, 40))

                    multi_segs.append(MultiSegment(self.grid, 14, 35, 19, 41))
                    multi_segs.append(MultiSegment(self.grid, 12, 36, 17))

                    multi_segs.append(MultiSegment(self.grid, 10, 31, 15, 37))
                    multi_segs.append(MultiSegment(self.grid, 8, 32, 13))

                    multi_segs.append(MultiSegment(self.grid, 6, 27, 11, 33))
                    multi_segs.append(MultiSegment(self.grid, 4, 28, 9))

                    multi_segs.append(MultiSegment(self.grid, 2, 23, 7, 29))

                    multi_segs.append(MultiSegment(self.grid, 24, 5))
                    multi_segs.append(MultiSegment(self.grid, 3, 25))

                    for i, multi_seg in enumerate(multi_segs):
                        rule = Rule().hue_linear(5).fade_in(1, 0).fade_out(1, 5).animate(40)
                        if 1 <= i <= 2:
                            rule.offset(SEG_WIDTH * 4)
                        elif 3 <= i <= 4:
                            rule.offset(SEG_WIDTH * 3)
                        elif 5 <= i <= 6:
                            rule.offset(SEG_WIDTH * 2)
                        elif 7 <= i <= 8:
                            rule.offset(SEG_WIDTH)
                        elif 10 <= i <= 11:
                            rule.offset(SEG_WIDTH)

                        multi_seg.set_rule(rule)
                if time_elapsed > 7:
                    self.set_mode(104)

            elif self.mode == 104:
                if not self.mode_initialized:
                    MultiSegment(self.grid, 22, 26, 30, 34, 38, 20, 21, 41, 37, 33, 29, 25, 3, 2,
                                 flipped_segs=(41, 37, 33, 29, 25, 3, 2)).set_rule(
                        Rule().stripes((RED, ORANGE, YELLOW), 12).animate(30).fade_in(1, 0).fade_out(1, 5)
                    )
                if time_elapsed > 7:
                    self.set_mode(101)

            elif self.mode == 105:
                if not self.mode_initialized:
                    width = 6
                    speed = 50
                    MultiSegment(self.grid, 31, 35, 39, 20, 38, 16, 12, 30, 8, flipped_segs=(20, 38, 12, 30)).set_rule(
                        Rule().stripes((WHITE, BLACK), width).crop(-200, 0).animate(speed)
                    )
                    MultiSegment(self.grid, 32, 36, 40, 21, 41, 17, 13, 33, 9, flipped_segs=(41, 17, 33, 9)).set_rule(
                        Rule().stripes((WHITE, BLACK), width).crop(-200, 0).animate(speed)
                    )
                    MultiSegment(self.grid, 27, 23, 2, 22, 4, flipped_segs=(27, 23, 2)).set_rule(
                        Rule().stripes((WHITE, BLACK), width).crop(-200, 0).animate(speed)
                    )
                    MultiSegment(self.grid, 28, 24, 3, 25, 5, flipped_segs=(28, 24, 5)).set_rule(
                        Rule().stripes((WHITE, BLACK), width).crop(-200, 0).animate(speed)
                    )
                if time_elapsed > 9:
                    self.set_mode(101)

        # Mode 200-299 - transition to game
        elif self.mode <= 299:
            if self.mode == 200:
                if not self.mode_initialized:
                    MultiSegment(self.grid, *BOXES[8], *BOXES[9]).set_rule(
                        Rule().fill(WHITE).fade_in(0, 0).fade_out(1, 2))
                    MultiSegment(self.grid, *BOXES[6], *BOXES[7]).set_rule(
                        Rule().fill(WHITE).fade_in(0, CASCADE_TIME).fade_out(1, 2 + CASCADE_TIME))
                    MultiSegment(self.grid, *BOXES[4], *BOXES[5]).set_rule(
                        Rule().fill(WHITE).fade_in(0, CASCADE_TIME * 2).fade_out(1, 2 + CASCADE_TIME * 2))
                    MultiSegment(self.grid, *BOXES[2], *BOXES[3]).set_rule(
                        Rule().fill(WHITE).fade_in(0, CASCADE_TIME * 3).fade_out(1, 2 + CASCADE_TIME * 3))
                    MultiSegment(self.grid, *BOXES[0], *BOXES[1]).set_rule(
                        Rule().fill(WHITE).fade_in(0, CASCADE_TIME * 4).fade_out(1, 2 + CASCADE_TIME * 4))

                if self.undertale_count < 5 and time_elapsed > self.undertale_count * CASCADE_TIME:
                    self.sound_player.play(sounds.UNDERTALE)
                    self.undertale_count += 1
                if time_elapsed > 7:
                    self.set_mode(300)

            elif self.mode == 201:
                if not self.mode_initialized:
                    speed = 80
                    interval = 0.9
                    self.sound_player.play(sounds.GLRL_ONCE)
                    self.grid.get_seg(39).set_rule(
                        Rule().fill(RED, -1000, 0).animate(speed / 3).flip()
                    )
                    self.grid.get_seg(40).set_rule(
                        Rule().fill(RED, -1000, 0).animate(speed / 3).flip()
                    )
                    MultiSegment(self.grid, 20, 38, 18, flipped_segs=(20, 38)).set_rule(
                        Rule().fill(RED, -1000, 0).animate(speed)
                    )
                    MultiSegment(self.grid, 21, 41, 19, flipped_segs=(41, 19)).set_rule(
                        Rule().fill(RED, -1000, 0).animate(speed)
                    )
                    self.grid.get_seg(35).set_rule(
                        Rule().fill(RED, -1000, -interval * speed / 3).animate(speed / 3).flip()
                    )
                    self.grid.get_seg(36).set_rule(
                        Rule().fill(RED, -1000, -interval * speed / 3).animate(speed / 3).flip()
                    )
                    MultiSegment(self.grid, 16, 34, 14, flipped_segs=(16, 34)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed).animate(speed)
                    )
                    MultiSegment(self.grid, 17, 37, 15, flipped_segs=(37, 15)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed).animate(speed)
                    )
                    self.grid.get_seg(31).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 2 / 3).animate(speed / 3).flip()
                    )
                    self.grid.get_seg(32).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 2 / 3).animate(speed / 3).flip()
                    )
                    MultiSegment(self.grid, 12, 30, 10, flipped_segs=(12, 30)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 2).animate(speed)
                    )
                    MultiSegment(self.grid, 13, 33, 11, flipped_segs=(33, 11)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 2).animate(speed)
                    )
                    self.grid.get_seg(27).set_rule(
                        Rule().fill(RED, -1000, -interval * speed).animate(speed / 3).flip()
                    )
                    self.grid.get_seg(28).set_rule(
                        Rule().fill(RED, -1000, -interval * speed).animate(speed / 3).flip()
                    )
                    MultiSegment(self.grid, 8, 26, 6, flipped_segs=(8, 26)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 3).animate(speed)
                    )
                    MultiSegment(self.grid, 9, 29, 7, flipped_segs=(29, 7)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 3).animate(speed)
                    )
                    self.grid.get_seg(23).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 4 / 3).animate(speed / 3).flip()
                    )
                    self.grid.get_seg(24).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 4 / 3).animate(speed / 3).flip()
                    )
                    MultiSegment(self.grid, 4, 22, 2, flipped_segs=(4, 22)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 4).animate(speed)
                    )
                    MultiSegment(self.grid, 5, 25, 3, flipped_segs=(25, 3)).set_rule(
                        Rule().fill(RED, -1000, -interval * speed * 4).animate(speed)
                    )

                if time_elapsed > 4.75:
                    self.set_mode(202)

            elif self.mode == 202:
                if not self.mode_initialized:
                    MultiSegment(self.grid, *ALL_SEGS).set_rule(
                        Rule().fill(GREEN).fade_out(1, 2)
                    )
                if time_elapsed > 3.5:
                    self.set_mode(300, clear_grid=True, clear_railings=True)

        # Modes 300-399 - gameplay
        elif self.mode <= 399:
            # Wait for user input on first row
            if self.mode == 300:
                if not self.mode_initialized:
                    # Determine winning changes
                    winning_chance = self.get_winning_chance()
                    if winning_chance < 0.0001:
                        print("Current chance of winning is negligible.")
                    elif winning_chance > 0.9999:
                        print("Current chance of winning is quite high.")
                    else:
                        percent_chance = str(round(winning_chance * 100, 2)) + "%"
                        print("Current chance of winning is", percent_chance)

                    # Initialize blinking boxes
                    tempo = self.sound_player.choose_music()
                    left_box = self.row * 2
                    right_box = left_box + 1
                    blink_on = 30 / tempo
                    blink_off = blink_on
                    left_segs = BOXES[left_box]
                    right_segs = BOXES[right_box]
                    MultiSegment(self.grid, *left_segs).set_rule(
                        Rule().fill(WHITE).blink(
                            blink_on, blink_on + blink_off * 2))
                    MultiSegment(self.grid, *right_segs).set_rule(
                        Rule().fill(WHITE).blink(
                            blink_on, blink_on + blink_off * 2,
                            start_time=time.time() - blink_on - blink_off))

                    # Initialize railings
                    self.grid.get_seg(0).set_rule(
                        Rule().stripes((RED, GREEN, BLUE, WHITE), 1).animate(3)
                    )
                    self.grid.get_seg(1).set_rule(
                        Rule().stripes((RED, GREEN, BLUE, WHITE), 1).animate(3)
                    )

                    # Initialize pumpkins
                    self.grid.get_seg(42).set_rule(Rule().hue_linear(15, mode=Mode.PIXEL).animate(10))
                    self.grid.get_seg(43).set_rule(Rule().hue_linear(15, mode=Mode.PIXEL).animate(10))

                # Handle transition after left/right box is stepped on
                left_pressed = keyboard.is_pressed(KEY_BOXES[self.row * 2]) or keyboard.is_pressed(KEY_LEFT)
                right_pressed = keyboard.is_pressed(KEY_BOXES[self.row * 2 + 1]) or keyboard.is_pressed(KEY_RIGHT)
                self.box = self.row * 2
                if right_pressed:
                    self.box += 1
                if left_pressed or right_pressed:
                    self.sound_player.stop()
                    if DO_BLINK:
                        self.set_mode(301, clear_grid=True)
                    else:
                        if self.is_tile_correct():
                            self.set_mode(302)  # Win
                        else:
                            self.set_mode(303)  # Lose

            # If blinking,
            elif self.mode == 301:
                if not self.mode_initialized:
                    MultiSegment(self.grid, *BOXES[self.box]).set_rule(
                        Rule().fill(BLUE).blink(REVEAL_BLINK_TIMES[self.row], REVEAL_BLINK_TIMES[self.row]))

                if time_elapsed > 2:
                    if self.is_tile_correct():
                        self.set_mode(302)  # Win
                    else:
                        self.set_mode(303)  # Lose

            # If winning,
            elif self.mode == 302:
                if not self.mode_initialized:
                    self.sound_player.correct()
                    self.correct_lights(self.box)

                if time_elapsed > WIN_TIME:
                    if self.row == 4:
                        self.set_mode(400, clear_grid=True, clear_railings=True)
                    else:
                        self.set_mode(300, clear_grid=True, clear_railings=True)  # Next round
                        self.row += 1

            # If losing,
            elif self.mode == 303:
                if not self.mode_initialized:
                    self.sound_player.wrong()
                    self.wrong_lights(self.box)

                if time_elapsed > 0.5 and not self.started_scream:
                    self.sound_player.scream()
                    self.started_scream = True
                if time_elapsed > LOSE_TIME:
                    self.reset_game()

        # Modes 400-499: Final win sequence
        elif self.mode <= 499:
            if not self.mode_initialized:
                print("The player has won. On to the next game!")
                self.sound_player.win()
                MultiSegment(self.grid, 22, 26, 30, 34, 38).set_rule(
                    Rule().hue_wave(120, 240, 0.4, Mode.PIXEL).animate(20).fade_out(2, 6))
                MultiSegment(self.grid, 23, 27, 31, 35, 39).set_rule(
                    Rule().hue_wave(120, 240, 0.4, Mode.PIXEL).animate(20).fade_out(2, 6))
                MultiSegment(self.grid, 24, 28, 32, 36, 40).set_rule(
                    Rule().hue_wave(120, 240, 0.4, Mode.PIXEL).animate(20).fade_out(2, 6))
                MultiSegment(self.grid, 25, 29, 33, 37, 41).set_rule(
                    Rule().hue_wave(120, 240, 0.4, Mode.PIXEL).animate(20).fade_out(2, 6))
                MultiSegment(self.grid, *[i for i in range(2, 22)]).set_rule(
                    Rule().hue_wave(120, 240, 2, Mode.TIME).fade_out(2, 6))
                self.grid.get_seg(0).set_rule(Rule().hue_wave(120, 240, 0.8).animate(10).fade_out(2, 6))
                self.grid.get_seg(1).set_rule(Rule().hue_wave(120, 240, 0.8).animate(10).fade_out(2, 6))
                self.grid.get_seg(42).set_rule(Rule().stripes((GREEN, BLACK), 3).animate(15).fade_out(2, 6))
                self.grid.get_seg(43).set_rule(Rule().stripes((GREEN, BLACK), 3).animate(-15).fade_out(2, 6))
            if time_elapsed > 9:
                self.reset_game()

        # If we just initialized, prevent re-initialization on next update cycles.
        if not self.mode_initialized and not self.new_mode:
            self.mode_initialized = True

    def correct_lights(self, box):
        """
        Set up light display if a player lands on a correct box.
        :param box: The ID of the correct box.
        """
        self.correct_lights1(box)

    def correct_lights1(self, box):
        """
        Correct light show 1.
        :param box: Correct box ID.
        """
        MultiSegment(self.grid, *ALL_SEGS).set_rule(
            Rule().stripes((GREEN, WHITE), 3).animate(12).fade_out(1, WIN_TIME - 1.5))
        MultiSegment(self.grid, *BOXES[box]).set_rule(
            Rule().fill(GREEN).fade_out(1, WIN_TIME - 1.5))

        bt = PUMPKIN_BLINK_TIME
        self.grid.get_seg(42).set_rule(
            Rule().fill(GREEN).blink(bt, bt, start_time=time.time() + bt).fade_out(1, WIN_TIME - 1.5)
        )
        self.grid.get_seg(43).set_rule(
            Rule().fill(GREEN).blink(bt, bt).fade_out(1, WIN_TIME - 1.5)
        )

    def wrong_lights(self, box):
        """
        Set up light display if a player lands on a wrong box.
        :param box: The ID of the wrong box.
        """
        self.wrong_lights1(box)

    def wrong_lights1(self, box):
        """
        Wrong light show 1.
        :param box: Wrong box ID.
        """
        MultiSegment(self.grid, *ALL_SEGS, continuous=False).set_rule(
            Rule().stripes((RED, OFF), 6).crop(-30, 200).animate(12))
        MultiSegment(self.grid, *BOXES[box], flipped_segs=(BOXES[box][0], BOXES[box][3])).set_rule(
            Rule().stripes((RED, OFF), 3).animate(10).fade_out(1.2, 2.5))
        self.grid.get_seg(0).set_rule(
            Rule().stripes((RED, OFF), 10).crop(0, 100).animate(15)
        )
        self.grid.get_seg(1).set_rule(
            Rule().stripes((RED, OFF), 10).crop(0, 100).animate(15)
        )

        bt = PUMPKIN_BLINK_TIME
        self.grid.get_seg(42).set_rule(
            Rule().fill(RED).blink(bt, bt, start_time=time.time() + bt).fade_out(1.2, 2.5)
        )
        self.grid.get_seg(43).set_rule(
            Rule().fill(RED).blink(bt, bt).fade_out(1.2, 2.5)
        )

    def is_tile_correct(self):
        """
        Determine if the tile a player stepped on is correct (i.e. won't break)
        :return: True if the tile didn't break.
        """
        tile = self.box % 2  # 0 if left, 1 if right
        correct = self.correct_tiles[self.row]

        # Calculate chance of something going wrong.
        power = 2 ** abs(self.difficulty)
        anomaly_chance = 1
        if power != 0:
            anomaly_chance = (power - 1) / power

        # Determine if tile is correct, then determine if the chance will adjust the outcome.
        if tile == correct:
            if self.difficulty > 0 and random.random() <= anomaly_chance:
                print("Correct tile, but it broke anyway. Difficulty =", self.difficulty)
                return False
            else:
                print("Correct tile!")
                return True
        else:
            if self.difficulty < 0 and random.random() <= anomaly_chance:
                print("Wrong tile, but it didn't break. Difficulty =", self.difficulty)
                return True
            else:
                print("Wrong tile!")
                return False

    def get_winning_chance(self):
        """
        :return: Current chance of winning as a percentage.
        """
        # Determine chance of anomaly
        power = 2 ** abs(self.difficulty)
        anomaly_chance = 1
        if power != 0:
            anomaly_chance = (power - 1) / power

        # Determine chance of winning overall
        turns_remaining = 5 - self.row
        if self.difficulty > 0:
            row_chance = 0.5 - (0.5 * anomaly_chance)
        else:
            row_chance = 0.5 + (0.5 * anomaly_chance)
        overall_chance = row_chance ** turns_remaining

        return overall_chance

    def set_mode(self, mode, clear=False):
        """
        Prepare for a new mode.
        """
        self.mode = mode
        self.start_time = time.time()
        self.mode_initialized = False
        if clear:
            self.grid.clear_rules()

        print("Set mode to", mode)

    def reset_game(self):
        """
        Re-initialize the game for a new round.
        """
        self.set_mode(100, clear_grid=True, clear_railings=True)
        self.row = 0
        self.box = -1
        self.correct_tiles = gen_correct_tiles()
        self.undertale_count = 0
        self.started_scream = False
