#!/usr/bin/env python3
"""
Quick fix script to fill null/0 values with dummy data
"""

import pandas as pd
import numpy as np

def quick_fill_nulls(csv_file_path, output_path=None):
    """Fill all null/0/empty values with dummy data"""
    
    # Read CSV
    df = pd.read_csv(csv_file_path)
    print(f"Original data shape: {df.shape}")
    print("Original data:")
    print(df)
    print()
    
    # Fill null/0/empty values for each column
    for col in df.columns:
        # Convert to string to handle all data types
        df[col] = df[col].astype(str)
        
        # Create mask for null/0/empty values
        null_mask = (df[col] == '0') | (df[col] == '') | (df[col] == 'nan') | (df[col] == 'None') | (df[col].isna())
        null_count = null_mask.sum()
        
        if null_count > 0:
            print(f"Column '{col}': Found {null_count} null/0/empty values")
            
            # Fill based on column type
            if 'phone' in col.lower():
                # Fill phone with dummy phone numbers
                dummy_phones = [f"940544{str(i+2242).zfill(4)}" for i in range(null_count)]
                df.loc[null_mask, col] = dummy_phones
                print(f"  → Filled with dummy phone numbers: {dummy_phones}")
                
            elif 'email' in col.lower():
                # Fill email with dummy emails
                dummy_emails = [f"user{i+1000}@example.com" for i in range(null_count)]
                df.loc[null_mask, col] = dummy_emails
                print(f"  → Filled with dummy emails: {dummy_emails}")
                
            elif 'name' in col.lower():
                # Fill name with dummy names
                dummy_names = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown']
                dummy_values = [dummy_names[i % len(dummy_names)] for i in range(null_count)]
                df.loc[null_mask, col] = dummy_values
                print(f"  → Filled with dummy names: {dummy_values}")
                
            elif 'age' in col.lower():
                # Fill age with random realistic ages
                dummy_ages = np.random.randint(18, 65, null_count)
                df.loc[null_mask, col] = dummy_ages
                print(f"  → Filled with dummy ages: {dummy_ages.tolist()}")
                
            elif 'id' in col.lower():
                # Fill ID with sequential numbers
                max_id = df[col][df[col] != '0'].astype(int).max() if df[col][df[col] != '0'].any() else 1000
                dummy_ids = list(range(max_id + 1, max_id + 1 + null_count))
                df.loc[null_mask, col] = dummy_ids
                print(f"  → Filled with sequential IDs: {dummy_ids}")
                
            else:
                # Fill other columns with generic dummy data
                df.loc[null_mask, col] = f"dummy_{col}"
                print(f"  → Filled with: dummy_{col}")
    
    print("\nProcessed data:")
    print(df)
    
    # Save to output file
    if not output_path:
        output_path = csv_file_path.replace('.csv', '_filled.csv')
    
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved filled data to: {output_path}")
    
    return df

if __name__ == "__main__":
    # Create test CSV with your phone data
    test_data = {
        'phone': ['9876543210', '8765432109', 0, '6543210987', '5432109876'],
        'name': ['John', 'Jane', '', 'Alice', 'Tom'],
        'email': ['john@test.com', 'jane@test.com', 0, 'alice@test.com', '']
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv('test_phone_data.csv', index=False)
    print("Created test_phone_data.csv")
    
    # Fill the data
    quick_fill_nulls('test_phone_data.csv')