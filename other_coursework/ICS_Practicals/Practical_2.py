"""
Experiment No. 2: Implementation of Transposition Cipher

AIM:
To implement a Columnar Transposition Cipher, which encrypts by rearranging character
positions rather than substituting them.

REQUIREMENTS:
Computer with Python 3.x and a text editor/IDE.
"""

def encrypt(msg, key):
    msg = msg.replace(" ", "").upper()
    while len(msg) % len(key):
        msg += "X"
    grid = [msg[i:i + len(key)] for i in range(0, len(msg), len(key))]
    order = sorted(range(len(key)), key=lambda k: key[k])
    return "".join(row[c] for c in order for row in grid)

def decrypt(cipher, key):
    num_rows = len(cipher) // len(key)
    order = sorted(range(len(key)), key=lambda k: key[k])
    
    # Reconstruct columns according to sorted key order
    cols = {}
    idx = 0
    for c in order:
        cols[c] = cipher[idx:idx + num_rows]
        idx += num_rows
    
    # Read row-wise
    msg = ""
    for r in range(num_rows):
        for c in range(len(key)):
            msg += cols[c][r]
    return msg


if __name__ == "__main__":
    key = "ZEBRA"
    plaintext = "MEET ME AFTER SCHOOL"
    ct = encrypt(plaintext, key)
    print("Plaintext :", plaintext)
    print("Key       :", key)
    print("Ciphertext:", ct)
    print("Decrypted :", decrypt(ct, key))
