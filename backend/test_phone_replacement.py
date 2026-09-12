#!/usr/bin/env python3
"""
Test phone number replacement specifically
"""

import pandas as pd
from augmentation_service import augmentation_service

def test_phone_replacement():
    # Create test data with 0 values in phone column
    test_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Tom'],
        'phone': ['+1234567890', 0, '0', '', None],
        'email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'alice@test.com', 'tom@test.com']
    }
    
    df = pd.DataFrame(test_data)
    print("Original data:")
    print(df)
    print()
    
    data_dict = df.to_dict('records')
    columns = list(df.columns)
    
    # Test the exact command
    command = "if there are 0 values in phone column replace it by 9405442242"
    
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
            print("Message:", result.get('message', ''))
            
            # Check if phone values were actually replaced
            phone_values = processed_df['phone'].tolist()
            print(f"\nPhone values after processing: {phone_values}")
            
            # Count how many were replaced with 9405442242
            replaced_count = phone_values.count('9405442242')
            print(f"Number of values replaced with 9405442242: {replaced_count}")
            
            if replaced_count > 0:
                print("🎉 Phone replacement SUCCESSFUL!")
            else:
                print("❌ Phone replacement FAILED!")
                
        else:
            print("❌ FAILED!")
            print("Error:", result.get('message'))
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_phone_replacement()