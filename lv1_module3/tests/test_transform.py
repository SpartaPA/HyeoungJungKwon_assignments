"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)

ATOL = 1e-12


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    inverse = inv_T(T)
    assert np.allclose(inverse @ T, np.eye(4), atol=ATOL)
    assert np.allclose(T @ inverse, np.eye(4), atol=ATOL)


def test_inv_T_matches_generic_inverse(T):
    assert np.allclose(inv_T(T), np.linalg.inv(T), atol=ATOL)  # 검산용


def test_point_and_direction_differ(T):
    vector = np.array([1.0, 0.0, 0.0])
    point = transform_point(T, vector)
    direction = transform_direction(T, vector)
    assert not np.allclose(point, direction, atol=ATOL)
    assert np.allclose(point - direction, T[:3, 3], atol=ATOL)
    assert np.isclose(np.linalg.norm(direction), np.linalg.norm(vector), atol=ATOL)


def test_transform_points_is_vectorized(T):
    points = np.arange(15.0).reshape(5, 3)
    vectorized = transform_points(T, points)
    loop = np.array([transform_point(T, point) for point in points])
    assert np.allclose(vectorized, loop, atol=ATOL)


def test_roundtrip_through_inverse(T):
    points = np.array([[0.0, 0.0, 0.0], [1.0, -2.0, 0.5], [3.0, 2.0, -1.0]])
    assert np.allclose(transform_points(inv_T(T), transform_points(T, points)), points, atol=ATOL)


def test_least_squares_matches_lstsq():
    rng = np.random.default_rng(42)
    matrix = rng.normal(size=(20, 4))
    truth = np.array([1.0, -2.0, 0.5, 3.0])
    observation = matrix @ truth + rng.normal(0.0, 1e-3, size=20)
    estimate, residual = least_squares_normal_equation(matrix, observation)
    reference = np.linalg.lstsq(matrix, observation, rcond=None)[0]  # 비교 대상
    assert np.allclose(estimate, reference, atol=ATOL)
    assert np.allclose(matrix.T @ residual, 0.0, atol=ATOL)
