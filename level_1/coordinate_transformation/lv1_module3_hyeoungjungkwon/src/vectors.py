"""문제 1 — 벡터 연산 모듈. (학생 작성용 템플릿)

내적 · 사이각 · 정규화 · 정사영 · 반대칭행렬(외적) · 평면 법선과
가우스 소거 기반의 rank / 행렬식 / 역행렬을 **직접** 구현한다.

규칙
----
- `np.linalg` 는 노트북에서 **검산용으로만** 쓰고, 이 모듈 안에서는 쓰지 않는다.
  (`inverse_gauss_jordan` 이 던지는 `np.linalg.LinAlgError` 예외 타입만 예외)
- 각 함수의 docstring 에 적힌 계약(입력/출력/예외)을 그대로 지킨다.
  노트북의 검증 셀과 `tests/` 가 이 계약을 기준으로 채점된다.
- 각 함수의 계약과 예외 조건을 유지한다.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "as_vector",
    "dot",
    "norm",
    "angle_between",
    "normalize",
    "project",
    "reject",
    "skew",
    "cross",
    "plane_normal",
    "row_echelon",
    "rank",
    "det",
    "gauss_eliminate",
    "inverse_gauss_jordan",
]


# ---------------------------------------------------------------- 기본 연산

def as_vector(v) -> np.ndarray:
    """입력(리스트/튜플/배열)을 1차원 float 배열로 변환한다.

    1차원이 아니면 ValueError 를 던진다.

    [구현 예시] 아래 세 줄이 이 파일에서 기대하는 코드 스타일이다.
    나머지 함수도 이런 식으로 채워 넣으면 된다.
    """
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr


def dot(a, b) -> float:
    """내적. sum(a_i * b_i) 를 직접 계산한다 (`np.dot` 사용 금지).

    두 벡터의 차원이 다르면 ValueError.
    """
    a_arr = as_vector(a)
    b_arr = as_vector(b)
    if a_arr.shape != b_arr.shape:
        raise ValueError(f"벡터 차원이 다릅니다: {a_arr.shape} != {b_arr.shape}")
    return float(np.sum(a_arr * b_arr))


def norm(v) -> float:
    """유클리드 노름. sqrt(v·v) — 위에서 만든 dot 을 재사용한다."""
    return float(np.sqrt(max(dot(v, v), 0.0)))


def angle_between(a, b, degrees: bool = True) -> float:
    """두 벡터 사이각. degrees=True 면 도(°), False 면 라디안.

    cos(theta) = (a·b) / (|a||b|)

    주의 1. 영벡터가 들어오면 사이각이 정의되지 않는다 -> ValueError.
    주의 2. 부동소수점 오차로 |cos| 가 1 을 아주 조금 넘으면 arccos 가 nan 을 낸다.
            [-1, 1] 로 clip 해야 무작위 입력에서도 안전하다.
    """
    a_arr = as_vector(a)
    b_arr = as_vector(b)
    denominator = norm(a_arr) * norm(b_arr)
    if denominator <= 1e-12:
        raise ValueError("영벡터와의 사이각은 정의되지 않습니다")
    cosine = np.clip(dot(a_arr, b_arr) / denominator, -1.0, 1.0)
    angle = float(np.arccos(cosine))
    return float(np.degrees(angle)) if degrees else angle


def normalize(v, eps: float = 1e-12) -> np.ndarray:
    """단위벡터로 정규화한다. v / |v|

    영벡터를 어떻게 처리할지는 **문제 1-2 에서 직접 정한다.**
    노트북 1-2 에서 (1) 아무 처리 없이 나눴을 때 무슨 일이 나는지 관찰하고,
    (2) 선택한 처리 방식과 근거를 마크다운에 적은 뒤, 그 방식대로 여기에 구현한다.
    선택에 따라 노트북/테스트의 검증 코드도 그 방식에 맞춰 작성한다.
    """
    arr = as_vector(v)
    length = norm(arr)
    if length <= eps:
        raise ValueError("영벡터는 방향이 없어 정규화할 수 없습니다")
    return arr / length


def project(a, b) -> np.ndarray:
    """a 를 b 방향으로 정사영한 성분.

        proj_b(a) = (a·b / b·b) * b

    분모가 |b|^2 이므로 b 를 미리 정규화할 필요는 없다.
    b 가 영벡터면 ValueError.
    """
    a_arr = as_vector(a)
    b_arr = as_vector(b)
    if a_arr.shape != b_arr.shape:
        raise ValueError(f"벡터 차원이 다릅니다: {a_arr.shape} != {b_arr.shape}")
    denominator = dot(b_arr, b_arr)
    if denominator <= 1e-24:
        raise ValueError("영벡터 방향으로는 정사영할 수 없습니다")
    return (dot(a_arr, b_arr) / denominator) * b_arr


def reject(a, b) -> np.ndarray:
    """a 에서 b 방향 성분을 뺀 나머지(수직 성분). a = project + reject 가 성립해야 한다."""
    a_arr = as_vector(a)
    return a_arr - project(a_arr, b)


def skew(a) -> np.ndarray:
    """3차원 벡터 a 에 대응하는 반대칭행렬 [a]_x 를 만든다.

        [a]_x = [[  0, -a3,  a2],
                 [ a3,   0, -a1],
                 [-a2,  a1,   0]]

    만족해야 하는 성질: [a]_x @ b == a x b,  [a]_x.T == -[a]_x
    3차원이 아니면 ValueError.
    """
    arr = as_vector(a)
    if arr.shape != (3,):
        raise ValueError(f"3차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    x, y, z = arr
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def cross(a, b) -> np.ndarray:
    """외적을 **반대칭행렬 곱으로** 계산한다 (`np.cross` 사용 금지)."""
    a_arr = as_vector(a)
    b_arr = as_vector(b)
    if a_arr.shape != (3,) or b_arr.shape != (3,):
        raise ValueError("외적은 3차원 벡터 두 개에 대해서만 정의됩니다")
    return skew(a_arr) @ b_arr


def plane_normal(P1, P2, P3) -> np.ndarray:
    """세 점이 이루는 평면의 **단위** 법선 벡터.

    두 모서리 벡터(P2-P1, P3-P1)의 외적이 평면에 수직이다.
    세 점이 일직선이면 외적이 영벡터가 되어 평면이 하나로 정해지지 않는다 -> ValueError.
    """
    p1 = as_vector(P1)
    p2 = as_vector(P2)
    p3 = as_vector(P3)
    if p1.shape != (3,) or p2.shape != (3,) or p3.shape != (3,):
        raise ValueError("평면의 점은 모두 3차원이어야 합니다")
    return normalize(cross(p2 - p1, p3 - p1))


# ------------------------------------------------- 가우스 소거 기반 선형대수

def row_echelon(A, pivoting: bool = True):
    """행 사다리꼴(row echelon form) 로 만든다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅(각 열에서 절댓값이 가장 큰 행을 피벗으로 올림)

    Returns
    -------
    U : (m, n) 상삼각 형태 행렬
    pivot_cols : 피벗이 선 열 인덱스 리스트
    n_swaps : 행 교환 횟수 (행렬식 부호 계산에 필요)

    힌트: 0 인지 판정할 때는 `== 0` 대신 허용오차(tol)를 쓴다.
          예) tol = max(m, n) * np.finfo(float).eps * max(1.0, np.max(np.abs(U)))
    """
    U = np.asarray(A, dtype=float).copy()
    if U.ndim != 2:
        raise ValueError("2차원 행렬이 필요합니다")
    m, n = U.shape
    scale = max(1.0, float(np.max(np.abs(U))) if U.size else 0.0)
    tol = max(m, n, 1) * np.finfo(float).eps * scale
    pivot_cols = []
    n_swaps = 0
    pivot_row = 0

    for col in range(n):
        if pivot_row >= m:
            break
        if pivoting:
            candidate = pivot_row + int(np.argmax(np.abs(U[pivot_row:, col])))
            if abs(U[candidate, col]) <= tol:
                continue
            if candidate != pivot_row:
                U[[pivot_row, candidate]] = U[[candidate, pivot_row]]
                n_swaps += 1
        elif abs(U[pivot_row, col]) <= tol:
            continue

        for row in range(pivot_row + 1, m):
            factor = U[row, col] / U[pivot_row, col]
            U[row, col:] -= factor * U[pivot_row, col:]
            U[row, col] = 0.0
        pivot_cols.append(col)
        pivot_row += 1

    U[np.abs(U) <= tol] = 0.0
    return U, pivot_cols, n_swaps


def rank(A) -> int:
    """행 사다리꼴의 피벗 개수 = rank."""
    _, pivot_cols, _ = row_echelon(A, pivoting=True)
    return len(pivot_cols)


def det(A) -> float:
    """행렬식 = 행 사다리꼴 대각성분의 곱 x (-1)^(행 교환 횟수).

    피벗이 n 개보다 적으면(특이행렬) 0.0 을 돌려준다.
    정사각 행렬이 아니면 ValueError.
    """
    arr = np.asarray(A, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("행렬식은 정사각 행렬에 대해서만 정의됩니다")
    U, pivots, swaps = row_echelon(arr, pivoting=True)
    if len(pivots) < arr.shape[0]:
        return 0.0
    return float(((-1.0) ** swaps) * np.prod(np.diag(U)))


def gauss_eliminate(A, b, pivoting: bool = True, verbose: bool = False):
    """가우스 소거법 + 후진대입으로 Ax = b 를 푼다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅을 적용한다. False 면 피벗을 그대로 쓴다
               (문제 4-4 에서 두 경우의 오차를 비교하므로 **둘 다 동작해야 한다**).
    verbose  : True 면 각 소거 단계의 첨가행렬 [A|b] 를 출력한다
               (문제 4-1 이 요구하는 '단계별 출력').

    Returns
    -------
    x : 해 벡터
    steps : 단계별 첨가행렬 [A|b] 스냅샷 리스트 (초기 상태 포함)

    피벗이 0 이면 해가 유일하지 않다 -> ZeroDivisionError.
    """
    M = np.asarray(A, dtype=float).copy()
    rhs = as_vector(b).copy()
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("정사각 계수행렬이 필요합니다")
    if rhs.shape[0] != M.shape[0]:
        raise ValueError("계수행렬과 우변의 크기가 맞지 않습니다")

    n = M.shape[0]
    augmented = np.column_stack((M, rhs))
    steps = [augmented.copy()]
    scale = max(1.0, float(np.max(np.abs(M))))
    tol = n * np.finfo(float).eps * scale
    if verbose:
        print("[초기]\n", augmented)

    for col in range(n):
        if pivoting:
            candidate = col + int(np.argmax(np.abs(augmented[col:, col])))
            if candidate != col:
                augmented[[col, candidate]] = augmented[[candidate, col]]
        pivot_is_zero = (
            abs(augmented[col, col]) <= tol
            if pivoting
            else augmented[col, col] == 0.0
        )
        if pivot_is_zero:
            raise ZeroDivisionError("0에 가까운 피벗으로 인해 유일해를 구할 수 없습니다")
        for row in range(col + 1, n):
            factor = augmented[row, col] / augmented[col, col]
            augmented[row, col:] -= factor * augmented[col, col:]
            augmented[row, col] = 0.0
        steps.append(augmented.copy())
        if verbose:
            print(f"[{col + 1}단계]\n", augmented)

    x = np.zeros(n, dtype=float)
    for row in range(n - 1, -1, -1):
        x[row] = (
            augmented[row, -1] - np.sum(augmented[row, row + 1:n] * x[row + 1:n])
        ) / augmented[row, row]
    return x, steps


def inverse_gauss_jordan(A) -> np.ndarray:
    """가우스-조던 소거로 역행렬을 구한다. [A|I] -> [I|A^-1].

    정사각이 아니면 ValueError, 특이행렬이면 np.linalg.LinAlgError.
    (`np.linalg.inv` 를 부르지 말고 소거로 직접 구한다)
    """
    arr = np.asarray(A, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("역행렬은 정사각 행렬에 대해서만 정의됩니다")
    n = arr.shape[0]
    augmented = np.hstack((arr.copy(), np.eye(n)))
    scale = max(1.0, float(np.max(np.abs(arr))))
    tol = n * np.finfo(float).eps * scale

    for col in range(n):
        candidate = col + int(np.argmax(np.abs(augmented[col:, col])))
        if abs(augmented[candidate, col]) <= tol:
            raise np.linalg.LinAlgError("특이행렬은 역행렬이 없습니다")
        if candidate != col:
            augmented[[col, candidate]] = augmented[[candidate, col]]
        augmented[col] /= augmented[col, col]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row, col]
            augmented[row] -= factor * augmented[col]
            augmented[row, col] = 0.0
    return augmented[:, n:]
