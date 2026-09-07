import numpy as np
import pytest

from src.coordinate_chain import base_point_to_camera, camera_point_to_base, default_chain
from src.transform import inv_T

ATOL = 1e-12


def test_default_chain_has_expected_frames_and_composition():
    chain = default_chain()
    assert chain.frames() == ["base", "link", "camera"]
    assert np.allclose(chain.T("base", "camera"), chain.get("base", "link") @ chain.get("link", "camera"), atol=ATOL)
    assert np.allclose(chain.T("camera", "base"), inv_T(chain.T("base", "camera")), atol=ATOL)


def test_camera_base_roundtrip_supports_point_clouds():
    points = np.array([[0.1, 0.2, 0.8], [-0.2, 0.0, 0.5]])
    base = camera_point_to_base(points)
    assert base.shape == points.shape
    assert np.allclose(base_point_to_camera(base), points, atol=ATOL)


def test_unconnected_frame_raises_key_error():
    with pytest.raises(KeyError):
        default_chain().T("base", "missing")
