import ctypes
from ctypes import c_int, c_double
import os

def relative(*av):
    return os.path.join(
        os.path.dirname(__file__), *av
    )


class SWTParams(ctypes.Structure):
    _fields_ = [
        ('interval', c_int),        # [1] Intervals for scale invariant option.
        ('min_neighbors', c_int),   # [1] Minimal neighbors to make a detection valid, this is for scale-invariant version.
        ('scale_invariant', c_int), # [0] Enable scale invariant swt (to scale to different sizes and then combine the results)
        ('direction', c_int),       # [0] SWT direction. (black to white or white to black).
        ('same_word_thresh_1', c_double),  # [0.1] Overlapping more than 0.1 of the bigger one (0), and 0.9 of the smaller one (1)
        ('same_word_thresh_2', c_double),  # [0.8]

        # Canny parameters
        ('size', c_int),  # [3] Parameters for Canny edge detector.
        ('low_thresh', c_int),  # [124] Parameters for Canny edge detector.
        ('high_thresh', c_int),  # [204] Parameters for Canny edge detector.

        # Geometry filtering parameters
        ('max_height', c_int),  # [300] The maximum height for a letter.
        ('min_height', c_int),  # [8] The minimum height for a letter.
        ('min_area', c_int), # [38], The minimum occupied area for a letter.
        ('letter_occlude_thresh', c_int),  # [3]
        ('aspect_ratio', c_double),  # [8] The maximum aspect ratio for a letter.
        ('std_ratio', c_double),  # [0.83] The inner-class standard derivation when grouping letters.

        # Grouping parameters
        ('thickness_ratio', c_double),  # [1.5] The allowable thickness variance when grouping letters.
        ('height_ratio', c_double),     # [1.7] The allowable height variance when grouping letters.
        ('intensity_thresh', c_int),   # [31] The allowable intensity variance when grouping letters.
        ('distance_ratio', c_double),   # [2.9] The allowable distance variance when grouping letters.
        ('intersect_ratio', c_double),  # [1.3] The allowable intersect variance when grouping letters.
        ('elongate_ratio', c_double),   # [1.9] The allowable elongate variance when grouping letters.
        ('letter_thresh', c_int),      # [3] The allowable letter threshold.

        # Break text line into words
        ('breakdown', c_int),   # [1] Whether to break text lines into words.
        ('breakdown_ratio', c_double),   # [1.0] Apply OSTU and if inter-class variance above the threshold, it will be broken down into words.
    ]

class SWTRect(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int)
    ]

p_SWTRect = ctypes.POINTER(SWTRect)

swtlib = ctypes.CDLL(relative('../build/lib/libswt.dylib'))
swtlib.swt_detect.restype = ctypes.c_void_p
swtlib.swt_free.argtypes = [ctypes.c_void_p]
swtlib.swt_len.argtypes = [ctypes.c_void_p]
swtlib.swt_get.argtypes = [ctypes.c_void_p, ctypes.c_int]
swtlib.swt_get.restype = p_SWTRect


def swt(img,
    direction=0,
    interval=1,
    same_word_thresh=(0.1, 0.8),
    min_neighbors=1,
    scale_invariant=0,
    size=3,
    low_thresh=124,
    high_thresh=204,
    max_height=300,
    min_height=8,
    min_area=38,
    letter_occlude_thresh=3,
    aspect_ratio=8,
    std_ratio=0.83,
    thickness_ratio=1.5,
    height_ratio=1.7,
    intensity_thresh=31,
    distance_ratio=2.9,
    intersect_ratio=1.3,
    letter_thresh=3,
    elongate_ratio=1.9,
    breakdown=1,
    breakdown_ratio=1.0,
):

    params = SWTRect(
        direction=direction,
        interval=interval,
        same_word_thresh_1=same_word_thresh[0],
        same_word_thresh_2=same_word_thresh[1],
        min_neighbors=min_neighbors,
        scale_invariant=scale_invariant,
        size=size,
        low_thresh=low_thresh,
        high_thresh=high_thresh,
        max_height=max_height,
        min_height=min_height,
        min_area=min_area,
        letter_occlude_thresh=letter_occlude_thresh,
        aspect_ratio=aspect_ratio,
        std_ratio=std_ratio,
        thickness_ratio=thickness_ratio,
        height_ratio=height_ratio,
        intensity_thresh=intensity_thresh,
        distance_ratio=distance_ratio,
        intersect_ratio=intersect_ratio,
        letter_thresh=letter_thresh,
        elongate_ratio=elongate_ratio,
        breakdown=breakdown,
        breakdown_ratio=breakdown_ratio,
    )

    width, height = img.size
    # img = ImageOps.invert(img)
    bb = img.convert('L').tobytes()
    boxes = swtlib.swt_detect(bb, width, height, params)
    if boxes is None:
        return

    num_boxes = swtlib.swt_len(boxes)
    for i in range(num_boxes):
        box = swtlib.swt_get(boxes, i)
        x, y, width, height = box.contents.x, box.contents.y, box.contents.width, box.contents.height
        yield x, y, x+width, y+height

    swtlib.swt_free(boxes)
