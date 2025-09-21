import pandas as pd

def convert_readme_to_csv(input_file, output_file):
    """
    Extract table containing species and related file IDs from README file and convert to CSV.
    
    NOTE:  This data is very similar to the file NABBP lookup table species.csv.  Unfortunately,
    that file does not containe the necessary file ID numbers, so we have to extract them from the README file.

    Parameters:
    input_file (str): Path to input README file
    output_file (str): Path to output CSV file
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_marker = "All download groups with included bird species:"
    start_index = content.find(start_marker)
    
    if start_index == -1:
        raise ValueError(f"Could not find the marker: '{start_marker}'")
    
    data_section = content[start_index + len(start_marker):].strip()
    lines = data_section.split('\n')
    
    data_lines = []
    header_found = False
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        if line.startswith('grp_table') and 'species_id' in line:
            header_found = True
            continue
        
        if header_found and line.startswith('_'):
            parts = line.split('\t')
            if len(parts) >= 6:
                data_lines.append(parts)
    
    if not data_lines:
        raise ValueError("No valid data lines found after the header")
    
    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=['grp_table', 'species_id', 'ALPHA_CODE', 'SPECIES_NAME', 'SCI_NAME', 'count'])
    
    df['grp_table'] = df['grp_table'].str.replace('_', '', regex=False)
    df['count'] = df['count'].str.replace(r'[(),]', '', regex=True)    
    df['grp_table'] = pd.to_numeric(df['grp_table'], errors='coerce')
    df['species_id'] = pd.to_numeric(df['species_id'], errors='coerce')
    df['count'] = pd.to_numeric(df['count'], errors='coerce')
    
    
    df.to_csv(output_file, index=False, quoting=1)
    
    return df


if __name__ == "__main__":
    input_readme = 'notebooks/data/source_data/NABBP-2025/README_before_download.txt'
    output_csv = 'notebooks/data/augmented_data/nabbp_file_species_index.csv'
    df = convert_readme_to_csv(input_readme, output_csv)
    print(f"Extracted {len(df)} records to {output_csv}")