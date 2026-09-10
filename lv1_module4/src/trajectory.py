"""문제 4 — 궤적 보간. (학생 작성용 템플릿)

경유점(waypoint)을 지나는 궤적을 선형 보간 / 큐빅 스플라인으로 만들고,
시작·끝에서 속도와 가속도가 0 이 되는 5차 다항식 프로파일을 구현한다.

입력 규약
--------
- t_wp : (M,) 경유점 시각, 오름차순
- q_wp : (M,) 스칼라 궤적 또는 (M, D) 다차원 궤적 (예: 3차원 위치는 D = 3)
- t    : (N,) 평가할 시각 (t_wp[0] <= t <= t_wp[-1])
- 반환 : q_wp 가 (M,) 이면 (N,), (M, D) 이면 (N, D)

큐빅 스플라인은 `scipy.interpolate.CubicSpline` 을 써도 된다 (axis=0).
"""

from __future__ import annotations

import numpy as np

__all__ = ["linear_interp", "cubic_spline_interp", "quintic_profile", "finite_diff"]


def linear_interp(t_wp, q_wp, t) -> np.ndarray:
    """경유점 사이를 직선으로 잇는 보간. 각 차원마다 `np.interp` 를 쓰면 된다.

    위치는 이어지지만 경유점에서 속도가 불연속(꺾임)이다.
    """
    times = np.asarray(t_wp, dtype=float)
    values = np.asarray(q_wp, dtype=float)
    query = np.asarray(t, dtype=float)
    if times.ndim != 1 or values.shape[0] != len(times):
        raise ValueError("t_wp는 1차원이고 q_wp의 첫 축 길이가 같아야 합니다")
    if np.any(np.diff(times) <= 0):
        raise ValueError("t_wp는 오름차순이어야 합니다")
    if values.ndim == 1:
        return np.interp(query, times, values)
    if values.ndim == 2:
        return np.column_stack([np.interp(query, times, values[:, i]) for i in range(values.shape[1])])
    raise ValueError("q_wp는 1차원 또는 2차원이어야 합니다")


def cubic_spline_interp(t_wp, q_wp, t, bc_type: str = "natural") -> np.ndarray:
    """경유점을 지나는 큐빅 스플라인 보간 (위치·속도·가속도가 모두 연속, C2).

    bc_type : 양끝 경계 조건. "natural" (양끝 가속도 0) 또는 "clamped" (양끝 속도 0).
    """
    from scipy.interpolate import CubicSpline
    times = np.asarray(t_wp, dtype=float)
    values = np.asarray(q_wp, dtype=float)
    query = np.asarray(t, dtype=float)
    if times.ndim != 1 or values.shape[0] != len(times):
        raise ValueError("t_wp는 1차원이고 q_wp의 첫 축 길이가 같아야 합니다")
    if np.any(np.diff(times) <= 0):
        raise ValueError("t_wp는 오름차순이어야 합니다")
    return np.asarray(CubicSpline(times, values, axis=0, bc_type=bc_type)(query))


def quintic_profile(t, t0: float, tf: float, q0, qf,
                    v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """5차 다항식 궤적 q(t) 와 그 도함수 (q, qd, qdd) 를 돌려준다.

    경계 조건 6개 — q(t0)=q0, q(tf)=qf, qd(t0)=v0, qd(tf)=vf, qdd(t0)=a0, qdd(tf)=af —
    로 계수 6개 (c0 ~ c5) 를 정한다. 경계 속도·가속도가 모두 0 인 기본형은

        tau = (t - t0) / (tf - t0)
        s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
        q(t) = q0 + (qf - q0) s(tau)

    로 닫힌 꼴이 있고, 일반형은 6x6 선형계를 풀면 된다. 어느 쪽으로 구현해도 된다.
    q0, qf 가 스칼라이면 (N,), (D,) 이면 (N, D) 를 돌려준다.

    Returns
    -------
    q, qd, qdd : 위치, 속도, 가속도 (해석적 미분. 유한차분이 아니다)
    """
    if tf <= t0:
        raise ValueError("tf는 t0보다 커야 합니다")
    times = np.asarray(t, dtype=float)
    start = np.asarray(q0, dtype=float)
    end = np.asarray(qf, dtype=float)
    if start.shape != end.shape:
        raise ValueError("q0과 qf의 shape가 같아야 합니다")
    duration = float(tf - t0)
    tau = (times - t0) / duration
    A = np.array([
        [1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 2, 3, 4, 5],
        [0, 0, 2, 0, 0, 0],
        [0, 0, 2, 6, 12, 20],
    ], dtype=float)
    start, end, velocity_start, velocity_end, accel_start, accel_end = np.broadcast_arrays(
        start, end, np.asarray(v0, dtype=float), np.asarray(vf, dtype=float),
        np.asarray(a0, dtype=float), np.asarray(af, dtype=float)
    )
    boundary = np.stack([start, end, velocity_start * duration, velocity_end * duration,
                         accel_start * duration**2, accel_end * duration**2])
    coeff = np.linalg.solve(A, boundary.reshape(6, -1)).reshape((6,) + start.shape)
    powers = np.stack([tau**i for i in range(6)], axis=-1)
    q = np.tensordot(powers, coeff, axes=([-1], [0]))
    d_powers = np.stack([np.zeros_like(tau), np.ones_like(tau), 2*tau, 3*tau**2, 4*tau**3, 5*tau**4], axis=-1)
    dd_powers = np.stack([np.zeros_like(tau), np.zeros_like(tau), 2*np.ones_like(tau), 6*tau, 12*tau**2, 20*tau**3], axis=-1)
    qd = np.tensordot(d_powers, coeff, axes=([-1], [0])) / duration
    qdd = np.tensordot(dd_powers, coeff, axes=([-1], [0])) / duration**2
    return q, qd, qdd


def finite_diff(y, t) -> np.ndarray:
    """시간축(axis 0)에 대한 수치 미분. `np.gradient(y, t, axis=0)` 를 쓰면 된다.

    y : (N,) 또는 (N, D),  t : (N,)
    속도 = finite_diff(q, t),  가속도 = finite_diff(속도, t)
    """
    values = np.asarray(y, dtype=float)
    times = np.asarray(t, dtype=float)
    if times.ndim != 1 or values.shape[0] != times.shape[0]:
        raise ValueError("t의 길이는 y의 첫 축과 같아야 합니다")
    return np.gradient(values, times, axis=0)
