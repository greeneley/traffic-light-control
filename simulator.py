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

import operator
import os
import sys
import optparse
# from ValueSingleTon import ValueSingleTon
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa
import pandas as pd

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


class Program:
    def __init__(self, programs):
        self._programs = programs

    def run(self):
        fileOutputSummary = "sumoSummary_02.xml"

        options = get_options()

        sumoBinary = checkBinary('sumo-gui' if options.nogui else 'sumo')
        for _element in self._programs:
            index = self._programs.index(_element)
            step_time = 1
            traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "-b", "0", "-e", "3600",
                         "--quit-on-end", "--start",
                         "--summary",
                         "output/sumoSummary_" + str(index) + ".xml"], label="sim2")
            # traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "--delay", "50", "-b", "0", "-e", "3600",
            #              "--quit-on-end", "--start",
            #              "--summary",
            #              "output/sumoSummary_" + str(index) + ".xml"], label="sim2")
            traci.switch("sim2")
            traci.trafficlight.setCompleteRedYellowGreenDefinition("gneJ0", _element)
            while step_time < 3600 or traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                step_time += 1
            traci.close()
        traci.switch("sim1")

        # sys.stdout.flush()

    def getBestProgram(self):
        results = {}
        for _element in self._programs:
            index = self._programs.index(_element)
            fileSummary = pd.read_csv("output/sumoSummary_" + str(index) + ".csv", sep=";")
            speed = fileSummary["step_meanSpeed"].mean()
            results[index] = speed
        highest_value = max(results.items(), key=operator.itemgetter(1))[0]
        return self._programs[highest_value]



