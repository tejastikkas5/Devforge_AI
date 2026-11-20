#include <stdio.h>
#include "utils.h"

int main() {
    char test_cases[][100] = {"A man a plan a canal Panama", "Hello World", "Madam", "No lemon, no melon"};
    bool expected_results[] = {true, false, true, false};

    for (int i = 0; i < 4; i++) {
        if (is_palindrome(test_cases[i])) {
            printf("Test case %d passed.\n", i + 1);
        } else {
            printf("Test case %d failed.\n", i + 1);
        }
    }

    return 0;
}