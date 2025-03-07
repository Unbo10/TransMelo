from src.utilities.objects.route import Route

class Bus:
    def __init__(self, id: str, route: Route = None, capacity: int = 250):
        self.__id: str = id
        self.route: str = route
        self.capacity: int = capacity
        self.number_of_passangers: int = 0
        self.location: str = None
        self.distance_travelled: int = 0 #* To know how much distance has it travelled between two stations

    @property
    def id(self) -> str:
        return self.__id


    def is_full(self) -> bool:
        if self.__number_of_passangers == self.__capacity:
            return True
        return False