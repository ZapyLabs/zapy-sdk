from zapy.utils.singleton import SingletonMeta


class SingletonExample(metaclass=SingletonMeta):
    def __init__(self, a: int):
        self.a = a


def test_singleton():
    s1 = SingletonExample(3)

    for i in range(10):
        s2 = SingletonExample(i)
        assert s1 is s2
        assert s2.a == 3
    assert isinstance(s1, SingletonExample)
