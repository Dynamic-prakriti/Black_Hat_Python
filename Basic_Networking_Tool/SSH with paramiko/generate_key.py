import paramiko

key = paramiko.RSAKey.generate(2048)
private_key_file = "test_rsa.key"

# Save private key
with open(private_key_file, "w") as private_file:
    key.write_private_key_file(private_file)

# Save public key
with open(private_key_file + ".pub", "w") as public_file:
    public_file.write(f"{key.get_name()} {key.get_base64()}")
    
print(f"RSA keys generated: {private_key_file} and {private_key_file}.pub")
