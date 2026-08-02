from PerfectSequence import PerfectSequence
from EvenPerfectSequence import EvenPerfectSequence
from PIL import Image

class PerfectMap:

    MIN_ALPHABET_SIZE = 2
    MIN_SUB_ARRAY_SIZE = 2 
    DIGIT_SEPARATOR_THRESHOLD = 11

    def __init__(self, alphabet_size: int, sub_array_rows: int, sub_array_cols: int):
    
        # Validate input parameters
        if alphabet_size < self.MIN_ALPHABET_SIZE: 
            raise ValueError("alphabet size must be >= 2")
        if sub_array_rows < self.MIN_SUB_ARRAY_SIZE:
            raise ValueError("sub_array_rows must be >= 2")
        if sub_array_cols < self.MIN_SUB_ARRAY_SIZE:
            raise ValueError("sub_array_cols must be >= 2")

        self._alphabet_size = alphabet_size
        self._sub_array_rows = sub_array_rows 
        self._sub_array_cols = sub_array_cols

        # Generate the perfect map.
        if alphabet_size % 2 == 0 and sub_array_cols == 2:

            # Special cases when alphabet_size is even and the sub-array has 2 columns.    
            if sub_array_rows == 2 :
                # meshing construction
                self._meshing()
            else:
                # horizontal tiling with shifts
                self._horizontal_tiling()
        else:
            # Otherwise: vertical tiling construction
            self._vertical_tiling()

        # Ensure that the map has been generated.
        if self._array_rows <= 0:
            raise RuntimeError("Internal error: _array_rows must be > 0")
        if self._array_cols <= 0:
            raise RuntimeError("Internal error: _array_cols must be > 0")
        if self._array is None:
            raise RuntimeError("Internal error: _array is None")

        # Use a space separator for values with ≥ 2 digits
        self._separator = "" if self._alphabet_size < self.DIGIT_SEPARATOR_THRESHOLD else " "

    
    def _meshing(self) -> None:
        """Generate the perfect map from one even perfect sequence.
        When alphabet_size is even and the sub-array has 2 columns and 2 rows. 
        Implements the algorithm MESH from [2].
        """

        sequence = EvenPerfectSequence(self._alphabet_size)

        array_side =  self._alphabet_size ** 2

        self._array_rows = array_side
        self._array_cols = array_side

        self._array = [[0 for _ in range(array_side)] for _ in range(array_side)]

        for i in range(array_side):
            for j in range(array_side):
                if (i+j) % 2 == 0:
                    self._array[i][j] = sequence[i]
                else:
                    self._array[i][j] = sequence[j]

    def _vertical_tiling(self) -> None:
        """Generate the perfect map from two perfect sequences. 
        Implements the algorithm PLANAR from [1].
        """

        vertical_sequence = PerfectSequence(self._alphabet_size, self._sub_array_rows)
        self._array_rows = len(vertical_sequence)

        shifting_sequence = PerfectSequence(self._alphabet_size ** self._sub_array_rows, (self._sub_array_cols - 1))
        self._array_cols = len(shifting_sequence)


        self._array = [[0 for _ in range(self._array_cols)] for _ in range(self._array_rows)]

        agg_shift = 0 
        for col in range(self._array_cols):
            agg_shift +=  shifting_sequence[col]

            for row in range(self._array_rows):
                self._array[row][col] = vertical_sequence[row + agg_shift]

    def _horizontal_tiling(self) -> None:
        """Generate the perfect map from two perfect sequences.
        When alphabet_size is even and the sub-array has 2 columns and more than 2 rows. 
        Implements the algorithm MESH from [2].
        """

        horizontal_sequence = PerfectSequence(self._alphabet_size, self._sub_array_cols)
        self._array_cols = len(horizontal_sequence)

        shifting_sequence = PerfectSequence(self._alphabet_size ** self._sub_array_cols, (self._sub_array_rows - 1))
        self._array_rows = len(shifting_sequence)

        self._array = [[0 for _ in range(self._array_cols)] for _ in range(self._array_rows)]

        agg_shift = 0
        for row in range(self._array_rows):
            agg_shift += shifting_sequence[row]

            for col in range(self._array_cols):
                self._array[row][col] = horizontal_sequence[col + agg_shift]


    def transpose(self) -> None:
        """Transposes the 2D backing array (swaps rows and columns).

        After transposition, the torus dimensions and the backing data are updated
        so that element (r, c) becomes (c, r).
        """
        self._array = [list(row) for row in zip(*self._array)]
        self._array_rows, self._array_cols = self._array_cols, self._array_rows

        
    def __getitem__(self, key: tuple):
        """
        Periodic (toroidal) indexing into the perfect map.

        Parameters:
            key: tuple
                A 2-tuple of the form (row, col).

        Returns:
            int
                The value at (row % self._array_rows, col % self._array_cols).

        Raises:
            TypeError: if `key` is not a 2-tuple.
        """
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("__getitem__ expects a (row, col) tuple indexing.")
        row, col = key
        return self._array[row % self._array_rows][col % self._array_cols]

    def __iter__(self):
        """Iterate over all toroidal sub-arrays.

        Each iteration yields a 2D list of shape:
            (sub_array_rows x sub_array_cols)

        The sub-array is taken with its top-left corner at each (row, col)
        position of the backing periodic array (row-major order).
        """
        rows = self._array_rows
        cols = self._array_cols
        subrows = self._sub_array_rows
        subcols = self._sub_array_cols

        for top in range(rows):
            for left in range(cols):
                sub = []
                for pos_in_sub_row in range(subrows):
                    actual_row = top + pos_in_sub_row
                    row_vals = []
                    for pos_in_sub_col in range(subcols):
                        actual_col = left + pos_in_sub_col
                        row_vals.append(self[actual_row, actual_col])  # periodic indexing via __getitem__
                    sub.append(row_vals)
                yield sub

    def is_valid(self) -> bool:
        """
        Check whether the current PerfectMap is valid.

        For each (row, col) position, compute the value of the
        sub-array of size (sub_array_rows x sub_array_cols) starting at that
        position, using toroidal/periodic indexing.

        Digits from the map are interpreted as a base-`alphabet_size` number:
            sub_array_value = sum(digit_i * alphabet_size^i)

        The map is valid if all computed sub-array values are unique across
        the entire (array_rows x array_cols) toroidal array.

        Returns:
            bool: True if all computed sub-array values are unique, otherwise False.
        """
        rows = self._array_rows
        cols = self._array_cols
        a = self._alphabet_size

        sr = self._sub_array_rows
        sc = self._sub_array_cols
        K = sr * sc

        # precompute powers
        # weights: 1, a, a^2, ..., a^(K-1)
        weights = [1] * K
        for i in range(1, K):
            weights[i] = weights[i - 1] * a

        check = bytearray(rows * cols)
        arr = self._array

        for row in range(rows):
            r_base = row
            for col in range(cols):
                sub_array_value = 0
                idx = 0

                c_base = col
                for sub_row in range(sr):
                    r = r_base + sub_row
                    arr_r = arr[r % rows]

                    for sub_col in range(sc):
                        sub_array_value += arr_r[(c_base + sub_col) % cols] * weights[idx]
                        idx += 1

                if check[sub_array_value]:
                    return False
                check[sub_array_value] = 1

        return True
    
    def rotate_horizontal(self, shift: int) -> None:
        """
        Rotate the map horizontally in-place (i.e., rotate columns within each row).

        Positive `shift` rotates to the right.
        Negative `shift` rotates to the left.

        Raises:
            TypeError: if `shift` is not an int.
            ValueError: if `shift == 0` or if `abs(shift) >= self._array_cols`.
        """
        if not isinstance(shift, int):
            raise TypeError("shift must be an int")

        if shift == 0 or abs(shift) >= self._array_cols:
            raise ValueError("shift must satisfy 1 <= abs(shift) <= self._array_cols - 1")

        # Normalize to a right rotation in [1, _array_cols-1]
        s = shift % self._array_cols  # s in {1, ..., _array_cols-1}

        for r in range(self._array_rows):
            row = self._array[r]
            # Right rotation by s: [..][-(s):] + [..][:-s]
            self._array[r] = row[-s:] + row[:-s]

    def rotate_vertical(self, shift: int) -> None:
        """
        Rotate the map vertically in-place (i.e., rotate rows within each column).

        Positive `shift` rotates downward.
        Negative `shift` rotates upward.

        Raises:
            TypeError: if `shift` is not an int.
            ValueError: if `shift == 0` or if `abs(shift) >= self._array_rows`.
        """
        if not isinstance(shift, int):
            raise TypeError("shift must be an int")

        if shift == 0 or abs(shift) >= self._array_rows:
            raise ValueError("shift must satisfy 1 <= abs(shift) <= self._array_rows - 1")

        # Normalize to a downward rotation in [1, _array_rows-1]
        s = shift % self._array_rows  # s in {1, ..., _array_rows-1}

        # Rotate by moving rows: new[r][c] = old[(r - s) mod rows][c]
        old = [row[:] for row in self._array]  # copy to rotate correctly
        for r in range(self._array_rows):
            src_r = (r - s) % self._array_rows
            self._array[r] = old[src_r]

    def __str__(self) -> str:
        return "\n".join(self._separator.join(str(num) for num in row) for row in self._array)

    def to_file(self, filepath: str) -> None:
        """Write the self._array values to the given file."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(self._separator.join(str(num) for num in row) for row in self._array))

    def info(self) -> str:
        """Return a human-readable summary of the configuration."""
        return f"alphabet size = {self._alphabet_size}, {self._sub_array_rows} x {self._sub_array_cols}, {self._array_rows} x {self._array_cols}"

    def shift_symbols(self, shift: int) -> None:
        """Shift every symbol by a constant offset (mod alphabet size).

        Parameters
        ----------
        shift : int
            The offset to add to each symbol. Must satisfy
            1 <= shift < alphabet_size.
        """
        if not isinstance(shift, int):
            raise TypeError("shift must be an int")
        if shift < 1 or shift >= self._alphabet_size:
            raise ValueError("shift must satisfy 1 <= shift < alphabet_size")

        for row in range(self._array_rows):
            for col in range(self._array_cols):
                self._array[row][col] = (self._array[row][col] + shift) % self._alphabet_size

    def to_pixel_image(
        self,
        filepath: str | None = None,
        colors: list[tuple[int, int, int]] | None = None,
        scale: int = 1,
    ):

        """
        Render this PerfectMap as an RGB pixel image.

        Each entry of the underlying integer array (values in [0, alphabet_size - 1])
        is drawn as a solid square of size (scale x scale) pixels.

        Args:
            filepath: If provided, the image is saved to this path and the function returns None.
                    If None, the PIL Image object is returned.
            colors: Optional palette of RGB tuples (R, G, B). The i-th entry in this list
                    is used for array value i. Must contain at least `self._alphabet_size`
                    colors. If None, a default palette is used.
            scale: Pixel size multiplier. Each array cell becomes a (scale x scale) block.

        Returns:
            PIL.Image.Image if `filepath` is None, otherwise None.

        Raises:
            ValueError: If `scale < 1`, or if `colors` is provided with fewer than `self._alphabet_size`
                        elements.
        """

        if not isinstance(scale, int) or scale < 1:
            raise ValueError("scale must be an int >= 1")

        rows, cols = self._array_rows, self._array_cols
        n = self._alphabet_size

        if colors is None:
            colors = [
                (0,0,0),(255,250,240),
                (255,0,0),(0,255,0),(0,0,255),
                (0,255,255),(255,0,255,),(255,255,0)
            ]

        if len(colors) < n:
            raise ValueError("colors must have at least alphabet_size elements")

        img = Image.new("RGB", (cols * scale, rows * scale))
        px = img.load()

        # array values are in [0, alphabet_size-1]
        for r in range(rows):
            y0 = r * scale
            for c in range(cols):
                x0 = c * scale
                col = colors[self._array[r][c]]
                for dy in range(scale):
                    yy = y0 + dy
                    for dx in range(scale):
                        px[x0 + dx, yy] = col

        if filepath is not None:
            img.save(filepath)
            return None
        return img
   

if __name__ == "__main__":

    pm = PerfectMap(2,2,2)
    print(pm.info())
    print(pm)
    print("Valid!" if pm.is_valid() else "Not valid!")

    print("All subarray in the perfect map:")
    number = 0
    for subarray in pm:
        number +=1 
        print(f"{number:2d}. {subarray}")

    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=2_2_2_4_4.png", scale = 100)

    pm = PerfectMap(2,3,2)
    print(pm.info())
    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=2_3_2_16_4.png",scale = 30)

    pm = PerfectMap(2,3,3)
    print(pm.info())
    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=2_3_3_8_64.png",scale = 20)

    pm = PerfectMap(3,2,2)
    print(pm.info())
    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=3_2_2_9_9.png",scale = 50)

    pm = PerfectMap(4,2,2)
    print(pm.info())
    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=4_2_2_16_16.png",scale = 30)

    pm = PerfectMap(6,2,2)
    print(pm.info())
    pm.to_pixel_image(filepath = "results/Perfect_map_alpha=6_2_2_36_36.png",scale = 10)
