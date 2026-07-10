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

        # Update .env file
        update_env_file(public_key_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating RSA keys: {e}")
        print("Make sure you have OpenSSL installed on your system.")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ OpenSSL is not found in your system. Please install OpenSSL first.")
        sys.exit(1)
    
    print("=" * 60)


def update_env_file(public_key_path):
    """Update the root .env file with the new public key."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    if not env_path.exists():
        print(f"⚠️  Warning: Root .env file not found at {env_path}")
        print("   Skipping .env update.")
        return

    try:
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
            
        # Format key for .env (preserving newlines in a quoted string)
        env_key_value = f'JWT_RSA_PUBLIC_KEY="{public_key}"'
        
        # Read existing .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        new_lines = []
        key_found = False
        
        for line in lines:
            if line.strip().startswith("JWT_RSA_PUBLIC_KEY="):
                new_lines.append(env_key_value + "\n")
                key_found = True
            else:
                new_lines.append(line)
        
        if not key_found:
            if new_lines and not new_lines[-1].endswith('\n'):
                 new_lines.append('\n')
            new_lines.append(env_key_value + "\n")
            
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
        print(f"✅ Updated {env_path} with new JWT_RSA_PUBLIC_KEY")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")


if __name__ == "__main__":
    generate_rsa_keys()