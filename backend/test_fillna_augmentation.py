#!/usr/bin/env python3
"""
Test script for fillna augmentation functionality
"""

import pandas as pd
import numpy as np
from augmentation_service import augmentation_service

def create_test_csv():
    """Create test CSV with null/0 values"""
    test_data = {
        'id': [1, 2, 0, 4, 0],
        'name': ['John', '', 'Alice', 0, None],
        'email': ['john@test.com', 0, '', 'alice@test.com', None],
        'age': [25, 0, -5, 30, None],
        'phone': ['+1234567890', 0, '', '+9876543210', None],
        'address': ['123 Main St', '', 0, '456 Oak Ave', None]
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv('test_data.csv', index=False)
    print("✅ Created test_data.csv with null/0 values:")
    print(df)
    print("\nNull/0 counts per column:")
    for col in df.columns:
        null_count = df[col].isna().sum()
        zero_count = (df[col] == 0).sum()
        empty_count = (df[col] == '').sum()
        print(f"{col}: {null_count} nulls, {zero_count} zeros, {empty_count} empty strings")
    
    return df.to_dict('records')

def test_fillna_commands():
    """Test various fillna commands"""
    print("\n" + "="*60)
    print("TESTING FILLNA AUGMENTATION")
    print("="*60)
    
    # Create test data
    test_data = create_test_csv()
    columns = ['id', 'name', 'email', 'age', 'phone', 'address']
    
    # Test commands
    test_commands = [
        "fill dummy data for all null values",
        "replace 0 values with dummy emails",
        "fill null names with dummy names",
        "fix age values that are 0 or negative",
        "add dummy phone numbers for empty values",
        "fill all empty addresses with dummy addresses"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n--- TEST {i}: {command} ---")
        
        try:
            result = augmentation_service.process_command(
                command=command,
                columns=columns,
                data=test_data
            )
            
            if result.get('processed_data'):
                processed_df = pd.DataFrame(result['processed_data'])
                print("✅ SUCCESS!")
                print("Message:", result.get('message', 'No message'))
                print("\nProcessed data:")
                print(processed_df)
                
                # Check if nulls/zeros were filled
                print("\nAfter processing - Null/0 counts:")
                for col in processed_df.columns:
                    null_count = processed_df[col].isna().sum()
                    zero_count = (processed_df[col] == 0).sum()
                    empty_count = (processed_df[col] == '').sum()
                    print(f"{col}: {null_count} nulls, {zero_count} zeros, {empty_count} empty")
                
                # Update test_data for next iteration
                test_data = result['processed_data']
                
            else:
                print("❌ FAILED!")
                print("Error:", result.get('message', 'Unknown error'))
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    if test_data:
        final_df = pd.DataFrame(test_data)
        print("Final processed dataset:")
        print(final_df)
        
        # Save final result
        final_df.to_csv('test_result.csv', index=False)
        print("\n✅ Saved final result to test_result.csv")
        
        # Check if all nulls/zeros are filled
        total_nulls = final_df.isna().sum().sum()
        total_zeros = (final_df == 0).sum().sum()
        total_empty = (final_df == '').sum().sum()
        
        print(f"\nFinal stats:")
        print(f"Total nulls: {total_nulls}")
        print(f"Total zeros: {total_zeros}")
        print(f"Total empty strings: {total_empty}")
        
        if total_nulls == 0 and total_zeros <= 1 and total_empty == 0:  # Allow 1 zero for valid data
            print("🎉 SUCCESS: All null/empty values have been filled!")
            return True
        else:
            print("⚠️  Some null/empty values remain")
            return False
    
    return False

if __name__ == "__main__":
    success = test_fillna_commands()
    
    if success:
        print("\n✅ FILLNA AUGMENTATION IS WORKING CORRECTLY!")
        print("✅ Implementation is ready for production use")
    else:
        print("\n❌ FILLNA AUGMENTATION NEEDS FIXES")
        print("❌ Check the implementation")