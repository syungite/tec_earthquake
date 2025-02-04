import math
def timelist(start_time, end_time):
    timelist = [chr(i+97) for i in range(math.floor(start_time), math.ceil(end_time))]
    print(timelist)

if __name__ == '__main__':
    timelist(4.5, 5.8)