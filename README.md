
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



# Voltaiq Data Format
Downloadable [Voltaiq Data Format Specification](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/Voltaiq%20Data%20Format.pdf)


# Example Files
Example [Metadata file](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDFMetadata_Voltaiq_EV_HPPC_Cell01-72.csv) in Voltaiq Data Format

Example [Raw Test data file](https://github.com/vq-clininger/VoltaiqDataFormat/blob/main/VDF_Voltaiq_EV_HPPC_Cell01.xlsx) in Voltaiq Data Format

# FAQ
### How do I use Voltaiq Data Format?
When you collect data that describes the performance of a battery, write that data to, or collect that data in Voltaiq Data Format. Voltaiq Data Format outlines the format and conventions for the battery data. The data can then be uploaded to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/) and added to the large database of battery data for Machine Learning and Data Science for battery performance data. 
When you collect metadata about your batteries or battery data, collect that data in Voltaiq Metadata Format, and similarly, upload to [Voltaiq Community Edition](https://www.voltaiqcommunity.com/).

### How do I learn more about Voltaiq Data Format?
There is a [publication](https://www.frontiersin.org/articles/10.3389/fenrg.2022.1059154/full) about Voltaiq Data Format where you can read more about how this format came about.



