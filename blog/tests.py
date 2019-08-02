from django.test import TestCase

# Create your tests here.
from collections import Counter
result = {}
for i in set(arr):
    result[i] = arr.count(i)
    print(result)