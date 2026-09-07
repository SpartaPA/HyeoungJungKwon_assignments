import numpy as np
import pytest

from src.vectors import det, gauss_eliminate, inverse_gauss_jordan, rank

ATOL = 1e-12

A = np.array([[3.0, 1.0, 2.0], [1.0, 4.0, 1.0], [2.0, -1.0, 5.0]])
B = np.array([11.0, 1.0, 20.0])


def test_gaussian_elimination_finds_integer_solution_and_steps():
    x, steps = gauss_eliminate(A, B, pivoting=True)
    assert np.allclose(x, [2.0, -1.0, 3.0], atol=ATOL)
    assert np.allclose(A @ x, B, atol=ATOL)
    assert len(steps) == 4
    assert np.allclose(np.tril(steps[-1][:, :3], -1), 0.0, atol=ATOL)


def test_rank_classifies_unique_none_and_infinite_solutions():
    assert rank(A) == rank(np.column_stack((A, B))) == 3
    dependent = np.array([[1.0, 2.0], [2.0, 4.0]])
    assert rank(dependent) == rank(np.column_stack((dependent, [3.0, 6.0]))) == 1
    assert rank(dependent) < rank(np.column_stack((dependent, [3.0, 7.0])))


def test_determinant_and_inverse_match_reference():
    inverse = inverse_gauss_jordan(A)
    assert np.isclose(det(A), 42.0, atol=ATOL)
    assert np.allclose(A @ inverse, np.eye(3), atol=ATOL)
    assert np.allclose(inverse, np.linalg.inv(A), atol=ATOL)  # 검산용


def test_partial_pivoting_reduces_small_pivot_error():
    eps = 1e-12
    matrix = np.array([[eps, 1.0], [1.0, 1.0]])
    rhs = np.array([1.0, 2.0])
    exact = np.array([1.0 / (1.0 - eps), (1.0 - 2.0 * eps) / (1.0 - eps)])
    no_pivot, _ = gauss_eliminate(matrix, rhs, pivoting=False)
    pivoted, _ = gauss_eliminate(matrix, rhs, pivoting=True)
    error_no_pivot = np.sqrt(np.sum((no_pivot - exact) ** 2))
    error_pivoted = np.sqrt(np.sum((pivoted - exact) ** 2))
    assert error_pivoted < error_no_pivot


def test_singular_and_invalid_matrices_raise():
    with pytest.raises(np.linalg.LinAlgError):
        inverse_gauss_jordan([[1.0, 2.0], [2.0, 4.0]])
    with pytest.raises(ValueError):
        inverse_gauss_jordan(np.ones((2, 3)))
    with pytest.raises(ZeroDivisionError):
        gauss_eliminate([[0.0, 1.0], [0.0, 2.0]], [1.0, 2.0])
