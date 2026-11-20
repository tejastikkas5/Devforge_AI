"""
Experiment No. 1: Implementation of Substitution Cipher

AIM:
To implement a Substitution (Caesar) Cipher for encrypting and decrypting a message.

REQUIREMENTS:
Computer with Python 3.x and a text editor/IDE.
"""

def encrypt(text, key):
    result = ""
    for c in text:
        if c.isupper():
            result += chr((ord(c) + key - 65) % 26 + 65)
        elif c.islower():
            result += chr((ord(c) + key - 97) % 26 + 97)
        else:
            result += c
    return result

def decrypt(text, key):
    return encrypt(text, -key)


if __name__ == "__main__":
    pt = "HELLO WORLD"
    ct = encrypt(pt, 3)
    print("Plaintext :", pt)
    print("Ciphertext:", ct)
    print("Decrypted :", decrypt(ct, 3))
