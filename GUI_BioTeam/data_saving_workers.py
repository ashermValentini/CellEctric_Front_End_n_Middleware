from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QMutex, QThread, pyqtSlot

import time
import pandas as pd
from datetime import datetime  # This allows you to use datetime.now()
import os
import csv


class DataSavingWorker(QObject):
    error = pyqtSignal(str)
    folderExistsSignal = pyqtSignal()

    def __init__(self, aggregation_interval=250):
        super(DataSavingWorker, self).__init__()
        self.data_aggregated = pd.DataFrame(columns=['timestamp', 'temperature', 'pressure', 'ethanol_flowrate', 'sucrose_flowrate'])

        # Flags to determine which data to save
        self.flag_save_temp = False
        self.flag_save_pressure = False
        self.flag_save_ethanol_flowrate = False
        self.flag_save_sucrose_flowrate = False
        self.flag_start_saving_live_data = False

        # Flag to determine where to direct the flow rate value to(ethanol or sucrose)
        self.flag_ethanol_is_running = False 
        self.flag_sucrose_is_running = False

        self.interval = aggregation_interval

        # Setting up the timer for periodic data aggregation
        self.aggregation_timer = QTimer(self)
        self.aggregation_timer.timeout.connect(self.aggregate_data)
        self.aggregation_timer.start(aggregation_interval)

    # region: Methods that update update data to current values
    def update_temp_data(self, temp_data):
        self.current_temp = temp_data

    def update_pressure_data(self, pressure_data):
        self.current_pressure = pressure_data

    def update_ethanol_flowrate_data(self, flowrate_data):
        if(self.flag_ethanol_is_running):
            self.current_ethanol_flowrate = flowrate_data
        else: 
            self.current_ethanol_flowrate = 0

    def update_sucrose_flowrate_data(self, flowrate_data):
        if(self.flag_sucrose_is_running):
            self.current_sucrose_flowrate = flowrate_data
        else: 
            self.current_sucrose_flowrate = 0
    # endregion
    # region: Methods that process and save data
    def aggregate_data(self):
        """Aggregates the current data into the DataFrame."""
        if self.flag_start_saving_live_data:
            current_time = datetime.now()
            new_row = pd.DataFrame([{
                'timestamp': f"TS: {current_time.strftime("%Y-%m-%d %H:%M:%S")}",
                'temperature': self.current_temp if self.flag_save_temp else None,
                'pressure': self.current_pressure if self.flag_save_pressure else None,
                'ethanol_flowrate': self.current_ethanol_flowrate if self.flag_save_ethanol_flowrate else None,
                'sucrose_flowrate': self.current_sucrose_flowrate if self.flag_save_sucrose_flowrate else None,
            }])
            self.data_aggregated = pd.concat([self.data_aggregated, new_row], ignore_index=True)

    def create_live_data_folder(self, folder_name):
        """
        Creates a data folder at a predefined base path and an empty 'activity_log.csv' file within that folder.

        :param folder_name: The name of the folder where the file will be created.
        :returns: True if the folder and file were successfully created, False otherwise.
        """
        # Hard-coded base path where the folder will be created
        base_path = "C:/"
        
        # Construct the full path to the folder
        folder_path = os.path.join(base_path, folder_name)
        
        # Check if the folder already exists
        if os.path.exists(folder_path):
            print(f"Folder '{folder_path}' already exists.")
            return False
        
        try:
            # Create the folder if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)
            print(f"Folder '{folder_path}' created successfully.")
            
            # Construct the full path to the CSV file and create it with headers
            file_path = os.path.join(folder_path, "activity_log.csv")
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Command"])  # Define headers for the CSV
            print(f"Activity log CSV file created at: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to create folder or CSV file: {str(e)}")
            return False
    
    def save_non_pg_data_to_csv(self, folder_name):
        """Saves the aggregated data to a CSV file."""
        # Use string formatting to insert the folder name
        file_path = r"C:\{}\sys_data.csv".format(folder_name)
        try:
            # Check if the file exists to determine whether to write the header
            header = not os.path.exists(file_path)
            self.data_aggregated.to_csv(file_path, mode='a', header=header, index=False)
            self.data_aggregated.drop(self.data_aggregated.index, inplace=True)  # Clear the DataFrame after saving
        except Exception as e:
            self.error.emit(f"Failed to save data to CSV: {str(e)}")

    def save_header_info_to_csv(self, header_values, folder_name):
        """
        Saves header information to a CSV file.

        :param header_values: Dictionary containing the values from line edits.
        """
        # Default values if line edits are empty
        default_values = {
            "Name": "NA",
            "Email": "NA",
            "Purpose": "NA",
            "ID": "NA",
            "Strain Name": "NA",
            "Fresh Sucrose": "NA"
        }

        # Update default values with actual values if provided
        for key in default_values.keys():
            if key in header_values and header_values[key].strip() != "":
                default_values[key] = header_values[key].strip()

        # Create DataFrame from the updated values
        df_header = pd.DataFrame(data=default_values, index=[0])

        # Define the file path (consider making this a parameter or a class attribute)
        # Use string formatting to insert the folder name
        file_path = r"C:\{}\header_info.csv".format(folder_name)

        # Save the DataFrame to CSV
        try:
            df_header.to_csv(file_path, index=False)
            print("Header info saved successfully.")
        except Exception as e:
            print(f"Failed to save header info to CSV: {str(e)}")

    def save_activity_log(self, command, folder_name):
        """
        Appends a command and the current timestamp to the CSV log file.

        :param command: The command string to log.
        :param folder_name: The folder name where the log file resides.
        """
        command = command.strip()
        # Hard-coded base path where the folder was created
        base_path = "C:/"
        
        # Construct the full path to the log file
        log_file_path = os.path.join(base_path, folder_name, "activity_log.csv")

        # Get the current timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Open the log file and append the new row
        with open(log_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, command])

        print(f"Logged command: {command}")

    def save_pg_data_to_csv(self, pg_data, VP, VN, T, pulse_number, PL, RP, folder_name):
        # Construct the file name based on the current date and time
        current_time = datetime.now()
        filename = current_time.strftime("%Y%m%d_%H%M%S") + "_experiment_data.csv"

        # Define the directory where the file will be saved
        #save_directory = r"C:\Users\BSG2_UI\OneDrive\Desktop\Experiments"  # Use raw string for Windows paths
        save_directory = r"C:\{}".format(folder_name)

        full_path = os.path.join(save_directory, filename)
        
        # Create a DataFrame for the header information
        header_info = [
                f"Date: {current_time.strftime("%Y-%m-%d %H:%M:%S")}",
                f"#Pulse Number: {pulse_number}",
                f"#Voltage Pos: {VP}",
                f"#Voltage Neg: {VN}",
                f"#Temperature: {T}",
                f"#Pulse Length: {PL}",
                "#Transistor on time: 75",
                f"#Rate: {RP}"
            ]
        

        # Calculate the pulse number (assuming the method is called every 10 seconds)
        pulse_number = pulse_number + 1

        header_df = pd.DataFrame({'Column1': header_info,'Column2': ['']*len(header_info)})

        # Create a DataFrame for the data
        voltage_data_df = pd.DataFrame({'Column1': pg_data[:, 0]})
        current_data_df = pd.DataFrame({'Column2': pg_data[:, 1] })

        combined_pg_data_df = pd.concat([voltage_data_df, current_data_df], axis=1)
        combined_output_df = pd.concat([header_df, combined_pg_data_df], ignore_index=True)

        # Save to CSV
        combined_output_df.to_csv(full_path, index=False, header=False)
        print(f"Saving experiment data to {filename}...")
    
    # endregion
    # region: Methods to set flags based on GUI interactions or other logic
    def set_save_temp(self, value):
        self.flag_save_temp = value

    def set_save_pressure(self, value):
        self.flag_save_pressure = value

    def set_save_ethanol_flowrate(self, value):
        self.flag_save_ethanol_flowrate = value

    def set_save_sucrose_flowrate(self, value):
        self.flag_save_sucrose_flowrate = value

    def set_sucrose_is_running(self, value):
        self.flag_sucrose_is_running = value

    def set_ethanol_is_running(self, value):
        self.flag_ethanol_is_running = value

    def start_saving_live_non_pg_data(self, value):
        self.flag_start_saving_live_data = value
    #endregion
    # region: Close event 
    def _stop_timer(self):
        if self.aggregation_timer.isActive():
            self.aggregation_timer.stop()
            print('timer stopped in instance method')
    #endregion