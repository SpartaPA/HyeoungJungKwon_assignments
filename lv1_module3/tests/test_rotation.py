"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- `@pytest.mark.parametrize` 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다 (아래 ANGLES / MAKERS 참고).
- 비교는 반드시 `np.isclose` / `np.allclose` 로 한다 (부동소수점).
- `np.linalg` 는 검산용으로만 쓰고, 쓸 때는 주석으로 검산임을 밝힌다.
- assert 에 실패 메시지를 붙이면 어디가 깨졌는지 바로 보인다.
- 4개는 **최소 개수**다. 반사 행렬 반례, 로드리게스 일치, 축·각 왕복 같은
  테스트를 더 붙이면 좋다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)
from src.vectors import det

ANGLES = [0.0, np.deg2rad(22.5), np.pi / 6, np.pi / 4, np.pi / 2, 2.0, np.pi, -1.234]
MAKERS = [rot_x, rot_y, rot_z]
ATOL = 1e-12


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    R = maker(theta)
    assert np.allclose(R.T @ R, np.eye(3), atol=ATOL), "열이 직교 단위벡터가 아닙니다"


# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    assert np.isclose(det(maker(theta)), 1.0, atol=ATOL), "회전행렬의 행렬식은 1이어야 합니다"


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    R = maker(theta)
    inverse = np.linalg.inv(R)  # 검산용
    assert np.allclose(inverse, R.T, atol=ATOL)
    assert np.allclose(R.T @ R, np.eye(3), atol=ATOL)


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    original = rot_z(0.4) @ rot_y(-0.2) @ rot_x(0.7)
    noisy = original + rng.normal(0.0, 1e-5, size=(3, 3))
    restored = gram_schmidt(noisy)
    assert orthogonality_error(restored) < ATOL
    assert np.isclose(det(restored), 1.0, atol=ATOL)
    assert is_rotation(restored, atol=ATOL)


def test_reflection_is_not_a_rotation():
    reflection = np.diag([1.0, 1.0, -1.0])
    assert not is_rotation(reflection, atol=ATOL)


@pytest.mark.parametrize("theta", ANGLES)
def test_rodrigues_matches_rot_z(theta):
    assert np.allclose(rodrigues([0, 0, 1], theta), rot_z(theta), atol=ATOL)


def test_gram_schmidt_rejects_dependent_columns():
    dependent = np.array([[1.0, 2.0], [0.0, 0.0], [0.0, 0.0]])
    with pytest.raises(ValueError):
        gram_schmidt(dependent)


def test_is_rotation_rejects_wrong_shape():
    assert not is_rotation(np.eye(4), atol=ATOL)
