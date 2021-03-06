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
import subprocess

OD_file = "./data/NguyenVanLinh/"

def generate_odfile(counts):
    if os.path.exists(OD_file + "nvl_generation.od"):
        os.remove(OD_file + "nvl_generation.od")
    with open(OD_file + "nvl_generation.od", "w") as file:
        print("""$O;D2s * From-Time  To-Time
0.00 1.00
* Factor
2.00
* some
* additional
* comments""", file=file)
        print(f"""         1          5       {counts["north"]}
         1          6       {counts["north"]}
         1          7       {counts["north"]}
         1          8       {counts["north"]}""", file=file)
        print(f"""        2          5       {counts["west"]}
         2          7       {counts["west"]}
         2          8       {counts["west"]}""", file=file)
        print(f"""        3          5       {counts["south"]}
         3          6       {counts["south"]}
         3          7       {counts["south"]}
         3          8       {counts["south"]}""", file=file)
        print(f"""        4          5       {counts["east"]}
         4          6       {counts["east"]}
         4          7       {counts["east"]}""", file=file)
        file.close()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


class Program:
    def __init__(self, programs, counts):
        self._programs = programs
        self.counts = counts

    def run(self):

        options = get_options()
        sumoBinary = checkBinary('sumo-gui' if options.nogui else 'sumo')

        generate_odfile(self.counts)

        subprocess.run(f"od2trips -c {OD_file}nvl_generation.config.xml -n {OD_file}nvl.taz.xml -d {OD_file}nvl_generation.od -o {OD_file}nvl_generation.odtrips.xml",shell=True)
        subprocess.run(f"duarouter -c {OD_file}nvl_generation.trips2routes.duarcfg",shell=True)

        for _element in self._programs:
            index = self._programs.index(_element)
            step_time = 1
            traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl_generation.sumocfg",
                         "--quit-on-end", "--start", "--no-warnings",
                         "--summary",
                         "output/sumoSummary_" + str(index) + ".xml"], label="sim2")
            # traci.start([sumoBinary, "-c", "data/NguyenVanLinh/nvl.sumocfg", "--delay", "50", "-b", "0", "-e", "3600",
            #              "--quit-on-end", "--start",
            #              "--summary",
            #              "output/sumoSummary_" + str(index) + ".xml"], label="sim2")
            traci.switch("sim2")
            traci.trafficlight.setCompleteRedYellowGreenDefinition("gneJ0", _element)
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                step_time += 1
            traci.close()
            subprocess.run(f"python /home/tdinh/Documents/Project/sumo/tools/xml/xml2csv.py output/sumoSummary_{str(index)}.xml", shell=True)

        traci.switch("sim1")

        # sys.stdout.flush()

    def getBestProgram(self):
        results = {}
        for _element in self._programs:
            index = self._programs.index(_element)
            fileSummary = pd.read_csv("output/sumoSummary_" + str(index) + ".csv", sep=";")
            speed = fileSummary["step_waiting"].mean()
            results[index] = speed
        highest_value = min(results.items(), key=operator.itemgetter(1))[0]
        return self._programs[highest_value]

