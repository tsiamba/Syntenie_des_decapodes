import os
import glob
import pandas as pd
import argparse

def summarize_rearrangements(target_dir):
    # Ensure absolute or correct relative path resolution
    search_path = os.path.join(target_dir, "Run_r*", "*.rearrangements.tsv")
    files = glob.glob(search_path)
    
    # Fallback search if directory structure varies slightly
    if not files:
        search_path = os.path.join(target_dir, "**", "*.rearrangements.tsv")
        files = glob.glob(search_path, recursive=True)

    if not files:
        print(f"[-] No rearrangement files found in target directory: {target_dir}")
        return

    summary_data = []

    for filepath in files:
        # Extract relative directory components or path parts to find Run_r*
        rel_path = os.path.relpath(filepath, target_dir)
        dirname = rel_path.split(os.sep)[0]
        
        # Parse model (r2 or r3) and threshold (m1 to m5) from the directory name
        parts = dirname.replace('Run_', '').split('-')
        model = parts[0]
        threshold = parts[1] if len(parts) > 1 else 'm5'  # defaults to m5 if no hyphen suffix
        
        # Read the rearrangement file
        df = pd.read_csv(filepath, sep="\t")
        
        # Count occurrences of each event type
        counts = df['event'].value_counts().to_dict()
        
        # Metadata tagging
        counts['model'] = model
        counts['threshold'] = threshold
        counts['source_folder'] = dirname
        
        summary_data.append(counts)

    # Create a clean DataFrame summary
    summary_df = pd.DataFrame(summary_data)

    # Reorder columns for readability
    cols_order = ['model', 'threshold', 'source_folder', 'fusion', 'fission', 'translocation']
    existing_cols = [c for c in cols_order if c in summary_df.columns]
    other_cols = [c for c in summary_df.columns if c not in existing_cols]
    summary_df = summary_df[existing_cols + other_cols]

    # Sort neatly by model and numerical threshold value
    summary_df['m_num'] = summary_df['threshold'].str.replace('m', '').astype(int)
    summary_df = summary_df.sort_values(by=['model', 'm_num']).drop(columns=['m_num'])

    # Fill NaN counts with 0
    summary_df = summary_df.fillna(0)

    # Save output summary file inside the target directory
    output_filename = "rearrangements_summary.tsv"
    output_path = os.path.join(target_dir, output_filename)
    summary_df.to_csv(output_path, sep="\t", index=False)
    
    print(f"[+] Summary successfully saved to: {output_path}")
    print("\n--- Summary Preview ---")
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize syngraph rearrangement runs across parameter folders.")
    parser.add_argument(
        "-d", "--directory", 
        default=".", 
        help="Path to the parent directory containing the Run_r* folders (default: current directory)."
    )
    args = parser.parse_args()
    
    summarize_rearrangements(args.directory)
