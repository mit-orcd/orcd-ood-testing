#!/usr/bin/env python
# coding: utf-8
# Author: Shahzod Nazirov, Jonathan Murray, ORCD
# Purpose: To give users quick reporting on their activities
# essentially parses sacct output
# for OOD front end, eventually
# Date: 2025-02-12

# Import necessary libraries
import pandas as pd
import glob
from datetime import datetime, timedelta

# Get a list of all files matching the pattern 'sacct_*.lst'
file_list = glob.glob('sacct_*.lst')
df_list = []  # Initialize an empty list to store dataframes
sum_rows = 0  # Initialize a counter for the total number of rows

print("hello")  # Print a greeting message

# Loop through each file in the file list
for file in file_list:
    # Read the file into a dataframe, skipping bad lines
    df = pd.read_csv(file, delimiter='|', low_memory=False, on_bad_lines='skip')
    # Add the number of rows in the current dataframe to the total count
    sum_rows += df.shape[0]
    # Print the number of rows in the current dataframe
    print(df.shape[0])
    # Append the current dataframe to the list of dataframes
    df_list.append(df)

# Print the total number of rows across all dataframes
print(sum_rows)

# Combine all dataframes in the list into a single dataframe
combined_df = pd.concat(df_list, ignore_index=True, join='outer')
# Generate summary statistics for the combined dataframe
summary_stats = combined_df.describe()

# Convert specific columns to numeric, coercing errors to NaN
combined_df['CPUTimeRAW'] = pd.to_numeric(combined_df['CPUTimeRAW'], errors='coerce')
combined_df['AllocCPUS'] = pd.to_numeric(combined_df['AllocCPUS'], errors='coerce')
combined_df['AllocNodes'] = pd.to_numeric(combined_df['AllocNodes'], errors='coerce')

# Group the combined dataframe by 'User' and aggregate specific columns
grouped_summary = combined_df.groupby('User').agg({
    'CPUTimeRAW': 'sum',  # Sum of CPUTimeRAW
    'AllocCPUS': 'sum',   # Sum of AllocCPUS
    'AllocNodes': 'sum',  # Sum of AllocNodes
    'JobID': 'count'      # Count of JobID
})

# Rename the 'JobID' column to 'Total Number of Jobs'
grouped_summary = grouped_summary.rename(columns={'JobID': 'Total Number of Jobs'})

# Define a function to convert seconds to a formatted string (days:hours:minutes:seconds)
def convert_seconds(seconds):
    days, remainder = divmod(seconds, 86400)   # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600) # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)   # 60 seconds in a minute
    return f"{int(days)}:{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Apply the conversion function to the 'CPUTimeRAW' column after summing
grouped_summary['CPUTime'] = grouped_summary['CPUTimeRAW'].apply(convert_seconds)

# Print the grouped summary dataframe
print(grouped_summary)