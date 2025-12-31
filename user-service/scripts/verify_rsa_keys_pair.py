#!/usr/bin/env python3
"""
Script to verify if the RSA private and public keys in user-service/secrets match.

This script uses the cryptography library to load the private key, derive its 
public key, and compare it with the public key on disk.
"""

import sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def verify_keys():
    # Define paths
    secrets_dir = Path(__file__).parent.parent / "secrets"
    private_key_path = secrets_dir / "jwt-private.pem"
    public_key_path = secrets_dir / "jwt-public.pem"

    print("=" * 60)
    print("🔍 RSA Key Pair Verifier")
    print("=" * 60)

    # 1. Check if files exist
    if not private_key_path.exists():
        print(f"❌ Error: Private key not found at {private_key_path}")
        sys.exit(1)
    if not public_key_path.exists():
        print(f"❌ Error: Public key not found at {public_key_path}")
        sys.exit(1)

    try:
        # 2. Load private key
        print(f"📂 Loading private key: {private_key_path.name}")
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )

        if not isinstance(private_key, rsa.RSAPrivateKey):
            print("❌ Error: Key is not an RSA private key.")
            sys.exit(1)

        # 3. Derive public key from private key
        derived_public_key = private_key.public_key()
        derived_public_pem = derived_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # 4. Load public key from disk
        print(f"📂 Loading public key: {public_key_path.name}")
        with open(public_key_path, "rb") as key_file:
            public_pem_on_disk = key_file.read()

        # Normalize PEMs for comparison (strip whitespace/newlines)
        def normalize_pem(pem_bytes):
            return b"".join(pem_bytes.strip().split())

        # 5. Compare
        if normalize_pem(derived_public_pem) == normalize_pem(public_pem_on_disk):
            print("\n✅ Success: Private and Public keys MATCH perfectly!")
            print("   These keys are a valid pair and ready for JWT RS256.")
        else:
            print("\n❌ Failure: Private and Public keys DO NOT match!")
            print("   The public key on disk was not derived from this private key.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        sys.exit(1)

    print("=" * 60)

if __name__ == "__main__":
    verify_keys()
