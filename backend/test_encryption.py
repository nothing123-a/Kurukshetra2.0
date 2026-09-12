#!/usr/bin/env python3
"""
Test encryption functionality with dummy data
"""
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from privacy_security import PrivacySecurityManager

def test_encryption():
    print("🧪 Testing Encryption with Dummy Data")
    print("=" * 50)
    
    # Create dummy data
    dummy_data = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
        'Email': ['john@email.com', 'jane@email.com', 'bob@email.com', 'alice@email.com'],
        'Phone': ['123-456-7890', '987-654-3210', '555-123-4567', '444-987-6543'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 70000, 55000]
    })
    
    print("📊 Original Data:")
    print(dummy_data)
    print()
    
    # Initialize privacy manager
    privacy_manager = PrivacySecurityManager()
    
    # Test encryption on selected columns
    privacy_config = {
        'columns': ['Name', 'Email', 'Phone'],
        'method': 'hash'
    }
    
    print(f"🔒 Applying encryption to columns: {privacy_config['columns']}")
    print(f"🔐 Method: {privacy_config['method']}")
    print()
    
    # Apply encryption
    encrypted_data = privacy_manager.apply_privacy_protection(dummy_data.copy(), privacy_config)
    
    print("🔐 Encrypted Data:")
    print(encrypted_data)
    print()
    
    # Verify encryption
    print("✅ Encryption Verification:")
    for col in privacy_config['columns']:
        original_values = dummy_data[col].tolist()
        encrypted_values = encrypted_data[col].tolist()
        
        print(f"Column: {col}")
        print(f"  Original: {original_values[0]}")
        print(f"  Encrypted: {encrypted_values[0]}")
        print(f"  Is Encrypted: {'ENC_' in str(encrypted_values[0]) or 'MASK_' in str(encrypted_values[0])}")
        print()
    
    # Test masking
    print("🎭 Testing Masking Method:")
    privacy_config_mask = {
        'columns': ['Phone'],
        'method': 'mask'
    }
    
    masked_data = privacy_manager.apply_privacy_protection(dummy_data.copy(), privacy_config_mask)
    print(f"Original Phone: {dummy_data['Phone'].iloc[0]}")
    print(f"Masked Phone: {masked_data['Phone'].iloc[0]}")
    print()
    
    return encrypted_data, masked_data

if __name__ == "__main__":
    test_encryption()