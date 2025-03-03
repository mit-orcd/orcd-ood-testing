import pandas as pd
import glob
import math
import pydoc

# Function to display the menu in three columns and get user input
def display_menu(headers):
    num_columns = 5
    num_rows = math.ceil(len(headers) / num_columns)
    
    print("Available headers:")
    for row in range(num_rows):
        for col in range(num_columns):
            index = row + col * num_rows
            if index < len(headers):
                print(f"{index + 1}. {headers[index]:<20}", end=' ')
        print()
    
    selected_indices = input("Enter the numbers of the headers you want to include in the report, separated by commas: ")
    selected_indices = [int(index.strip()) - 1 for index in selected_indices.split(',')]
    selected_headers = [headers[i] for i in selected_indices]
    
    return selected_headers

# Function to generate the custom report
def generate_report(df, selected_headers, user):
    # Filter the dataframe based on the user input
    user_df = df[df['User'] == user]
    custom_report = user_df[selected_headers]
    return custom_report

# Get a list of all files matching the pattern 'sacct_*.lst'
file_list = glob.glob('sacct_*.lst')
df_list = []

# Read all files into dataframes and append to the list
for file in file_list:
    df = pd.read_csv(file, delimiter='|', low_memory=False, on_bad_lines='skip')
    df_list.append(df)

# Combine all dataframes into a single dataframe
combined_df = pd.concat(df_list, ignore_index=True, join='outer')

# Get the list of headers (columns) from the combined dataframe
headers = combined_df.columns.tolist()

# Ask for the user's name
user = input("Enter your username: ")

# Display the menu and get the selected headers from the user
selected_headers = display_menu(headers)

# Generate the custom report based on the selected headers and user
custom_report = generate_report(combined_df, selected_headers, user)

# Convert the custom report to a string without the index column
report_str = custom_report.to_string(index=False)

# Use pydoc.pager to display the report with paging functionality
pydoc.pager(report_str)