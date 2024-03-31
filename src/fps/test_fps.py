import pytest
import numpy as np

from . import FPS

@pytest.fixture
def init():
    return FPS()

def test_init(init):
    assert isinstance(init, FPS)

def test_initsEmpty(init):
    assert init.fps == []

def test_addition(init):
    testValue = 99.0
    init.update(testValue)
    assert testValue in init.fps

def test_min_value(init):
    input = [5,10]
    for value in input:
        init.update(value)

    rtn = init.get_min()

    assert rtn == np.min(input)
    assert rtn != np.max(input)

def test_max_value(init):
    input = [5,10]
    for value in input:
        init.update(value)

    rtn = init.get_max()

    assert rtn == np.max(input)
    assert rtn != np.min(input)

def test_mean_value(init):
    input = [5,10,50]
    
    for value in input:
        init.update(value)

    rtn = init.get_mean()

    assert rtn == np.mean(input)
    assert rtn != 10
    assert rtn != 5

def test_max_value2(init):
    input = [5,10]
    
    for value in input:
        init.update(value)
    
    rtn = init.get_max()

    assert rtn == 10
    # assert init.get_min() != 10