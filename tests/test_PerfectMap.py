import os
import pytest
import sys

# Get the absolute path of the current script
current_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the current_parent_dir directory to sys.path
sys.path.append(current_parent_dir)

from PerfectMap import PerfectMap


@pytest.mark.parametrize(
    "alphabet_size, sub_array_rows, sub_array_cols",
    [
        (1, 2, 2),  # alphabet_size too small
        (2, 1, 2),  # sub_array_rows too small
        (2, 2, 1),  # sub_array_cols too small
    ],
)
def test_init_validation_raises(alphabet_size, sub_array_rows, sub_array_cols):
    with pytest.raises(ValueError):
        PerfectMap(alphabet_size, sub_array_rows, sub_array_cols)


@pytest.mark.parametrize(
    "alphabet_size, sub_array_rows, sub_array_cols",
    [
        (2, 2, 2),
        (2, 2, 3),
        (2, 3, 2),
        (4, 2, 2),
        (4, 2, 3),
        (4, 3, 2),
    ],
)
def test_map_is_valid(alphabet_size, sub_array_rows, sub_array_cols):
    pm = PerfectMap(alphabet_size, sub_array_rows, sub_array_cols)
    assert pm.is_valid() is True


def test_getitem_periodic_indexing_wraps():
    pm = PerfectMap(4, 2, 3)
    rows = pm._array_rows
    cols = pm._array_cols

    assert pm[rows, 0] == pm[0, 0]
    assert pm[0, cols] == pm[0, 0]
    assert pm[rows + 1, cols + 2] == pm[1, 2]


def test_getitem_type_error_for_wrong_key():
    pm = PerfectMap(2, 2, 2)

    with pytest.raises(TypeError):
        _ = pm[0]  # not a (row, col) tuple
    with pytest.raises(TypeError):
        _ = pm[(0,)]  # wrong tuple length
    with pytest.raises(TypeError):
        _ = pm["not a tuple"]


@pytest.mark.parametrize(
    "alphabet_size, sub_array_rows, sub_array_cols",
    [
        (2, 2, 2),
        (4, 2, 3),
        (4, 3, 2),
    ],
)
def test_iter_yields_correct_number_and_shape(
    alphabet_size, sub_array_rows, sub_array_cols
):
    pm = PerfectMap(alphabet_size, sub_array_rows, sub_array_cols)

    rows = pm._array_rows
    cols = pm._array_cols

    expected_yields = rows * cols
    produced = 0

    for sub in pm:
        produced += 1

        assert isinstance(sub, list)
        assert len(sub) == sub_array_rows
        assert all(isinstance(r, list) for r in sub)
        assert all(len(r) == sub_array_cols for r in sub)

        # Values should be in [0, alphabet_size - 1]
        for r in sub:
            for x in r:
                assert 0 <= x < alphabet_size

    assert produced == expected_yields


def test_transpose_swaps_dimensions_and_preserves_periodic_mapping():
    pm = PerfectMap(4, 3, 2)

    before_rows = pm._array_rows
    before_cols = pm._array_cols

    a00 = pm[0, 0]
    a10 = pm[1, 0]  # old value at (1,0)
    a01 = pm[0, 1]  # old value at (0,1)

    pm.transpose()

    assert pm._array_rows == before_cols
    assert pm._array_cols == before_rows

    # After transpose, (r, c) should become (c, r)
    assert pm[0, 0] == a00
    assert pm[0, 1] == a10
    assert pm[1, 0] == a01


@pytest.mark.parametrize("shift", [-1, 1, 2, -2])
def test_rotate_horizontal_matches_expected_shift(shift):
    pm = PerfectMap(4, 2, 3)
    rows = pm._array_rows
    cols = pm._array_cols

    if shift == 0 or abs(shift) >= cols:
        pytest.skip("Expected ValueError in current implementation.")

    before = [row[:] for row in pm._array]
    pm.rotate_horizontal(shift)

    s = shift % cols
    for r in range(rows):
        expected = before[r][-s:] + before[r][:-s]
        assert pm._array[r] == expected


@pytest.mark.parametrize("shift", [-1, 1, 2, -2])
def test_rotate_vertical_matches_expected_shift(shift):
    pm = PerfectMap(4, 2, 3)
    rows = pm._array_rows

    if shift == 0 or abs(shift) >= rows:
        pytest.skip("Expected ValueError in current implementation.")

    before = [row[:] for row in pm._array]
    pm.rotate_vertical(shift)

    s = shift % rows
    for r in range(rows):
        src_r = (r - s) % rows
        assert pm._array[r] == before[src_r]


def test_rotate_horizontal_invalid_shift_raises():
    pm = PerfectMap(4, 2, 3)
    cols = pm._array_cols

    with pytest.raises(ValueError):
        pm.rotate_horizontal(0)
    with pytest.raises(ValueError):
        pm.rotate_horizontal(cols)
    with pytest.raises(TypeError):
        pm.rotate_horizontal(1.5)


def test_rotate_vertical_invalid_shift_raises():
    pm = PerfectMap(4, 2, 3)
    rows = pm._array_rows

    with pytest.raises(ValueError):
        pm.rotate_vertical(0)
    with pytest.raises(ValueError):
        pm.rotate_vertical(rows)
    with pytest.raises(TypeError):
        pm.rotate_vertical("1")


def test_str_and_to_file_smoke(tmp_path):
    pm = PerfectMap(4, 2, 2)

    s = str(pm)
    assert s.count("\n") == pm._array_rows - 1

    out = tmp_path / "map.txt"
    pm.to_file(str(out))
    assert out.exists()

    expected = "\n".join(
        pm._separator.join(str(num) for num in row) for row in pm._array
    )
    assert out.read_text(encoding="utf-8") == expected


def test_shift_symbols_modulo_behavior():
    pm = PerfectMap(4, 2, 3)
    before = [row[:] for row in pm._array]
    a = pm._alphabet_size

    pm.shift_symbols(1)
    for r in range(pm._array_rows):
        for c in range(pm._array_cols):
            assert pm._array[r][c] == (before[r][c] + 1) % a

    pm.shift_symbols(a - 1)
    for r in range(pm._array_rows):
        for c in range(pm._array_cols):
            assert pm._array[r][c] == before[r][c]


def test_shift_symbols_invalid_shift_raises():
    pm = PerfectMap(4, 2, 3)

    with pytest.raises(TypeError):
        pm.shift_symbols("1")
    with pytest.raises(ValueError):
        pm.shift_symbols(0)
    with pytest.raises(ValueError):
        pm.shift_symbols(4)

if __name__ == "__main__":
    pytest.main()
