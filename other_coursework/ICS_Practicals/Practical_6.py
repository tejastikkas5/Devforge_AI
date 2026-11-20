"""
Experiment No. 6: Cryptographic Hash Functions (SHA-1, SHA-256, SHA-3)

AIM:
To implement SHA-1, SHA-256 and SHA-3 to generate message digests of given input data.

REQUIREMENTS:
Python 3.x with the built-in hashlib library.
"""

import hashlib


def main():
    data = "Information and Cyber Security".encode()

    print("Input Text:", "Information and Cyber Security")
    print("SHA-1    :", hashlib.sha1(data).hexdigest())
    print("SHA-256  :", hashlib.sha256(data).hexdigest())
    print("SHA3-256 :", hashlib.sha3_256(data).hexdigest())


if __name__ == "__main__":
    main()
