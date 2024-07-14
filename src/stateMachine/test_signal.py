import pytest

from . import Signal

def test_init():
    sut = Signal()

    assert not sut.get_current()
    assert not sut.get_last()
    assert not sut.turned_active()
    assert not sut.turned_inactive()
    
def test_turnsActive():
    sut = Signal()

    sut.update(True)

    assert sut.get_current()
    assert not sut.get_last()
    assert sut.turned_active()
    assert not sut.turned_inactive()

def test_staysActive():
    sut = Signal()

    sut.update(True)
    sut.update(True)

    assert sut.get_current()
    assert sut.get_last()
    assert not sut.turned_active()
    assert not sut.turned_inactive()

def test_turnsInactive():
    sut = Signal()

    sut.update(True)
    sut.update(False)

    assert not sut.get_current()
    assert sut.get_last()
    assert not sut.turned_active()
    assert sut.turned_inactive()

def test_staysInactive():
    sut = Signal()

    sut.update(True)
    sut.update(False)
    sut.update(False)

    assert not sut.get_current()
    assert not sut.get_last()
    assert not sut.turned_active()
    assert not sut.turned_inactive()