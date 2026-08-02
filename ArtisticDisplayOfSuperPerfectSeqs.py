from PIL import Image, ImageDraw, ImageColor
import math
from SuperPerfectSequence import SuperPerfectSequence


BACKGROUND = (224, 224, 224)
BLACK = (0, 0, 0)


def sequence_in_clockwise_spiral(
    sequence: SuperPerfectSequence,
    max_number_of_circles: int,
    colors: list,
    filename: str,
    just_show: bool,
) -> None:
    """
    Draws the first `max_number_of_circles` elements of `sequence` as filled circles placed
    along a clockwise spiral, and either saves the result to `filename` or displays it.

    Each circle uses `sequence[j]` as an index into `colors` and is drawn with a black outline.
    Consecutive circles are connected with a thin black line.

    Args:
        sequence: Sequence of integers; each value is used as an index into `colors`.
        max_number_of_circles: Number of circles to draw from the start of `sequence`.
            Must be <= len(sequence). Also must be non-negative.
        colors: List of RGB colors (PIL-compatible), indexed by values from `sequence`.
        filename: Output image filename when `just_show` is False.
        just_show: If True, calls `im.show()`. If False, saves the image to `filename`.

    Raises:
        ValueError: If `max_number_of_circles` is greater than len(sequence),
            if it is negative, or if `colors` is empty.
        IndexError: If any sequence value is out of bounds for the `colors` list.
    """

    if max_number_of_circles > len(sequence):
        raise ValueError(
            f"max_number_of_circles must be <= len(sequence) "
            f"({len(sequence)}), got {max_number_of_circles}"
        )
    if not colors:
        raise ValueError("colors must not be empty")

    image_width = image_height = 800
    im = Image.new("RGB", (image_width, image_height), BACKGROUND)
    draw = ImageDraw.Draw(im)

    cx = cy = image_width // 2
    cr = 5

    t = 0.0
    a, b = 15.0, 5.0

    draw_line = False
    line_prev_x = line_prev_y = 0.0

    for j in range(max_number_of_circles):
        r = a + b * t
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)

        x0, y0 = x - cr, y - cr
        x1, y1 = x + cr, y + cr

        color_idx = sequence[j]
        if not (0 <= color_idx < len(colors)):
            raise IndexError(
                f"sequence[{j}]={color_idx} out of bounds for colors length {len(colors)}"
            )

        draw.ellipse((x0, y0, x1, y1), fill=colors[color_idx], outline=BLACK)

        if draw_line:
            draw.line([(line_prev_x, line_prev_y), (x, y)], fill=BLACK, width=1)
        else:
            draw_line = True

        line_prev_x, line_prev_y = x, y
        t += (60.0 * math.pi) / 1000.0

    if just_show:
        im.show()
    else:
        im.save(filename)


def sequence_in_clockwise_spiral_grid(
    sequence: SuperPerfectSequence,
    square_size: int,
    rectangle_size: int,
    colors: list,
    filename: str,
    just_show: bool,
) -> None:
    """
    Draws the first `square_size * square_size` elements of `sequence` into a grid of squares,
    traversed along a spiral-like path, and either saves the result to `filename` or displays it.

    The grid consists of square cells sized by `rect_width = rectangle_size` and
    `rect_height = rectangle_size` (with overall canvas size derived from `square_size`).
    Each visited cell uses `sequence[num_squares]` as an index into `colors` and is drawn
    with a black outline.

    Args:
        sequence: Sequence of integers; each value is used as an index into `colors`.
        square_size: Grid dimension; the expected number of squares is `square_size * square_size`.
        rectangle_size: Pixel size of each grid cell side (both width and height).
        colors: List of RGB colors (PIL-compatible), indexed by values from `sequence`.
        filename: Output image filename when `just_show` is False.
        just_show: If True, calls `im.show()`. If False, saves the image to `filename`.

    Raises:
        ValueError: If `sequence` is shorter than `square_size * square_size`,
            or if `colors` is empty.
        IndexError: If any sequence value is out of bounds for the `colors` list.
        RuntimeError: If the function did not draw exactly the expected number of squares
            (internal consistency check).
    """

    expected_len = square_size * square_size
    if len(sequence) < expected_len:
        raise ValueError(f"sequence length must be {expected_len}, got {len(sequence)}")
    if not colors:
        raise ValueError("colors must not be empty")

    rect_width = rectangle_size
    rect_height = rectangle_size
    image_width = square_size * rect_width
    image_height = image_width

    im = Image.new("RGB", (image_width, image_height), BACKGROUND)
    draw = ImageDraw.Draw(im)

    start_i = start_j = square_size // 2 if square_size % 2 else square_size // 2 - 1
    current_i, current_j = start_i, start_j

    moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    num_squares = 0
    d = 1
    for i in range((square_size * 2) - 1):
        for _ in range(d):
            if num_squares >= expected_len:
                break

            color_idx = sequence[num_squares]
            if not (0 <= color_idx < len(colors)):
                raise IndexError(
                    f"sequence[{num_squares}]={color_idx} out of bounds for colors length {len(colors)}"
                )

            x0 = rect_width * current_i
            y0 = rect_height * current_j
            x1 = rect_width * (current_i + 1)
            y1 = rect_height * (current_j + 1)

            draw.rectangle((x0, y0, x1, y1), fill=colors[color_idx], outline=BLACK)

            num_squares += 1
            di, dj = moves[i % 4]
            current_i += di
            current_j += dj

        d = d + (i % 2)

    if num_squares != expected_len:
        raise RuntimeError(f"Internal error: drew {num_squares} squares, expected {expected_len}")

    if just_show:
        im.show()
    else:
        im.save(filename)


'''
Drawing part of infinite SuperPerfectSequences

'''

list_of_colors = [
    ImageColor.getrgb("white"),
    ImageColor.getrgb("black"),
    ImageColor.getrgb("red"),
    ImageColor.getrgb("green"),
    ImageColor.getrgb("blue"),
    ImageColor.getrgb("yellow"),
    ImageColor.getrgb("purple"),
    ImageColor.getrgb("orange"),
]

just_show = False 

sequence_in_clockwise_spiral(SuperPerfectSequence(2, 4), 417, list_of_colors, "results/Super_perfect_seq_in_spiral_alpha_2.png", just_show)
sequence_in_clockwise_spiral(SuperPerfectSequence(6, 2), 417, list_of_colors, "results/Super_perfect_seq_in_spiral_alpha_4.png", just_show)
sequence_in_clockwise_spiral_grid(SuperPerfectSequence(2, 4), 256, 4, list_of_colors, "results/Super_perfect_seq_in_square_alpha_2.png", just_show)
sequence_in_clockwise_spiral_grid(SuperPerfectSequence(6,2), 216, 4, list_of_colors, "results/Super_perfect_seq_in_square_alpha_6.png", just_show)
