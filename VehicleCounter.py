
class VehicleCounter():
    def __init__(self, traci):

        self.traci = traci
        self._motocycle_count = 0
        self._car_count = 0
        self._bus_count = 0
        self._truck_count = 0

    @property
    def motocycle_count(self):
        return self._motocycle_count

    @property
    def car_count(self):
        return self._car_count

    @property
    def bus_count(self):
        return self._bus_count

    @property
    def truck_count(self):
        return self._truck_count

    @car_count.setter
    def car_count(self, new_value):
        self._car_count = new_value

    def getVehicleCount(self):
        self.car_count = len(self.traci.vehicle.getIDList())