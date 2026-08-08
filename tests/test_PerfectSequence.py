import os
import pytest
import sys

# Get the absolute path of the current script
current_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the current_parent_dir directory to sys.path
sys.path.append(current_parent_dir)

from PerfectSequence import PerfectSequence


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 1),
        (3, 2),
        (4, 2),
    ],
)
def test_len_is_period(alphabet_size, pattern_size):
    ps = PerfectSequence(alphabet_size, pattern_size)
    assert len(ps) == alphabet_size ** pattern_size


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (2, 1),
        (3, 1),
        (2, 2),
        (3, 2),
        (4, 2),
    ],
)
def test_getitem_is_cyclic(alphabet_size, pattern_size):
    ps = PerfectSequence(alphabet_size, pattern_size)
    n = len(ps)
    for i in [0, 1, n - 1]:
        assert ps[i] == ps[i + n]
        assert ps[i] == ps[i - n]


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 1),
        (3, 2),
    ],
)
def test_iter_yields_correct_patterns_and_count(alphabet_size, pattern_size):
    ps = PerfectSequence(alphabet_size, pattern_size)
    seq = ps.sequence
    n = len(ps)
    m = pattern_size

    patterns = list(iter(ps))
    assert len(patterns) == n

    for start in range(n):
        expected = [seq[(start + offset) % n] for offset in range(m)]
        assert patterns[start] == expected


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 1),
        (3, 2),
        (4, 1),
    ],
)
def test_is_valid_for_small_params(alphabet_size, pattern_size):
    ps = PerfectSequence(alphabet_size, pattern_size)
    assert ps.is_valid() is True


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (2, 2),
        (3, 2),
    ],
)
def test_to_file_writes_exact_content(tmp_path, alphabet_size, pattern_size):
    ps = PerfectSequence(alphabet_size, pattern_size)
    out = tmp_path / "seq.txt"

    ps.to_file(str(out))

    with open(out, "r", encoding="utf-8") as f:
        content = f.read()

    # The current to_file behavior writes the whole sequence on one line
    # joined by _separator. Build the expected string from internal data.
    seq_str = ps._separator.join(map(str, ps.sequence))
    assert content == seq_str


@pytest.mark.parametrize(
    "alphabet_size,pattern_size",
    [
        (1, 1),
        (2, 0),
        ("2", 1),
        (2, "1"),
    ],
)
def test_constructor_validation(alphabet_size, pattern_size):
    with pytest.raises((TypeError, ValueError)):
        PerfectSequence(alphabet_size, pattern_size)
        
if __name__ == "__main__":
    pytest.main()
