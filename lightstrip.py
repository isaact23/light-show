from copy import deepcopy

NEOPIXEL_ENABLED = False

# Import modules for controlling LEDs from RPi
try:
    import board
    import neopixel
    NEOPIXEL_ENABLED = True
except Exception as e:
    print("Error when importing board and/or neopixel:", str(e))


class LightStrip:
    """
    An LED strip.
    """

    def __init__(self, size):
        """
        :param controller: The Controller object this LED strip is assigned to.
        :param size: The number of LEDs on this strip.
        """
        self.size = size
        self.pixels = [(0, 0, 0)] * size
        self.rule = None  # Color generation rule
        self.rgb_flip_ranges = []  # Pixel ranges for which to flip red and green values
        # self.neopixel = neopixel.NeoPixel(board.D18, 150, auto_write=False)

    def get_segment(self, start, end):
        """
        Generate a Segment, which controls only some of the pixels on this LightStrip.
        :param start: The first pixel to control (inclusive).
        :param end: The last pixel to control (exclusive).
        :return: A Segment object with control over the specified pixels.
        :raises IndexError: If start or end are outside the bounds of this LightStrip.
        """
        # Assert start/end are within the bounds of this strip.
        if start < 0 or end > self.size:
            raise IndexError("Attempted to create a Segment outside the bounds of a LightStrip")

        return self.Segment(self, start, end)

    def set_rule(self, r):
        """
        Set a Rule for LED color generation to be used on every use_rule() call.
        :param r: The Rule object.
        """
        self.rule = r

    def use_rule(self):
        """
        Apply the Rule set by set_rule() to generate LED strip colors on this LightStrip.
        """
        if self.rule is not None:
            for i in range(self.size):
                self.set_pixel(i, self.rule(pixel=i, seg_size=self.size()))
        else:
            for i in range(self.size):
                self.set_pixel(i, (0, 0, 0))

    def set_pixel(self, pixel, color):
        self.pixels[pixel] = color

    def get_pixels(self):
        """
        :return: An array of colors for each pixel on this LightStrip.
        """
        return self.pixels

    def write(self):
        """
        Send pixel data to this LED strip.
        """
        try:
            pixel_count = 1000
            pixels = neopixel.NeoPixel(board.D18, pixel_count, auto_write=False)
            for i in range(pixel_count):
                color = self.pixels[i]
                flip = False
                for pixel_range in self.rgb_flip_ranges:
                    if i in pixel_range:
                        flip = True
                        break
                if flip:
                    color = color[1], color[0], color[2]
                pixels[i] = color
            pixels.write()
        except NameError:
            pass
    
    def update(self):
        """
        Use rules and write to strip.
        """
        self.use_rule()
        self.write()


    class Segment:
        """
        A segment of pixels, defined by the start and end pixels of one of the light strips.
        """

        def __init__(self, strip, start, end):
            """
            Initialize a new segment. If end is less than start, flip the Segment.
            :param strip: The strip object this array lies on.
            :param start: The first pixel to activate
            :param end: The last pixel to activate
            """
            self.strip = strip
            self.start = start
            self.end = end
            if self.end < self.start:
                temp = self.end
                self.end = self.start
                self.start = temp
                self.flip = True
            else:
                self.flip = False
            self.rule = None

        def set_rule(self, r):
            """
            Set a function for LED color generation to be used on every use_func() call.
            :param r: The anonymous function.
            """
            if self.flip:
                self.rule = r.flip()
            else:
                self.rule = r

        def use_rule(self):
            """
            Apply the function set by set_func() to generate LED strip colors on this Segment.
            """
            if self.rule is not None:
                for i in range(self.start, self.end):
                    self.strip.set_pixel(i, self.rule(pixel=i - self.start, seg_size=self.size()))
            else:
                for i in range(self.start, self.end):
                    self.strip.set_pixel(i, (0, 0, 0))

        def get_pixels(self):
            """
            :return: An array of colors for each pixel on this Segment.
            """
            return self.strip.get_pixels()[self.start:self.end]

        def size(self):
            """
            :return: The number of LEDs this Segment controls.
            """
            return self.end - self.start
