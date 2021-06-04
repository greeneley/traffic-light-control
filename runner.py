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

import os
import sys
import optparse
from VehicleCounter import VehicleCounter
from LaneInfo import LaneInfo
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


# def generate_routefile():
#     random.seed(42)  # make tests reproducible
#     N = 3600  # number of time steps
#     # demand per second from different directions
#     pWE = 1. / 10
#     # pEW = 1. / 11
#     pNS = 1. / 10
#     with open("data/cross.rou.xml", "w") as routes:
#         print("""<routes>
#         <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
# guiShape="passenger"/>
#         <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>
#
#         <route id="right" edges="51o 1i 2o 52i" />
#         <route id="left" edges="52o 2i 1o 51i" />
#         <route id="down" edges="54o 4i 3o 53i" />""", file=routes)
#         vehNr = 0
#         for i in range(N):
#             if random.uniform(0, 1) < pWE:
#                 print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
#                     vehNr, i), file=routes)
#                 vehNr += 1
#             # if random.uniform(0, 1) < pEW:
#             #     print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
#             #         vehNr, i), file=routes)
#             #     vehNr += 1
#             if random.uniform(0, 1) < pNS:
#                 print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
#                     vehNr, i), file=routes)
#                 vehNr += 1
#         print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>

GREEN_TIME_DEFAULT = 31
CYCLE_TIME = 68



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

def changeGreenTimeTrafficLightControlForEachLanes(traci, tlsID, density_level):

    currentphase = getInfoCurrentTrafficLight(traci, tlsID)

    thoigianbutru = 0

    phases = []

    count = 0

    for _element in currentphase.phases:
        if _element.duration < 10:
            continue
        else:
            if density_level[currentphase.phases.index(_element)] == "B":
                thoigianbutru += _element.duration * 0.5
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "C":
                thoigianbutru += _element.duration * 0.7
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "D":
                thoigianbutru += _element.duration * 0.3
                count += 1

            elif density_level[currentphase.phases.index(_element)] == "E":
                thoigianbutru += _element.duration * 0.4
                count += 1

    for _element in currentphase.phases:
        if _element.duration < 10:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            if density_level[currentphase.phases.index(_element)] == "B":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * (1 - 0.5), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "C":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * (1 - 0.7), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "D":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * (1 - 0.3), state=_element.state))

            elif density_level[currentphase.phases.index(_element)] == "E":
                phases.append(traci.trafficlight.Phase(duration=_element.duration * (1 - 0.4), state=_element.state))

            else:
                phases.append(traci.trafficlight.Phase(duration=_element.duration + (thoigianbutru/count), state=_element.state))

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
        if _element.duration < 10:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            newDuration = _element.duration * (1 - K)
            phases.append(traci.trafficlight.Phase(duration=newDuration - 5, state=_element.state))
    newProgram = traci.trafficlight.Logic(tlsID, 0, 0, phases)
    return newProgram

def changeCycleTimeTrafficLightControl(traci, tlsID):
    """
    Input: Nhan vao traci mang thong tin chuong trinh tin hieu hien tai
    Output: mot chuong trinh tin hieu moi bao gom:
    """
    currentphase = getInfoCurrentTrafficLight(traci, tlsID)
    phases = []
    for _element in currentphase.phases:
        if _element.duration < 10:
            phases.append(traci.trafficlight.Phase(duration=_element.duration, state=_element.state))
        else:
            phases.append(traci.trafficlight.Phase(duration=_element.duration*0.75, state=_element.state))
    newProgram = traci.trafficlight.Logic(tlsID, 0, 0, phases)

    return newProgram
    #
    # phases.append(traci.trafficlight.Phase(GREEN_TIME, "GrGr"))
    # phases.append(traci.trafficlight.Phase(3, "yryr"))
    # phases.append(traci.trafficlight.Phase(GREEN_TIME, "rGrG"))
    # phases.append(traci.trafficlight.Phase(3, "ryry"))
    # logic = traci.trafficlight.Logic("0", 0, 0, phases)
    #
    # return logic

def getDensityValue(VehicleCounter, LaneInfo):

    return (0.25*VehicleCounter.motocycle_count + 1*VehicleCounter.car_count + 3*VehicleCounter.bus_count + 2.5*VehicleCounter.truck_count)/(LaneInfo.number_lane * LaneInfo.length * LaneInfo.width)

def getDensityClass(vehicleCounter, laneInfo):
    """
    Phan loai Density cua giao lo
    """
    densityValue = getDensityValue(vehicleCounter, laneInfo)
    print(densityValue)
    if densityValue < 0.05:
        return "A"
    elif densityValue < 0.9:
        return "B"
    elif densityValue < 1.3:
        return "C"
    elif densityValue < 1.75:
        return "D"
    elif densityValue < 2.25:
        return "E"
    else:
        return "F"

def average_speed(speedList):
    if len(speedList) != 0:
        return sum(speedList) / len(speedList)

def run():
    traci.switch("sim1")
    # traci.edge.getLastStepVehicelNumber: lay all vehicle tren 1 edge
    # traci.lanearea.getLastStepVehicleNumber: count vehicle tren 1 detector
    """execute the TraCI control loop"""
    step = 1


    # NORTH_DETECTOR = ["e2det_gneE2_0", "e2det_gneE2_1"]
    # SOUTH_DETECTOR = ["e2det_-695429325#0_1", "e2det_-695429325#0_0"]
    # WEST_DETECTOR = ["e2det_695504114#2_0", "e2det_695504114#2_1", "e2det_695504114#2_2"]
    # EAST_DETECTOR = ["e2det_695446624#1_2", "e2det_695446624#1_1", "e2det_695446624#1_0"]

    NS_DETECTOR = ["e2det_-695446623#0_1", "e2det_-695446623#0_0", "e2det_-695429325#0_1", "e2det_-695429325#0_0"]
    WE_DETECTOR = ["e2det_695504114#2_0", "e2det_695504114#2_1", "e2det_695504114#2_2","e2det_695446624#1_2", "e2det_695446624#1_1", "e2det_695446624#1_0"]

    # phases = []
    # phases.append(traci.trafficlight.Phase(GREEN_TIME, "GrGr"))
    # phases.append(traci.trafficlight.Phase(3, "yryr"))
    # phases.append(traci.trafficlight.Phase(GREEN_TIME, "rGrG"))
    # phases.append(traci.trafficlight.Phase(3, "ryry"))
    # logic = traci.trafficlight.Logic("0", 0, 0, phases)
    # traci.trafficlight.setCompleteRedYellowGreenDefinition("0", logic)

    # # we start with phase 2 where EW has green
    # traci.trafficlight.setProgram("0", "0")
    # traci.trafficlight.setPhase("0", 2)
    # global GREEN_TIME_DEFAULT
    # global CYCLE_TIME
    # laneInfo = LaneInfo()

    while step < 8400 or traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()



        """
        MODULE 1: TIME OF DAY
        DONE: DA DUOC THIET LAP TRONG TRAFFIC_LIGHT
        """
        # draftPrograms = []
        # draftPrograms.append(changeCycleTimeTrafficLightControl(traci, tlsID="gneJ0"))

        # changeCycleTimeTrafficLightControl(traci, tlsID="gneJ0")

        """
        MODULE 2: DANH GIA TINH TRANG GIAO THONG
        """

        draftPrograms = []

        if (step % CYCLE_TIME == 0):

            print(f"""KET THUC CHU KY TIN HIEU: KIEM TRA TINH TRANG GIAO THONG""")

            """
            MODULE 2.1: Danh gia toan phan
            """

            # draftPrograms.append(changeGreenTimeTrafficLightControlForEachLanes(traci, tlsID="gneJ0"))

            laneInfo_NS = LaneInfo(number_lane=len(NS_DETECTOR))
            vehicleCount_NS = VehicleCounter(traci)
            vehicleCount_NS.getVehicleCountInDetector(NS_DETECTOR)
            densityClass_NS = getDensityClass(vehicleCount_NS, laneInfo_NS)
            print(f"STEP: {step}, Density class: {densityClass_NS}")

            laneInfo_WE = LaneInfo(number_lane=len(WE_DETECTOR))
            vehicleCount_WE = VehicleCounter(traci)
            vehicleCount_WE.getVehicleCountInDetector(WE_DETECTOR)
            densityClass_WE = getDensityClass(vehicleCount_WE, laneInfo_WE)
            print(f"STEP: {step}, Density class: {densityClass_WE}")

            densityClass_NS = "B"
            densityClass_WE = "D"
            draftPrograms.append(changeGreenTimeTrafficLightControlForEachLanes(traci, tlsID="gneJ0", density_level=[densityClass_NS,densityClass_NS,densityClass_WE,densityClass_WE]))

            # if densityClass == "D" or densityClass == "E" or densityClass == "F":
            #     draftPrograms.append(changeCycleTimeTrafficLightControl(traci, tlsID="gneJ0"))
            #     draftPrograms.append(changeGreenTimeTrafficLightControl(traci, tlsID="gneJ0"))



            """
            MODULE 2.2: Danh gia rieng phan
            """

            laneInfo = LaneInfo(number_lane=11)
            vehicleCount = VehicleCounter(traci)
            vehicleCount.getVehicleCount()
            densityClass = getDensityClass(vehicleCount, laneInfo)
            print(f"STEP: {step}, Density class: {densityClass}")

        """
        MODULE 2.2: Danh gia rieng phan
        """

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

            traci.trafficlight.setCompleteRedYellowGreenDefinition("gneJ0", bestProgram)
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
    print(sumoBinary)
    # first, generate the route file for this simulation
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    # traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg",
    #                          "--tripinfo-output", "tripinfo.xml",
    #                         "--fcd-output", "sumoTrace.xml"])
    traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "--start", "--delay", "50", "--summary", "output/" + fileOutputSummary], label="sim1")
    run()

