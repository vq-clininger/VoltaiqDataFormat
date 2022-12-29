% .mat to VDF conversion script

% RELIES on mat_to_vdf_config.json for variables and units

% This script MUST be given variable arrays of the same size 
% this is represented by each variables "location" in the json

% Update Log %
% Json incorporation | 10/7/22 | Juveria Masood
% Creation | 9/13/22 | Juveria Masood
    
%Read in JSON config file
fileName = 'mat_to_vdf_config.json'; 
fid = fopen(fileName); 
raw = fread(fid,inf); 
str = char(raw');
fclose(fid); 
data = jsondecode(str);

% Fetch EChem dta and variables 
echemdata = load(data.filepath);
struct = data.variables;
fn = fieldnames(struct);

% Validate existance of Test Time, Current, Potential fields (minimum
% requirements)
matches = strfind(fn, 'Test_Time');
tf = any(vertcat(matches{:}));
if ~tf
    fprintf(2, 'ERROR')
    disp('json file does not contain definition for Test_Time');
    return
end
matches = strfind(fn, 'Current');
tf = any(vertcat(matches{:}));
if ~tf
    fprintf(2, 'ERROR')
    disp('json file does not contain definition for Current');
    return
end
matches = strfind(fn, 'Potential');
tf = any(vertcat(matches{:}));
if ~tf
    fprintf(2, 'ERROR')
    disp('json file does not contain definition for Potential');
    return
end

% Validate Filepath
% Ex. "/home/Matlab/mat_to_vdf/example_echem_data.mat"
[filepath,name,ext] = fileparts(data.filepath);
if ext~='.mat'
    fprintf(2, 'ERROR')
    disp('File is not .mat')
    return
end

% Validate Start Time
% Ex. 2013-09-29T18:46:19Z
utc_regex = '^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z$';
start_time_input = data.starttime;
if isnumeric(start_time_input) && numel(num2str(start_time_input))==10
     start_time_resolved = start_time_input;
elseif regexp(start_time_input,utc_regex)
     start_time_resolved = start_time_input;
else 
    fprintf(2, 'ERROR')
    disp('Time field is invalid')
    return
end

% Validate Time Zone
% Ex. +05:30
utc_offset_regex = '[+-]([01]\d|2[0-4])(:?[0-5]\d)?';
timezone_input = data.timezone;
if any(isletter(timezone_input))
    time_zone_resolved = timezone_input;
elseif regexp(timezone_input,utc_offset_regex)
    time_zone_resolved = timezone_input;
else 
    fprintf(2, 'ERROR')
    disp('Timezone field is invalid')
    return
end

% Begin restructuring
num_variables = numel(fn);
variable_names = strings(1,num_variables);
units=strings(1,num_variables);
for i=1:num_variables
    fn1=fieldnames(struct.(fn{i}));
    if struct.(fn{i}).(fn1{1})
        location = "echemdata." + struct.(fn{i}).(fn1{1});
    else
        fprintf(2, 'ERROR')
        X=['No variable location found for ', fn{i}, ' in json config file'];
        disp(X)
        return
    end
    units{i} = struct.(fn{i}).(fn1{2});
    variable_name = fn{i};
    variable_names{i} = strrep(fn{i}, '_', ' ');
    results_struct.(variable_name) = num2cell(eval(location));
end

% Structure metadata lines for VDF file
column_placeholders = strings(1, num_variables-1);
metadata_starttime = "Start Time: " + start_time_resolved;
metadata_starttime_row = [metadata_starttime, column_placeholders];
metadata_timezone = "Timezone: " + time_zone_resolved;
metadata_timezone_row = [metadata_timezone, column_placeholders];
columns = variable_names;
data_start = ["[DATA START]",column_placeholders];
table_header_info=array2table([string(metadata_starttime_row);string(metadata_timezone_row);string(data_start);string(columns);string(units)]);

% Set file name
vdf_file_name = [name, '_vdf.txt'];

% Create final result
temp_array = cell(1,num_variables);
data_array = results_struct(1).(fn{1});
for i=2:num_variables
    temp_array = cat(2, data_array, results_struct(1).(fn{i}));
    data_array = temp_array;
end
table = array2table(temp_array);
table.Properties.VariableNames = table_header_info.Properties.VariableNames;
final_out = [table_header_info;table];

% Write
writetable(final_out,vdf_file_name,'Delimiter','\t','WriteVariableNames',0,'QuoteStrings',false);  
fprintf(2,'\nFile created\n')
