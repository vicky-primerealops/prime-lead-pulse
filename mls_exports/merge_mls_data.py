import pandas as pd
import glob
import os

def merge_csv_files(input_folder, output_file):
    print(f"Scanning folder: {input_folder}")
    
    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in the specified folder.")
        return
    
    print(f"Found {len(csv_files)} CSV files. Merging...")
    
    dataframes = []
    
    for file in csv_files:
        try:
            # Read each CSV file
            df = pd.read_csv(file, low_memory=False)
            dataframes.append(df)
            print(f"Loaded {os.path.basename(file)}: {len(df)} rows")
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    if not dataframes:
        print("No data could be read.")
        return
        
    # Concatenate all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    initial_count = len(merged_df)
    print(f"\nTotal rows before deduplication: {initial_count}")
    
    # Deduplicate. Usually MLS # (ML Number) is the unique identifier.
    # We will try to find a column that looks like 'MLS Number', 'ML Number', 'MLS#', 'ML#', 'Listing ID'
    possible_id_columns = ['MLS Number', 'ML Number', 'MLS#', 'ML#', 'Listing ID', 'MLS', 'MLS_Number']
    
    id_col = None
    for col in merged_df.columns:
        if col.strip() in possible_id_columns or 'MLS' in col.upper():
            id_col = col
            break
            
    if id_col:
        print(f"Found unique identifier column: '{id_col}'")
        # Drop duplicates based on the MLS Number
        merged_df = merged_df.drop_duplicates(subset=[id_col])
        final_count = len(merged_df)
        print(f"Total rows after deduplication: {final_count}")
        print(f"Removed {initial_count - final_count} duplicate rows.")
    else:
        print("Warning: Could not automatically detect an MLS Number column.")
        print("Deduplicating based on all columns (exact row matches)...")
        merged_df = merged_df.drop_duplicates()
        final_count = len(merged_df)
        print(f"Total rows after deduplication: {final_count}")
        print(f"Removed {initial_count - final_count} duplicate rows.")
        
    # Export to the final CSV
    merged_df.to_csv(output_file, index=False)
    print(f"\nSuccess! Merged data saved to: {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Merge Matrix MLS CSV exports.")
    parser.add_argument("--input", default=".", help="Folder containing the CSV files to merge (default: current directory '.')")
    parser.add_argument("--output", default="Master_MLS_Export_Last_12_Months.csv", help="Name of the final merged output file")
    
    args = parser.parse_args()
    
    merge_csv_files(args.input, args.output)
