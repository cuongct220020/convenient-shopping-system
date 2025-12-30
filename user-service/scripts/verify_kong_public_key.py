#!/usr/bin/env python3
"""
Script to verify if the RSA public key in user-service/secrets/jwt-public.pem 
matches the one configured in api-gateway/kong.dev.yml.
"""

import sys
import yaml
from pathlib import Path

def normalize_pem(pem_str):
    """Remove headers, footers, whitespace and newlines for comparison."""
    if not pem_str:
        return ""
    lines = pem_str.strip().splitlines()
    # Filter out header/footer lines if they exist
    content_lines = [line for line in lines if not line.startswith("---")]
    return "".join(content_lines).strip()

def verify_kong_key():
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    public_key_path = base_dir / "user-service" / "secrets" / "jwt-public.pem"
    kong_config_path = base_dir / "api-gateway" / "kong.dev.yml"

    print("=" * 60)
    print("🔍 Kong Public Key Verifier")
    print("=" * 60)

    # 1. Check if files exist
    if not public_key_path.exists():
        print(f"❌ Error: Public key not found at {public_key_path}")
        sys.exit(1)
    if not kong_config_path.exists():
        print(f"❌ Error: Kong config not found at {kong_config_path}")
        sys.exit(1)

    try:
        # 2. Load public key from disk
        print(f"📂 Reading local public key: {public_key_path.name}")
        local_pem = public_key_path.read_text()
        normalized_local = normalize_pem(local_pem)

        # 3. Load and parse Kong config
        print(f"📂 Reading Kong config: {kong_config_path.name}")
        with open(kong_config_path, "r") as f:
            kong_config = yaml.safe_load(f)

        # 4. Extract key from Kong config
        # Structure: consumers -> shopping-user-service -> jwt_secrets -> rsa_public_key
        kong_pem = None
        target_consumer = "shopping-user-service"
        
        consumers = kong_config.get("consumers", [])
        for consumer in consumers:
            if consumer.get("username") == target_consumer:
                jwt_secrets = consumer.get("jwt_secrets", [])
                if jwt_secrets:
                    # Taking the first secret
                    kong_pem = jwt_secrets[0].get("rsa_public_key")
                    break
        
        if not kong_pem:
            print(f"❌ Error: Could not find 'rsa_public_key' for consumer '{target_consumer}' in Kong config.")
            sys.exit(1)

        normalized_kong = normalize_pem(kong_pem)

        # 5. Compare
        if normalized_local == normalized_kong:
            print("\n✅ Success: Local public key and Kong Gateway config MATCH!")
            print("   Kong is using the correct public key for JWT verification.")
        else:
            print("\n❌ Failure: Local public key and Kong config DO NOT match!")
            print("   You need to update 'rsa_public_key' in api-gateway/kong.dev.yml")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        sys.exit(1)

    print("=" * 60)

if __name__ == "__main__":
    verify_kong_key()
