"""a console to test inputs and outputs in the command line to ensure compatibillity with the dart AES implementation
not used in the server"""

from src.aes import AESGCM


while True:
    password = input("Enter password: ")
    action = input("Encrypt or decrypt? (e/d): ").lower()
    if action == "e":
        plaintext = input("Enter plaintext: ")
        cipher = AESGCM(password)
        encrypted = cipher.encrypt(plaintext)
        print(f"Encrypted: {encrypted}")
    elif action == "d":
        ciphertext = input("Enter ciphertext: ")
        cipher = AESGCM(password)
        try:
            decrypted = cipher.decrypt(ciphertext)
            print(f"Decrypted: {decrypted}")
        except ValueError as e:
            print(f"Decryption failed: {e}")
    else:
        break
