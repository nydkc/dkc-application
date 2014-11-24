#! /usr/bin/python

import random, string

LENGTH = 100

choices = string.digits + string.letters
secret_key = "".join( [random.choice(choices) for i in xrange(LENGTH)] )

print secret_key
