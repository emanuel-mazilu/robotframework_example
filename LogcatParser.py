#!/usr/bin/env python3
import argparse
from datetime import datetime
import yaml
import sys

def cmd_line():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-f", "--file", help="Input logcat file", required=True)
    parser.add_argument("-o", "--output", help="Output yaml file", required=False, default="output.yml")
    parser.add_argument("-p", "--percentage", help="Total app pass percentage", required=False, default=75, type=int)
    parser.add_argument("-l", "--lifespan", help="App max lifespan", required=False, default=30, type=int)
    args = parser.parse_args()
    return args


class LogcatParser():
    

    def __init__(self) -> None:
        self.apps = []
        self.matching_lines_start = []
        self.matching_lines_stop = []
        self.applications = {}


    def print(self, message):
        from robot.api import logger
        logger.info(message, html=True, also_console=True)
        # force flush to display at runtime
        sys.stdout.flush()

    def setup(self, input_file):
        with open(input_file) as f:
            lines = f.readlines()
        for line in lines:
            if "ActivityTaskManager: START u0" in line:
                # Find full name of the app
                start_index = line.find("cmp=") + len("cmp=")
                end_index = line.find(" ", start_index)
                app = line[start_index:end_index]
                self.apps.append(app)
                self.matching_lines_start.append(line)
            if "Layer: Destroyed ActivityRecord" in line:
                self.matching_lines_stop.append(line)
        if self.apps != []:
            return True, "SETUP PASSED"


    def run(self, output="output.yml"):
        self.applications = {}

        format = "%H:%M:%S.%f"

        for app in self.apps:
            self.applications[app] = {"start_times": [], "stop_times": []}

            #Get start time
            for start_line in self.matching_lines_start:
                if app in start_line:
                    app_start = start_line.split(" ")[1]
                    self.applications[app]["start_times"].append(app_start) 

            #Get stop time
            for stop_line in self.matching_lines_stop:
                if app.split("/")[0] in stop_line:
                    app_stop = stop_line.split(" ")[1]
                    self.applications[app]["stop_times"].append(app_stop)

            #Calculate lifespan
            for i in range(len(self.applications[app]["start_times"])):
                stop_time = self.applications[app]["stop_times"][i]
                start_time =self.applications[app]["start_times"][i]
                t1 = datetime.strptime(start_time, format)
                t2 = datetime.strptime(stop_time, format)
                result = t2 - t1
                self.applications[app]["lifespan"] = result.total_seconds()

        yaml_string = yaml.dump(self.applications)
        with open(output, "w") as f:
            f.write(yaml_string)

        return True, "Run PASSED"


    def teardown(self, max_lifespan=30, total_app_percentage=75):
        no_of_apps = len(self.applications)
        i = 0
        for app in self.applications:
            if self.applications[app]["lifespan"] > max_lifespan:
                i = i + 1
                self.print("WARNING: " + app + " took " + str(self.applications[app]["lifespan"]) + "s")

        print("Total no of apps", no_of_apps)
        print("Good times no of apps", no_of_apps - i)
        print("Bad times no of apps", i)
        print(total_app_percentage, "% apps", no_of_apps * total_app_percentage / 100)
        print("Test verdict:  ", end="")

        # Get verdict
        if no_of_apps - i > no_of_apps * total_app_percentage / 100:
            print("PASS")
            return True, "TEST PASS"
        else:
            print("FAIL")
            return False, "TEST FAIL"


if __name__ == "__main__":
    args = cmd_line()
    logcatparser = LogcatParser()
    logcatparser.setup(args.file)
    logcatparser.run(args.output)
    logcatparser.teardown(args.lifespan, args.percentage)
