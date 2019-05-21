#!/usr/bin/env python


'''
Adapted from https://github.com/matthewgadd/RobotCarDataset-Scraper
'''

'''
Gets a list of available datasets from the Oxford Robotcar Dataset website.

Matt Gadd
Mar 2019
Oxford Robotics Institute, Oxford University.

'''

import requests
import re

from scrape_mrgdatashare import datasets_url
import argparse
from pathlib import Path


available_sensor_types = [
    'tags',
    'stereo_centre',
    'stereo_left',
    'stereo_right',
    'vo',
    'mono_left',
    'mono_right',
    'mono_rear',
    'lms_front',
    'lms_rear',
    'ldmrs',
    'gps'
]

def absolute_sensor_type(sensor_type):
    # if sensor_type is like stereo_centre_01
    if sensor_type[-2:].isdigit():
        return sensor_type[:-3] # stereo_centre

    return sensor_type

def main(asked_sensors, selected_sequences):
    # open session
    session_requests = requests.session()

    # get http response from website
    result = session_requests.get(datasets_url)
    text = result.text

    # parse response text
    text_locations = [text_location.end()
                      for text_location in re.finditer(datasets_url, text)]
    datasets = [str(text[text_location:text_location + 19])
                for text_location in text_locations]

    # ignore metadata and sort unique datasets
    datasets = datasets[2:]
    datasets = sorted(list(set(datasets)))

    # write output text file
    datasets_file = "datasets.csv"
    with open(datasets_file, "w") as file_handle:
        # iterate datasets
        filtered_datasets = (dataset for dataset in datasets if dataset in selected_sequences)
        for dataset in filtered_datasets:

            # url to dataset page
            dataset_url = datasets_url + dataset
            result = session_requests.get(dataset_url)
            text = result.text

            # parse text for sensor type
            start = [
                text_location.end() for text_location in re.finditer(
                    "download/\?filename=datasets", text)]
            sensor_types = []
            for s in start:
                ss = s
                while text[ss + 40:ss + 44] != ".tar":
                    ss += 1
                sensor_type = text[s + 41:ss + 40]
                if absolute_sensor_type(sensor_type) in asked_sensors:
                    sensor_types.append(str(sensor_type))

            # write dataset entry
            file_handle.write(dataset + "," + ",".join(sensor_types) + "\n")



if __name__ == "__main__":
    # option parsing suite
    argument_parser = argparse.ArgumentParser(
        description="get_datasets input parameters")

    # specify CL args
    argument_parser.add_argument(
        "--sensors",
        dest="asked_sensors",
        help="list of sensors types you want to download, separated by a ',' (default: all sensor types).\n"
            + "e.g: --sensors 'tags,stereo_centre'\n"
            + f"list of available sensor types: {available_sensor_types}",
        default=available_sensor_types
    )

    argument_parser.add_argument(
        "--sequences",
        dest="selected_sequences",
        help="file with the list of sequences you want to download, one sequence by line (default: all sequences).",
        default=None
    )


    # parse CL
    parse_args = argument_parser.parse_args()

    asked_sensors = parse_args.asked_sensors
    asked_sensors.replace(" ", "")
    asked_sensors = set(asked_sensors.split(','))
    assert asked_sensors.issubset(set(available_sensor_types)), asked_sensors - set(available_sensor_types)

    selected_sequences_file = parse_args.selected_sequences
    selected_sequences_file = Path(selected_sequences_file).expanduser().read_text()
    selected_sequences = selected_sequences_file.splitlines()

    main(asked_sensors, selected_sequences)
