import os
import re
import time
import datetime
from pathlib import Path
import logging


class ChannelMonitorFunctions:
    def __init__(self):
        pass

    def find_mpr_files(self, directory):
        """
        Find all files with .mpr extension in the directory and subdirectories.
        :param directory: Path to the directory where the .mpr files are located
        :return: mpr_files list
        """
        try:
            logging.debug(f"Finding .mpr files in {directory}")
            mpr_files = []
            for root, dirs, files in os.walk(directory):
                for name in files:
                    if name.endswith(".mpr"):
                        mpr_files.append(Path(root) / name)
            logging.debug(f"Found {len(mpr_files)} .mpr files")
            return mpr_files
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return None

    def filter_recent_files(self, paths, days_threshold=360):
        """
        Filter the mpr_files list to files that were created 3 days ago or earlier
        :param paths: List of Path objects representing .mpr files found in the directory and subdirectories.
        :param days_threshold: Number of days to consider a file as recent
        :return: filtered_files list
        """
        logging.debug(f"Filtering files created {days_threshold} days ago or earlier")
        filtered_files = []
        current_time = time.time()
        threshold_time = current_time - (days_threshold * 24 * 60 * 60)

        for file_path in paths:
            if os.path.isfile(file_path):
                creation_time = os.path.getctime(file_path)  # I have to modify this
                if creation_time > threshold_time:
                    filtered_files.append(file_path)
        logging.debug(f"Found {len(filtered_files)} files created {days_threshold} days ago or earlier")
        return filtered_files

    def check_file_activity(self, paths):
        """
        Check the activity of the mpr files
        :param paths: Paths to the .mpr files
        :return: active_files list
        """
        logging.debug("Checking file activity")
        recent_files = self.filter_recent_files(paths)
        active_files = []
        total_files = len(recent_files)
        files_checked = 0

        for file_path in recent_files:
            filename = os.path.basename(file_path)
            frequency = self.get_file_modification_frequency(file_path)
            files_checked += 1
            progress_percentage = (files_checked / total_files) * 100
            print(f"Files analyzed = {progress_percentage} %")
            if frequency > 0:
                print(f"File '{filename}' is active.")
                # Perform other operations on active file
                active_files.append(file_path)
            else:
                print(f"File '{filename}' is not active. Skipping...")
        logging.debug(f"Found {len(active_files)} active files")
        return active_files

    def get_birth_time(self, file_path):
        """
        Get the birth time (creation time) of the file
        :param file_path: path to the file
        :return: datetime object representing the creation time of the file
        """
        logging.debug(f"Getting birth time of {file_path.stem}")

        # Get the file attributes
        file_attributes = os.stat(file_path)

        # Retrieve the birth time (creation time)
        birth_time_timestamp = file_attributes.st_ctime

        # Convert the timestamp to a datetime object
        birth_time = datetime.datetime.fromtimestamp(birth_time_timestamp)

        logging.debug(f"Birth time of {file_path.stem} is {birth_time}")
        return birth_time

    def get_last_modified_time(self, file_path):
        """
        Get the last modified time of the file
        :param file_path: Path to the file
        :return: datetime object representing the last modified time of the file
        """
        logging.debug(f"Getting last modified time of {file_path.stem}")

        # Get the file attributes
        file_attributes = os.stat(file_path)

        # Retrieve the last modified time
        last_modified_time_timestamp = file_attributes.st_mtime

        # Convert the timestamp to a datetime object
        last_modified_time = datetime.datetime.fromtimestamp(last_modified_time_timestamp)

        logging.debug(f"Last modified time of {file_path.stem} is {last_modified_time}")
        return last_modified_time

    def get_file_modification_frequency(self, file_path, interval_seconds=20):
        """
        Get the frequency of file modification
        :param file_path: Path to the mpr file
        :param interval_seconds: frequency of file modification
        :return: frequency of file modification in seconds
        """
        logging.debug(f"Getting file modification frequency of {file_path.stem}")

        # Get initial modification time
        last_modification_time = os.path.getmtime(file_path)

        while True:
            # Wait for the specified interval
            time.sleep(interval_seconds)

            # Get current modification time
            current_modification_time = os.path.getmtime(file_path)

            # Calculate time difference
            time_difference_seconds = current_modification_time - last_modification_time

            # Calculate frequency
            if time_difference_seconds > 0:
                frequency = 1 / time_difference_seconds
                logging.debug(f"File modification frequency of {file_path.stem} is {frequency}")
                return frequency
            else:
                return 0  # No modifications detected during interval


    def extract_technique(self, paths):
        """
        Extract the technique type from the file name
        :param paths: path or list of paths to the .mpr files
        :return: List of technique types
        """
        try:

            logging.debug("Extracting technique from file name")
            # Define the default pattern
            technique_pattern = r'(?P<Technique>Formation-Capacity-Check|Cycle-Life|FC-DCIR-Rate|DCIR-Rate|DCIR-rate)'
            technique_list = []

            for file_path in paths:
                path_string = file_path.stem
                technique = (re.findall(technique_pattern, path_string))[0]
                technique_list.append(technique)
            logging.debug(f"Extracted {len(technique_list)} techniques")
            return technique_list
        except Exception as e:
            logging.debug(f"No technique in {e}")
            return None

    def extract_channel_number(self, paths):
        """
        Extract the channel number from the file name
        :param paths: Path or list of paths to the .mpr files
        :return: channel_number_list
        """
        try:
            logging.debug("Extracting channel number from file name")
            # Define the default pattern
            channel_pattern = r'(?P<Channel>C[A-Z]\d)'
            channel_number_list = []

            for file_path in paths:
                path_string = file_path.stem
                # Find all matches of the pattern
                channels = re.findall(channel_pattern, path_string)
                if channels:
                    # Extract the last match
                    channel = channels[-1]
                    channel_number = channel.replace('C', '', 1)
                    channel_number_list.append(channel_number)
            logging.debug(f"Extracted {len(channel_number_list)} channel numbers")
            return channel_number_list
        except Exception as e:
            logging.debug(f"No channel number in {e}")
            return None

    def categorize_availability(self, hour):
        """
        Categorize the availability of the channel according to the hour of the day it will be available
        :param hour:
        :return: string representing the availability category
        """
        if 0 <= hour <= 7:
            return 'Available by 7 am'
        if 7 < hour <= 12:
            return 'Available by 12 noon'
        elif 12 < hour <= 17:
            return 'Available by 5 pm'
        else:
            return 'Available after 5 pm'
