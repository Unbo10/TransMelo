from src.utilities.data_structures.lList import LList
from src.utilities.data_structures.intArr import IntArr
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_getter.data_array import create_data_array
from src.utilities.objects.route import Route
from src.utilities.objects.route_list import joint

#TODO: Implement a method that returns an object array containing the entries and exits from some stations passed as arguments of the create_data_array function. They should be entries and exits per minute
#*Stations will be implemented separately, since the amount of passangers in them varies


def sort_by_first_element(arr: ObjArr) -> ObjArr:
    """
    Sort an object array by the station name (the 4th element, index 3) of each element
    """
    n = len(arr)
    result = ObjArr(n)
    
    # First copy all elements to the result array
    for i in range(n):
        result[i] = arr[i]
    
    # Bubble sort implementation
    for i in range(n):
        # Last i elements are already in place, so we don't need to check them
        for j in range(0, n-i-1):
            # Compare the name of the stations (strings) from the 7th position onwards
            if result[j][3][7:] > result[j+1][3][7:]:
                # Swap the elements
                result[j], result[j+1] = result[j+1], result[j]
    
    return result


def clean_data_arr(start_time: int = 3, end_time: int = 4) -> ObjArr:
    joint_routes = joint()
    data_arr: ObjArr = create_data_array("data/20250211.csv", route=joint_routes, start_time=start_time, end_time=end_time, filter_entrances=False) #!The filter can be set to true if we are guaranteed there will be data for every 15-minute interval of time
    sorted_arr = sort_by_first_element(data_arr)
    # print(sorted_arr)

    clean_arr: ObjArr = ObjArr(len(joint_routes.station_names))
    for i in range(clean_arr.capacity):
        clean_arr[i] = LList()
    i: int = 0
    time_range: int = 0
    current_station_code: str = "06100"
    hour_tracker: str = data_arr[0][1][0:2]
    minute_tracker: str = "00"
    entrances: int = 0 #*[6]
    exits: int = 0 #*[7]
    time_elapsed: int = 0
    station_num: int = 0
    modulo_correction_entrances: int = 0
    modulo_correction_exits: int = 0

    #!ISSUE: Skipping the info of one station (doesn't seem to be the last one nor the first one)
    #!May be related to override.

    #*The clean array will store the entrances and exits of every station at
    #*any minute
    while i < len(sorted_arr):
        current_station_code = sorted_arr[i][3][1:6]
        time_elapsed = 0
        hour_tracker: str = data_arr[0][1][0:2]
        minute_tracker: str = "00"
        #*Traverse all the info of a station
        while i < len(sorted_arr) and sorted_arr[i][3][1:6] == current_station_code:
            #*Check how many devices are there for the station
            time_range = 0
            print(i)
            print(f"{hour_tracker}:{minute_tracker}")
            if int(minute_tracker) % 60 == 0 and minute_tracker != "00":
                minute_tracker = "00"
                hour_tracker = sorted_arr[i][1][0:2]
            # print(sorted_arr[i + time_range][1][0:5], f"{hour_tracker}:{minute_tracker}")
            while i + time_range < len(sorted_arr) and sorted_arr[i + time_range][1][0:5] == f"{hour_tracker}:{minute_tracker}":
                time_range += 1
            
            # print("AAA")
            #*Count the total number of entrances and exits recorded in the
            #*time period
            entrances = 0
            exits = 0
            for j in range(i, i + time_range):
                entrances += int(sorted_arr[j][6])
                exits += int(sorted_arr[j][7])
                # print(entrances, exits)

            #*(Assumption) Every person is equally-likely to board any of the
            #*six buses that are on average in each station and direction
            entrances = entrances // 6 + (entrances % 6)
            exits = exits // 6 + (exits % 6)
            print("Station", current_station_code, "Entrances", entrances, "Exits", exits, f"{hour_tracker}:{minute_tracker}")
            #*Extrapolate a 15-minute interval into 15 minutes
            for k in range(time_elapsed, time_elapsed + 15):
                entrances_and_exits: IntArr = IntArr(2)
                entrances_and_exits[0] += entrances // 15
                entrances_and_exits[1] += exits // 15
                # print(clean_arr.capacity, clean_arr)
                clean_arr[station_num].append(entrances_and_exits)

            #*(Assumption for optimization) In case the numbers are not
            #*divisible by 15
            if entrances >= 15:
                modulo_correction_entrances = 1
            else:
                modulo_correction_entrances = 0
            if exits >= 15:
                modulo_correction_exits = 1
            else:
                modulo_correction_exits = 0
            clean_arr[station_num][time_elapsed][0] = (entrances % 15) + modulo_correction_entrances
            clean_arr[station_num][time_elapsed][1] = (exits % 15) + modulo_correction_exits
            time_elapsed += 15
            minute_tracker = str(int(minute_tracker) + 15)

            i = i + time_range
        #*Once there's no more info about the station, proceed to the next one
        print(i)
        try:
            clean_arr[station_num].append(sorted_arr[i][3][7:])
        except IndexError:
            clean_arr[station_num].append(sorted_arr[i - 1][3][7:])
        station_num += 1
        
    for station in clean_arr:
        print("---")
        print(station)
    
if __name__ == "__main__":
    clean_data_arr() #! Temporary