

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    def __init__(self, step):
        self.value = step + 15
    def getValue(self):
        return self.value

if __name__ == "__main__":
    s1 = Singleton(12)
    s2 = Singleton(14)
    s1.getValue()
    s2.getValue()
    print(s1.value)
    print(s2.value)
    del s1
    s2 = Singleton(14)
    s2.getValue()
    print(s2.value)

