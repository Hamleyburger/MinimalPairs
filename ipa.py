# -*- coding: utf-8 -*-


mystring = "ʁ"
urstring = "i"

print("I like '{}', but '{}' is also okay".format(mystring, urstring))

print(urstring)

a = "d"
b = "d"

print("the {} and {} look the same, but is it the truth?".format(a, b))

istrue = a == b

print("It is {}".format(istrue))

rovhul = u"ʁœwhɔl"
bovhul = u"bœwhɔl"

differences = 0

for i, char in enumerate(rovhul):
    print(u"{}: {} - {}".format(i, char, bovhul[i]))
    if char != bovhul[i]:
        differences += 1
        print(u"{} is not {}".format(char, bovhul[i]))
