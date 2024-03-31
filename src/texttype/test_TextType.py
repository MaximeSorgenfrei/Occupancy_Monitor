import pytest

from . import TextType

def test_buildsOnEmpty():
    result = TextType()
    
    assert isinstance(result, TextType) 