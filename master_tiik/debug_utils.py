from time import time


class TimeItMetacls(type):
    measures = {}

    def __call__(cls, name) -> 'TimeIt':
        if name in TimeItMetacls.measures:
            return TimeItMetacls.measures[name]
        instance = super().__call__(name)
        TimeItMetacls.measures[name] = instance
        return instance

    def __str__(self):
        return "\n\n".join([str(instance) for instance in TimeItMetacls.measures.values()])


class TimeIt(metaclass=TimeItMetacls):
    def __init__(self, name):
        self.start_time = 0
        self.times = []
        self.name = name

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, *args):
        self.times.append(time() - self.start_time)

    def __str__(self):
        return f"Resume for part {self.name}" \
               f"\n\tIterations : {len(self.times)}" \
               f"\n\tAverage time: {sum(self.times) / len(self.times)}" \
               f"\n\tTotal time taken : {sum(self.times)}"


if __name__ == '__main__':
    with TimeIt("tets"):
        for i in range(1000000):
            pass
    with TimeIt("tets"):
        for i in range(1000000):
            pass
    print(TimeIt)
