# Description
This repository stores the Voltaiq Data Format standardization, conventions, and examples.

Voltaiq Data Format is a CSV format for battery data collected across the battery development lifecycle. Standardization of format and conventions allows for ease of comparison and usability of the battery data across disparate collection methods, organizations, and testing protocols.

The Voltaiq Data Format requires the following assumptions to be true:
* Data files are CSV format with a "Tab" delimiter, and files end with the extension .csv.
* Each data file represents one and only one test — tests will not be split across data files and data files will not contain data from multiple tests.
* Uniqueness for a test will be determined by the data file name; all datafiles should have a unique file name to be imported correctly.
    * To help create unique file names, relevant metadata should be included in the naming convention.
      * An example convention might be: “{date}_{channel number}_{test name}.csv” -> “2023-01-05_2_CyclingData.csv”
    * A subsequent check on “Start Time”, “Channel Number”, and “Tester ID” (if present) will be conducted to guarantee uniqueness on those constraints. 

## Metadata Header 
Each data file should begin with a specially formatted Metadata Header which can be any number of lines, in which each line contains a single "key: value" pair representing one piece of metadata (with a “: ” delimiter). There are a set of required fields. Additionally, up to 1024 key: value pairs of metadata may also be included. The termination of the header is indicated by a line containing only the string "[DATA START]". If the “REQUIRED” metadata are not present, the data file will not be imported. Sample files can be seen in the [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.
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
After the Metadata Header and the "[DATA START]" line, the remainder of the file should contain a data header followed by time-series performance data. Sample files can be seen in the [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.

### Data Header
The Data Header begins on the line directly after the "[DATA START]" line. The data header is two sequential lines that describes the measurements and units associated with the measurements. The data header and all data lines are delimited by a tab character. The order of the columns is not important, and can be in any order.

The first data header line contains labels for each data column. Some common examples of this might be: “Voltage”, “Current”, or “Power”. The second data header line contains units for each column, from the list of supported units provided by Voltaiq (see Appendix A). If a unit is desired that is not currently supported by Voltaiq, let us know (community@voltaiq.com).
### Data Columns
Data columns are the time series data that will be imported and displayable in the Voltaiq Application.
### Data Columns (REQUIRED)
The following columns are required, and must be present in each data file in order for any data to be imported into Voltaiq. If these columns are not present, the data file will not be imported.

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



# Voltaiq Data Format
Downloadable [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf)


# Sample Files
Sample [Metadata file](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDFMetadata_Voltaiq_EV_HPPC_Cell01-72.csv) in Voltaiq Data Format

Sample [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) in Voltaiq Data Format

# Sample Data Conversion Scripts
Existing data will need to be converted into Voltaiq Data Format. While manual conversion may be acceptable on a handful of files, manual conversion is not practical for large volumes of data. Scripts can be written to automate the conversion of data into Voltaiq Data Format. Here we provide example scripts.

### .mat Conversion to Voltaiq Data Format
Battery data in .mat format can be converted to Voltaiq Data Format. We have included an example .mat script which performs this conversion. This script reads electrochemical data stored in a .mat file and - with the help of a json configuration file - creates a VDF file with the same data that can be successfully uploaded. 
 [.mat conversion to VDF](https://github.com/vq-clininger/VoltaiqDataFormat/tree/main/mat%20-_%20vdf%20conversion)

### .csv, excel, and .rtf Conversion to Voltaiq Data Format
Included here is a sample script to convert battery data in a generic .csv format to the Voltaiq Data Format. 

The **generic_vdf_munge.py** script provides methods, mainly through the GenericVDFMunger class, for converting data files to the Voltaiq Data Format (VDF).

The GenericVDFMunger class needs 2 inputs: the data file to convert, and a config .yaml file containing munge information to convert the file, such as desired column and unit mappings.

Currently Supported:
- csv files
- excel files (single and multi tab)
- .rtf files if they can be read in as a csv

[.csv, excel, and .rtf conversion to VDF](https://github.com/vq-clininger/VoltaiqDataFormat/tree/main/excel%2C%20.csv%2C%20and%20.rtf%20-%20vdf%20conversion)


# FAQ
### How do I use Voltaiq Data Format?
When you collect data that describes the performance of a battery, write that data to, or collect that data in Voltaiq Data Format. Voltaiq Data Format outlines the format and conventions for the battery data. The data can then be uploaded to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/) and added to the large database of battery data for Machine Learning and Data Science for battery performance data. 
When you collect metadata about your batteries or battery data, collect that data in Voltaiq Metadata Format, and similarly, upload to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/).

### How do I learn more about Voltaiq Data Format?
There is a [publication](https://www.frontiersin.org/articles/10.3389/fenrg.2022.1059154/full) about Voltaiq Data Format where you can read more about how this format came about.












# OLD

# Description
This document describes this repository, which stores Voltaiq Data Format standardization and conventions and examples of Voltaiq Data Format.

Voltaiq Data Format is a CSV format describing the format and conventions to write battery data into. Standardization of format and conventions allows for ease of comparison and usability of the battery data across disparate collection methods, organizations, and testing protcols.

The Voltaiq Data Format requires the following assumptions to be true.
* Data files are CSV format with a "Tab" delimiter, and files end with the extension .csv.
* Each data file represents one and only one test — tests will not be split across data files and data files will not contain data from multiple tests.
* Uniqueness for a test will be determined by the data file name: all datafiles should have a unique file name to be imported correctly.
    * To help create unique filenames, we recommend including relevant metadata in the naming convention.
      * An example convention might be “{date}_{channel number}_{test name}.csv” -> “2000-01-01_2_CyclingData.csv”
    * A subsequent check on “Start Time”, “Channel Number”, and “Tester ID” (if present) will be conducted to guarantee uniqueness on those constraints 

## Metadata Header 
Each data file should begin with a specially formatted Metadata Header which can be any number of lines, in which each line contains a single "key: value" pair representing one piece of metadata (with a “: ” delimiter). There are a set of required fields, but any amount of metadata can be included in the header, up to 1024 key: value pairs. The termination of the header is indicated by a line containing only the string "[DATA START]". If the “REQUIRED” metadata are not present, the data file will not be imported. Sample files can be seen in the [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.
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
After the Metadata Header and the "[DATA START]" line, the remainder of the file should contain a data header followed by time-series performance data. Sample files can be seen in the [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) directory.

### Data Header
The Data Header begins on the line directly after the "[DATA START]" line. The data header is two sequential lines that describe the measurement and unit associated with the measurement. The data header and all data lines are delimited by a tab character. The order of the columns is not important, they can come in any order.

The first data header line contains labels for each data column. Some common examples of this might be: “Voltage”, “Current”, or “Power”. The second data header line contains units for each column, from the list of supported units provided by Voltaiq (see Appendix A). If a unit is desired that is not currently supported by Voltaiq, let us know (community@voltaiq.com).
### Data Columns
Data columns are the time series data that will be imported and displayable in the Voltaiq Application.
### Data Columns (REQUIRED)
The following columns are required, and must be present in each data file in order for any data to be imported into Voltaiq. If these columns are not present, the data file will not be imported.

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



# Voltaiq Data Format
Downloadable [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf)


# Sample Files
Sample [Metadata file](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDFMetadata_Voltaiq_EV_HPPC_Cell01-72.csv) in Voltaiq Data Format

Sampe [Raw Test data files](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) in Voltaiq Data Format

# FAQ
### How do I use Voltaiq Data Format?
When you collect data that describes the performance of a battery, write that data to, or collect that data in Voltaiq Data Format. Voltaiq Data Format outlines the format and conventions for the battery data. The data can then be uploaded to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/) and added to the large database of battery data for Machine Learning and Data Science for battery performance data. 
When you collect metadata about your batteries or battery data, collect that data in Voltaiq Metadata Format, and similarly, upload to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/).

### How do I learn more about Voltaiq Data Format?
There is a [publication](https://www.frontiersin.org/articles/10.3389/fenrg.2022.1059154/full) about Voltaiq Data Format where you can read more about how this format came about.



