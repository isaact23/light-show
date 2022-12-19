import enum, time, math, colorsys

def zero_to_one(num):
    """
    Ensure a number is between 0 and 1 by adding or subtracting 1.
    :param num: The number to normalize.
    :return: A number between 0 and 1.
    """
    while num < 0:
        num += 1
    while num > 1:
        num -= 1
    return num


class Mode(enum.Enum):
    """
    Different modes for color functions - determines whether colors change based on pixels or time.
    """
    PIXEL = 'pixel'
    TIME = 'time'

class Rule:
    """
    Class passable to Segments and LightStrips that determines LED colors at runtime.
    """

    def __init__(self):
        self.func_chain = []  # Every time a new function is generated, append it here.

    def __call__(self, **kwargs):
        """
        Evaluate this rule based on kwargs.
        :param kwargs: Properties needed to determine color, e.g. led index, segment size, etc.
        :return: The generated color.
        """
        if len(self.func_chain) == 0:
            return 0, 0, 0
        return self.func_chain[-1](**kwargs)

    # Primary rules - these generate colors and don't modify any functions.

    def fill(self, color, start=None, end=None):
        """
        Set LEDs in a range to the same color.
        :param color: The color to set all pixels to.
        :param start: The first pixel to modify (inclusive, optional).
        :param end: The last pixel to modify (exclusive, optional).
        """

        def f(**kwargs):
            if start is None or end is None or start <= kwargs['pixel'] < end:
                return color
            return 0, 0, 0

        self.func_chain.append(f)
        return self

    def hue_linear(self, frequency=1, mode=Mode.PIXEL):
        """
        Fill pixels with color hue increasing with every pixel.
        :param frequency: How fast hue should increase.
        :param mode: Color determination mode - either pixel or time.
        """
        start_time = time.time()

        def f(**kwargs):
            # Based on mode, determine the independent variable (i.e. what changes the color).
            var = 0
            if mode == Mode.PIXEL:
                var = kwargs['pixel']
            elif mode == Mode.TIME:
                var = time.time() - start_time
            else:
                raise RuntimeError("Mode", mode, "is invalid for Rule hue_linear().")

            hue = var * frequency / 360
            hue = zero_to_one(hue)
            rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            return tuple(round(c * 255) for c in rgb)

        self.func_chain.append(f)
        return self

    def hue_wave(self, low_hue, high_hue, frequency=1, mode=Mode.PIXEL):
        """
        Generate a rainbow sine wave ranging from low_hue to high_hue.
        :param low_hue: The low hue value (0 thru 360)
        :param high_hue: The high hue value (0 thru 360)
        :param frequency: How often waves should appear (inverse of wavelength).
        :param mode: Color determination mode - either pixel or time.
        """

        start_time = time.time()

        def f(**kwargs):
            # Based on mode, determine the independent variable (i.e. what changes the color).
            var = 0
            if mode == Mode.PIXEL:
                var = kwargs['pixel']
            elif mode == Mode.TIME:
                var = time.time() - start_time
            else:
                raise RuntimeError("Mode", mode, "is invalid for Rule hue_wave().")

            mid = ((high_hue + low_hue) / 2) / 360
            amplitude = (high_hue - low_hue) / 720
            hue = mid + amplitude * math.sin(var * frequency)

            # Ensure hue is between 0 and 1
            hue = zero_to_one(hue)

            # Generate RGB value from hue
            rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            return tuple(round(c * 255) for c in rgb)

        self.func_chain.append(f)
        return self

    def stripes(self, colors, width):
        """
        Generate stripes with alternating colors.
        :param colors: The colors to choose from.
        :param width: The width of each stripe.
        """

        def f(**kwargs):
            return colors[(kwargs['pixel'] // width) % len(colors)]

        self.func_chain.append(f)
        return self

    # Secondary rules - modify the existing Rule.

    def animate(self, speed):
        """
        Animate the original function, causing it to move over time.
        :param speed: The speed at which the function should move.
        """

        start_time = time.time()
        last_func = self.get_last_func()

        def f2(**kwargs):
            kwargs['pixel'] -= round((time.time() - start_time) * speed)
            return last_func(**kwargs)

        self.func_chain.append(f2)
        return self

    def blink(self, time_on, time_off, start_time=None):
        """
        Spend time_on with function enabled and time_off black, alternating.
        :param time_on: Time (s) with function enabled.
        :param time_off: Time (s) with lights off.
        :param start_time: Start time override (s).
        """

        if start_time is None:
            start_time = time.time()
        last_func = self.get_last_func()

        def f2(**kwargs):
            time_elapsed = time.time() - start_time
            time_since_blink = time_elapsed % (time_on + time_off)
            if time_since_blink < time_on:
                return last_func(**kwargs)
            else:
                return 0, 0, 0

        self.func_chain.append(f2)
        return self

    def crop(self, first=None, last=None):
        """
        Only show the pixels within a specified range.
        :param first: First pixel in the range (inclusive, optional)
        :param last: Last pixel in the range (exclusive, optional)
        """
        last_func = self.get_last_func()

        def f2(**kwargs):
            if first is not None and kwargs['pixel'] < first:
                return 0, 0, 0
            if last is not None and kwargs['pixel'] >= last:
                return 0, 0, 0
            return last_func(**kwargs)

        self.func_chain.append(f2)
        return self

    def fade_in(self, fade_time, delay):
        """
        Fade from black to the function color.
        :param fade_time: How long the fade effect should take.
        :param delay: Time in seconds to wait to fade in.
        """

        start_time = time.time()
        last_func = self.get_last_func()

        def f2(**kwargs):
            time_elapsed = time.time() - start_time
            if time_elapsed < delay:
                return 0, 0, 0
            full_color = last_func(**kwargs)
            if fade_time == 0 or time_elapsed > fade_time + delay:
                return full_color
            percent = (time.time() - delay - start_time) / fade_time
            new_color = tuple(round(c * percent) for c in full_color)
            return new_color

        self.func_chain.append(f2)
        return self

    def fade_out(self, fade_time, delay):
        """
        Fade from the function color to black.
        :param fade_time: How long the fade effect should take.
        :param delay: Time in seconds to wait to fade out.
        """

        start_time = time.time()
        last_func = self.get_last_func()

        def f2(**kwargs):
            time_elapsed = time.time() - start_time
            if time_elapsed > fade_time + delay:
                return 0, 0, 0
            full_color = last_func(**kwargs)
            if time_elapsed < delay:
                return full_color
            percent = 1 - ((time.time() - delay - start_time) / fade_time)
            new_color = round(full_color[0] * percent), round(full_color[1] * percent), round(full_color[2] * percent)
            return new_color

        self.func_chain.append(f2)
        return self

    def flip(self):
        """
        Flip the original function, so the last pixel is in the place of the first pixel, etc.
        """

        last_func = self.get_last_func()

        def f2(**kwargs):
            kwargs['pixel'] = kwargs['seg_size'] - kwargs['pixel']
            return last_func(**kwargs)

        self.func_chain.append(f2)
        return self

    def offset(self, pixels):
        """
        Shift this Rule by a certain number of pixels.
        :param pixels: The number of pixels to shift.
        """

        last_func = self.get_last_func()

        def f2(**kwargs):
            kwargs['pixel'] += pixels
            return last_func(**kwargs)

        self.func_chain.append(f2)
        return self

    # Others - fade, ripple, etc.

    # Miscellaneous functions

    def get_last_func(self):
        """
        :return: The last function in the function chain.
        """
        if len(self.func_chain) == 0:
            raise RuntimeError("Tried to call modifier function on Rule without defining the rule first.")
        return self.func_chain[-1]
