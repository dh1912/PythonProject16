import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify_all_tasks import *

test_task1()
test_task2()
test_task3()
test_task4()
test_task5()

print("ALL TESTS PASSED")