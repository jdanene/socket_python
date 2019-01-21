import sys, pytest, os
sys.path.append('../src')


# content of test_sample.py
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5


# content of test_class.py
class TestClass(object):
    def test_one(self):
        x = "this"
        assert 'h' in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, 'check')