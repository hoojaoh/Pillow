#
# The Python Imaging Library.
# $Id$
#
# standard filters
#
# History:
# 1995-11-27 fl   Created
# 2002-06-08 fl   Added rank and mode filters
# 2003-09-15 fl   Fixed rank calculation in rank filter; added expand call
#
# Copyright (c) 1997-2003 by Secret Labs AB.
# Copyright (c) 1995-2002 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

import functools


class Filter(object):
    pass


class MultibandFilter(Filter):
    pass


class Kernel(MultibandFilter):
    """
    Create a convolution kernel.  The current version only
    supports 3x3 and 5x5 integer and floating point kernels.

    In the current version, kernels can only be applied to
    "L" and "RGB" images.

    :param size: Kernel size, given as (width, height). In the current
                    version, this must be (3,3) or (5,5).
    :param kernel: A sequence containing kernel weights.
    :param scale: Scale factor. If given, the result for each pixel is
                    divided by this value.  the default is the sum of the
                    kernel weights.
    :param offset: Offset. If given, this value is added to the result,
                    after it has been divided by the scale factor.
    """
    name = "Kernel"

    def __init__(self, size, kernel, scale=None, offset=0):
        if scale is None:
            # default scale is sum of kernel
            scale = functools.reduce(lambda a, b: a+b, kernel)
        if size[0] * size[1] != len(kernel):
            raise ValueError("not enough coefficients in kernel")
        self.filterargs = size, scale, offset, kernel

    def filter(self, image):
        if image.mode == "P":
            raise ValueError("cannot filter palette images")
        return image.filter(*self.filterargs)


class BuiltinFilter(Kernel):
    def __init__(self):
        pass


class RankFilter(Filter):
    """
    Create a rank filter.  The rank filter sorts all pixels in
    a window of the given size, and returns the **rank**'th value.

    :param size: The kernel size, in pixels.
    :param rank: What pixel value to pick.  Use 0 for a min filter,
                 ``size * size / 2`` for a median filter, ``size * size - 1``
                 for a max filter, etc.
    """
    name = "Rank"

    def __init__(self, size, rank):
        self.size = size
        self.rank = rank

    def filter(self, image):
        if image.mode == "P":
            raise ValueError("cannot filter palette images")
        image = image.expand(self.size//2, self.size//2)
        return image.rankfilter(self.size, self.rank)


class MedianFilter(RankFilter):
    """
    Create a median filter. Picks the median pixel value in a window with the
    given size.

    :param size: The kernel size, in pixels.
    """
    name = "Median"

    def __init__(self, size=3):
        self.size = size
        self.rank = size*size//2


class MinFilter(RankFilter):
    """
    Create a min filter.  Picks the lowest pixel value in a window with the
    given size.

    :param size: The kernel size, in pixels.
    """
    name = "Min"

    def __init__(self, size=3):
        self.size = size
        self.rank = 0


class MaxFilter(RankFilter):
    """
    Create a max filter.  Picks the largest pixel value in a window with the
    given size.

    :param size: The kernel size, in pixels.
    """
    name = "Max"

    def __init__(self, size=3):
        self.size = size
        self.rank = size*size-1


class ModeFilter(Filter):
    """
    Create a mode filter. Picks the most frequent pixel value in a box with the
    given size.  Pixel values that occur only once or twice are ignored; if no
    pixel value occurs more than twice, the original pixel value is preserved.

    :param size: The kernel size, in pixels.
    """
    name = "Mode"

    def __init__(self, size=3):
        self.size = size

    def filter(self, image):
        return image.modefilter(self.size)


class GaussianBlur(MultibandFilter):
    """Gaussian blur filter.

    :param radius: Blur radius.
    """
    name = "GaussianBlur"

    def __init__(self, radius=2):
        self.radius = radius

    def filter(self, image):
        return image.gaussian_blur(self.radius)


class BoxBlur(MultibandFilter):
    """Blurs the image by setting each pixel to the average value of the pixels
    in a square box extending radius pixels in each direction.
    Supports float radius of arbitrary size. Uses an optimized implementation
    which runs in linear time relative to the size of the image
    for any radius value.

    :param radius: Size of the box in one direction. Radius 0 does not blur,
                   returns an identical image. Radius 1 takes 1 pixel
                   in each direction, i.e. 9 pixels in total.
    """
    name = "BoxBlur"

    def __init__(self, radius):
        self.radius = radius

    def filter(self, image):
        return image.box_blur(self.radius)


class UnsharpMask(MultibandFilter):
    """Unsharp mask filter.

    See Wikipedia's entry on `digital unsharp masking`_ for an explanation of
    the parameters.

    :param radius: Blur Radius
    :param percent: Unsharp strength, in percent
    :param threshold: Threshold controls the minimum brightness change that
      will be sharpened

    .. _digital unsharp masking: https://en.wikipedia.org/wiki/Unsharp_masking#Digital_unsharp_masking

    """
    name = "UnsharpMask"

    def __init__(self, radius=2, percent=150, threshold=3):
        self.radius = radius
        self.percent = percent
        self.threshold = threshold

    def filter(self, image):
        return image.unsharp_mask(self.radius, self.percent, self.threshold)


class BLUR(BuiltinFilter):
    name = "Blur"
    filterargs = (5, 5), 16, 0, (
        1,  1,  1,  1,  1,
        1,  0,  0,  0,  1,
        1,  0,  0,  0,  1,
        1,  0,  0,  0,  1,
        1,  1,  1,  1,  1
        )


class CONTOUR(BuiltinFilter):
    name = "Contour"
    filterargs = (3, 3), 1, 255, (
        -1, -1, -1,
        -1,  8, -1,
        -1, -1, -1
        )


class DETAIL(BuiltinFilter):
    name = "Detail"
    filterargs = (3, 3), 6, 0, (
        0, -1,  0,
        -1, 10, -1,
        0, -1,  0
        )


class EDGE_ENHANCE(BuiltinFilter):
    name = "Edge-enhance"
    filterargs = (3, 3), 2, 0, (
        -1, -1, -1,
        -1, 10, -1,
        -1, -1, -1
        )


class EDGE_ENHANCE_MORE(BuiltinFilter):
    name = "Edge-enhance More"
    filterargs = (3, 3), 1, 0, (
        -1, -1, -1,
        -1,  9, -1,
        -1, -1, -1
        )


class EMBOSS(BuiltinFilter):
    name = "Emboss"
    filterargs = (3, 3), 1, 128, (
        -1,  0,  0,
        0,  1,  0,
        0,  0,  0
        )


class FIND_EDGES(BuiltinFilter):
    name = "Find Edges"
    filterargs = (3, 3), 1, 0, (
        -1, -1, -1,
        -1,  8, -1,
        -1, -1, -1
        )


class SHARPEN(BuiltinFilter):
    name = "Sharpen"
    filterargs = (3, 3), 16, 0, (
        -2, -2, -2,
        -2, 32, -2,
        -2, -2, -2
        )


class SMOOTH(BuiltinFilter):
    name = "Smooth"
    filterargs = (3, 3), 13, 0, (
        1,  1,  1,
        1,  5,  1,
        1,  1,  1
        )


class SMOOTH_MORE(BuiltinFilter):
    name = "Smooth More"
    filterargs = (5, 5), 100, 0, (
        1,  1,  1,  1,  1,
        1,  5,  5,  5,  1,
        1,  5, 44,  5,  1,
        1,  5,  5,  5,  1,
        1,  1,  1,  1,  1
        )


class Color3DLUT(MultibandFilter):
    """Three-dimensional color lookup table.

    Transforms 3-channel pixels using the values of the channels as coordinates
    in the 3D lookup table and interpolating the nearest elements.

    This method allows you to apply almost any color transformation
    in constant time by using pre-calculated decimated tables.

    :param size: Size of the table. One int or tuple of (int, int, int).
                 Minimal size in any dimension is 2, maximum is 65.
    :param table: Flat lookup table. A list of ``channels * size**3``
                  float elements or a list of ``size**3`` channels-sized
                  tuples with floats. Channels are changed first,
                  then first dimension, then second, then third.
                  Value 0.0 corresponds lowest value of output, 1.0 highest.
    :param channels: Number of channels in the table. Could be 3 or 4.
                     Default is 3.
    :param target_mode: A mode for the result image. Should have not less
                        than ``channels`` channels. Default is ``None``,
                        which means that mode wouldn't be changed.
    """
    name = "Color 3D LUT"

    def __init__(self, size, table, channels=3, target_mode=None):
        self.size = size = self._check_size(size)
        self.channels = channels
        self.mode = target_mode

        table = list(table)
        # Convert to a flat list
        if table and isinstance(table[0], (list, tuple)):
            table, raw_table = [], table
            for pixel in raw_table:
                if len(pixel) != channels:
                    raise ValueError("The elements of the table should have "
                                     "a length of {}.".format(channels))
                for color in pixel:
                    table.append(color)

        if len(table) != channels * size[0] * size[1] * size[2]:
            raise ValueError(
                "The table should have either channels * size**3 float items "
                "or size**3 items of channels-sized tuples with floats. "
                "Table size: {}x{}x{}. Table length: {}".format(
                    size[0], size[1], size[2], len(table)))
        self.table = table

    @staticmethod
    def _check_size(size):
        try:
            _, _, _ = size
        except ValueError:
            raise ValueError("Size should be either an integer or "
                             "a tuple of three integers.")
        except TypeError:
            size = (size, size, size)
        size = [int(x) for x in size]
        for size1D in size:
            if not 2 <= size1D <= 65:
                raise ValueError("Size should be in [2, 65] range.")
        return size

    @classmethod
    def generate(cls, size, callback, channels=3, target_mode=None):
        """Generates new LUT using provided callback.

        :param size: Size of the table. Passed to the constructor.
        :param callback: Function with three parameters which correspond
                         three color channels. Will be called ``size**3``
                         times with values from 0.0 to 1.0 and should return
                         a tuple with ``channels`` elements.
        :param channels: Passed to the constructor.
        :param target_mode: Passed to the constructor.
        """
        size1D, size2D, size3D = cls._check_size(size)
        table = []
        for b in range(size3D):
            for g in range(size2D):
                for r in range(size1D):
                    table.append(callback(
                        r / float(size1D-1),
                        g / float(size2D-1),
                        b / float(size3D-1)))

        return cls((size1D, size2D, size3D), table, channels, target_mode)

    def filter(self, image):
        from . import Image

        return image.color_lut_3d(
            self.mode or image.mode, Image.LINEAR, self.channels,
            self.size[0], self.size[1], self.size[2], self.table)