from src.utilities.data_structures.strArr import StrArr

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
        self.__stations_code: StrArr = stations_code_list
        self.__stations_name: StrArr = stations_name_list
        self.__zones: StrArr = zones


    @property
    def identifier(self) -> str:
        """Getter for the route's identifier (ID)"""
        return self.__identifier
    
    
    @property
    def stations_code(self) -> StrArr:
        """Getter for the route's stations code list"""
        return self.__stations_code


    @property
    def stations_name(self) -> StrArr:
        """Getter for the route's stations name list"""
        return self.__stations_name
    

    @property
    def zones(self) -> StrArr:
        """Getter for the route's zones"""
        return self.__zones