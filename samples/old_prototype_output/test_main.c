#include <stdio.h>
#include "main.h"

int main() {
    char input[100];
    printf("Enter a string: ");
    scanf("%s", input);
    if (is_palindrome(input)) {
        printf("The string is a palindrome.\n");
    } else {
        printf("The string is not a palindrome.\n");
    }
    return 0;
}