import pytest

from .. import stateMachine

def test_init():
    testValue = 20
    sut = stateMachine.Debouncer(testValue)
    assert not sut.is_debounced()

def test_debounce():
    iterations = 20
    sut = stateMachine.Debouncer(iterations)

    for _ in range(iterations - 1):
        sut.update(True)
        assert not sut.is_debounced()

    sut.update(True)
    assert sut.is_debounced()

def test_debounce_resets():
    iterations = 20
    sut = stateMachine.Debouncer(iterations)
    half_iterations = iterations // 2

    for _ in range(half_iterations - 1):
        sut.update(True)
        assert not sut.is_debounced()

    for _ in range(iterations):
        sut.update(False)
        assert not sut.is_debounced()