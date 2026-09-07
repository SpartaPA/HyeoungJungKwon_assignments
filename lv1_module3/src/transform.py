"""문제 5 — 4x4 동차변환 모듈. (학생 작성용 템플릿)

동차변환 생성/역변환, 점과 방향의 구분, 벡터화된 점군 변환,
정규방정식 기반 최소자승법을 직접 구현한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import inverse_gauss_jordan

__all__ = [
    "make_T",
    "inv_T",
    "inv_T_batch",
    "to_homogeneous",
    "transform_point",
    "transform_direction",
    "transform_points",
    "least_squares_normal_equation",
    "rmse",
]


def make_T(R, t) -> np.ndarray:
    """회전 R(3x3)과 병진 t(3,)로 4x4 동차변환을 만든다.

        T = [[R, t],
             [0, 1]]

    R 이 3x3 이 아니면 ValueError.
    """
    rotation = np.asarray(R, dtype=float)
    translation = np.asarray(t, dtype=float)
    if rotation.shape != (3, 3):
        raise ValueError(f"3x3 회전행렬이 필요합니다. 받은 shape={rotation.shape}")
    if translation.shape != (3,):
        raise ValueError(f"(3,) 병진 벡터가 필요합니다. 받은 shape={translation.shape}")
    T = np.eye(4, dtype=float)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T


def inv_T(T) -> np.ndarray:
    """동차변환의 역변환. **일반 역행렬 함수를 쓰지 않고** 공식으로 구한다.

        T^-1 = [[R^T, -R^T t],
                [  0,      1]]

    유도: T^-1 을 [[S, u], [0, 1]] 로 두고 T T^-1 = I 를 풀면
          R S = I -> S = R^T (R 이 직교),  R u + t = 0 -> u = -R^T t.

    4x4 가 아니면 ValueError.
    """
    arr = np.asarray(T, dtype=float)
    if arr.shape != (4, 4):
        raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={arr.shape}")
    rotation = arr[:3, :3]
    translation = arr[:3, 3]
    return make_T(rotation.T, -rotation.T @ translation)


def inv_T_batch(Ts) -> np.ndarray:
    """(N, 4, 4) 동차변환 묶음을 **반복문 없이** 한 번에 역변환한다.

    `inv_T` 와 같은 공식을 배치 축으로 확장한 것이다.
    문제 5-4 의 속도 비교에서 쓴다 — 단건 호출은 파이썬/NumPy 호출 오버헤드가
    지배해서 연산량 차이가 드러나지 않기 때문이다.

    힌트: 전치는 `np.swapaxes(..., 1, 2)`, 배치 행렬-벡터 곱은
          `np.einsum("nij,nj->ni", ...)` 로 쓸 수 있다.
    """
    arr = np.asarray(Ts, dtype=float)
    if arr.ndim != 3 or arr.shape[1:] != (4, 4):
        raise ValueError(f"(N,4,4) 변환 묶음이 필요합니다. 받은 shape={arr.shape}")
    result = np.zeros_like(arr)
    rotation = arr[:, :3, :3]
    rotation_t = np.swapaxes(rotation, 1, 2)
    result[:, :3, :3] = rotation_t
    result[:, :3, 3] = -np.einsum("nij,nj->ni", rotation_t, arr[:, :3, 3])
    result[:, 3, 3] = 1.0
    return result


def to_homogeneous(P, w: float = 1.0) -> np.ndarray:
    """(3,) 또는 (N,3) 좌표에 마지막 성분 w 를 붙인다.

    w = 1 이면 점(위치), w = 0 이면 방향(벡터).
    """
    arr = np.asarray(P, dtype=float)
    if arr.ndim == 1:
        if arr.shape != (3,):
            raise ValueError(f"(3,) 좌표가 필요합니다. 받은 shape={arr.shape}")
        return np.concatenate((arr, [w]))
    if arr.ndim == 2 and arr.shape[1] == 3:
        return np.concatenate((arr, np.full((arr.shape[0], 1), w)), axis=1)
    raise ValueError(f"(3,) 또는 (N,3) 좌표가 필요합니다. 받은 shape={arr.shape}")


def transform_point(T, p) -> np.ndarray:
    """점 변환 (w = 1): 회전과 병진이 모두 적용된다. 반환은 (3,)."""
    return transform_points(T, p, w=1.0)


def transform_direction(T, v) -> np.ndarray:
    """방향 변환 (w = 0): 회전만 적용되고 병진은 무시된다. 반환은 (3,)."""
    return transform_points(T, v, w=0.0)


def transform_points(T, P, w: float = 1.0) -> np.ndarray:
    """(N,3) 점군을 **반복문 없이** 한 번에 변환한다. (3,) 입력도 받아야 한다.

    힌트: (T @ P_h.T).T 대신 P_h @ T.T 를 쓰면 전치가 한 번으로 끝나고
          메모리 접근도 행 방향이라 캐시에 유리하다.
    """
    arr = np.asarray(P, dtype=float)
    homogeneous = to_homogeneous(arr, w=w)
    if arr.ndim == 1:
        return (np.asarray(T, dtype=float) @ homogeneous)[:3]
    return (homogeneous @ np.asarray(T, dtype=float).T)[:, :3]


def least_squares_normal_equation(A, b):
    """정규방정식 (A^T A) x = A^T b 를 직접 세워 최소자승해를 구한다.

    - (A^T A) 의 역행렬은 문제 4 에서 만든 `inverse_gauss_jordan` 으로 구한다
      (`np.linalg.lstsq` 는 노트북에서 **비교 대상**으로만 쓴다).
    - 근거: 잔차 r = b - A x 가 최소일 때 r 은 A 의 열공간에 수직이므로 A^T r = 0.

    Returns
    -------
    x : 최소자승해
    residual : b - A x
    """
    matrix = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float)
    if matrix.ndim != 2 or vector.ndim != 1 or matrix.shape[0] != vector.shape[0]:
        raise ValueError("A는 2차원, b는 1차원이며 행 수가 같아야 합니다")
    normal_matrix = matrix.T @ matrix
    x = inverse_gauss_jordan(normal_matrix) @ (matrix.T @ vector)
    residual = vector - matrix @ x
    return x, residual


def rmse(residual) -> float:
    """잔차의 RMSE = sqrt(mean(r^2))."""
    values = np.asarray(residual, dtype=float)
    if values.size == 0:
        raise ValueError("빈 잔차의 RMSE는 정의되지 않습니다")
    return float(np.sqrt(np.mean(values * values)))
