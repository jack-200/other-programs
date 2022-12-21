import timeit

NUMBER_OF_EXECUTIONS = 1000000


def code_to_test1():
    text = 1234567890
    text = str(text)


def code_to_test2():
    text = 1234567890
    text = f"{text}"


time1 = timeit.timeit(stmt = code_to_test1, number = NUMBER_OF_EXECUTIONS)
time2 = timeit.timeit(stmt = code_to_test2, number = NUMBER_OF_EXECUTIONS)

print(f"time1: {time1}\ntime2: {time2}")

# print out the variable that contains the fastest time
if (time1, time2).index(min(time1, time2)) == 0:
    print("fastest: time1")
else:
    print("fastest: time2")
