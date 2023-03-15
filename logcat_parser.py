#!/usr/bin/env python3
import argparse
from datetime import datetime

def cmd_line():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-f", "--file", help="Input logcat file", required=True)
    parser.add_argument("-o", "--output", help="Output yaml file", required=False, default="output.yaml")
    args = parser.parse_args()
    return args


class LogcatParser():
    
    def __init__(self) -> None:
        self.apps = []
        self.matching_lines_start = []
        self.matching_lines_stop = []
        self.applications = {}


    def setup(self, input_file):
        with open(input_file) as f:
            lines = f.readlines()
        for line in lines:
            if "ActivityTaskManager: START u0" in line:
                start_index = line.find("cmp=") + len("cmp=")
                end_index = line.find(" ", start_index)
                app = line[start_index:end_index]
                self.apps.append(app)
                self.matching_lines_start.append(line)
            if "Layer: Destroyed ActivityRecord" in line:
                self.matching_lines_stop.append(line)
        if self.apps != []:
            return True

    def run(self):
        self.applications = {}

        format = "%H:%M:%S.%f"

        for app in self.apps:
            self.applications[app] = {"start_times": [], "stop_times": []}

            for start_line in self.matching_lines_start:
                if app in start_line:
                    app_start = start_line.split(" ")[1]
                    self.applications[app]["start_times"].append(app_start) 

            for stop_line in self.matching_lines_stop:
                if app.split("/")[0] in stop_line:
                    app_stop = stop_line.split(" ")[1]
                    self.applications[app]["stop_times"].append(app_stop)

            for i in range(len(self.applications[app]["start_times"])):
                stop_time = self.applications[app]["stop_times"][i]
                start_time =self.applications[app]["start_times"][i]
                t1 = datetime.strptime(start_time, format)
                t2 = datetime.strptime(stop_time, format)
                result = t2 - t1
                self.applications[app]["lifespan"] = result.total_seconds()

        return self.applications


    def teardown(self):
        pass

if __name__ == "__main__":
    args = cmd_line()
    logcatparser = LogcatParser()
    logcatparser.setup(args.file)
    logcatparser.run()
    logcatparser.teardown()
