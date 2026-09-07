import numpy as np
import pytest

from src.vectors import (
    angle_between,
    cross,
    det,
    dot,
    norm,
    normalize,
    plane_normal,
    project,
    rank,
    reject,
    skew,
)

ATOL = 1e-12


def test_dot_norm_and_angle():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    assert np.isclose(dot(a, b), 32.0, atol=ATOL)
    assert np.isclose(norm([3.0, 4.0]), 5.0, atol=ATOL)
    assert np.isclose(angle_between([1, 0], [0, 1]), 90.0, atol=ATOL)


def test_zero_vector_is_rejected():
    with pytest.raises(ValueError):
        normalize([0.0, 0.0, 0.0])
    with pytest.raises(ValueError):
        angle_between([0.0, 0.0], [1.0, 0.0])


def test_projection_and_rejection_reconstruct_vector():
    a = np.array([3.0, 4.0, 1.0])
    b = np.array([1.0, 2.0, 0.0])
    p = project(a, b)
    r = reject(a, b)
    assert np.isclose(dot(r, b), 0.0, atol=ATOL)
    assert np.allclose(p + r, a, atol=ATOL)


def test_skew_cross_and_plane_normal():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([-2.0, 0.5, 4.0])
    assert np.allclose(skew(a) @ b, np.cross(a, b), atol=ATOL)
    assert np.allclose(skew(a).T, -skew(a), atol=ATOL)
    assert np.allclose(cross(a, b), np.cross(a, b), atol=ATOL)
    assert np.allclose(
        plane_normal([0, 0, 0], [1, 0, 0], [0, 1, 0]),
        [0, 0, 1],
        atol=ATOL,
    )


def test_rank_and_determinant_for_dependent_vectors():
    matrix = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 2]], dtype=float)
    assert rank(matrix) == 2
    assert np.isclose(det(matrix), 0.0, atol=ATOL)


def test_invalid_shapes_and_degenerate_plane():
    with pytest.raises(ValueError):
        dot([1, 2], [1, 2, 3])
    with pytest.raises(ValueError):
        project([1, 2], [0, 0])
    with pytest.raises(ValueError):
        skew([1, 2])
    with pytest.raises(ValueError):
        plane_normal([0, 0, 0], [1, 1, 1], [2, 2, 2])
