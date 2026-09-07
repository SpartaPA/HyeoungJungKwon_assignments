import numpy as np
import pytest

from src.rotation import rodrigues, rot_x, rot_y, rot_z
from src.vectors import det

ATOL = 1e-12


@pytest.mark.parametrize("maker", [rot_x, rot_y, rot_z])
@pytest.mark.parametrize("angle", [0.0, np.pi / 6, np.pi / 2, -1.2])
def test_axis_rotation_is_orthogonal_with_positive_determinant(maker, angle):
    R = maker(angle)
    assert np.allclose(R.T @ R, np.eye(3), atol=ATOL)
    assert np.isclose(det(R), 1.0, atol=ATOL)


def test_quarter_turns_follow_right_hand_rule():
    assert np.allclose(rot_x(np.pi / 2) @ [0, 1, 0], [0, 0, 1], atol=ATOL)
    assert np.allclose(rot_y(np.pi / 2) @ [0, 0, 1], [1, 0, 0], atol=ATOL)
    assert np.allclose(rot_z(np.pi / 2) @ [1, 0, 0], [0, 1, 0], atol=ATOL)


def test_composition_order_changes_the_result():
    first = rot_y(np.pi / 2) @ rot_z(np.pi / 2)
    second = rot_z(np.pi / 2) @ rot_y(np.pi / 2)
    assert not np.allclose(first, second, atol=ATOL)


def test_rodrigues_matches_axis_specific_rotations():
    angle = 0.73
    assert np.allclose(rodrigues([1, 0, 0], angle), rot_x(angle), atol=ATOL)
    assert np.allclose(rodrigues([0, 1, 0], angle), rot_y(angle), atol=ATOL)
    assert np.allclose(rodrigues([0, 0, 1], angle), rot_z(angle), atol=ATOL)


def test_rodrigues_normalizes_axis_and_preserves_it():
    axis = np.array([1.0, 2.0, -0.5])
    unit_axis = axis / np.sqrt(np.sum(axis * axis))
    R = rodrigues(axis, 1.1)
    assert np.allclose(R @ unit_axis, unit_axis, atol=ATOL)
    assert np.isclose(det(R), 1.0, atol=ATOL)


def test_reflection_is_not_a_rotation():
    reflection = np.diag([1.0, 1.0, -1.0])
    assert np.allclose(reflection.T @ reflection, np.eye(3), atol=ATOL)
    assert np.isclose(det(reflection), -1.0, atol=ATOL)
