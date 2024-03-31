import pytest

from . import EMailService

def test_buildsOnEmpty():
    result = EMailService()

    assert isinstance(result, EMailService)