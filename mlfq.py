from typing import List
import collections

class MLFQ:

    # TODO finish out methods

    def __init__(self, time_quantums: List[float] = None, num_queues: int = 4, boost_interval: int = 1000):
        '''
        Initialize the MLFQ algorithm
        '''
        if (time_quantums != None):
            if (len(time_quantums) != num_queues):
                print("The provided time quantums does not match the number of queues")
                raise ValueError
        else:
            # TODO assign time quantums properly
            self.time_quantums = [2**i for i in range(num_queues)]
            pass

        self.queues = [collections.deque() for _ in range(num_queues)]
        self.boost_intervals = boost_interval
        self.cur_time = 0
        self.last_boost_time = 0


    def boost_priority(self):
        pass

    def schedule(self):
        pass

    def add_process(self):
        pass


if __name__ == "__main__":
    pass