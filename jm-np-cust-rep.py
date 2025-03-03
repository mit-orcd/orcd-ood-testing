import pandas as pd
import glob

# Function to display the menu and get user input
def display_menu(headers):
    print("Available headers:")
    for i, header in enumerate(headers):
        print(f"{i + 1}. {header}")
    
    selected_indices = input("Enter the numbers of the headers you want to include in the report, separated by commas: ")
    selected_indices = [int(index.strip()) - 1 for index in selected_indices.split(',')]
    selected_headers = [headers[i] for i in selected_indices]
    
    return selected_headers

# Function to generate the custom report
def generate_report(df, selected_headers):
    custom_report = df[selected_headers]
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

# Display the menu and get the selected headers from the user
selected_headers = display_menu(headers)

# Generate the custom report based on the selected headers
custom_report = generate_report(combined_df, selected_headers)

# Print the custom report
print("\nCustom Report:")
print(custom_report)
