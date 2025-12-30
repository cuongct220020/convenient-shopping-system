#!/usr/bin/env python3
"""
Script to generate RSA key pair for JWT authentication in user-service.

This script creates the required RSA private and public key files needed for 
RS256 JWT algorithm in the user-service secrets directory.
"""

import subprocess
import sys
from pathlib import Path


def generate_rsa_keys():
    """Generate RSA key pair for JWT authentication."""
    
    # Define the secrets directory path
    secrets_dir = Path(__file__).parent.parent / "secrets"
    
    # Create the secrets directory if it doesn't exist
    secrets_dir.mkdir(exist_ok=True)
    
    # Define key file paths
    private_key_path = secrets_dir / "jwt-private.pem"
    public_key_path = secrets_dir / "jwt-public.pem"
    
    print("=" * 60)
    print("🔐 RSA Key Generator for User-Service JWT Authentication")
    print("=" * 60)
    
    # Check if key files already exist
    if private_key_path.exists() or public_key_path.exists():
        print(f"⚠️  Warning: Key files already exist!")
        print(f"   - Private key: {private_key_path}")
        print(f"   - Public key: {public_key_path}")
        
        response = input("Do you want to overwrite them? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            return
    
    try:
        # Generate private key
        print(f"📝 Generating private key: {private_key_path}")
        subprocess.run([
            "openssl", "genpkey", 
            "-algorithm", "RSA", 
            "-out", str(private_key_path), 
            "-pkeyopt", "rsa_keygen_bits:2048"
        ], check=True, capture_output=True)
        
        # Generate public key from private key
        print(f"🔑 Generating public key: {public_key_path}")
        subprocess.run([
            "openssl", "rsa", 
            "-in", str(private_key_path), 
            "-pubout", 
            "-out", str(public_key_path)
        ], check=True, capture_output=True)
        
        # Set appropriate permissions for private key
        private_key_path.chmod(0o600)  # Read/write for owner only
        
        print("\n✅ RSA key pair generated successfully!")
        print(f"   Private key: {private_key_path}")
        print(f"   Public key: {public_key_path}")
        print("\n📋 These files are now ready for use with the RS256 JWT algorithm.")
        print("   Make sure your .env file has JWT_ALGORITHM=RS256")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating RSA keys: {e}")
        print("Make sure you have OpenSSL installed on your system.")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ OpenSSL is not found in your system. Please install OpenSSL first.")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    generate_rsa_keys()