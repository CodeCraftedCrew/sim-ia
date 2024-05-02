import glob
import os
import pandas as pd

from events.event import EventType


def analyze_logs(logs_path, specific=False):

    if not specific:
        log_files = glob.glob(os.path.join(logs_path, "*.log"))

        latest_log = max(log_files, key=os.path.getmtime)

        with open(latest_log, 'r') as f:
            content = f.read()

    else:
        with open(logs_path, 'r') as f:
            content = f.read()

    data = []

    for log in content:
        elements = log.split(':')

        data.append({"time": float(elements[2]), "event_type": EventType[elements[3].split(".")[-1]],
                     "agent_id": elements[4], "driver_id": elements[5]})

    last_event_per_agent = {}
    walking = 0
    waiting_times = []
    passengers_per_driver = {}
    impossible_plans = 0

    for event in data:

        if event["driver_id"] == "undefined":
            continue

        if event["agent_id"] not in last_event_per_agent:
            last_event_per_agent[event["agent_id"]] = (event["time"], event["event_type"])

        else:

            if event["event_type"] == EventType.IMPOSSIBLE_PLAN:
                impossible_plans += 1
                if event["agent_id"] in passengers_per_driver:
                    last_event_per_agent.pop(event["agent_id"])

            last_time, last_event = last_event_per_agent[event["agent_id"]]

            if last_event == EventType.DEPARTURE:

                if event["event_type"] == EventType.AT_GOAL:
                    walking += 1
                    last_event_per_agent.pop(event["agent_id"])
                else:
                    last_event_per_agent[event["agent_id"]] = (event["time"], event["event_type"])

                continue

            if last_event == EventType.AT_STOP:

                if event["event_type"] == EventType.AT_STOP:
                    continue

                if event["event_type"] == EventType.BOARD_VEHICLE:
                    waiting_times.append((event["time"] - last_time, event["agent_id"]))
                    last_event_per_agent.pop(event["agent_id"])


