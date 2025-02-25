import ctypes

class StrArr:
    def __init__(self, capacity: int):
        """
        Initializes a new instance of an array of strings with a specified
        capacity.
        
        Parameters
        ----------
        capacity : int
            The maximum number of elements that the array can hold.
        """

        self.__capacity: int = capacity
        self.__size: int = 0
        
        #*Allocate a capacity-long block of memory to hold char pointers
        self.__arr = (ctypes.POINTER(ctypes.c_char) * capacity)()
        
        #*Initialize all elements to None
        for i in range(capacity):
            self.__arr[i] = None


    def __setitem__(self, index: int, value: str) -> None:
        """
        Sets the value at the specified index in the array.
        
        Parameters
        ----------
        index : int
            The index at which the value should be set.
        value : str
            The string value to set at the specified index.
        
        Raises
        ------
        IndexError
            If the index is out of bounds.
        
        Notes
        -----
        If there is already a value at the specified index, it will be replaced.
        The size of the array is updated if the index is greater than or equal to the current size.
        """
        if not (0 <= index < self.__capacity):
            raise IndexError("Index out of bounds.")
        
        #*Allocate memory using create_string_buffer
        encoded_value = value.encode("utf-8")
        str_buffer = ctypes.create_string_buffer(encoded_value)

        if index >= self.__size:
            self.__size = index + 1

        # Store pointer in the array
        self.__arr[index] = ctypes.cast(str_buffer, ctypes.POINTER(ctypes.c_char))


    def __getitem__(self, index: int) -> str:
        """
        Retrieves the string at the specified index in the array.
        
        Parameters
        ----------
        index : int
            The index of the string to retrieve.
            
        Returns
        -------
        str
            The string at the specified index. Returns an empty string if the index is uninitialized.
            
        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        if not (0 <= index < self.__capacity):
            raise IndexError("Index out of bounds.")

        if not self.__arr[index]:
            return ""

        return ctypes.cast(self.__arr[index], ctypes.c_char_p).value.decode("utf-8")


    def append(self, value: str) -> None:
        """
        Appends a value to the end of the array if there is enough capacity.
        
        Parameters
        ----------
        value : str
            The string value to append to the array.
        
        Raises
        ------
        MemoryError
            If there is not enough space in the array to append the value.
        """
        if self.__size < self.__capacity:
            self[self.__size] = value
            self.__size += 1
        else:
            raise MemoryError("Not enough space in the array")


    def __len__(self) -> int:
        return self.__size


    def __iter__(self):
        """
        Iterates over the elements of the StrArr instance, yielding non-None
        values.

        Yields
        ------
        str
            The next non-None element in the StrArr instance.
        """
        for i in range(self.__size):
            if self.__arr[i] is not None:
                yield self[i]


    def __contains__(self, value: str) -> bool:
        """
        Checks if the given value is present in the array.
        
        Parameters
        ----------
        value : str
            The string value to search for in the array.
        
        Returns
        -------
        bool
            True if the value is found in the array, False otherwise.
        """
        for i in range(self.__size):
            if self.__arr[i] and ctypes.cast(self.__arr[i], ctypes.c_char_p).value.decode("utf-8") == value:
                return True
        return False


    def __repr__(self) -> str:
        """
        Returns a string representation of the StrArr object.
        Just like you would expect with a list of strings, it returns a string
        with the format `['str1', 'str2', ..., 'strk']`, where the i-th string
        will be null if the i-th string is `None`.

        Returns
        -------
        str
            A string representation of the array.
        """
        repr_str = "["
        for i in range(self.__size):
            if self.__arr[i]:
                str_value = ctypes.cast(self.__arr[i], ctypes.c_char_p).value.decode("utf-8")
                repr_str += f'\'{str_value}\''
            else:
                repr_str += "NULL"
            
            if i < self.__size - 1:
                repr_str += ", "
        repr_str += "]"
        return repr_str


def __del__(self) -> None:
    #*Free each string buffer that was allocated
    for i in range(self.__capacity):
        if self.__arr[i] is not None:
            #*Setting to none is equivalent to decreasing the reference count
            #*of the object (so that it can be collected by Python's garbage)
            self.__arr[i] = None

    self.__arr = None
