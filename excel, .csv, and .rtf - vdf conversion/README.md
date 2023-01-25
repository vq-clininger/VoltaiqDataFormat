# VDF Conversion Script

The **generic_vdf_convert.py** script provides methods, mainly through the GenericVDFConverter class, for converting data files to the Voltaiq Data Format (VDF).

The GenericVDFConverter class needs 2 inputs: the data file to convert, and a config .yaml file containing information on how to convert the file, such as desired column and unit mappings.

Currently Supported:
- csv files
- excel files (single and multi tab)
- .rtf files if they can be read in as a csv


## Quick Start

1. Make sure the data files you want to convert are uploaded to VAS.

2. Create the configuration file to map columns and units (See **Deep Dive** section for more details)

3. (a) Run the code below (see **example_vdf_conversion.ipynb** for an example notebook)

```python
# import the generic converter
from generic_vdf_convert import GenericVDFConverter

# Set input paths
config_path = "path_to_convert_config.yaml"
file_path = "folder/path_to_data_file.xyz"

# Instantiate the converter for that data file and convert to VDF
converter = GenericVDFConverter(file_path, config_path)
converter.convert()
```

3. (b) Running the code for all files in a folder

If you have multiple files in a folder and you want to convert all of them at once, you can do so with the following:

```python
# import the generic converter
from generic_vdf_convert import GenericVDFConverter
import os

# Set input paths
config_path = "path_to_convert_config.yaml"
folder = "path_of_data_folder/"

# Convert each file in the folder
for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    converter = GenericVDFConverter(file_path, config_path)
    converter.convert()
        
# If you want to convert only the .csv files in the folder (For example, if you also have some .txt files in their that you want to ignore) 
for filename in os.listdir(folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(folder, filename)
        converter = GenericVDFConverter(file_path, config_path)
        converter.convert()

```

4. Download the data to your computer and import it into the server of your choice through the front-end uploader.


## Deep Dive

### Configuration File

The configuration file must be a .yaml file with the following format (see *example_convert_config.yaml* for an example):

```yaml
columns:
  <column_name>: <- Should be the exact column name of the column in your file.
    new_name: <new_name> # Creates a new col. (duplicate) with <new_name> if specified.
    rename: <new_name>  # Renames col. with new_name if specified.
    unit: <unit> # Valid units can be found under the 'Key' column of util/units.csv
  <column_name>:
    new_name: <new_name>
    rename: <new_name>
    unit: <unit>
   <column_name>:
       skip: true # Optional: Will skip this column name in the data read from file_path 
create_columns:
    <column_name>: # Name of the column you want to create
        value: <value> # Value you want to give to all rows of the created column. Required.
        unit: <unit> 
metadata:
  Start Time: Optional
  Timezone: Europe/Berlin
  
time format: <- Optional: string representing time format to pass in to datetime.strptime. Doc.
epoch unit: <s> <- if timestamp epoch other than 'ms', specify unit.
time_data_tab: <sheet_name> <- Name of tab containing time data if excel file with multiple sheets.
skiprows: <Number of rows to skip when reading in data file> <- i.e If 3, then the converter will ignore the first 3 lines of the datafile. You can also use this to fill 
```

#### columns
You can specify the mapping for as many columns as you wish. You do not need to provide a mapping for all the columns in your file, only to the ones you wish to rename or for which you want to specify a unit. The 'new_name', 'rename' and 'unit' options are all optional.

Note that the following columns are required: 

    - Voltage (or Potential)
    - Current
    - Test Time (or Timestamp)
    
If a column has no units specified in the config, but the column name follows the format 'Column Name (\<unit>)', the script will try to get the unit from the column name.

#### create_columns
You can create some columns from scratch with a single value to be applied to all rows.

This is particularly useful for EIS data, so that you can create a 'Current' column with value 0.

    
#### metadata
metadata is optional. You can add whatever metadata fields you want following the format: \<metadata field name>: \<value> (Example- Timezone: Europe/Berlin)
    
    - Start Time: If specified, this field will be used as the Test's start time. It can be given in epoch time (in milliseconds) (Here is a good resource for converting a date to epoch https://www.epochconverter.com/), or in ISO 8601 standard date format ("yyyy-MM-dd'T'HH:mm:ssZ"). If not specified, the script will pull the Start Time from the first value of the Timestamp column. If there is neither a Start Time specified or a 'Timestamp' column, the script will throw an error.
    
    - Timezone: The timezone where the test is being run. This should be in either International timezone format ("America/New_York"), or UTC offset ("-4:00"). If Timezone is not given, it will default to PST ('America/Los_Angeles'). *Note: Will work on making available a list of all valid timezones*
    
    - Other metadata will get added to the test record's platform data upon import.
    
    
    
### GenericVDFConverter Class
    
    
All the following examples assume that you have already created *converter = GenericVDFConverter(file_path, config_path)*
    

#### read_data()

converter.read_data() reads in and returns the raw time data from the given file. 

read_data() currently supports csv and excel files (if the excel file has mutliple sheets, the one containing the data needs to be specified in the config using the time_data_tab option.)

You can access the raw time data read in by the converter with:

```python
converter.time_df()
```

#### format_data(time_df)

converter.format_data(converter.time_df) takes the raw time data and formats it according to the config: renaming columns, and creating the Test Time column from the Timestamp column if needed.

You can access the formatted time data with:

```python
converter.formatted_df()
```

#### add_units(formatted_df)

converter.add_units(converter.formatted_df) takes the formatted time data and information from the configuration to add the required units row to the time data. Specifically, it looks at converter.unit_map to get the column to unit mapping information.

You can access the final time data (formatted data with units) with:

```python
converter.final_df()
```

#### get_data()

converter.get_data() is the combination of the functions above. It reads in the data, formats it, creates the metadata and adds the units. It will return the final time data and the metadata headers that are then used to write the VDF file.

```python
# If you want to run this as a standalone:
metadata, final_data = converter.get_data()

# Note that this function already runs as part of convert(), and you can access the created metadata with converter.header_dict and the final data with converter.final_df()
converter.header_dict
converter.final_df
```

#### verify_vdf(final_data, metadata)

converter.verify_vdf(converter.final_df, converter.header_dict) will verify that your data and metadata meets minimum VDF requirements. It will perform checks such as:

- Required columns (Voltage, Current, and Test Time) are present.
- All units added are valid Voltaiq units.
- The Test Time column is in ascending order.
- Required metadata (Start Time and Timezone) are present.


#### write_to_csv(final_data, metadata)

converter.write_to_csv(converter.final_df, converter.header_dict) will use the provided data and metadata to write the file to VDF. The convention used by the converter for the output path is to create a VDF folder in the same location as the sample file, and to add the VDF file to that folder, adding "_VDF" to the end of the filename.


#### convert()
    
converter.convert() is a combination of the above functions. It reads in the data, formats its, adds the units, creates the metadata, verifies that the time data and metadata meet VDF requirements, and writes the file to VDF.

```python
converter.convert()
```
    Reading in data...
    Formatting data...
    Updating header dictionary...
    Timezone was not defined: defaulted to PST
    Adding units...
    Completed generation of VDF file at path: sample_files/VDF/example_file_VDF.csv