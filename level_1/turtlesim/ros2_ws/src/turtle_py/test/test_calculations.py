import math
import pytest
from turtle_py.calculations import distance, normalize_angle, reached, target_angle

def test_distance_normal_and_zero():
    assert distance(0, 0, 3, 4) == pytest.approx(5.0)
    assert distance(2, 2, 2, 2) == pytest.approx(0.0)

@pytest.mark.parametrize('angle', [math.pi, -math.pi, 3*math.pi, -3*math.pi])
def test_normalize_angle(angle):
    assert -math.pi <= normalize_angle(angle) <= math.pi

def test_target_angle_and_normalized_error():
    assert target_angle(0, 0, 0, 1) == pytest.approx(math.pi / 2)
    error = normalize_angle(target_angle(0, 0, -1, -0.1) - math.pi)
    assert -math.pi <= error <= math.pi

def test_reached_boundary_and_invalid_tolerance():
    assert reached(0, 0, 0.5, 0, 0.5)
    assert not reached(0, 0, 0.51, 0, 0.5)
    with pytest.raises(ValueError): reached(0, 0, 0, 0, -1)
