
See page here:
https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/README.md



Text:

# Description
This repository stores the Voltaiq Data Format standardization, conventions, and examples.

Voltaiq Data Format is a text-file format for battery data collected across the battery lifecycle. Standardization of format and conventions enables easy, interoperable comparison and analysis of battery data across disparate collection methods, organizations, testing protocols, and hardware. For example, data in VDF format can be natively imported to any Voltaiq system, including the open-access Voltaiq Community platform.

See this [publication](https://www.frontiersin.org/articles/10.3389/fenrg.2022.1059154/full) about the Voltaiq Data Format to learn more about the origins of this format and how it can streamline collaboration and extraction of insights across the battery lifecycle.

The Voltaiq Data Format requires the following:
* Datafiles are CSV format with a "Tab" delimiter, and filenames use the extension .csv.
* Each datafile represents one and only one performance record (where a performance record can contain data from a battery test, formation cycling, in-application performance, or similar). Records will not be split across datafiles and datafiles will not contain data from multiple records.
* Uniqueness of a record will be determined by the datafile name; all datafiles must have a unique fil name.
    * To help create unique file names, relevant metadata should be included in the naming convention.
      * An example convention might be: “{date}_{channel number}_{test name}.csv” -> “2023-01-05_2_CyclingData.csv”
    * To ensure uniqueness, “Start Time”, “Channel Number”, and “Tester ID” (if present) in combination with filename should be unique. 

# Sample Files
Sample [Metadata file](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDFMetadata_Voltaiq_EV_HPPC_Cell01-72.csv) in Voltaiq Data Format

Sample [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) in Voltaiq Data Format

# Sample Data Conversion Scripts
Existing data can be converted into Voltaiq Data Format. While manual conversion may be acceptable on a handful of files, manual conversion is not practical for large volumes of data. Scripts can be written to automate the conversion of data into Voltaiq Data Format. Here we provide example scripts.

### .mat Conversion to Voltaiq Data Format
Battery data in .mat format (the standard for MATLAB software) can be converted to Voltaiq Data Format. We have included an example .mat script which performs this conversion. This script reads electrochemical data stored in a .mat file and - with the help of a json configuration file - creates a VDF file with the same data. 
 [.mat conversion to VDF](https://github.com/vq-clininger/VoltaiqDataFormat/tree/main/mat%20-_%20vdf%20conversion)

### .csv, excel, and .rtf Conversion to Voltaiq Data Format
Included here is a sample script to convert battery data in a generic .csv format to the Voltaiq Data Format. 

The **generic_vdf_munge.py** script provides methods, mainly through the GenericVDFMunger class, for converting datafiles to the Voltaiq Data Format (VDF).

The GenericVDFMunger class needs 2 inputs: the datafile to convert, and a config .yaml file containing munge information to convert the file, such as desired column and unit mappings.

Currently Supported:
- csv files
- excel files (single and multi tab)
- .rtf files if they can be read in as a csv

[.csv, excel, and .rtf conversion to VDF](https://github.com/vq-clininger/VoltaiqDataFormat/tree/main/excel%2C%20.csv%2C%20and%20.rtf%20-%20vdf%20conversion)

# Voltaiq Data Format Requirements
Downloadable [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf)

## Metadata Header 
Each datafile should begin with a specially formatted Metadata Header which can be any number of lines, in which each line contains a single "key: value" pair representing one piece of metadata (with a “: ” delimiter). There are a set of required fields listed below. The termination of the header is indicated by a line containing only the string "[DATA START]". If the “REQUIRED” metadata are not present, the datafile will not be imported. Sample files can be seen in the [Raw Test datafiles](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.
### Metadata (REQUIRED)
* “Start Time”
   * UTC timestamp for the start of this test. Either of these formats is allowed:
   * Unix epoch timestamp- in milliseconds.
   * ISO 8601 standard: ("yyyy-MM-dd'T'HH:mm:ssZ").
* "Timezone"
   * The timezone where the test is being run. Either of these formats is allowed:
   * International timezone format ("America/New_York").
   * UTC offset ("-4:00").

Other optional metadata entries can be seen in the [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf).

## Data
After the Metadata Header and the "[DATA START]" line, the remainder of the file should contain a data header followed by time-series performance data. Sample files can be seen in the [Raw Test datafiles](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.

### Data Header
The Data Header begins on the line directly after the "[DATA START]" line. The data header is two sequential lines that describe the measurements and units associated with the measurements. The data header and all data lines are delimited by a tab character. The order of the columns is not important, and can be in any order.

The first data header line contains labels for each data column. Some common examples of this might be: “Voltage”, “Current”, or “Power”. The second data header line contains units for each column, from the list of supported units provided by Voltaiq (see Appendix A). If a unit is desired that is not currently supported by Voltaiq, let us know (community@voltaiq.com).
### Data Columns
Data columns are the time series data that will be imported and displayable in the Voltaiq Application.
### Data Columns (REQUIRED)
The following columns are required, and must be present in each datafile in order for any data to be imported into Voltaiq. If these columns are not present, the datafile will not be imported.

Note: for columns with a Dimension other than “None”, a Unit from Appendix A matching the specified dimension must be included on the second data header line.

* “Test Time”
   * Definition: Time elapsed since the start of the test.
   * Data Type: Float
   * Dimension: Time
   * Logical requirements and notes:
   * Sequential values within the test may not decrease (i.e. values should be in ascending order).
* “Current”
   * Definition: Instantaneous value of current.
   * Data Type: Float
   * Dimension: Current
   * Logical requirements and notes:
   * The sign convention is positive for charge current and negative for discharge current.

* “Voltage”
   * Definition: Instantaneous value of potential.
   * Data Type: Float
   * Dimension: Potential
   * Logical requirements and notes: N/A

Other optional data entries can be seen in the [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf).

# FAQ
### How do I use Voltaiq Data Format?
Voltaiq Data Format can be used as an interoperable standard for battery performance data and metadata collection. The data can then be used as an internal data standard, shared with partners, and/or uploaded to any Voltaiq system, including the open-access [Voltaiq Community](https://www.voltaiqcommunity.com/). Using this open standard can facilitate the assembly of large battery datasets for subsequent analysis using cutting-edge data science and machine learning techniques. 
When you collect metadata about your batteries or battery data, collect that data in Voltaiq Metadata Format, and similarly, upload to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/).

### How do I learn more about Voltaiq Data Format?
There is a [publication](https://www.frontiersin.org/articles/10.3389/fenrg.2022.1059154/full) about Voltaiq Data Format where you can learn more about the origins of this format and how it can streamline collaboration and extraction of insights across the battery lifecycle.



