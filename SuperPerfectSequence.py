from PerfectSequence import PerfectSequence

class SuperPerfectSequence:
    
    def __init__(self, alphabet_size: int, iterations: int = 1):
        """
        Initialize a SuperPerfectSequence.

        Parameters
        ----------
        alphabet_size : int
            The size of the alphabet (must be >= 2).
        iterations : int, default=1
            Number of levels to build. Starting from level 1, the internal
            period is rebuilt `iterations - 1` times by calling `next_level()`.

        Raises
        ------
        TypeError
            If `alphabet_size` or `iterations` is not an int.
        ValueError
            If `alphabet_size < 2` or `iterations < 1`.
        """

        # Validate inputs
        if not isinstance(alphabet_size, int):
            raise TypeError("alphabet_size must be an int")
        if alphabet_size < 2:
            raise ValueError("alphabet_size must be >= 2")

        if not isinstance(iterations, int):
            raise TypeError("iterations must be an int")
        if iterations < 1:
            raise ValueError("iterations must be >= 1")

        self._alphabet_size = alphabet_size
        self._level = 1
        self._sequence = PerfectSequence(alphabet_size, 1)
        self._length = len(self._sequence)

        for _ in range(1, iterations):
            self.next_level()

    def next_level(self) -> None:
        """Advance by one level by continuing the infinity periodic sequence.

        Rebuilds the underlying PerfectSequence for the next level by
        constructing a new instance with the current alphabet size and
        current period length, then rotating it to align with the start
        of the previous period.
        """
        
        new_sequence = PerfectSequence(self._alphabet_size, self._length)
        new_sequence.rotate_to_start(self._sequence.sequence)
        self._sequence = new_sequence
        self._length = len(self._sequence)
        self._level += 1


    def __len__(self) -> int:
        """Return the period (length) of the sequence."""
        return self._length

    def __getitem__(self, index: int) -> int:
        """Return the symbol at the given (periodic) index.

        index must be integer.
        The sequence is cyclic, so any integer index is mapped modulo the
        period length.
        """
        return self._sequence[index % self._length]

    def __str__(self) -> str:
        """Return a string representation of the underlying cyclic sequence."""
        # WARNING: Can become very large for big alphabet_size/pattern_size because it joins the entire sequence.
        return str(self._sequence)

    def info(self) -> str:
        """Return human-readable summary of the configuration."""
        return f"level= {self._level}, {self._sequence.info()}"
        

if __name__ == "__main__":
    sps = SuperPerfectSequence(2)
    print(sps)
    sps.next_level()
    print(sps)
    sps.next_level()
    print(sps)
    print(sps.info())
    
    sps.next_level()
    print(sps.info())

    sps = SuperPerfectSequence(3,2)
    print("SuperPerfectSequence:",sps)