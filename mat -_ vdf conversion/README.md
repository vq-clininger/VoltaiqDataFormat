# Description

This script reads electrochemical data stored in a .mat file and - with the help of a json configuration file - creates a VDF file with the same data that can be successfully uploaded.
In this README, we discuss how to use the conversion script and configure the json file it depends on.

# Setup
Before the script is run and the json is configured, users must have an understanding of how varaibles are structured in the .mat file. In the example .mat file, [example_echem_data.mat](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/mat%20-_%20vdf%20conversion/example_echem_data.mat), loading the file creates a 1x1 struct named meas with 8 fields. Inspecting the meas variable shows that Current is stored in meas.Current. This mapped value for Current will be necessary to configure the json file.
All variables must be of the same size. In this example, meas.Current, meas.Time, and meas.Voltage are all 38718x1 arrays.

# The JSON configuration File
The JSON file must be placed in the same directory as mat_to_vdf.m. 
Here is an example mat_to_vdf_config.json file:
```json
{
    "description": "This json configuration file aids mat_to_vdf.m by converting electrochemical data stored in .mat to VDF [Voltaiq Data Format]",
    "filepath": "/home/Matlab/mat_to_vdf/example_echem_data.mat",
    "variables": 
        {
            "Test_Time": {
                "location" : "meas.Time",
                "unit" : "second"
            },
            "Current": {
                "location" : "meas.Current",
                "unit" : "amp"
            },
            "Potential": {
                "location" : "meas.Voltage",
                "unit" : "volt"
            }
        },
    "starttime" : "2013-09-29T18:46:19Z",
    "timezone" : "Europe/Berlin"
}
```

Where the necessary components of the file are:
filepath - the filepath to the .mat file to convert.
variables - the name, location and unit of each variable within the .mat file that will be converted. This must include Test_Time, Current and Potential at minimum. Any variable with a space (Test Time) must be replaced with an underscore (Test_Time).
    Test Time - the time elapsed since the start of the test. Values must be in ascending order
    Current - Instantaneous value of current. Values must be positive for charge current and negative for discharge current
    Potential - Instantaneous value of Potential
starttime - UTC Timestamp for the start of the test. Must be in Unix epoch time stamp (ms) or ISO 8601 standard: ("yyyy-MM-dd'T'HH:mm:ssZ").
timezone - The timezone where the test is being run. Must be in International timezone format ("America/New_York") or UTC offset ("-4:00")
Output
Once the JSON file is configured, run mat_to_vdf.m. A file will be created in the same directory as the source .mat file appended with _vdf.txt.
