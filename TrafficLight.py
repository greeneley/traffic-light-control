



class TrafficLight:
    def __init__(self, traci, green_time, scale):
        self.traci = traci
        self.green_time = green_time
        self.scale = scale

    def __format__(self, scale: float) -> float:
        return super().__format__(float)

    def setScale(self, scale):
        self.scale = scale



    def setNewRedYellowGreen(self, scale):
        phases = []
        phases.append(self.traci.trafficlight.Phase(self.green_time * scale, "GrGr"))
        phases.append(self.traci.trafficlight.Phase(3, "yryr"))
        phases.append(self.traci.trafficlight.Phase(self.green_time * scale, "rGrG"))
        phases.append(self.traci.trafficlight.Phase(3, "ryry"))
        logic = self.traci.trafficlight.Logic("0", 0, 0, phases)
        self.traci.trafficlight.setCompleteRedYellowGreenDefinition("0", logic)
