"""
Experiment No. 4: Simulation of RSA Algorithm

AIM:
To implement the RSA public-key algorithm for key generation, encryption and decryption.

REQUIREMENTS:
Computer with Python 3.x and a text editor/IDE.
"""

from math import gcd


def modinv(e, phi):
    for d in range(2, phi):
        if (e * d) % phi == 1:
            return d
    return None


def main():
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    while gcd(e, phi) != 1:
        e += 2
    d = modinv(e, phi)

    M = 65
    C = pow(M, e, n)

    print("Public Key :", (e, n), " Private Key:", (d, n))
    print("Original M :", M)
    print("Encrypted  :", C, " Decrypted:", pow(C, d, n))


if __name__ == "__main__":
    main()
