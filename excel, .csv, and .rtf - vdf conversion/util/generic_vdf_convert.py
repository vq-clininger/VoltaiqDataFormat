""" Generic methods for converting custom files to VDF format"""

import pandas as pd
import numpy as np
import csv
import os
from dateutil import parser
import datetime
import re
import yaml
from pathlib import Path
from os import path
import logging
import collections

LOG = logging.getLogger(__name__)

volta_units_df = pd.read_csv("util/units.csv", sep=";", skipinitialspace=True) # Need better way to get up-to-date unit - especially for users outside of company.

### Util functions
def verify_vdf_time_data(time_data):
    """
    Verify that time data is in acceptable vdf format
    Print summary.
    """
    # Check that required columns exist
    if "Test Time" not in time_data.columns:
        print(f"Verification Warning: data is missing required column 'Test Time'")
    if "Current" not in time_data.columns:
        print(f"Verification Warning: data is missing required column 'Current'")
    if "Voltage" not in time_data.columns and "Potential" not in time_data.columns:
        print(f"Verification Warning: data is missing required column 'Voltage'/'Potential'")
    # Check that unit row exists, and units are all acceptable
    volta_units = volta_units_df["Key"].to_list()
    custom_units_dict = time_data.iloc[0].to_dict()
    for k, v in custom_units_dict.items():
        if v not in volta_units and v is not None and v is not np.nan:
            print(f"Verification Warning: Unit '{v}' for column '{k}' is not valid.")
    # Check for duplicate column names (lower case name + unit)
    column_keys = [f"{k.lower()}_{v}" for k, v in custom_units_dict.items()]
    duplicate_keys = [item for item, count in collections.Counter(column_keys).items() if count > 1]
    for (
        key
    ) in duplicate_keys:  # ...Note might not catch everything, since importer can change units
        print(
            f"Verification Warning: Found duplicate column key {key} - make sure column names are unique."
        )
    # Check that required/optional columns are in required format
    if not time_data[1:]["Test Time"].drop_duplicates().is_monotonic_increasing:
        print(f"Verification Warning: Test Time is not in ascending order. Check that it is not getting reset during the test.")
    if "Cycle Number" in time_data.columns and not time_data[1:]["Cycle Number"].drop_duplicates().is_monotonic_increasing:
        print(f"Verification Warning: Cycle Number is not in ascending order.")

def verify_vdf_metadata(header_dict):
    """
    Verify that metadata dict has acceptable vdf values

    Returns True/False, msgs - or just summary?
    """
    # Check that required metadata is present and in required format.
    # Start Time. exists and right format
    if not header_dict.get("Start Time"):
        print(f"Verification Warning: metadata is missing required value 'Start Time'")
    # Timezone. exists and right format (recongized by tzinfo)
    if not header_dict.get("Timezone"):
        print(f"Verification Warning: metadata is missing required value 'Timezone'")

def get_unit_key(unit):
    volta_units = volta_units_df["Key"].to_list()
    unit_symbol_to_key_dict = volta_units_df.set_index("Symbol")["Key"].to_dict()
    unit_name_to_key_dict = {k.lower(): v for k, v in volta_units_df.set_index("Name")["Key"].to_dict().items()}
    if unit in volta_units:
        return unit, None
    elif unit in unit_symbol_to_key_dict.keys():
        return unit_symbol_to_key_dict[unit], None
    elif unit.lower() in unit_name_to_key_dict.keys():
        return unit_name_to_key_dict[unit.lower()], None
    else:
        return '', f"Could not convert unit {unit}"

    
class GenericVDFConverter:
    """
    Desired flow:
    - Run()
        -> convert()
        -> verify()
    - convert()
        -> header_dict, dp_data = get_data()
        -> write_to_csv(dp_data, header_dict)
    - verify()
        -> verify_time_data(dp_data)
        -> verify_metadata(header_dict)
    """

    def __init__(self, filepath, config_path):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        # sometimes custom output file name logic?
        self.time_df = None  # empty dataframe instead?
        self.formatted_df = None  # Formatted df, no units.
        self.final_df = None  # formatted df with added units.
        # self.metadata_df = None # Attribute for metadata tab if applies.
        self.config = {}  # parse_config to create this
        self.rename_map = {}  # parse_config to create this
        self.new_col_map = {}  # parse_config to create this
        self.create_col_map = {} # parse config to create this
        self.unit_map = {}  # parse config to create this
        self.skip_columns = [] # parse config to create this
        self.parse_config(config_path)
        self.time_format = self.config.get("time format")
        self.header_dict = self.config.get("metadata", {})
        self.epoch_unit = self.config.get("epoch unit", 'ms')

    def convert(self):
        header_dict, dp_data = self.get_data()
        self.verify_vdf(dp_data, header_dict)
        self.write_to_csv(dp_data, header_dict)

    def parse_config(self, config_path):
        # Read in config file
        with open(config_path) as config_file:
            self.config = yaml.safe_load(config_file)
        # Create column & unit mappings
        if self.config.get("columns"):
            for k, v in self.config["columns"].items():
                unit = v.get("unit")
                rename = v.get("rename")
                new_name = v.get("new_name")
                skip_columns = v.get("skip")
                if unit:
                    self.unit_map[k] = unit
                if rename:
                    self.rename_map[k] = rename
                    if unit:
                        self.unit_map[rename] = unit
                if new_name:
                    self.new_col_map[k] = new_name
                    if unit:
                        self.unit_map[new_name] = unit
                if skip_columns:
                    self.skip_columns.append(k)
                    
        # Create new columns (& unit mappings)
        if self.config.get("create_columns"):
            for name, v in self.config["create_columns"].items():
                #value = v.get("value")
                unit = v.get("unit")
                if "value" in v.keys():
                    self.create_col_map[name] = v.get("value")
                    if unit:
                        self.unit_map[name] = unit
                else:
                    print(f"Warning: Will not create column {name}, no value was given.")

    def get_data(self):
        """
        Read custom data from file path, format and return header data and timeseries data.

        Parameters
        ----------
        file_path: str
            file path for custom data file.

        Returns
        -------
        header_dict: dict
            Dictionary of header key/values to write to vdf format.
        hist_data_df: pd.Dataframe
            Dataframe of timeseries data from custom file.
        """
        # Read data into a DataFrame
        #   - Could be one sheet or multiple sheets
        #   - how to handle when a sheet has metadata info?
        print("Reading in data...")
        self.time_df = self.read_data()

        # Format Data (time_df)
        print("Formatting data...")
        self.formatted_df = self.format_data(self.time_df)

        # Create header dict.
        print("Updating header dictionary...")
        self.update_header_dict()

        # Add Units
        print("Adding units...")
        self.parse_units_from_name(self.formatted_df.columns)
        self.final_df = self.add_units(self.formatted_df)

        return self.header_dict, self.final_df

    def read_data(self):
        """
        Read in custom data from file path and return dataframe.

        For now supports:
        - .csv, .xls, and .xlsx extensions
        - Supports skipping rows if skipwors is specified in the config.
        - Support files with multiple tabs if time_data_tab is specified in the config.

        Parameters
        ----------
        file_path: str
            file path for custom data file.

        Returns
        -------
        hist_data_df: pd.Dataframe
            Dataframe of unformatted timeseries data from custom file.
        """
        file_type = os.path.splitext(self.filename)[-1]
        if file_type.lower() in [".csv", ".rtf"]:
            data = pd.read_csv(self.filepath, skiprows = self.config.get("skiprows"))
        elif file_type.lower() == ".xls" or file_type.lower() == ".xlsx":
            data = pd.read_excel(self.filepath, self.config.get("time_data_tab"), skiprows = self.config.get("skiprows"))
        else:
            raise Exception(
                f"Could not read in file: unrecognized file format {file_type}"
            )  # update
        # Need check that data is dataframe, not dict...
        if isinstance(data, pd.DataFrame):
            if self.skip_columns:
                data = data.drop(columns = self.skip_columns)
            return data
        else:
            raise Exception("File is not a dataframe - could have multiple tabs.")

    def format_data(self, time_df):
        """Return formatted time_df"""
        temp_df = time_df.copy()
        # Add columns
        for k, v in self.new_col_map.items():
            # if col not in file, warning. #DO I WANT DEBUG MODE? don't always want these warnings.
            if k in temp_df.columns:
                temp_df[v] = temp_df[k]
            else:
                print(f"Warning: Did not create new column from {k}, did not exist.")
                LOG.warning(f"Did not create new column from {k}, did not exist.")
        # Rename columns.
        temp_df.rename(columns=self.rename_map, inplace=True)
        # Warning for columns that don't exist. Better way to do this?
        # for k, v in self.rename_map.items():
        #     if k not in temp_df.columns:
        #         print(f"Did not rename column {k} to {v}, {k} does not exist.")
                # LOG.warning(f"Did not rename column {k} to {v}, {k} does not exist.")
            
        # Drop columns that are all NaN (ignore time columns)
        # This means that if the time column has a value but non of the other columns do, drop it.
        non_time_columns = [col for col in temp_df.columns if col not in ["Test Time", "Timestamp"]]
        temp_df.dropna(subset=non_time_columns, how='all', inplace=True)
        
        # Create new columns.
        for name, value in self.create_col_map.items():
            try:
                temp_df[name] = value
            except Exception as e:
                print(f"Warning: Could not create column {name} with value {value}. Reason: {e}")

        # If timestamp column, check and convert to accepted format
        # Use function instead so can override? Maybe somrtimes want to get timestamp differently.
        if "Timestamp" in temp_df.columns:
            temp_df["Timestamp"] = temp_df["Timestamp"].apply(self.timestamp_to_datetime)

        # Create Test Time column from Timestamp if doesn't exist.
        # Use function instead so can override? Maybe somrtimes want to get test time differently.
        if "Test Time" not in temp_df.columns:
            if "Timestamp" in temp_df.columns:
                temp_df = self.create_test_time_from_timestamp(
                    temp_df
                )  # is it necessary to assign, or will it modify df throughout?
            else:
                print(
                    "Could not create a Test Time column - no Timestamp column could be found"
                )  # Just log warning, because could still get added in other_formatting.

        # Other formatting
        temp_df = self.other_formatting(temp_df)

        return temp_df

    def get_units(self, df, unit_map):
        units = []
        for col in df.columns:
            if col in unit_map.keys():
                units.append(unit_map[col])
            else:
                units.append(None)
        return units

    def parse_units_from_name(self, columns):
        msgs = []
        regex = ".*\((?P<unit>.+)\)$"
        for col in [x for x in columns if x not in self.unit_map.keys()]:
            match = re.match(regex, col)
            if match:
                unit, msg = get_unit_key(match.group("unit"))
                if unit:
                    self.unit_map[col] = unit
                if msg:
                    msgs.append(msg)
        for msg in set(msgs):
            print(msg)

    def other_formatting(self, temp_df):
        return temp_df

    def update_header_dict(self):
        if not self.header_dict.get("Start Time"):
            self.header_dict["Start Time"] = self.get_start_time()
        if not self.header_dict.get("Timezone"):
            print("Timezone was not defined: defaulted to PST")
            self.header_dict["Timezone"] = "America/Los_Angeles"

    def timestamp_to_datetime(self, timestamp):  # pass in epoch_unit and time_format as args?
        # Other Note: Doing these "if" checks for every row. Better performance to determine what to use before calling function?
        # How to avoid all these indented try-except blocks?
        # Note: if already a timestamp, will throw the last log "Could not convert", since parser does not convert timestamp to timestamp (throws exception)
        if self.time_format:
            try:
                return datetime.datetime.strptime(timestamp, self.time_format)
            except:
                print(
                    f"Could not convert timestamp {timestamp} using the provided time_format {self.time_format} - time format not used"
                )
        try:
            return parser.parse(timestamp)
        except:
            # try epoch
            try:
                return pd.to_datetime(
                    str(timestamp), unit=self.epoch_unit
                )  # Need to define logic to get proper epoch unit.
            except:
                print(f"Could not convert timestamp {timestamp}, keeping original value")
                return timestamp

    def create_test_time_from_timestamp(self, df):
        # Call if Test Time does not exist. If neither timestamp or test time exist, error.
        # Assuming Timestamp is datetime object.
        # Suggestion: Try changing "apply" with "map" - should be faster.
        try:
            df["Test Time"] = (df["Timestamp"] - df["Timestamp"].iloc[0]).apply(
                lambda x: x.total_seconds()
            )
            self.unit_map["Test Time"] = "second"
        except:
            print("Could not create Test Time column from Timestamp.")
        return df

    def get_start_time(self):
        # Get from timestamp if exists, else from current time.
        if "Timestamp" in self.formatted_df.columns:
            return self.formatted_df["Timestamp"].iloc[0]
        else:
            print("Could not obtain a start time for the test: defaulted to 0 ms (epoch)")
            return 0

    def add_units(self, df):
        temp_df = df.copy()
        temp_df.loc[-1] = self.get_units(temp_df, self.unit_map)
        return temp_df.sort_index()

    def write_to_csv(self, time_series_data: pd.DataFrame, header_data: dict):
        """Write csv to the given output path.

        Parameters
        ----------
        time_series_data: Pandas Dataframe
            Dataframe of the time series data from excel file
        """
        output_file_name = self.get_output_file_name()
        output_dir = self.get_output_dir()
        output_file = output_dir + "/" + output_file_name

        # Create dir if it doesn't exist
        if not path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, mode="w") as test_file:
            test_writer = csv.writer(test_file, delimiter="\t")
            # pylint: disable=expression-not-assigned
            for k, v in header_data.items():
                test_writer.writerow([f"{k}:{v}"])
            test_writer.writerow(["[DATA START]"])
        time_series_data.to_csv(output_file, mode="a", sep="\t", index=False)

        print(f"Completed generation of VDF file at path: {output_file}")
        LOG.info(f"Completed generation of VDF file at path: {output_file}")

    def get_output_file_name(self):
        """ Function to return output file name"""
        return os.path.splitext(self.filename)[0] + "_VDF.csv"

    def get_output_dir(self):
        """ Function to return output directory"""
        return os.path.join(os.path.dirname(self.filepath), "VDF")

    def verify_vdf(self, time_data, header_dict):
        # verify dp data and verify header_dict
        verify_vdf_time_data(time_data)
        verify_vdf_metadata(header_dict)
