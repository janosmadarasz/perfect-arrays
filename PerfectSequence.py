class PerfectSequence:

    """Represent a perfect sequence over a fixed alphabet = (0, 1, N-1) and pattern size

    Parameters
    ----------
    alphabet_size : int
        The number of symbols in the alphabet. Must be >= 2.
    pattern_size : int
        The length of each pattern (subsequence). Must be >= 1.

    Notes
    -----
    The generated internal sequence is periodic with period equal to
    ``alphabet_size ^ pattern_size``.
    """

    MIN_ALPHABET_SIZE = 2
    MIN_PATTERN_SIZE = 1
    DIGIT_SEPARATOR_THRESHOLD = 11

    def __init__(self, alphabet_size: int, pattern_size: int):
        """Create the perfect sequence.

        Parameters
        ----------
        alphabet_size : int
            Size of the alphabet. Must be >= 2.
        pattern_size : int
            Length of patterns to cover. Must be >= 1.
        """
        if not isinstance(alphabet_size, int):
            raise TypeError("alphabet_size must be an int")
        if not isinstance(pattern_size, int):
            raise TypeError("pattern_size must be an int")

        if alphabet_size < self.MIN_ALPHABET_SIZE:
            raise ValueError("alphabet_size must be >= 2")
        if pattern_size < self.MIN_PATTERN_SIZE:
            raise ValueError("pattern_size must be >= 1")


        self._alphabet_size = alphabet_size
        self._pattern_size = pattern_size
        self._length: int
        self._sequence: list[int]

        # Generate the perfect sequence.
        self._generate()

        # Ensure that the sequence has been generated.
        if self._length <= 0:
            raise RuntimeError("Internal error: _length must be > 0")
        if len(self._sequence) != self._length:
            raise RuntimeError("Internal error: _sequence length mismatch")

        # Use a space separator for values with ≥ 2 digits
        self._separator = "" if self._alphabet_size < self.DIGIT_SEPARATOR_THRESHOLD else " "


    def _generate(self) -> None:
        """Generate the perfect sequence.

        For pattern size = 1, the sequence is simply [0, 1, ..., alphabet size - 1].
        For larger pattern size, the sequence is constructed so that every
        pattern appears exactly once in the sequence.
        Implements the algorithm MARTIN from [2].
        """

        if self._pattern_size == 1:
            
            self._length = self._alphabet_size
            self._sequence = list(range(self._alphabet_size))
            return

        # Optimal-Martin algorithm

        # Initialise sequence
        self._length = self._alphabet_size ** self._pattern_size
        self._sequence = [0] * self._length

        # Initialise counter array
        length_of_counter_array = self._length // self._alphabet_size
        counter_array = [self._alphabet_size -1] * length_of_counter_array
        
        # Calculate the sequence 
        for i in range(self._pattern_size, self._length):
            k = self._sequence[i - self._pattern_size + 1]
            for j in range(2, self._pattern_size):
                k = k * self._alphabet_size + self._sequence[i - self._pattern_size + j]
            self._sequence[i] = counter_array[k]
            counter_array[k] = counter_array[k] - 1

    def __len__(self) -> int:
        """Return the period (length) of the perfect sequence."""
        return self._length

    def __getitem__(self, index: int) -> int:
        """Return the symbol at the given (periodic) index.

        The sequence is cyclic, so any integer index is mapped modulo the
        period length.
        """
        return self._sequence[index % self._length]

    def __iter__(self):
        """Iterate over all patterns.

        Yields
        ------
        list[int] - subsequence of sequence with length of pattern size.
            The pattern starting at each index (0... length of sequence - 1).
        """
        for pattern_start in range(self._length):
            yield [self._sequence[(pattern_start + offset) % self._length]
                for offset in range(self._pattern_size)]

    def __str__(self) -> str:
        """Return a string representation of the perfect sequence."""
        # WARNING: Can become very large for big alphabet_size/pattern_size because it joins the entire sequence.
        return self._separator.join(map(str, self._sequence))   

    def __repr__(self) -> str:
        """Return a concise representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"alphabet_size={self._alphabet_size}, "
            f"pattern_size={self._pattern_size}, "
            f"length={self._length})"
        )

    @property
    def sequence(self) -> list[int]:
        """Return the generated perfect sequence as a list."""
        return list(self._sequence)

    def info(self) -> str:
        """Return a human-readable summary of the configuration."""
        return (
            f"alphabet size: {self._alphabet_size}, "
            f"pattern size: {self._pattern_size}, length: {self._length}"
        )

    def is_valid(self) -> bool:
        """
        Check whether the generated cyclic sequence is a perfect sequence.

        For pattern_size == 1 the sequence is trivially valid.
        For larger pattern sizes, this method verifies that every contiguous
        cyclic pattern over the fixed alphabet
        appears exactly once among the windows in one full period.

        Returns
        -------
        bool
            True if every pattern appears exactly once (i.e., the sequence is
            perfect), otherwise False.
        """

        if self._pattern_size == 1:
            return True

        # Initialise checking array 
        check_array = bytearray(self._length)

        # Calculate the value of the last place in the pattern
        last_place_value = self._alphabet_size ** (self._pattern_size - 1)

        # Value for pattern starting at the beginning of the sequence (i=0)
        value = self._pattern_value(self._sequence[: self._pattern_size])

        # Go through the sequence  
        for i in range(self._length):

            # Check whether the value has already been found
            if check_array[value]:
                return False
            # It is a new value, so go on
            check_array[value] = 1

            # We reach the end of the sequence
            if i + 1 == self._length:
                break

            # Calculate the value of the rolling pattern
            out_digit = self._sequence[i]
            in_digit = self._sequence[(i + self._pattern_size) % self._length]
            value = self._roll_value(value, out_digit, in_digit, last_place_value)

        return True

    def rotate(self, shift: int) -> None:
        """
        Rotate the cyclic sequence by a constant offset.

        The internal sequence is treated as cyclic with period of self._length.
        If shift > 0, rotate right by shift.
        If shift < 0, rotate left by abs(shift).
        If shift == 0 or shift == self._length, the sequence would remain unchanged, which is not allowed.

        Parameters
        ----------
        shift : int
            Number of positions to rotate. Must satisfy
            1 <= abs(shift) <= self._length - 1 
            (i.e., it cannot be 0 and cannot rotate by a full period).

        Raises
        ------
        TypeError
            If shift is not an int.
        ValueError
            If shift is not in the allowed range.
        """
        if not isinstance(shift, int):
            raise TypeError("shift must be an int")

        if shift == 0 or not (1 <= abs(shift) <= self._length - 1):
            raise ValueError("shift must satisfy 1 <= abs(shift) <= self._length - 1")

        if shift > 0:
            # right by shift == left by (self._length - shift)
            s = self._length - shift
        else:
            # left by abs(shift)
            s = -shift

        self._sequence = self._sequence[s:] + self._sequence[:s]

    def reverse(self) -> None:
        """Reverse the perfect sequence in-place.

        After calling this method, the period (length) remains the same,
        but the order of symbols in the internal sequence is reversed.
        """
        self._sequence.reverse()

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

        for i in range(self._length):
            self._sequence[i] = (self._sequence[i] + shift) % self._alphabet_size

    def rotate_to_start(self, start_list: list[int]) -> None:
        """
        Rotate the cyclic sequence so it starts with a specific pattern.

        The internal sequence is treated as cyclic with period self._length.
        This method finds a pattern that matches start_list.
        Once found, the underlying sequence is rotated so that this
        matching pattern becomes the first pattern in the period.

        Parameters
        ----------
        start_list : list[int]
            Desired starting pattern. Must have length pattern_size and each
            symbol must be an integer in the range [0, alphabet_size).

        Raises
        ------
        ValueError
            If start_list does not have length pattern_size, contains invalid
            symbols, or if the pattern is not found in the perfect sequence.

        Notes
        -----
        A perfect sequence contains each contiguous pattern exactly once,
        so a valid start_list is expected to be found exactly once within the period.
        """

        if len(start_list) != self._pattern_size:
            raise ValueError("start_list must have length pattern_size")
        if any((not isinstance(x, int)) or x < 0 or x >= self._alphabet_size for x in start_list):
            raise ValueError("start_list contains symbols outside the alphabet range")

        seq = self._sequence

        target = self._pattern_value(start_list)

        last_place_value = self._alphabet_size ** (self._pattern_size - 1)

        # numeric value for the initial window starting at i = 0
        value = self._pattern_value(seq[: self._pattern_size])

        for start in range(self._length):
            if value == target:
                if start:
                    self._sequence = seq[start:] + seq[:start]
                return

            if start + 1 == self._length:
                break

            out_digit = seq[start]
            in_digit = seq[(start + self._pattern_size) % self._length]
            value = self._roll_value(value, out_digit, in_digit, last_place_value)

        raise ValueError("start_list not found in the sequence")


    def to_file(self, filepath: str) -> None:
        """Write the sequence values to a file (single line).

        Notes
        -----
        The output size is O(length). For large (alphabet_size, pattern_size),
        `length = alphabet_size ** pattern_size` grows quickly, so the produced
        file can become very large and the write operation may take noticeable
        time and disk space.
        """
        if not isinstance(filepath, str) or not filepath:
            raise ValueError("filepath must be a non-empty string")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self._separator.join(map(str, self._sequence)))


        
    def _pattern_value(self, digits: list[int]) -> int:
        """Convert a digit list to its base alphabet_size value."""
        value = 0
        for digit in digits:
            value = value * self._alphabet_size + digit
        return value

    def _roll_value(
        self,
        value: int,
        out_digit: int,
        in_digit: int,
        last_place_value: int,
    ) -> int:
        """Update a rolling pattern value."""
        return (value - out_digit * last_place_value) * self._alphabet_size + in_digit


if __name__ == "__main__":

    ps = PerfectSequence(2,2)
    print("Perfect sequence:",ps)
    print("All patterns in perfect sequence:")
    for pattern in ps:
        print(pattern)


    print(ps.info())
    print("Valid!" if ps.is_valid() else "Not valid!")

    print(ps.sequence)
    ps.rotate_to_start([0,1])
    print(ps)

    ps = PerfectSequence(3,1)
    print(ps) 
    print(ps.sequence)
    ps.reverse()
    print(ps.sequence)
    #ps.to_file("Ps.txt")

    ps = PerfectSequence(3,2)
    print(ps)
    ps.shift_symbols(1)
    print(ps)
    ps.rotate(-2)
    print(ps)