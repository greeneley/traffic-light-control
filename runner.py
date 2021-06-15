#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2021 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import optparse
import os
import sys

from LaneInfo import LaneInfo
from VehicleCounter import VehicleCounter
from simulator import Program

# from ValueSingleTon import ValueSingleTon
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary  # noqa
import traci  # noqa


GREEN_TIME_DEFAULT = 31
CYCLE_TIME = 89
REPEAT = 5


def getVehicleCountInDetector(traci, detectors):
    count = 0
    for _element in detectors:
        count += traci.lanearea.getLastStepVehicleNumber(_element)
    return count

def getInfoCurrentTrafficLight(traci, tlsID):

    nameProgram = traci.trafficlight.getProgram(tlsID)
    all_program_logics = traci.trafficlight.getAllProgramLogics(tlsID)

    currentphase = None

    for _element in all_program_logics:
        if _element.programID == nameProgram:
            currentphase = _element
            break

    return currentphase

def changeGreenTimeTrafficLightControlForEachLanes(traci, tlsID, density_level, scale=1.0):

    currentphase = getInfoCurrentTrafficLight(traci, tlsID)

    thoigianbutru = 0

    phases = []

    count = 0

    for _element in currentphase.phases:
        if "y" in _element.state:
            continue
        else:
            if density_level[currentphase.phases.index(_element)] == "B":
                thoigianbutru += _element.duration * scale * 0.5
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "C":
                thoigianbutru += _element.duration * scale * 0.7
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "D":
                thoigianbutru += _element.duration * scale * 0.3
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "E":
                thoigianbutru += _element.duration * scale * 0.4
                count += 1
            else:
                count = 1
    for _element in currentphase.phases:
        if "y" in _element.state:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            if density_level[currentphase.phases.index(_element)] == "B":

                phases.append(traci.trafficlight.Phase(duration=_element.duration * scale * (1 + 0.5), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "C":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * scale * (1 + 0.7), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "D":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * scale * (1 + 0.3), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "E":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * scale * (1 + 0.4), state=_element.state))
            else:
                phases.append(traci.trafficlight.Phase(duration=_element.duration * scale - (thoigianbutru/count), state=_element.state))

    newProgram = traci.trafficlight.Logic(tlsID, 0, 0, phases)
    return newProgram

def changeGreenTimeTrafficLightControl(traci, tlsID, density_level):

    currentphase = getInfoCurrentTrafficLight(traci, tlsID)

    phases = []

    K = 0

    if density_level == "B":
        K = 0.5
    elif density_level == "C":
        K = 0.7
    elif density_level == "D":
        K = 0.3
    elif density_level == "E":
        K = 0.4

    for _element in currentphase.phases:
        if "y" in _element.state:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            newDuration = _element.duration * (1 - K)
            phases.append(traci.trafficlight.Phase(duration=newDuration - 5, state=_element.state))
    newProgram = traci.trafficlight.Logic(tlsID, 0, 0, phases)
    return newProgram

def changeCycleTimeTrafficLightControl(traci, tlsID, scale):
    """
    Input: Nhan vao traci mang thong tin chuong trinh tin hieu hien tai
    Output: mot chuong trinh tin hieu moi bao gom:
    """
    currentphase = getInfoCurrentTrafficLight(traci, tlsID)
    phases = []
    for _element in currentphase.phases:
        if "y" in _element.state:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            phases.append(traci.trafficlight.Phase(duration=_element.duration*scale, state=_element.state))
    newProgram = traci.trafficlight.Logic(tlsID, 0, 0, phases)

    return newProgram


def getVolumeToCapacity(VehicleCounter, laneInfo):
    return (0.25*VehicleCounter.motocycle_count + 1*VehicleCounter.car_count + 3*VehicleCounter.bus_count + 2.5*VehicleCounter.truck_count)/laneInfo.capacity


def get_level_of_service(vehicleCounter, laneInfo):
    """
    Phan loai Density cua giao lo
    """
    densityValue = getVolumeToCapacity(vehicleCounter,laneInfo)
    if densityValue < 0.6:
        return "A"
    elif densityValue < 0.7:
        return "B"
    elif densityValue < 0.8:
        return "C"
    elif densityValue < 0.9:
        return "D"
    elif densityValue < 1:
        return "E"
    else:
        return "F"

def average_speed(speedList):
    if len(speedList) != 0:
        return sum(speedList) / len(speedList)

def is_reset_initial(densityList):
    if all(item == "A" for item in densityList):
        return True
    else:
        return False

def run():
    traci.switch("sim1")
    step = 1
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
    traci.close()
    sys.stdout.flush()

def evaluation_road(traci, detectorset, number_lane, capacity):
    """
    laneInfo = LaneInfo(number_lane=11, capacity=66.6)
    vehicleCount = VehicleCounter(traci)
    vehicleCount.getVehicleCountInDetector(NS_DETECTOR + WE_DETECTOR)
    densityClass = get_level_of_service(vehicleCount, laneInfo)
    print(f"DANH GIA TOAN PHAN")
    print(f"STEP: {step}, Density class: {densityClass}")
    """
    laneInfo = LaneInfo(number_lane=number_lane, capacity=capacity)
    vehicleCount = VehicleCounter(traci)
    vehicleCount.getVehicleCountInDetector(detectorset)
    los = get_level_of_service(vehicleCount, laneInfo)
    return los


def run_with_new_program():
    traci.switch("sim1")
    # traci.edge.getLastStepVehicelNumber: lay all vehicle tren 1 edge
    # traci.lanearea.getLastStepVehicleNumber: count vehicle tren 1 detector
    """execute the TraCI control loop"""
    step = 1
    count_reset = 0

    NS_DETECTOR = ["e2det_-695446623#0_1", "e2det_-695446623#0_0", "e2det_-695429325#0_1", "e2det_-695429325#0_0"]
    WE_DETECTOR = ["e2det_695504114#2_0", "e2det_695504114#2_1", "e2det_695504114#2_2","e2det_695446624#1_2", "e2det_695446624#1_1", "e2det_695446624#1_0"]
    SCALE_LEVEL = [0.8, 1.0, 1.15]

    # while step traci.simulation.getMinExpectedNumber() > 0:
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        """
        MODULE 1: TIME OF DAY
        DONE: DA DUOC THIET LAP TRONG TRAFFIC_LIGHT
        """
        """
        MODULE 2: DANH GIA TINH TRANG GIAO THONG
        """

        draftPrograms = [getInfoCurrentTrafficLight(traci, tlsID="gneJ0")]

        if (step % CYCLE_TIME == 0):

            """TEST"""
            # draftPrograms.append(changeCycleTimeTrafficLightControl(traci, tlsID="gneJ0"))

            print("="*50)
            print(f"Ket thuc 1 chu ky tin hieu")
            print(f"Kiem tra tinh trang giao thong hien tai")

            """
            MODULE 2.1: Danh gia toan phan
            """

            lostotal = evaluation_road(traci, detectorset=NS_DETECTOR + WE_DETECTOR, number_lane=11, capacity=66.6)
            print(f"DANH GIA TOAN PHAN")
            print(f"STEP: {step}, Density class: {lostotal}")

            """
            MODULE 2.2: Danh gia rieng phan
            """
            print(f"DANH GIA RIENG PHAN")

            los_part_NS = evaluation_road(traci, detectorset=NS_DETECTOR, number_lane=len(NS_DETECTOR), capacity=26.6)
            print(f"STEP: {step}, Density class: {los_part_NS}")

            los_part_WE = evaluation_road(traci, detectorset=WE_DETECTOR, number_lane=len(WE_DETECTOR), capacity=40)
            print(f"STEP: {step}, Density class: {los_part_WE}")


            if count_reset == REPEAT:
                if is_reset_initial([lostotal, los_part_WE, los_part_NS]):
                    print("=" * 50)
                    print("Reset chuong trinh tin hieu")
                    traci.trafficlight.setProgram("gneJ0", "morning")
                count_reset = 0
            elif count_reset == 0:
                if lostotal in ["D", "C", "F"]:
                    for _scale in SCALE_LEVEL:
                        draftPrograms.append(changeCycleTimeTrafficLightControl(traci, tlsID="gneJ0", scale=0.85 * _scale))
                if not los_part_NS == los_part_WE == "A":
                    for _scale in SCALE_LEVEL:
                        draftPrograms.append(changeGreenTimeTrafficLightControlForEachLanes(traci, tlsID="gneJ0",
                                                                                            density_level=[
                                                                                                los_part_NS,
                                                                                                los_part_NS,
                                                                                                los_part_WE,
                                                                                                los_part_WE], scale=_scale))
            else:
                count_reset += 1

        """
        MODULE 3: THUC HIEN SIMULATOR CHO TUNG QUYET DINH
        """

        """
        MODULE 4: CAP NHAT CHUONG TRINH DIEU KHIEN TIN HIEU PHU HOP
        """
        if len(draftPrograms) > 0:
            simulator = Program(draftPrograms)
            simulator.run()
            bestProgram = simulator.getBestProgram()
            print("=" * 50)
            print(f"Apply new program in step: {step}:")
            print(f"{bestProgram}")

            traci.trafficlight.setCompleteRedYellowGreenDefinition("gneJ0", bestProgram)
            if bestProgram == draftPrograms[0]:
                count_reset = 0
            else:
                count_reset += 1
            traci.switch("sim1")
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    fileOutputSummary = "sumoSummary_01.xml"
    options = get_options()
    sumoBinary = checkBinary('sumo' if options.nogui else 'sumo-gui')
    traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "--start", "--delay", "100", "--summary", "output/" + fileOutputSummary], label="sim1")
    run_with_new_program()
