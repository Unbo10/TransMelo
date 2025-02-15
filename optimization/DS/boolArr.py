import ctypes

class BoolArr:
    def __init__(self, capacity: int = 0):
        """
        Initializes a boolean array with a given capacity.

        Parameters:
        -----------
        - capacity : int, optional
            The number of boolean elements the array can hold (default is 0).

        Raises:
        -------
        - MemoryError
            If memory allocation fails.

        Attributes:
        -----------
        __capacity: int
            The maximum number of elements the array can hold, equal to the
            current number of elements too (default is 0).
        __arr: ctypes.POINTER
            A pointer to the allocated memory for the array elements.
        """
        self.__arr: ctypes.POINTER = ctypes.cast(
            ctypes.CDLL(None).malloc(capacity * ctypes.sizeof(ctypes.c_bool)),
            ctypes.POINTER(ctypes.c_bool)
        ) #*Allocate memory to the array positions and point the pointer
        #*to the first one
        self.__capacity: int = capacity
        
        for i in range(capacity):
            self.__arr[i] = False

    
    def __setitem__(self, index: int, value: bool) -> None:
        """
        Sets the value at the specified index in the array. It casts 
        zeros (`0`) and ones (`1`) into their boolean equivalents in case
        `value` is an integer.

        Parameters:
        -----------
        - index : int
            The index at which to set the value.
        - value : bool or int
            The value to set at the specified index.

        Raises:
        -------
        - TypeError
            If the value is not a boolean, 1 or 0.
        - IndexError
            If the index is out of range.
        """
        if isinstance(value, int):
            if (value == 1):
                if 0 <= index < self.__capacity:
                    self.__arr[index] = True
                else:
                    raise IndexError("Index out of range")
            elif value == 0:
                if 0 <= index < self.__capacity:
                    self.__arr[index] = False
                else:
                    raise IndexError("Index out of range")
            else:
                raise TypeError("Incorrect type. Only supports booleans")
        elif isinstance(value, bool):
            if 0 <= index < self.__capacity:
                self.__arr[index] = value
            else:
                raise IndexError("Index out of range")
        else:
            raise TypeError("Incorrect type. Only supports booleans")
        

    def __getitem__(self, index: int) -> bool:
        """
        Retrieves the value at the specified index in the array.

        Parameters:
        -----------
        - index : int
            The index from which to retrieve the value.

        Raises:
        -------
        - IndexError
            If the index is out of range (negative or greater than the array's size).
        """
        if 0 <= index < self.__capacity:
            return self.__arr[index]
        else:
            raise IndexError("Index out of range")


    def __repr__(self) -> str:
        """
        Prints the array in the conventional notation
        `[1st element, 2nd element, ..., size-th element]`
        """
        repr: str = "["
        for i in range(self.__capacity - 1):
            repr += f"{self.__arr[i]}, "
        if self.__capacity > 0:
            repr += f"{self.__arr[self.__capacity - 1]}"
        repr += "]"
        return repr


    def __len__(self) -> int:
        """
        Returns the capacity of the array (by default, all positions are
        set to `False`)
        """
        return self.__capacity
    

    def __del__(self) -> None:
        """Frees the memory of the head pointer"""
        ctypes.CDLL(None).free(self.__arr)


if __name__ == "__main__":
    empty_arr: BoolArr = BoolArr()
    print("Empty:", empty_arr)
    arr: BoolArr = BoolArr(4)
    print("Example array:")
    for i in range(3):
        print(arr[i])
        arr[i] = True
    print("Capacity:", len(arr))
    print(arr)