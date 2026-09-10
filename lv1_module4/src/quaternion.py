"""문제 3 — 쿼터니언 변환과 SLERP. (학생 작성용 템플릿)

규약
----
- 쿼터니언은 길이 4 배열 **(x, y, z, w)** 다. 모듈 ③ 의 `quaternion_from_axis_angle` 과
  SciPy `Rotation.as_quat()` 와 같은 순서다. w 가 스칼라(실수부)다.
- q 와 -q 는 같은 회전이다 (이중 덮개). 비교할 때는 부호를 무시하거나 |q . q_ref| 를 본다.
- 보간은 항상 **짧은 호**를 택한다: q0 . q1 < 0 이면 q1 의 부호를 뒤집고 시작한다.

SciPy 는 검산(비교) 용도로만 쓴다. 이 파일 안에서는 numpy 만 사용한다.
"""

from __future__ import annotations

import numpy as np

__all__ = ["matrix_to_quaternion", "quaternion_to_matrix", "slerp", "lerp_quat", "quat_angle"]


def matrix_to_quaternion(R) -> np.ndarray:
    """회전행렬 (3,3) -> 단위 쿼터니언 (x, y, z, w).

    권장 방법 (Shepperd): trace 가 양수이면 w 부터, 아니면 대각성분이 가장 큰 축부터 계산해
    0 으로 나누는 일을 피한다. 180도 회전(trace = -1)에서도 동작해야 한다.

        t = trace(R)
        t > 0        : s = 2 sqrt(1 + t);      w = s/4; x = (R21 - R12)/s; ...
        R00 이 최대  : s = 2 sqrt(1 + R00 - R11 - R22);  x = s/4; w = (R21 - R12)/s; ...
        (R11, R22 최대인 경우도 같은 꼴)

    반환값은 반드시 정규화하고, w >= 0 이 되도록 부호를 맞춘다 (비교가 편해진다).
    """
    matrix = np.asarray(R, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError("회전행렬은 3x3이어야 합니다")
    trace = float(np.trace(matrix))
    if trace > 0.0:
        s = 2.0 * np.sqrt(trace + 1.0)
        w = 0.25 * s
        x = (matrix[2, 1] - matrix[1, 2]) / s
        y = (matrix[0, 2] - matrix[2, 0]) / s
        z = (matrix[1, 0] - matrix[0, 1]) / s
    else:
        diagonal = np.diag(matrix)
        index = int(np.argmax(diagonal))
        if index == 0:
            s = 2.0 * np.sqrt(max(1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2], 0.0))
            x = 0.25 * s
            y = (matrix[0, 1] + matrix[1, 0]) / s
            z = (matrix[0, 2] + matrix[2, 0]) / s
            w = (matrix[2, 1] - matrix[1, 2]) / s
        elif index == 1:
            s = 2.0 * np.sqrt(max(1.0 + matrix[1, 1] - matrix[0, 0] - matrix[2, 2], 0.0))
            x = (matrix[0, 1] + matrix[1, 0]) / s
            y = 0.25 * s
            z = (matrix[1, 2] + matrix[2, 1]) / s
            w = (matrix[0, 2] - matrix[2, 0]) / s
        else:
            s = 2.0 * np.sqrt(max(1.0 + matrix[2, 2] - matrix[0, 0] - matrix[1, 1], 0.0))
            x = (matrix[0, 2] + matrix[2, 0]) / s
            y = (matrix[1, 2] + matrix[2, 1]) / s
            z = 0.25 * s
            w = (matrix[1, 0] - matrix[0, 1]) / s
    q = np.array([x, y, z, w], dtype=float)
    q /= np.linalg.norm(q)
    return -q if q[3] < 0.0 else q


def quaternion_to_matrix(q) -> np.ndarray:
    """단위 쿼터니언 (x, y, z, w) -> 회전행렬 (3,3).

        R = [[1 - 2(y^2 + z^2),   2(xy - zw),        2(xz + yw)],
             [2(xy + zw),         1 - 2(x^2 + z^2),  2(yz - xw)],
             [2(xz - yw),         2(yz + xw),        1 - 2(x^2 + y^2)]]

    입력이 정확히 단위가 아닐 수 있으므로 먼저 정규화한다. q 와 -q 는 같은 R 을 준다.
    """
    values = np.asarray(q, dtype=float)
    if values.shape != (4,):
        raise ValueError("쿼터니언은 (4,) 배열이어야 합니다")
    length = np.linalg.norm(values)
    if length <= np.finfo(float).eps:
        raise ValueError("영 쿼터니언은 회전을 나타내지 않습니다")
    x, y, z, w = values / length
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
    ])


def quat_angle(q0, q1) -> float:
    """두 단위 쿼터니언이 나타내는 회전 사이의 각도 [rad], 0 <= angle <= pi.

        angle = 2 * arccos(|q0 . q1|)
    """
    a = np.asarray(q0, dtype=float); b = np.asarray(q1, dtype=float)
    if a.shape != (4,) or b.shape != (4,):
        raise ValueError("쿼터니언은 모두 (4,) 배열이어야 합니다")
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    return float(2.0 * np.arccos(np.clip(abs(a @ b), -1.0, 1.0)))


def slerp(q0, q1, t: float, eps: float = 1e-8) -> np.ndarray:
    """구면 선형 보간 (Spherical Linear intERPolation).

        d = q0 . q1                      (d < 0 이면 q1 = -q1, d = -d 로 짧은 호 선택)
        omega = arccos(d)
        q(t) = [sin((1-t) omega) q0 + sin(t omega) q1] / sin(omega)

    경계 상황
    - 두 자세가 거의 같아 d > 1 - eps 이면 sin(omega) ~ 0 이라 나눗셈이 불안정하다.
      이때는 선형 보간 후 정규화로 대체한다.
    - d 는 부동소수점 오차로 1 을 살짝 넘을 수 있으므로 clip 한다.

    반환값은 단위 쿼터니언이어야 한다. t = 0 이면 q0, t = 1 이면 (부호를 맞춘) q1.
    """
    a = np.asarray(q0, dtype=float); b = np.asarray(q1, dtype=float)
    if a.shape != (4,) or b.shape != (4,):
        raise ValueError("쿼터니언은 모두 (4,) 배열이어야 합니다")
    if not 0.0 <= t <= 1.0:
        raise ValueError("t는 0과 1 사이여야 합니다")
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    d = float(a @ b)
    if d < 0.0:
        b = -b; d = -d
    d = float(np.clip(d, -1.0, 1.0))
    if d > 1.0 - eps:
        result = (1.0 - t) * a + t * b
        return result / np.linalg.norm(result)
    omega = np.arccos(d)
    sin_omega = np.sin(omega)
    result = (np.sin((1.0 - t) * omega) * a + np.sin(t * omega) * b) / sin_omega
    return result / np.linalg.norm(result)


def lerp_quat(q0, q1, t: float, normalize: bool = False) -> np.ndarray:
    """성분별 단순 선형 보간 (비교용).

        q(t) = (1 - t) q0 + t q1          (q0 . q1 < 0 이면 q1 부호를 먼저 뒤집는다)

    normalize=False 이면 정규화하지 않은 값을 그대로 돌려준다 — 크기가 1 에서 얼마나
    벗어나는지 관찰하는 데 쓴다. normalize=True 이면 정규화한다 (NLERP).
    """
    a = np.asarray(q0, dtype=float); b = np.asarray(q1, dtype=float)
    if a.shape != (4,) or b.shape != (4,):
        raise ValueError("쿼터니언은 모두 (4,) 배열이어야 합니다")
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    if a @ b < 0.0:
        b = -b
    result = (1.0 - t) * a + t * b
    return result / np.linalg.norm(result) if normalize else result
