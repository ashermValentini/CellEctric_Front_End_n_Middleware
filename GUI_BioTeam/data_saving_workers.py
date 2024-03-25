from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import pandas as pd
from datetime import datetime
import os

class DataSavingWorker(QObject):
    error = pyqtSignal(str)

    def __init__(self, aggregation_interval=5000, save_interval=10000):
        super(DataSavingWorker, self).__init__()
        self.data_aggregated = pd.DataFrame(columns=['timestamp', 'temperature', 'pressure', 'ethanol_flowrate', 'sucrose_flowrate'])

        # Flags to determine which data to save
        self.flag_save_temp = False
        self.flag_save_pressure = False
        self.flag_save_ethanol_flowrate = False
        self.flag_save_sucrose_flowrate = False
        self.flag_start_saving_live_data = False

        # Setting up the timer for periodic data aggregation
        self.aggregation_timer = QTimer(self)
        self.aggregation_timer.timeout.connect(self.aggregate_data)
        self.aggregation_timer.start(aggregation_interval)

    def update_temp_data(self, temp_data):
        self.current_temp = temp_data

    def update_pressure_data(self, pressure_data):
        self.current_pressure = pressure_data

    def update_ethanol_flowrate_data(self, flowrate_data):
        self.current_ethanol_flowrate = flowrate_data

    def update_sucrose_flowrate_data(self, flowrate_data):
        self.current_sucrose_flowrate = flowrate_data

    def aggregate_data(self):
        """Aggregates the current data into the DataFrame."""
        if self.flag_start_saving_live_data:
            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'temperature': self.current_temp if self.flag_save_temp else None,
                'pressure': self.current_pressure if self.flag_save_pressure else None,
                'ethanol_flowrate': self.current_ethanol_flowrate if self.flag_save_ethanol_flowrate else None,
                'sucrose_flowrate': self.current_sucrose_flowrate if self.flag_save_sucrose_flowrate else None,
            }])
            self.data_aggregated = pd.concat([self.data_aggregated, new_row], ignore_index=True)

    def save_non_pg_data_to_csv(self):
        """Saves the aggregated data to a CSV file."""
        file_path = r"C:\Users\BSG2_UI\OneDrive\Desktop\BSG2_System_Data\my_data.csv"  # Corrected file path
        try:
            # Check if the file exists to determine whether to write the header
            header = not os.path.exists(file_path)
            self.data_aggregated.to_csv(file_path, mode='a', header=header, index=False)
            self.data_aggregated.drop(self.data_aggregated.index, inplace=True)  # Clear the DataFrame after saving
        except Exception as e:
            self.error.emit(f"Failed to save data to CSV: {str(e)}")

    def save_header_info_to_csv(self, header_values):
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
        file_path = r"C:\Users\BSG2_UI\OneDrive\Desktop\BSG2_System_Data\header_info.csv"

        # Save the DataFrame to CSV
        try:
            df_header.to_csv(file_path, index=False)
            print("Header info saved successfully.")
        except Exception as e:
            print(f"Failed to save header info to CSV: {str(e)}")


    # Methods to set flags based on GUI interactions or other logic
    def set_save_temp(self, value):
        self.flag_save_temp = value

    def set_save_pressure(self, value):
        self.flag_save_pressure = value

    def set_save_ethanol_flowrate(self, value):
        self.flag_save_ethanol_flowrate = value

    def set_save_sucrose_flowrate(self, value):
        self.flag_save_sucrose_flowrate = value

    def start_saving_live_non_pg_data(self, value):
        self.flag_start_saving_live_data = value
