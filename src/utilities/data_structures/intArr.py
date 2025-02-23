import ctypes

from .boolArr import BoolArr

class IntArr:
    def __init__(self, capacity: int = 0):
        """
        Initializes an integer array with a specified capacity.

        Parameters
        ----------
        capacity : int, optional
            The maximum number of elements the array can hold (default is 0).

        Attributes
        ----------
        __capacity : int
            The maximum number of elements the array can hold.
        __size : int
            The current number of elements in the array.
        __assigned : BoolArr
            An instance of BoolArr to track assigned elements.
        __arr : ctypes.POINTER
            A pointer to the allocated memory for the array.

        Raises
        ------
        MemoryError
            If memory allocation fails.
        """
        self.__capacity: int = capacity
        self.__size: int = 0
        self.__assigned: BoolArr = BoolArr(capacity)
        self.__arr: ctypes.POINTER = ctypes.cast(
            ctypes.create_string_buffer(capacity * ctypes.sizeof(ctypes.c_int32)),
            ctypes.POINTER(ctypes.c_int32)
        ) #* Allocate memory using malloc to avoid using C's built-in arrays        
        if not self.__arr:
            raise MemoryError("Failed to allocate memory.")


    def __setitem__(self, index: int, value: int) -> None: #? If index is not given, should we default it to size of the array? Sounds useful
        """
        Sets the value at the specified index in the array.

        Parameters
        ----------
        index : int
            The index at which to set the value.
        value : int
            The value to set at the specified index.

        Raises
        ------
        TypeError
            If the value is not an integer.
        IndexError
            If the index is out of range.
        """
        if not isinstance(value, int):
            raise TypeError("This array only supports integers.")
        if 0 <= index < self.__capacity:
            if self.__assigned[index] == False: 
                self.__size += 1
                self.__assigned[index] = True
            self.__arr[index] = value
        else:
            raise IndexError("Index out of range")


    def __getitem__(self, index: int) -> int:
        """
        Retrieves the value at the specified index in the array.

        Parameters
        ----------
        index : int
            The index from which to retrieve the value.

        Raises
        ------
        IndexError
            If the index is out of range (negative or greater than the array's capacity).
        """
        if 0 <= index < self.__capacity:
            if self.__arr[index] is None:
                raise IndexError("Index has no assigned value")
            return self.__arr[index] #!Make sure this is legal
        raise IndexError("Index out of range")


    def __repr__(self) -> str:
        """
        Prints the array in the conventional notation
        `[1st element, 2nd element, ..., size-th element]`
        """
        repr: str = "["
        for i in range(self.__size - 1):
            repr += f"{self.__arr[i]}, "
        if self.__size > 0:
            repr += f"{self.__arr[self.__size - 1]}"
        repr += "]"
        return repr


    def __iter__(self):
        """
        Returns an iterator for the array.

        Yields
        ------
        int
            The next value in the array.
        """
        for i in range(self.__capacity):
            if self.__assigned[i]:
                yield self.__arr[i]


    def __contains__(self, value: int) -> bool:
        """
        Checks if the array contains the specified value.

        Parameters
        ----------
        value : int
            The value to check for in the array.

        Returns
        -------
        bool
            True if the value is found in the array, False otherwise.
        """
        for i in range(self.__capacity):
            if self.__assigned[i] and self.__arr[i] == value:
                return True
        return False


    def __len__(self) -> int:
        """Returns the size of the array"""
        return self.__size


    def __del__(self) -> None:
        """
        Frees the memory of the head pointer, since Python's garbage collector
        doesn't free C's pointers allocated in the heap
        """
        pass
        # ctypes.CDLL(None).free(self.__arr)