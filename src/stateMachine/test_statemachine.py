import pytest

from . import Monitor, State, Detection

def test_init():
    needed_updates = 20
    sut = Monitor(needed_updates)

    assert Detection.noDetection == sut.get_detection()
    assert State.noOccupancy == sut.get_state()

def test_changesToDetecting():
    needed_updates = 20
    sut = Monitor(needed_updates)

    sut.update(True)

    assert Detection.detecting == sut.get_detection()
    assert State.noOccupancy == sut.get_state()

def test_changesToOccupancyWhenDebounced():
    needed_updates = 20
    sut = Monitor(needed_updates)

    for _ in range(needed_updates):
        sut.update(True)

    assert Detection.ObjectDetected == sut.get_detection()
    assert State.Occupancy == sut.get_state()

def test_staysOnOccupiedWhenUpdatedWithFalseButNotDebounced():
    needed_updates = 20
    sut = Monitor(needed_updates)

    for _ in range(needed_updates):
        sut.update(True)
    
    sut.update(False)

    assert Detection.noDetection == sut.get_detection()
    assert State.Occupancy == sut.get_state()

def test_changesToNoOccupationUpdatedWithFalseAndDebounced():
    needed_updates = 20
    sut = Monitor(needed_updates)

    for _ in range(needed_updates):
        sut.update(True)

    for _ in range(needed_updates):
        sut.update(False)
    
    assert Detection.noDetection == sut.get_detection()
    assert State.noOccupancy == sut.get_state()