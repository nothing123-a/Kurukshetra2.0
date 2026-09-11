#!/usr/bin/env python3
"""
Test enhanced fillna with specific user commands
"""

import pandas as pd
import numpy as np
from augmentation_service import augmentation_service

def test_specific_commands():
    """Test specific user commands for filling data"""
    
    # Create test data with null/0 values
    test_data = {
        'id': [1, 2, 0, 4, 0],
        'name': ['John', '', 'Alice', 0, None],
        'email': ['john@test.com', 0, '', 'alice@test.com', None],
        'phone': ['+1234567890', 0, '', '+9876543210', None],
        'age': [25, 0, -5, 30, None]
    }
    
    df = pd.DataFrame(test_data)
    print("Original data:")
    print(df)
    print()
    
    data_dict = df.to_dict('records')
    columns = list(df.columns)
    
    # Test specific commands
    test_commands = [
        "fill phone with 9097865656",
        "replace email 0 values with dummy emails", 
        "set name to John Smith for empty values",
        "fix age negative values with 25"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"=== TEST {i}: {command} ===")
        
        try:
            result = augmentation_service.process_command(
                command=command,
                columns=columns,
                data=data_dict
            )
            
            if result.get('processed_data'):
                processed_df = pd.DataFrame(result['processed_data'])
                print("✅ SUCCESS!")
                print("Result:")
                print(processed_df)
                print()
                print("Message:", result.get('message', ''))
                print()
                
                # Update data for next test
                data_dict = result['processed_data']
                
            else:
                print("❌ FAILED!")
                print("Error:", result.get('message'))
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        print("-" * 60)
        print()

if __name__ == "__main__":
    test_specific_commands()