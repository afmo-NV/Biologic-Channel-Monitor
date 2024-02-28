import os
import channel_monitor_functions as cmf
import yaml
import datetime
import pandas as pd
from bar_plot import create_plot_channel_availability, save_figure
from excel_report import create_excel_report, save_excel_report
from logger_configurator import configure_logging
import logging

# Path to the directory where the script is located
base_directory = os.path.dirname(os.path.abspath(__file__))

# Configure logging
configure_logging(base_directory)
logging.debug("MAIN. BioLogic Channel Monitor started")

# Get the export folder from directory_config.yaml
try:
    logging.debug("MAIN. Getting export folder from directory_config.yaml")
    with open(os.path.join(base_directory, 'cml_directory_config.yaml')) as file:
        doc = yaml.load(file, Loader=yaml.FullLoader)
    mpr_folder = doc['path_cml_folder']
    # logging.debug(f"MAIN. Export folder is {export_folder}")
except Exception as e:
    logging.error(f"MAIN. An error occurred while getting export folder: {e}")
    raise

# Create an instance of the ChannelMonitorFunctions class
monitor = cmf.ChannelMonitorFunctions()

# Find all files with .mpr extension in the directory and subdirectories
mpr_files = monitor.find_mpr_files(mpr_folder)

# Filter the mpr_files list to files that were created 3 days ago or earlier
active_files_list = monitor.check_file_activity(mpr_files)

# Extract the technique from the active files
techniques_list = monitor.extract_technique(active_files_list)

# Extract the channel number from the active files
channels_active = monitor.extract_channel_number(active_files_list)

# Create a dictionary with the duration of the cycling protocols
with open('cycling protocols_duration.yaml', 'r') as file:
    time_mapping = yaml.safe_load(file)

# Create a list with the duration of the cycling protocols
experimental_time = [time_mapping.get(val, 0) for val in techniques_list]

# Create a list with the creation time of the active files
all_channels_list = [letter + str(number) for letter in ['A', 'B', 'C', 'D', 'E', 'F'] for
                     number in range(1, 9)]

# Create a list with the empty channels
empty_channels_list = [item for item in all_channels_list if item not in channels_active]

# Create a list with the creation time of the active files
creation_time_list = [monitor.get_birth_time(file_path) for file_path in active_files_list]

# Create a list with the estimated finish times
estimated_finish_times = [creation_time + datetime.timedelta(seconds=time) for creation_time, time in
                          zip(creation_time_list, experimental_time)]

# If there are empty channels, add 'Now' to the estimated_finish_times list
estimated_finish_times.extend(['Now' for i in range(len(empty_channels_list))])

# Create a dictionary with the data
data = {'Channel': channels_active + empty_channels_list,
        'Status': ['Active' for i in range(len(channels_active))] + ['Empty' for i in range(len(empty_channels_list))],
        'Next estimated free slot': estimated_finish_times}

# Create a dataframe with the previous dictionary
df = pd.DataFrame(data)

# Sort the dataframe by 'Channel' alphabetically
df = df.sort_values(by='Channel')

###################################################################################################################
# Create an Excel report from the dataframe #######################################################################
###################################################################################################################

# Date of the report
current_date = datetime.date.today()

# Filename of the report
filename = f'Channel_Monitor_BCS_3_{current_date}.xlsx'

# Create a directory to save the report
channel_monitor_dir = os.path.join(base_directory, 'Channel_Monitor_Report')

# Create the directory if it does not exist
if not os.path.exists(channel_monitor_dir):
    os.makedirs(channel_monitor_dir)

# Create the full path to the report
channel_report = os.path.join(channel_monitor_dir, filename)

# Create an Excel report from the dataframe
wb = create_excel_report(df)

# Save the report to a file
save_excel_report(wb, channel_report)

##############################################################################################################
# Create a bar plot of channel availability per day and availability category ################################
##############################################################################################################
# Replace "Now" with current datetime
now_datetime = pd.Timestamp.now()

# Replace "Now" with current datetime
df['Next estimated free slot'] = df['Next estimated free slot'].replace('Now', now_datetime)

# Extract year, month, day, and hour
df['Year'] = df['Next estimated free slot'].dt.year
df['Month'] = df['Next estimated free slot'].dt.month
df['Day'] = df['Next estimated free slot'].dt.day
df['Hour'] = df['Next estimated free slot'].dt.hour

# Categorize availability with a function from the monitor object with a loop
availability_list = []
for hour in df['Hour']:
    availability = monitor.categorize_availability(hour)
    availability_list.append(availability)

# Add the availability list to the dataframe
df['Availability'] = availability_list

# Sort dataframe by hour
df = df.sort_values(by='Hour')

# Create a bar plot of channel availability per day and availability category
bar_plot = create_plot_channel_availability(df)

# Save the figure to a file in the report directory
plot_filename = f'Channel_Monitor_BCS_3_{current_date}.png'
plot_path = os.path.join(channel_monitor_dir, plot_filename)
save_figure(bar_plot, plot_path)

# Log the end of the script
logging.debug(f'MAIN. BioLogic Channel Monitor finished at {datetime.datetime.now()}')