from src.utilities.data_structures.lList import LList
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.strArr import StrArr
from src.utilities.objects.route import Route

def create_data_array(file_name: str, route: Route) -> ObjArr:
    with open(file_name, mode="r", encoding="utf-8") as file:
        #*Group all the data into a single string to avoid using lists
        content: str = file.read() #!Can we use built-in strings?

    EOF_reached: bool = False
    row_start: int = 89
    row_end: int = 90
    line_indices_list: LList = LList()
    while not EOF_reached:
        try:
            while content[row_end] != "\n":
                if row_end > 5000: #! If removed, it will take forever (in the future, it will be replaced for a time frame that will condition the last row to be checked)
                    raise IndexError
                row_end += 1
            if content[row_start + 21 : row_start + 23] in route.zones:
                #TODO: Implement a way to check the stations and not only the zone (we could have an array indicating what's the name associated to each zone code)
                # if content[row_start + 42 : row_start + 47] in route.stations_code:
                line_indices_list.add(row_start)
                line_indices_list.add(row_end)

        except IndexError:
            print("Reached EOF")
            EOF_reached = True
        row_start = row_end + 1
        row_end += 50 #*We can safely say each row will have more than 50 chrs

    data: ObjArr = ObjArr(len(line_indices_list)//2) #*Since there are an even number of end and start indices
    #*It will look like this: [date, time, zone, station, station access, device, entrances, exits]
    i: int = 0
    j: int = 0
    col_start: int = 0
    col_end: int = 0
    row_data: StrArr = StrArr(8)

    while i + 1 <  len(line_indices_list):
        while (content[line_indices_list[i] + col_end] != "," and content[line_indices_list[i] + col_end] != "\n"):
            col_end += 1
        #* It's a comma now
        row_data[j] = content[line_indices_list[i] + col_start: line_indices_list[i] + col_end] #* Doesn't include the comma
        j += 1
        if j == 8:
            data[i//2] = row_data
            row_data = StrArr(8) #*To avoid having a reference to the same array (shallow copy)
            i += 2 #* Go to the next start-index
            col_start = 0
            col_end = col_start + 5 #* Just to make it a bit more efficient, since the time will always be in the Hours:Minutes:Seconds format
            j = 0
        else:
            col_end += 1 #* Go one position past the comma
            col_start = col_end
    
    print("AAAA")
    for arr in data:
        print(i)
        print(arr)

    return data
