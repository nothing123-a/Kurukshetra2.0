#!/usr/bin/env python3
"""
Test with real phone data that user provided
"""

import pandas as pd
from augmentation_service import augmentation_service

def test_real_phone_data():
    # Create test data with user's exact phone data
    test_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Tom'],
        'phone': ['9876543210', '8765432109', 0, '6543210987', '5432109876']
    }
    
    df = pd.DataFrame(test_data)
    print("Original data (user's exact data):")
    print(df)
    print()
    
    data_dict = df.to_dict('records')
    columns = list(df.columns)
    
    # Test the command to replace 0 with 9405442242
    command = "replace 0 values in phone column with 9405442242"
    
    print(f"Testing command: {command}")
    print("=" * 60)
    
    try:
        result = augmentation_service.process_command(
            command=command,
            columns=columns,
            data=data_dict
        )
        
        if result.get('processed_data'):
            processed_df = pd.DataFrame(result['processed_data'])
            print("✅ SUCCESS!")
            print("Processed data:")
            print(processed_df)
            print()
            
            # Check if the 0 was replaced
            phone_values = processed_df['phone'].tolist()
            print(f"Phone values after processing: {phone_values}")
            
            if '9405442242' in phone_values and 0 not in phone_values and '0' not in phone_values:
                print("🎉 Phone 0 replacement SUCCESSFUL!")
                
                # Save to CSV to verify
                processed_df.to_csv('test_phone_result.csv', index=False)
                print("📁 Saved to test_phone_result.csv")
            else:
                print("❌ Phone 0 replacement FAILED!")
                print(f"Expected: 9405442242 in list, 0 not in list")
                print(f"Got: {phone_values}")
                
        else:
            print("❌ FAILED!")
            print("Error:", result.get('message'))
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_real_phone_data()