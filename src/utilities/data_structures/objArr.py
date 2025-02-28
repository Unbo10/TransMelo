import ctypes

class ObjArr:
    def __init__(self, capacity: int = 0):
        """
        Initializes a new instance of the dynamic array with a specified
        capacity.

        Parameters:
        -----------
        capacity: int
            The initial capacity of the dynamic array (default is 0).

        Raises:
        -------
        MemoryError
            If memory allocation fails.

        Attributes:
        -----------
        __capacity: int
            The maximum number of elements the array can hold.
        __size: int
            The current number of elements in the array.
        __arr: ctypes.POINTER
            A pointer to the allocated memory for the array elements.
        """

        self.__capacity: int = capacity
        self.__size: int = 0
        self.__arr = ctypes.cast(
            (ctypes.py_object * capacity)(),
            ctypes.POINTER(ctypes.py_object)
        )
        #? py_obj is about 7 times the capacity of a c_int
        #? stores any type of object, so it can be treated as a list
        if not self.__arr:
            raise MemoryError("Failed to allocate memory.")

        #*Initialize all elements to None (required due to ctypes.py_object
        #*not being handled by ctypes by default, and for the reference
        #*handling implementation)
        for i in range(capacity):
            #* To check if there's a free space
            self.__arr[i] = None 


    def __setitem__(self, index: int, value: any) -> None:
        """
        Sets the value at the specified index in the array.

        Parameters:
        -----------
        index: int
            The index at which to set the value.
        value: any
            The value to set at the specified index.

        Raises:
        -------
        IndexError
            If the index is out of range.
        """
        if 0 <= index < self.__capacity:
            #*Decrease reference count for the old object before replacing (not managed by Python's garbage collector)
            if self.__arr[index] is None:
                self.__size += 1
            self.__arr[index] = value #!Make sure this is legal (arguably it is, since it's just an operator and how Python manages pointer dereferencing and arithmetic)
        else:
            raise IndexError("Index out of range")


    def __getitem__(self, index: int) -> any:
        """
        Retrieves the value at the specified index in the array.

        Parameters:
        -----------
        index: int
            The index from which to retrieve the value.

        Raises:
        -------
        IndexError
            If the index is out of range (negative or greater than the
            array's size).
        """
        if 0 <= index < self.__size:
            return self.__arr[index]
        raise IndexError("Index out of range")


    def __repr__(self) -> str:
        """
        Prints the array in the conventional notation
        `[1st element, 2nd element, ..., size-th element]`. If the elements
        don't have an implementation of `__repr__`, it will default to
        Python's
        """
        repr: str = "["
        for i in range(self.__size - 1):
            if self.__arr[i] is not None:
                repr += f"{self.__arr[i]}, "
        if self.__size > 0 and self.__arr[self.__size - 1] is not None:
            repr += f"{self.__arr[self.__size - 1]}"
        repr += "]"
        return repr
    

    def __iter__(self) -> any:
        for i in range(self.__size):
            if self.__arr[i] is not None:
                yield self[i]


    def __eq__(self, other: 'ObjArr') -> bool:
        """
        Checks if this array is equal to another array.

        Parameters
        -----------
        other: ObjArr
            The other array to compare with.

        Returns
        --------
        bool
            True if the arrays are equal, False otherwise.
        """
        if not isinstance(other, ObjArr):
            return False
        if self.__size != other.__size:
            return False
        for i in range(self.__size):
            if self.__arr[i] != other.__arr[i]:
                return False
        return True


    def __len__(self) -> int:
        """Returns the size of the array"""
        return self.__size


    def __del__(self) -> None:
        """
        Frees the memory of the head pointer
        """
        #*No need to use ctype since Python objects are being stored in the
        #*array
        del self.__arr
    
    