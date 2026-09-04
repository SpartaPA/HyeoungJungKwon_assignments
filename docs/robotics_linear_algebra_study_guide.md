# 로보틱스를 위한 선형대수와 ROS 2 TF2 학습 가이드

이 문서는 로봇의 위치·자세·좌표계 변환을 이해하는 데 필요한 선형대수를 ROS 2 TF2와 연결해 설명한다. 저장소의 turtlesim 구현을 기준으로 `world → turtle1` 변환, 목표점 거리, 목표 방향, 각도 정규화를 수식과 수치 예제로 해석한다.

## 1. 먼저 정할 표기법

좌표 변환은 표기 방향을 혼동하면 계산 결과가 완전히 달라진다. 이 문서는 다음 규칙을 사용한다.

- 벡터는 열벡터로 쓴다: \(\mathbf{p}=[x\ y\ z]^T\)
- \({}^{A}\mathbf{p}\)는 점 \(\mathbf{p}\)를 좌표계 `A`에서 표현한 좌표다.
- \({}^{A}\mathbf{R}_{B}\)는 `B` 좌표계의 벡터를 `A` 좌표계 표현으로 회전한다.
- \({}^{A}\mathbf{T}_{B}\)는 `B` 좌표계의 점을 `A` 좌표계 표현으로 변환한다.
- 회전은 오른손 좌표계와 반시계 방향의 양의 각도를 사용한다.
- ROS 메시지의 쿼터니언 필드 순서는 `(x, y, z, w)`다.

따라서 다음 식은 `B`에서 본 점을 `A`에서 본 점으로 바꾼다.

$$
{}^{A}\mathbf{p}
= {}^{A}\mathbf{R}_{B}\,{}^{B}\mathbf{p}
+ {}^{A}\mathbf{t}_{B}
$$

## 2. 벡터: 로봇의 위치와 이동을 나타내는 기본 단위

### 2.1 위치벡터와 변위벡터

2차원에서 로봇 위치와 목표 위치를 각각 다음과 같이 두자.

$$
\mathbf{p}=\begin{bmatrix}x\\y\end{bmatrix},\qquad
\mathbf{g}=\begin{bmatrix}g_x\\g_y\end{bmatrix}
$$

현재 위치에서 목표로 향하는 변위는 두 위치의 차다.

$$
\Delta\mathbf{p}=\mathbf{g}-\mathbf{p}
=\begin{bmatrix}g_x-x\\g_y-y\end{bmatrix}
$$

예를 들어 로봇이 \((1,2)\), 목표가 \((4,6)\)이면 다음과 같다.

$$
\Delta\mathbf{p}
=\begin{bmatrix}4-1\\6-2\end{bmatrix}
=\begin{bmatrix}3\\4\end{bmatrix}
$$

위치는 기준 좌표계가 필요하지만 변위는 두 점 사이의 차를 표현한다. ROS 2에서 `Pose.position`은 위치이고 `Twist.linear`은 단위 시간당 변위인 선속도에 해당한다.

### 2.2 노름, 거리, 단위벡터

벡터의 유클리드 노름은 길이를 뜻한다.

$$
\lVert\mathbf{v}\rVert_2
=\sqrt{v_x^2+v_y^2+v_z^2}
$$

두 점 사이의 거리는 변위의 노름이다.

$$
d(\mathbf{p},\mathbf{g})
=\lVert\mathbf{g}-\mathbf{p}\rVert_2
=\sqrt{(g_x-x)^2+(g_y-y)^2}
$$

앞의 \((3,4)\) 변위에 적용하면 거리는 \(\sqrt{3^2+4^2}=5\)다. 저장소의 `calculations.py`와 거리 publisher는 같은 계산을 `math.hypot`으로 수행한다.

방향만 필요하면 길이로 나누어 단위벡터를 만든다.

$$
\hat{\mathbf{v}}=\frac{\mathbf{v}}{\lVert\mathbf{v}\rVert}
$$

따라서 \([3\ 4]^T\)의 단위벡터는 \([0.6\ 0.8]^T\)다. 단, 영벡터는 길이가 0이므로 정규화할 수 없다. 로봇이 이미 목표점에 도착했을 때 방향 벡터를 계산하려면 이 경우를 먼저 검사해야 한다.

### 2.3 내적: 방향 정렬과 투영

두 벡터의 내적은 다음과 같다.

$$
\mathbf{a}\cdot\mathbf{b}
=a_xb_x+a_yb_y+a_zb_z
=\lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert\cos\theta
$$

내적의 부호로 두 방향의 관계를 빠르게 판단할 수 있다.

| 내적 | 방향 관계 | 로봇 사례 |
|---:|---|---|
| \(>0\) | 90°보다 작은 각 | 목표가 대체로 전방에 있음 |
| \(=0\) | 직교 | 목표가 정확히 측면에 있음 |
| \(<0\) | 90°보다 큰 각 | 목표가 후방에 있음 |

로봇의 전방 단위벡터가 \(\mathbf{f}=[\cos\theta\ \sin\theta]^T\)이고 목표 방향 단위벡터가 \(\hat{\mathbf{d}}\)라면, \(\mathbf{f}\cdot\hat{\mathbf{d}}\)는 목표를 얼마나 정면으로 바라보는지 나타낸다.

수치 예제로 로봇이 +x 방향을 보고 있고 목표 방향이 \([0.6\ 0.8]^T\)라면 다음과 같다.

$$
\begin{bmatrix}1\\0\end{bmatrix}\cdot
\begin{bmatrix}0.6\\0.8\end{bmatrix}=0.6
$$

두 방향의 각도는 \(\cos^{-1}(0.6)\approx53.13^\circ\)다.

벡터 \(\mathbf{v}\)를 단위벡터 \(\hat{\mathbf{u}}\) 방향으로 투영한 스칼라 성분은 \(\mathbf{v}\cdot\hat{\mathbf{u}}\), 벡터 성분은 다음과 같다.

$$
\operatorname{proj}_{\hat{\mathbf{u}}}(\mathbf{v})
=(\mathbf{v}\cdot\hat{\mathbf{u}})\hat{\mathbf{u}}
$$

이는 카메라가 관측한 속도에서 로봇 진행축 성분만 분리하거나, 힘 센서 값을 관절축 방향 성분으로 분해할 때 사용한다.

### 2.4 외적: 회전 방향과 법선벡터

3차원 외적 \(\mathbf{a}\times\mathbf{b}\)는 두 벡터 모두에 수직인 벡터다.

$$
\mathbf{a}\times\mathbf{b}
=\begin{bmatrix}
a_yb_z-a_zb_y\\
a_zb_x-a_xb_z\\
a_xb_y-a_yb_x
\end{bmatrix}
$$

2차원 벡터는 z 성분을 0으로 두어 외적의 z 성분만 사용할 수 있다.

$$
(\mathbf{a}\times\mathbf{b})_z=a_xb_y-a_yb_x
$$

로봇 전방이 \([1\ 0]^T\), 목표 방향이 \([0\ 1]^T\)이면 z 성분은 1이다. 오른손 법칙에서 양수이므로 목표가 로봇의 왼쪽에 있고 반시계 방향 회전이 필요하다. 음수이면 오른쪽 회전이 필요하다.

## 3. 행렬: 여러 축의 관계를 한 번에 표현하기

### 3.1 행렬과 선형변환

행렬 \(\mathbf{A}\)를 벡터에 곱하면 크기 조정, 회전, 투영 같은 선형변환을 표현할 수 있다.

$$
\mathbf{y}=\mathbf{A}\mathbf{x}
$$

예를 들어 다음 행렬은 x축 크기를 2배, y축 크기를 0.5배로 바꾼다.

$$
\begin{bmatrix}2&0\\0&0.5\end{bmatrix}
\begin{bmatrix}3\\4\end{bmatrix}
=\begin{bmatrix}6\\2\end{bmatrix}
$$

행렬의 각 열은 입력 좌표계의 기저벡터가 출력 좌표계에서 어디로 이동하는지를 보여 준다. 회전행렬의 열벡터가 새 좌표축의 방향으로 해석되는 이유가 여기에 있다.

### 3.2 행렬 곱셈 순서

행렬 곱셈은 일반적으로 교환법칙이 성립하지 않는다.

$$
\mathbf{A}\mathbf{B}\neq\mathbf{B}\mathbf{A}
$$

열벡터 표기에서는 오른쪽 변환부터 적용한다.

$$
\mathbf{p}'=\mathbf{T}_1\mathbf{T}_2\mathbf{p}
$$

즉, \(\mathbf{T}_2\)를 먼저 적용하고 \(\mathbf{T}_1\)을 적용한다. TF 트리를 따라 변환을 합성할 때 가장 자주 발생하는 오류가 이 순서를 반대로 쓰는 것이다.

### 3.3 역행렬, 행렬식, 특이성

정방행렬 \(\mathbf{A}\)에 대해 다음을 만족하는 행렬이 역행렬이다.

$$
\mathbf{A}^{-1}\mathbf{A}=\mathbf{I}
$$

\(\det(\mathbf{A})=0\)이면 역행렬이 존재하지 않는다. 로봇 팔의 자코비안이 특이해지면 특정 말단 속도를 만들기 위한 관절 속도를 유일하게 구할 수 없거나 매우 큰 관절 속도가 필요해진다.

회전행렬은 직교행렬이므로 역행렬 계산이 간단하다.

$$
\mathbf{R}^{-1}=\mathbf{R}^{T},\qquad
\mathbf{R}^{T}\mathbf{R}=\mathbf{I},\qquad
\det(\mathbf{R})=1
$$

## 4. 2차원 회전과 이동

### 4.1 2차원 회전행렬

반시계 방향 회전각 \(\theta\)의 회전행렬은 다음과 같다.

$$
\mathbf{R}(\theta)=
\begin{bmatrix}
\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta
\end{bmatrix}
$$

\(\theta=90^\circ=\pi/2\)일 때 x축 단위벡터를 회전하면 y축 단위벡터가 된다.

$$
\begin{bmatrix}0&-1\\1&0\end{bmatrix}
\begin{bmatrix}1\\0\end{bmatrix}
=\begin{bmatrix}0\\1\end{bmatrix}
$$

### 4.2 회전과 평행이동 결합

로봇 좌표계 `base_link`의 점 \({}^{base}\mathbf{p}\)를 `world` 좌표계로 바꾸려면 먼저 회전하고 평행이동을 더한다.

$$
{}^{world}\mathbf{p}
= {}^{world}\mathbf{R}_{base}\,{}^{base}\mathbf{p}
+ {}^{world}\mathbf{t}_{base}
$$

로봇의 `world` 위치가 \((2,1)\), yaw가 90°이고 로봇 전방 1 m에 센서 점이 있다고 하자.

$$
{}^{world}\mathbf{R}_{base}
=\begin{bmatrix}0&-1\\1&0\end{bmatrix},\quad
{}^{base}\mathbf{p}=\begin{bmatrix}1\\0\end{bmatrix},\quad
{}^{world}\mathbf{t}_{base}=\begin{bmatrix}2\\1\end{bmatrix}
$$

계산 결과는 다음과 같다.

$$
{}^{world}\mathbf{p}
=\begin{bmatrix}0\\1\end{bmatrix}
+\begin{bmatrix}2\\1\end{bmatrix}
=\begin{bmatrix}2\\2\end{bmatrix}
$$

로봇이 +y 방향을 바라보므로 로봇 전방 1 m 지점은 `world`의 \((2,2)\)다.

### 4.3 동차변환행렬

회전과 평행이동을 하나의 행렬 곱으로 표현하기 위해 점에 1을 추가한다.

$$
{}^{A}\mathbf{T}_{B}
=\begin{bmatrix}
{}^{A}\mathbf{R}_{B}&{}^{A}\mathbf{t}_{B}\\
\mathbf{0}^{T}&1
\end{bmatrix}
$$

2차원에서는 3×3 행렬이 된다.

$$
{}^{world}\mathbf{T}_{base}
=\begin{bmatrix}
0&-1&2\\
1&0&1\\
0&0&1
\end{bmatrix}
$$

앞의 점을 동차좌표로 계산하면 같은 결과를 얻는다.

$$
\begin{bmatrix}
0&-1&2\\
1&0&1\\
0&0&1
\end{bmatrix}
\begin{bmatrix}1\\0\\1\end{bmatrix}
=\begin{bmatrix}2\\2\\1\end{bmatrix}
$$

동차변환의 역변환은 다음과 같다.

$$
\mathbf{T}^{-1}
=\begin{bmatrix}
\mathbf{R}^{T}&-\mathbf{R}^{T}\mathbf{t}\\
\mathbf{0}^{T}&1
\end{bmatrix}
$$

위 예제의 역변환은 다음과 같다.

$$
{}^{base}\mathbf{T}_{world}
=\begin{bmatrix}
0&1&-1\\
-1&0&2\\
0&0&1
\end{bmatrix}
$$

`world`의 점 \((2,2)\)에 역변환을 적용하면 `base_link`의 \((1,0)\)으로 돌아온다.

### 4.4 여러 좌표계 합성

`map → odom → base_link → laser`처럼 여러 좌표계가 연결되어 있으면 경로의 변환을 곱한다.

$$
{}^{map}\mathbf{T}_{laser}
= {}^{map}\mathbf{T}_{odom}
{}^{odom}\mathbf{T}_{base}
{}^{base}\mathbf{T}_{laser}
$$

간단한 수치 예제로 회전 없이 다음 평행이동만 있다고 하자.

- `map → odom`: \((1.0, 0.5)\) m
- `odom → base_link`: \((2.0, 1.0)\) m
- `base_link → laser`: \((0.2, 0.0)\) m

그러면 `map → laser` 평행이동은 \((3.2, 1.5)\) m다. 회전이 포함되면 단순히 평행이동 벡터를 더하면 안 된다. 각 자식 좌표계의 이동을 부모 좌표계 방향으로 회전한 뒤 합성해야 한다.

## 5. 3차원 회전과 쿼터니언

### 5.1 축별 회전행렬

3차원 회전은 x, y, z축 회전행렬로 표현할 수 있다.

$$
\mathbf{R}_x(\phi)=
\begin{bmatrix}
1&0&0\\
0&\cos\phi&-\sin\phi\\
0&\sin\phi&\cos\phi
\end{bmatrix}
$$

$$
\mathbf{R}_y(\theta)=
\begin{bmatrix}
\cos\theta&0&\sin\theta\\
0&1&0\\
-\sin\theta&0&\cos\theta
\end{bmatrix}
$$

$$
\mathbf{R}_z(\psi)=
\begin{bmatrix}
\cos\psi&-\sin\psi&0\\
\sin\psi&\cos\psi&0\\
0&0&1
\end{bmatrix}
$$

roll-pitch-yaw를 고정축 x-y-z 회전으로 해석하면 흔히 다음 순서로 합성한다.

$$
\mathbf{R}=\mathbf{R}_z(\psi)\mathbf{R}_y(\theta)\mathbf{R}_x(\phi)
$$

오일러각은 직관적이지만 회전 순서에 따라 결과가 달라지고, pitch가 ±90° 부근일 때 두 회전축이 겹치는 짐벌락 문제가 있다.

### 5.2 쿼터니언

단위축 \(\hat{\mathbf{u}}=[u_x\ u_y\ u_z]^T\)을 중심으로 \(\alpha\)만큼 회전하는 단위 쿼터니언은 다음과 같다.

$$
\mathbf{q}
=\left[
u_x\sin\frac{\alpha}{2},
u_y\sin\frac{\alpha}{2},
u_z\sin\frac{\alpha}{2},
\cos\frac{\alpha}{2}
\right]
$$

ROS 메시지 순서 `(x, y, z, w)`를 적용해 z축으로 90° 회전하면 다음과 같다.

$$
\mathbf{q}
=\left[0,0,\sin45^\circ,\cos45^\circ\right]
\approx[0,0,0.7071,0.7071]
$$

단위 쿼터니언은 다음 조건을 만족해야 한다.

$$
\lVert\mathbf{q}\rVert
=\sqrt{x^2+y^2+z^2+w^2}=1
$$

부동소수점 연산을 반복하면 노름이 1에서 벗어날 수 있으므로 필요할 때 정규화한다. 또한 \(\mathbf{q}\)와 \(-\mathbf{q}\)는 동일한 회전을 나타낸다. 두 쿼터니언을 단순 비교하거나 보간할 때 이 이중 표현을 고려해야 한다.

turtlesim은 평면에서 움직이므로 roll과 pitch는 0이고 yaw만 사용한다. 저장소의 broadcaster는 다음 변환을 사용한다.

```python
q = quaternion_from_euler(0, 0, msg.theta)
t.transform.rotation.x = q[0]
t.transform.rotation.y = q[1]
t.transform.rotation.z = q[2]
t.transform.rotation.w = q[3]
```

## 6. 로봇 제어에 직접 쓰이는 계산

### 6.1 목표 거리와 도달 판정

목표 도달 여부는 거리와 허용 오차 \(\varepsilon\)로 판단할 수 있다.

$$
\text{reached}=
\begin{cases}
\text{true},&\lVert\mathbf{g}-\mathbf{p}\rVert\le\varepsilon\\
\text{false},&\text{otherwise}
\end{cases}
$$

예를 들어 현재 위치가 \((1.0,1.0)\), 목표가 \((1.3,1.4)\)이면 거리는 0.5 m다. 허용 오차가 0.5 m이면 경계값을 포함하므로 도달한 상태다. 저장소의 `reached` 함수도 `<= tolerance`를 사용하며 음수 허용 오차는 `ValueError`로 거부한다.

### 6.2 목표 방향

목표점의 절대 방향은 `atan2`로 구한다.

$$
\theta_{goal}=\operatorname{atan2}(g_y-y,\ g_x-x)
$$

현재 위치 \((1,2)\), 목표 \((4,6)\)이면 다음과 같다.

$$
\theta_{goal}=\operatorname{atan2}(4,3)
\approx0.9273\text{ rad}\approx53.13^\circ
$$

`atan2(y, x)`는 사분면을 보존하고 \(x=0\)도 처리하므로 `atan(y/x)`보다 안전하다.

### 6.3 각도 오차 정규화

목표 방향과 현재 yaw의 차를 그대로 사용하면 ±π 경계에서 긴 방향으로 회전할 수 있다. 각도 오차를 \([-\pi,\pi)\)로 정규화한다.

$$
e_\theta
=\operatorname{wrap}_{[-\pi,\pi)}(\theta_{goal}-\theta)
$$

저장소 구현과 같은 식은 다음과 같다.

$$
\operatorname{wrap}(\alpha)
=(\alpha+\pi)\bmod(2\pi)-\pi
$$

현재 yaw가 170°, 목표 yaw가 -170°이면 단순 차는 -340°다. 정규화하면 +20°가 되어 반시계 방향으로 짧게 회전한다.

### 6.4 비례 제어와 속도 제한

간단한 목표 추종은 거리와 각도 오차에 비례한 속도를 사용할 수 있다.

$$
v=K_v d,\qquad \omega=K_\omega e_\theta
$$

실제 로봇에서는 최대 속도를 넘지 않도록 제한한다.

$$
v=\operatorname{clip}(K_vd,-v_{max},v_{max})
$$

예를 들어 \(K_v=0.8\), \(d=2.0\) m, \(v_{max}=1.0\) m/s이면 계산값은 1.6 m/s지만 명령은 1.0 m/s로 제한한다. 각도 오차가 클 때는 선속도를 줄여 목표를 등진 채 전진하는 현상을 막을 수 있다.

## 7. ROS 2 TF2의 핵심 개념

### 7.1 TF2가 해결하는 문제

로봇에는 `map`, `odom`, `base_link`, `camera_link`, `laser`처럼 여러 좌표계가 있다. 센서 데이터가 어느 좌표계와 어느 시각의 값인지 모르면 서로 결합할 수 없다. TF2는 시간에 따라 변하는 좌표계 관계를 버퍼에 저장하고, 프레임 사이의 변환을 합성해 제공한다.

예를 들어 레이저 점 \({}^{laser}\mathbf{p}\)를 지도에 표시하려면 TF2가 `map → ... → laser` 경로를 찾고 다음 계산에 해당하는 변환을 제공한다.

$$
{}^{map}\mathbf{p}
= {}^{map}\mathbf{T}_{laser}\,{}^{laser}\mathbf{p}
$$

### 7.2 부모·자식 프레임과 트리 구조

TF2의 각 변환은 부모 프레임과 자식 프레임을 가진다.

```text
world
└── turtle1
```

저장소에서는 `header.frame_id = 'world'`, `child_frame_id = 'turtle1'`로 설정한다. 이 메시지는 `turtle1` 좌표계의 자세가 `world`에서 어떻게 보이는지를 나타내며, 이 문서 표기로는 \({}^{world}\mathbf{T}_{turtle1}\)이다.

정상적인 TF 구조는 트리다.

- 한 자식 프레임은 동시에 하나의 부모만 가진다.
- 순환 연결을 만들지 않는다.
- 프레임 이름은 의미와 기준이 분명해야 한다.
- 같은 물리 프레임을 여러 broadcaster가 경쟁해 발행하지 않는다.

### 7.3 동적 변환과 정적 변환

| 구분 | 대표 도구 | 토픽 | 사용 사례 |
|---|---|---|---|
| 동적 변환 | `TransformBroadcaster` | `/tf` | 이동 로봇의 `odom → base_link` |
| 정적 변환 | `StaticTransformBroadcaster` | `/tf_static` | 고정 장착된 `base_link → laser` |

고정 센서 장착 위치를 주기적으로 `/tf`에 발행할 필요는 없다. 정적 변환으로 발행하면 새 노드가 늦게 참여해도 해당 관계를 받을 수 있고 통신량도 줄어든다.

### 7.4 시간은 좌표계 이름만큼 중요하다

움직이는 로봇의 변환은 시각에 따라 달라진다.

$$
{}^{world}\mathbf{T}_{base}(t_1)
\neq{}^{world}\mathbf{T}_{base}(t_2)
$$

센서 메시지를 변환할 때는 가능하면 센서 데이터의 `header.stamp`에 해당하는 변환을 조회한다. 최신 변환을 과거 센서 데이터에 적용하면 로봇이 이동한 만큼 공간 오차가 생긴다. TF2 조회가 실패하는 대표 원인은 다음과 같다.

- 요청 시각의 변환이 아직 버퍼에 들어오지 않음
- 너무 오래된 시각이라 버퍼에서 제거됨
- 두 프레임 사이에 연결 경로가 없음
- 프레임 이름이 다르거나 철자가 틀림
- 서로 다른 시간 기준을 사용함

### 7.5 `lookup_transform` 방향 읽기

Python에서 다음 형태로 조회한다.

```python
transform = tf_buffer.lookup_transform(
    target_frame,
    source_frame,
    query_time,
)
```

결과는 `source_frame`의 데이터를 `target_frame` 표현으로 바꾸는 변환이다. 즉 다음 식의 \({}^{target}\mathbf{T}_{source}\)에 해당한다.

$$
{}^{target}\mathbf{p}
= {}^{target}\mathbf{T}_{source}\,{}^{source}\mathbf{p}
$$

`lookup_transform('world', 'turtle1', time)`은 `turtle1` 좌표의 점을 `world` 좌표로 바꿀 때 사용하는 변환을 반환한다.

## 8. 저장소 구현으로 보는 `world → turtle1`

대상 파일은 `level_1/turtlesim/ros2_ws/src/turtle_py/turtle_py/tf_marker_broadcaster.py`다. pose 콜백의 핵심 의미는 다음과 같다.

```python
t.header.frame_id = 'world'
t.child_frame_id = 'turtle1'
t.transform.translation.x = msg.x
t.transform.translation.y = msg.y
q = quaternion_from_euler(0, 0, msg.theta)
self.tf.sendTransform(t)
```

`turtlesim/Pose`의 \((x,y,\theta)\)를 받아 다음 2차원 동차변환을 발행하는 것과 같다.

$$
{}^{world}\mathbf{T}_{turtle1}
=\begin{bmatrix}
\cos\theta&-\sin\theta&x\\
\sin\theta&\cos\theta&y\\
0&0&1
\end{bmatrix}
$$

예를 들어 pose가 \((x,y,\theta)=(5,3,\pi/2)\)이면 다음과 같다.

$$
{}^{world}\mathbf{T}_{turtle1}
=\begin{bmatrix}
0&-1&5\\
1&0&3\\
0&0&1
\end{bmatrix}
$$

`turtle1` 전방 2 m 지점 \([2\ 0\ 1]^T\)을 변환하면 `world`의 \([5\ 5\ 1]^T\)가 된다.

waypoint marker는 `header.frame_id = 'world'`로 발행한다. waypoint의 x, y가 이미 `world` 좌표이므로 별도의 좌표 변환이 필요 없다. 반대로 waypoint가 `turtle1` 기준 좌표라면 TF2로 `world` 좌표로 변환한 뒤 `world` marker로 발행하거나, marker의 frame을 `turtle1`로 지정해야 한다.

## 9. TF2 실행과 확인

다음 명령은 Ubuntu 22.04와 ROS 2 Humble을 기준으로 한다. 터미널마다 ROS 환경과 빌드한 overlay를 불러와야 한다.

### 9.1 빌드와 테스트

```bash
cd /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
python3 -m pytest -q src/turtle_py/test
```

### 9.2 노드 실행

터미널 1에서 turtlesim을 실행한다.

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

터미널 2에서 workspace overlay를 불러오고 TF broadcaster를 실행한다.

```bash
cd /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run turtle_py tf_marker_broadcaster
```

### 9.3 변환 확인

터미널 3에서 `world → turtle1` 변환을 계속 확인한다.

```bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros tf2_echo world turtle1
```

토픽과 프레임 설정도 확인할 수 있다.

```bash
ros2 topic echo /tf --once
ros2 topic info /tf --verbose
```

RViz2에서는 Fixed Frame을 `world`로 설정하고 TF display를 추가한다. waypoint도 보려면 Marker display의 토픽을 `/waypoint_markers`로 설정한 뒤 waypoint publisher를 실행한다.

```bash
cd /home/pa27/Git/HyeoungJungKwon_assginments/level_1/turtlesim/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run turtle_py waypoint_publisher
```

## 10. 자주 발생하는 오류와 진단 순서

### 좌표가 반대 방향으로 움직인다

- `target_frame`과 `source_frame`을 바꾸어 조회하지 않았는지 확인한다.
- \({}^{A}\mathbf{T}_{B}\)와 \({}^{B}\mathbf{T}_{A}\)를 혼동하지 않았는지 확인한다.
- 회전 후 이동인지, 이동 후 회전인지 행렬 곱 순서를 확인한다.

### RViz2에 프레임이나 marker가 보이지 않는다

- RViz2 Fixed Frame이 `world`인지 확인한다.
- `/turtle1/pose`, `/tf`, `/waypoint_markers`가 실제로 발행되는지 확인한다.
- marker의 `header.frame_id`가 TF 트리에 존재하는지 확인한다.
- marker alpha 값 `color.a`가 0이 아닌지 확인한다.

### TF 조회가 extrapolation 오류를 낸다

- 메시지 timestamp와 transform timestamp를 비교한다.
- 조회 직전에 충분한 변환이 buffer에 들어왔는지 확인한다.
- 시뮬레이션 시간 사용 여부와 `/clock` 설정을 확인한다.
- 무조건 최신 변환으로 대체하기 전에 시간 오차가 허용되는지 판단한다.

### 쿼터니언 자세가 이상하다

- ROS 필드 순서가 `(x, y, z, w)`인지 확인한다.
- 쿼터니언 노름이 1인지 확인한다.
- degree 값을 radian 인자로 전달하지 않았는지 확인한다.
- roll, pitch, yaw의 적용 순서를 확인한다.

### 각도 제어가 한 바퀴 가까이 회전한다

- 목표각에서 현재각을 뺀 뒤 결과를 \([-\pi,\pi)\)로 정규화한다.
- degree와 radian을 섞지 않는다.
- `atan` 대신 `atan2(\Delta y, \Delta x)`를 사용한다.

## 11. 계산 체크리스트

좌표 변환이나 TF2 문제를 풀 때 다음 순서로 확인한다.

1. 각 벡터가 어느 프레임에서 표현되었는지 적는다.
2. 변환의 부모 프레임과 자식 프레임을 적는다.
3. 원하는 결과가 \({}^{target}\mathbf{T}_{source}\)인지 확인한다.
4. 열벡터 기준으로 오른쪽 변환부터 적용한다.
5. 평행이동 벡터가 어느 부모 좌표계에서 표현되었는지 확인한다.
6. 회전행렬이면 \(\mathbf{R}^{T}\mathbf{R}=\mathbf{I}\), \(\det\mathbf{R}=1\)인지 확인한다.
7. 쿼터니언이면 노름과 `(x, y, z, w)` 순서를 확인한다.
8. 동적 TF이면 데이터와 변환의 timestamp를 확인한다.
9. 수치 예제 하나를 손으로 계산해 축 방향과 부호를 검산한다.

## 12. 연습문제와 정답

### 문제 1: 거리와 방향

로봇 위치가 \((2,1)\), 목표 위치가 \((5,5)\)다. 거리와 목표 방향을 구하라.

<details>
<summary>정답</summary>

변위는 \([3\ 4]^T\), 거리는 5다. 목표 방향은 \(\operatorname{atan2}(4,3)\approx0.9273\) rad, 즉 약 53.13°다.

</details>

### 문제 2: 좌표 변환

`world`에서 로봇 위치가 \((3,2)\), yaw가 90°다. 로봇 좌표계의 점 \((2,1)\)을 `world` 좌표로 변환하라.

<details>
<summary>정답</summary>

$$
\begin{bmatrix}0&-1\\1&0\end{bmatrix}
\begin{bmatrix}2\\1\end{bmatrix}
+\begin{bmatrix}3\\2\end{bmatrix}
=\begin{bmatrix}2\\4\end{bmatrix}
$$

</details>

### 문제 3: 각도 정규화

현재 yaw가 -175°, 목표 yaw가 170°다. 최단 회전을 위한 각도 오차를 구하라.

<details>
<summary>정답</summary>

단순 차는 345°이고 \([-180^\circ,180^\circ)\)로 정규화하면 -15°다. 따라서 시계 방향으로 15° 회전한다.

</details>

### 문제 4: TF2 조회 방향

카메라 좌표의 점을 `map` 좌표로 바꾸려 한다. `lookup_transform`의 target과 source에 무엇을 넣어야 하는가?

<details>
<summary>정답</summary>

`lookup_transform('map', 'camera_link', query_time)`으로 호출한다. 반환값은 \({}^{map}\mathbf{T}_{camera}\)다.

</details>

## 요약

- 벡터 차의 노름은 목표까지의 거리이고, `atan2`는 목표 방향을 제공한다.
- 내적은 방향 정렬과 투영, 외적의 부호는 좌우 회전 판단에 유용하다.
- 회전행렬은 축 방향을 바꾸고 동차변환은 회전과 평행이동을 한 번에 표현한다.
- 변환 합성은 순서가 중요하며, 역회전은 회전행렬의 전치로 구한다.
- ROS 2 TF2는 프레임 관계뿐 아니라 그 관계가 유효한 시각도 관리한다.
- `lookup_transform(target, source, time)`은 source 데이터를 target 좌표로 바꾸는 변환을 반환한다.
- 저장소의 broadcaster는 turtlesim pose를 \({}^{world}\mathbf{T}_{turtle1}\)과 z축 회전 쿼터니언으로 변환해 발행한다.
