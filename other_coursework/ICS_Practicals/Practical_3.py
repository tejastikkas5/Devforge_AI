"""
Experiment No. 3: Implementation of Block Cipher — DES / AES

AIM:
To implement AES, a modern symmetric block cipher, for encrypting and decrypting data.

REQUIREMENTS:
Python 3.x with the pycryptodome library (pip install pycryptodome).
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def main():
    key = get_random_bytes(16)
    data = b"Confidential Data!"

    # Encryption using AES in CBC mode
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(data, AES.block_size))

    # Decryption using same key and cipher initialization vector (IV)
    decipher = AES.new(key, AES.MODE_CBC, cipher.iv)
    pt = unpad(decipher.decrypt(ct), AES.block_size)

    print("Plaintext       :", data.decode())
    print("Ciphertext (hex):", ct.hex())
    print("Decrypted       :", pt.decode())


if __name__ == "__main__":
    main()
