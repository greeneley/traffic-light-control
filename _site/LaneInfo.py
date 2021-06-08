

class LaneInfo():
    def __init__(self, length=50, width=3.20, number_lane=None, capacity = None):
        self._length = length
        self._width = width
        self._number_lane = number_lane
        self._capacity = capacity
    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    @property
    def number_lane(self):
        return self._number_lane

    @property
    def capacity(self):
        return self._capacity

    @length.setter
    def length(self, new_length):
        self._length = new_length

    @width.setter
    def width(self, new_width):
        self._width = new_width

    @number_lane.setter
    def number_lane(self, new_number_lane):
        self._number_lane = new_number_lane

    @capacity.setter
    def capacity(self, new_capacity):
        self._capacity = new_capacity