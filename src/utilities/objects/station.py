

class Station:
    def __init__(self, name: str, current_passangers: int = 0):
        """
        Initializes a new Station object.

        Parameters
        ----------
        name : str
            The name of the station.
        current_passangers : int, optional
            The initial number of passengers at the station. Defaults to 0.
        """

        self.__name: str = name
        self.num_passangers: int = current_passangers

    
    @property
    def name(self) -> str:
        return self.__name