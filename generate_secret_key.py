import secrets

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    return secrets.token_hex(length//2)

# Generate a secret key with default length (32 bytes)
secret_key = generate_secret_key()

print("Generated Secret Key:", secret_key)
