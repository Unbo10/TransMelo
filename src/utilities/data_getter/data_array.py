from src.utilities.data_structures.lList import LList
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.strArr import StrArr
from src.utilities.objects.route import Route

def get_zone_name(zone_code: str, route: Route) -> str:
    """
    Retrieves the index of the given zone code from the route's zone codes.
    Args:
        zone_code (str): The zone code to search for.
        route (Route): The route object containing zone codes.
    Returns:
        str: The index of the zone code in the route's zone codes.
    Raises:
        ValueError: If the zone code is not found in the route's zone codes.
    """

    for i in range(len(route.zone_codes)):
        if int(zone_code) == route.zone_codes[i]:
            return i
    raise ValueError(f"Code {zone_code} not found in {route.zone_codes}")


def create_data_array(file_name: str, route: Route, start_time: int, end_time: int, filter_stations: bool = True, filter_entrances: bool = True) -> ObjArr:
    """
    Creates an ObjArr containing data parsed from a file, filtered by a given route and time range.
    
    Parameters
    ----------
    file_name : str
        The name of the file to read data from.
    route : Route
        The route object containing zones and stations to filter the data.
    start_time : int
        The starting time for filtering data (inclusive).
    end_time : int
        The ending time for filtering data (exclusive).
    filter_stations: bool, optional
        If True, filters out data that doesn't correspond to the route's stations (default is True).
    filter_entrances : bool, optional
        If True, filters out data entries where the number of entrances is 0 (default is True).
    Returns
    -------
    ObjArr
        An ObjArr containing the filtered data.
    Raises
    ------
    ValueError
        If the ending time is not greater than the starting time.
    """
    with open(file_name, mode="r", encoding="utf-8") as file:
        #*Group all the data into a single string to avoid using lists
        content: str = file.read() #!Can we use built-in strings?

    if end_time <= start_time:
        raise ValueError("Ending time must be greater than starting time")
    EOF_reached: bool = False
    row_start: int = 89
    row_end: int = 90
    line_indices_list: LList = LList()
    current_time: int = 0
    while not EOF_reached:
        #! Take start_time into account
        current_time: int = int(content[row_start + 11: row_start + 13]) #*24-hour format
        current_zone: str = int(content[row_start + 21 : row_start + 23]) #*Two-digit format
        try:
            while content[row_end] != "\n":
                if current_time > 0 and current_time >= end_time:
                    EOF_reached = True
                else:
                    pass
                row_end += 1
        except IndexError:
            EOF_reached = True
        if start_time <= current_time < end_time:
            if current_zone in route.zone_codes:
                if filter_stations == True:
                    zone_name_length: int = len(route.zone_names[get_zone_name(current_zone, route)])
                    #*19 is the distance from the first position of a row to the second comma,
                    #*and three is to account for the comma and the parenthesis that follow
                    #*each zone name
                    station_code: int = content[row_start + 19 + zone_name_length + 3: row_start + 19 + zone_name_length + 8]
                    if station_code in route.station_codes:
                        line_indices_list.add(row_start)
                        line_indices_list.add(row_end)
                        # print(content[row_start: row_end])
                    else:
                        pass
                else:
                    line_indices_list.add(row_start)
                    line_indices_list.add(row_end)
        else:
            pass
        row_start = row_end + 1
        #*We can safely say each row will have more than 50 chrs
        row_end += 50

    data: ObjArr = ObjArr(len(line_indices_list)//2) #*Since there are an even number of end and start indices
    #*It will look like this: [date, time, zone, station, station access, device, entrances, exits]
    i: int = 0
    j: int = 0
    k: int = 0
    col_start: int = 0
    col_end: int = 0
    row_data: StrArr = StrArr(8)
    # print(line_indices_list)

    while i + 1 <  len(line_indices_list):
        while (content[line_indices_list[i] + col_end] != "," and content[line_indices_list[i] + col_end] != "\n"):
            col_end += 1
        row_data[j] = content[line_indices_list[i] + col_start: line_indices_list[i] + col_end]
        j += 1
        if j == 8:
            #*Reached the last row
            if row_data[6] == "0" and filter_entrances == True:
                #*Ignore data entries where the number of entrances is 0
                pass
            else:
                # print(row_data)
                data[k] = row_data
                k += 1
            row_data = StrArr(8) #*To avoid having a reference to the same array (shallow copy)
            col_start = 0
            col_end = col_start + 7 #* Just to make it a bit more efficient, since the time will always be in the Hours:Minutes:Seconds format
            i += 2 #* Go to the next start-index
            j = 0
        else:
            col_end += 1 #* Go one position past the comma
            col_start = col_end


    return data
