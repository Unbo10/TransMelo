"""
This module provides the mixture between using c 
and python in order to create our own data structures
"""
import ctypes


class BoolArr:
    """
    A boolean array class that uses a C array of booleans to store the values.
    The array can be initialized with a given capacity, and the values can be
    set and retrieved using the `__setitem__` and `__getitem__` methods.
    """
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
            ctypes.create_string_buffer(capacity * ctypes.sizeof(ctypes.c_bool)),
            ctypes.POINTER(ctypes.c_bool)
        ) #*Allocate memory to the array positions and point the pointer
        #*to the first one
        self.__capacity: int = capacity
        for element in range(capacity):
            self.__arr[element] = False

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
            if value == 1:
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
        raise IndexError("Index out of range")


    def __repr__(self) -> str:
        """
        Prints the array in the conventional notation
        `[1st element, 2nd element, ..., size-th element]`
        """
        elements: str = "["
        for element in range(self.__capacity - 1):
            elements += f"{self.__arr[element]}, "
        if self.__capacity > 0:
            elements += f"{self.__arr[self.__capacity - 1]}"
        elements += "]"
        return elements


    def __len__(self) -> int:
        """
        Returns the capacity of the array (by default, all positions are
        set to `False`)
        """
        return self.__capacity
    def __del__(self) -> None:
        """Frees the memory of the head pointer"""
        # No need to manually free memory allocated by ctypes.create_string_buffer
        pass


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
