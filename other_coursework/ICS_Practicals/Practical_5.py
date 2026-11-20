"""
Experiment No. 5: Diffie-Hellman Key Exchange Algorithm

AIM:
To implement Diffie-Hellman key exchange, allowing two parties to agree on a shared
secret over an insecure channel.

REQUIREMENTS:
Computer with Python 3.x and a text editor/IDE.
"""

def main():
    # Public parameters
    q, alpha = 23, 5

    # Private keys
    XA, XB = 6, 15

    # Public values exchanged
    YA = pow(alpha, XA, q)
    YB = pow(alpha, XB, q)

    # Computed shared secret key
    KA = pow(YB, XA, q)
    KB = pow(YA, XB, q)

    print("Public Prime (q):", q, ", Primitive Root (alpha):", alpha)
    print("Alice Private Key (XA):", XA, ", Bob Private Key (XB):", XB)
    print("YA:", YA, "YB:", YB)
    print("Shared Key (Alice):", KA, " Shared Key (Bob):", KB)


if __name__ == "__main__":
    main()
