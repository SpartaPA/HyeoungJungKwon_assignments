"""문제 5 — 점군 자세 추정: PCA · Kabsch · 최소제곱 평면 피팅. (학생 작성용 템플릿)

- `pca_axes`        : 공분산 고유분해로 물체의 주축 3개를 뽑는다
- `kabsch`          : 대응이 알려진 두 점군 사이의 최적 회전·병진을 SVD 로 구한다
- `fit_plane_lstsq` : 최소제곱으로 평면을 피팅하고 점별 잔차를 돌려준다
- `remove_outliers` : 잔차가 큰 점을 걸러낸다

`rotation_angle_deg` 는 제공 코드다 (두 회전행렬 사이 각도).
"""

from __future__ import annotations

import numpy as np

__all__ = ["pca_axes", "kabsch", "fit_plane_lstsq", "remove_outliers", "rotation_angle_deg"]


def rotation_angle_deg(R_a, R_b) -> float:
    """두 회전행렬 사이의 각도 [deg] — R_a^T R_b 의 회전각. (제공 코드)"""
    R_rel = np.asarray(R_a, dtype=float).T @ np.asarray(R_b, dtype=float)
    cos_theta = np.clip((np.trace(R_rel) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.rad2deg(np.arccos(cos_theta)))


def pca_axes(P):
    """점군 (N,3) 의 주축을 고유분해로 뽑는다.

    1. centroid = P 의 평균, X = P - centroid
    2. C = X^T X / (N - 1)   (3x3 공분산)
    3. C 를 고유분해 (`np.linalg.eigh` — 대칭행렬 전용, 실수 고유값)
    4. 고유값 **내림차순**으로 정렬해 axes 의 열 0,1,2 가 각각 긴 축 -> 짧은 축이 되게 한다
    5. det(axes) = +1 이 되도록 (오른손 좌표계) 필요하면 마지막 열의 부호를 뒤집는다

    Returns
    -------
    axes : (3,3) 열이 주축 (단위벡터, 서로 직교, det = +1) — 회전행렬로 그대로 쓸 수 있다
    eigvals : (3,) 내림차순 고유값 (각 축 방향 분산)
    centroid : (3,) 점군 중심
    """
    points = np.asarray(P, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or points.shape[0] < 3:
        raise ValueError("P는 최소 3개의 3차원 점이어야 합니다")
    centroid = points.mean(axis=0)
    centered = points - centroid
    covariance = centered.T @ centered / (len(points) - 1)
    eigvals, eigvecs = np.linalg.eigh(covariance)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    axes = eigvecs[:, order]
    if np.linalg.det(axes) < 0.0:
        axes[:, -1] *= -1.0
    return axes, eigvals, centroid


def kabsch(P, Q):
    """대응이 알려진 두 점군 P, Q (N,3) 에 대해 Q ~ P @ R.T + t 를 만족하는 (R, t) 를 구한다.

    1. 두 점군의 중심 cP, cQ 를 빼서 X = P - cP, Y = Q - cQ
    2. H = X^T Y  (3x3 교차 공분산)
    3. U, S, Vt = svd(H)
    4. d = sign(det(V U^T)) — 반사가 나오면 (-1) 보정: D = diag(1, 1, d)
    5. R = V D U^T,  t = cQ - R cP

    Returns
    -------
    R : (3,3) 회전행렬 (det = +1)
    t : (3,) 병진
    """
    points_p = np.asarray(P, dtype=float); points_q = np.asarray(Q, dtype=float)
    if points_p.shape != points_q.shape or points_p.ndim != 2 or points_p.shape[1] != 3:
        raise ValueError("두 점군은 같은 (N,3) shape여야 합니다")
    c_p = points_p.mean(axis=0); c_q = points_q.mean(axis=0)
    X = points_p - c_p; Y = points_q - c_q
    U, _, Vt = np.linalg.svd(X.T @ Y)
    D = np.eye(3)
    D[-1, -1] = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ D @ U.T
    t = c_q - R @ c_p
    return R, t


def fit_plane_lstsq(P):
    """점군 (N,3) 에 평면 n . p + d = 0 을 최소제곱으로 피팅한다.

    권장 방법 (정규방정식): z = a x + b y + c 로 두고
        A = [x, y, 1],  b = z,   (A^T A) [a, b, c]^T = A^T b
    를 풀면 평면 a x + b y - z + c = 0 이므로 법선 n = (a, b, -1) 을 정규화한다.
    (평면이 z축과 나란하면 이 모델은 못 쓴다 — 그런 경우 SVD 로 최소 분산 방향을 쓴다.)

    Returns
    -------
    normal : (3,) 단위 법선
    d : float — 평면 상수 (n . p + d = 0)
    residuals : (N,) 각 점의 부호 있는 평면까지의 거리 n . p + d
    """
    points = np.asarray(P, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 3:
        raise ValueError("P는 최소 3개의 3차원 점이어야 합니다")
    A = np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])
    coeff = np.linalg.lstsq(A, points[:, 2], rcond=None)[0]
    normal = np.array([coeff[0], coeff[1], -1.0])
    normal /= np.linalg.norm(normal)
    d = -coeff[2] / np.linalg.norm(np.array([coeff[0], coeff[1], -1.0]))
    residuals = points @ normal + d
    return normal, float(d), residuals


def remove_outliers(P, residuals, k: float = 3.0):
    """잔차가 큰 점을 제거한다.

    기준: |residual| < k * sigma. sigma 는 이상치에 강한 추정치를 권장한다
        sigma = 1.4826 * median(|residual - median(residual)|)      (MAD)
    (단순 std 를 쓰면 이상치가 sigma 자체를 키워 걸러지지 않을 수 있다.)

    Returns
    -------
    P_clean : (M,3) 남은 점
    mask : (N,) bool — True 가 남긴 점. P 와 대응 점군에 같은 mask 를 적용해야 Kabsch 대응이 유지된다
    """
    points = np.asarray(P, dtype=float); values = np.asarray(residuals, dtype=float)
    if points.ndim != 2 or values.shape != (len(points),):
        raise ValueError("P와 residuals의 길이가 맞지 않습니다")
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    sigma = 1.4826 * mad
    if sigma <= np.finfo(float).eps:
        mask = np.isclose(values, median)
    else:
        mask = np.abs(values - median) < k * sigma
    return points[mask], mask
