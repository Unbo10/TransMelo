from src.utilities.data_structures.strArr import StrArr
from src.utilities.data_structures.intArr import IntArr

class Route:
    def __init__(self, id: str, stations_code_list: StrArr, stations_name_list: StrArr, zones: StrArr) -> None:
        """
        Initializes a Route object.

        Parameters
        ----------
        id : str
            The unique identifier for the route.
        stations_code_list : StrArr
            A list of station codes associated with the route.
        stations_name_list : StrArr
            A list of station names associated with the route.
        """
        self.__identifier: str = id
        self.__station_codes: StrArr = stations_code_list
        self.__station_names: StrArr = stations_name_list
        self.__zone_codes: IntArr = IntArr(len(zones))
        self.__zone_names: StrArr = StrArr(len(zones))
        for i in range(len(zones)):
            self.__zone_names[i] = zones[i]
            self.__zone_codes[i] = int(zones[i][1:3]) #*Gets only the number


    @property
    def identifier(self) -> str:
        """Getter for the route's identifier (ID)"""
        return self.__identifier
    
    
    @property
    def station_codes(self) -> StrArr:
        """Getter for the route's stations code array"""
        return self.__station_codes


    @property
    def station_names(self) -> StrArr:
        """Getter for the route's stations name array"""
        return self.__station_names
    

    @property
    def zone_codes(self) -> IntArr:
        """Getter for the route's zone codes array"""
        return self.__zone_codes
    

    @property
    def zone_names(self) -> IntArr:
        """Getter for the route's zone names array"""
        return self.__zone_names
    

    def __repr__(self) -> str:
        return f"Route {self.__identifier} with stations {self.__station_names}, and zones {self.__zone_names}"
