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
from TrafficLight import TrafficLight
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


def getDensityValue(VehicleCounter, LaneInfo):
    return (0.25*VehicleCounter.motocycle_count + 1*VehicleCounter.car_count + 3*VehicleCounter.bus_count + 2.5*VehicleCounter.truck_count)/(LaneInfo.number_lane * LaneInfo.length * LaneInfo.width)

def getDensityClass(vehicleCounter, laneInfo):
    """
    Phan loai Density cua giao lo
    """
    densityValue = getDensityValue(vehicleCounter, laneInfo)
    if densityValue < 11:
        return "A"
    elif densityValue < 18:
        return "B"
    elif densityValue < 26:
        return "C"
    elif densityValue < 35:
        return "D"
    elif densityValue < 45:
        return "E"
    else:
        return "F"

def average_speed(speedList):
    if len(speedList) != 0:
        return sum(speedList) / len(speedList)

def run():

    # traci.edge.getLastStepVehicelNumber: lay all vehicle tren 1 edge
    # traci.lanearea.getLastStepVehicleNumber: count vehicle tren 1 detector
    """execute the TraCI control loop"""
    step = 0
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

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if (step % CYCLE_TIME == 0):
            print(f"""KET THUC CHU KY TIN HIEU: KIEM TRA TINH TRANG GIAO THONG""")
            laneInfo = LaneInfo(number_lane=11)
            vehicleCount = VehicleCounter(traci)
            densityClass = getDensityClass(vehicleCount, laneInfo)
            print(f"DENSITYCLASS: {densityClass}")
        # tLight = TrafficLight(traci, GREEN_TIME_DEFAULT, scale=1.0)
        # count_number = len(traci.vehicle.getIDList())
        # print("Tong so phuong tien hien tai: {}".format(len(traci.vehicle.getIDList())))
        # # global_density_level = density_class(count_number)
        # # print("Muc do : {}".format(global_density_level))
        #
        # speed_vehicle = [float(traci.vehicle.getSpeed(_vehicleID)) for _vehicleID in traci.vehicle.getIDList()]
        # # print(speed_vehicle)
        # print("Average Speed: {}".format(average_speed(speed_vehicle)))
        #
        # if step % CYCLE_TIME == 0:
        #     print(f"""KET THUC CHU KY TIN HIEU: KIEM TRA TINH TRANG GIAO THONG""")
        #     global_density_level = density_class(count_number)
        #     print("Muc do density: {}".format(global_density_level))
        #
        #     if global_density_level == "B":
        #         # if not tLight.isChangeTemporary:
        #         print(f"""Change cycle time""")
        #         # tLight.setScale(0.5)
        #         tLight.setNewRedYellowGreen(1.25)
        #         count = 0
        #         while (count < (CYCLE_TIME - 3*2)*1.25*5):
        #             traci.simulationStep()
        #             count_number = len(traci.vehicle.getIDList())
        #             print("Tong so phuong tien hien tai tai nut giao thong: {}".format(len(traci.vehicle.getIDList())))
        #             global_density_level = density_class(count_number)
        #             print("level: {}".format(global_density_level))
        #             # print(f"""COUNT: {count}; STEP: {step}""")
        #             step += 1
        #             count += 1
        #             speed_vehicle = [float(traci.vehicle.getSpeed(_vehicleID)) for _vehicleID in traci.vehicle.getIDList()]
        #             print("Average Speed: {}".format(average_speed(speed_vehicle)))
        #             continue
        #         else:
        #             tLight.setNewRedYellowGreen(1.0)
        #
        #     if global_density_level == "F":
        #         # if not tLight.isChangeTemporary:
        #         print(f"""
        #             Change cycle time
        #         """)
        #         # tLight.setScale(0.5)
        #         tLight.setNewRedYellowGreen(0.75)
        #         count = 0
        #         while (count < (CYCLE_TIME - 3*2)*0.75*5):
        #             traci.simulationStep()
        #             count_number = len(traci.vehicle.getIDList())
        #             print("Tong so phuong tien hien tai: {}".format(len(traci.vehicle.getIDList())))
        #             global_density_level = density_class(count_number)
        #             print("level: {}".format(global_density_level))
        #             print(f"""COUNT: {count}; STEP: {step}""")
        #             step += 1
        #             count += 1
        #             continue
        #         else:
        #             tLight.setNewRedYellowGreen(1.0)
        #
        # if tLight.isChangeTemporary == True:
        #     print(f"""
        #     step change: {_step_change}
        #     """)
        #     if (step - _step_change > 15):
        #         print("RESET")
        #         # tLight.setBackChange()
        #         tLight.setNewRedYellowGreen(1.0)
        #         tLight.setIsChangeTemporary(False)

        #     print("Chu ky duoc reset")
        #     reset()
            # setScaleCycleTime(GREEN_TIME=31)
            # traci.trafficlight.setPhase("0", 2)
        # if step == 138:
        #     traci.trafficlight.setProgram("0", "0")

        # if step == 50:
        #     traci.trafficlight.setPhase("1", 2)
       # if traci.trafficlight.getPhase("0") == 2:
       #      # we are not already switching
       #      if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
       #          # there is a vehicle from the north, switch
       #          traci.trafficlight.setPhase("0", 3)
       #      else:
       #          # otherwise try to keep green for EW
       #          traci.trafficlight.setPhase("0", 2)
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
    traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "--summary", "output/" + fileOutputSummary])
    run()

