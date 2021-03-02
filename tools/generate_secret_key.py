#!/usr/bin/env python3

import argparse
import random
import string


def secret_key_of_length(length):
    choices = string.digits + string.ascii_letters
    secret_key = "".join([random.choice(choices) for _ in range(length)])
    return secret_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", "-l", type=int, default=101)
    args = parser.parse_args()

    print(secret_key_of_length(args.length))
