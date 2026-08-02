from PerfectSequence import PerfectSequence

class EvenPerfectSequence(PerfectSequence):
    """
    Generates the even perfect sequence for a given even alphabet size, 
    where the sequence length is alphabet_size squared.
    The generated sequence is stored in `self._sequence` 

    Args:
        alphabet_size: Size of the alphabet. Must be an even integer >= 2.
    """

    def __init__(self, alphabet_size: int):
        """
        Build the sequence for the given even alphabet size.
        Implements the algorithm EVEN from [2].

        Args:
            alphabet_size: Size of the alphabet (even integer >= 2).

        Raises:
            ValueError: If alphabet_size < 2 or alphabet_size is odd.
        """

        # Validate inputs
        if alphabet_size < self.MIN_ALPHABET_SIZE:
            raise ValueError(f"alphabet_size must be >= {self.MIN_ALPHABET_SIZE}.")
        if alphabet_size % 2 != 0:
            raise ValueError("alphabet_size must be even.")

        self._pattern_size = 2 
        self._alphabet_size = alphabet_size 

        # If alphabet size >= 11, then space separator needed.
        self._separator = "" if self._alphabet_size < self.DIGIT_SEPARATOR_THRESHOLD else " "

        self._length = alphabet_size * alphabet_size

        # Initialize temp array
        w = [0] * (self._length + 1)

        # Base case: for alphabet_size == 2, the sequence is "0011".
        w[3] = 1
        w[4] = 1
    
        for i in range(1, (alphabet_size // 2)):
            base = 4 * i * i

            for j in range(0, 2 * i):
                w[base + 2 * j + 1] = j

            for j in range(0, i):
                w[base + 2 + 4 * j] = 2 * i

            for j in range(0, i):
                w[base + 4 + 4 * j] = 2 * i + 1

            offset = base + 4 * i
            for j in range(0, 4 * i):
                w[offset + 1 + j] = w[offset - j]

            w[base + 8 * i + 1] = 2 * i + 1
            w[base + 8 * i + 2] = 2 * i
            w[base + 8 * i + 3] = 2 * i
            w[base + 8 * i + 4] = 2 * i + 1

        self._sequence = w[1:] 

if __name__ == "__main__":

    eps = EvenPerfectSequence(4)
    print(eps.info())
    print(eps)
    print("Valid!" if eps.is_valid() else "Not valid!")