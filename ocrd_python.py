import pandas as pd
import glob
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_data(file_pattern):
    """Loads and combines data from all files matching the pattern."""
    file_list = glob.glob(file_pattern)
    
    if not file_list:
        logging.warning("No files found matching the pattern.")
        return None
    
    df_list = []
    total_rows = 0

    for file in file_list:
        try:
            df = pd.read_csv(file, delimiter='|', low_memory=False, on_bad_lines='skip')
            total_rows += df.shape[0]
            df_list.append(df)
            logging.info(f"Loaded {df.shape[0]} rows from {file}")
        except Exception as e:
            logging.error(f"Error reading {file}: {e}")
    
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        logging.info(f"Total combined rows: {total_rows}")
        return combined_df
    return None

def preprocess_data(df):
    """Ensures relevant columns are numeric and drops unnecessary ones."""
    numeric_columns = ['CPUTimeRAW', 'AllocCPUS', 'AllocNodes']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            logging.warning(f"Column '{col}' not found in data.")
    
    # Deduplication logic: Remove duplicate jobs that appear across multiple reports
    if 'JobID' in df.columns and 'StartTime' in df.columns:
        df['StartTime'] = pd.to_datetime(df['StartTime'], errors='coerce')
        df.sort_values(by=['JobID', 'StartTime'], inplace=True)
        
        # Keep the first occurrence of each JobID (earliest StartTime)
        df = df.drop_duplicates(subset='JobID', keep='first')
        logging.info(f"Total rows after deduplication: {df.shape[0]}")
    else:
        logging.warning("Cannot deduplicate properly: 'JobID' or 'StartTime' column missing.")
    
    return df

def compute_summary(df):
    """Aggregates data by User, summing relevant columns."""
    if 'User' not in df.columns:
        logging.error("Column 'User' not found. Cannot compute summary.")
        return None

    summary = df.groupby('User').agg({
        'CPUTimeRAW': 'sum',
        'AllocCPUS': 'sum',
        'AllocNodes': 'sum',
        'JobID': 'count' if 'JobID' in df.columns else 'size'
    }).rename(columns={'JobID': 'Total Jobs'})

    return summary

def convert_seconds(seconds):
    """Converts seconds to days:hours:minutes:seconds format."""
    if pd.isna(seconds) or seconds < 0:
        return "0:00:00:00"
    
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

def add_readable_time(summary):
    """Adds a human-readable CPUTime column."""
    if 'CPUTimeRAW' in summary.columns:
        summary['CPUTime'] = summary['CPUTimeRAW'].apply(convert_seconds)
    return summary

def save_summary(summary, output_file):
    """Saves the summary to a CSV file."""
    try:
        summary.to_csv(output_file, index=True)
        logging.info(f"Summary saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving summary: {e}")

def main():
    # Argument parsing for input file pattern and output file name
    parser = argparse.ArgumentParser(description="Process SLURM job accounting data.")
    parser.add_argument("--input", type=str, default="sacct_*.lst", help="Input file pattern (default: sacct_*.lst)")
    parser.add_argument("--output", type=str, default="summary_results.csv", help="Output file name (default: summary_results.csv)")
    
    args = parser.parse_args()
    
    df = load_data(args.input)
    if df is None:
        logging.error("No data loaded. Exiting program.")
        return
    
    df = preprocess_data(df)
    summary = compute_summary(df)
    
    if summary is not None:
        summary = add_readable_time(summary)
        logging.info("\nSummary Statistics:\n")
        print(summary)

        # Save to file
        save_summary(summary, args.output)

if __name__ == "__main__":
    main()
