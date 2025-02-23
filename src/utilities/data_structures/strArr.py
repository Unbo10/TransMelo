import ctypes

class StrArr:
    def __init__(self, capacity: int):
        self.__capacity: int = capacity
        self.__size: int = 0

        self.malloc = ctypes.pythonapi.malloc
        self.free = ctypes.pythonapi.free
        self.malloc.restype = ctypes.c_void_p  # Ensure malloc returns a void pointer
        self.free.argtypes = [ctypes.c_void_p]  # Ensure free accepts a void pointer

        #*Allocate memory for char** (array of char* pointers)
        self.__arr = ctypes.cast(
            self.malloc(capacity * ctypes.sizeof(ctypes.POINTER(ctypes.c_char))),
            ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
        )
        if not self.__arr:
            raise MemoryError("Failed to allocate memory for StrArr.")

        #*Initialize all elements to NULL
        for i in range(capacity):
            self.__arr[i] = None

    def __setitem__(self, index: int, value: str) -> None:
        """
        Sets the value at the specified index in the array.

        Parameters
        ----------
        index : int
            The index at which to set the `value`.
        value : str
            The value to set at the specified index.

        Raises
        ------
        MemoryError
            If it was not possible to allocate memory for `value`.
        IndexError
            If the index is out of range.
        """
        if not (0 <= index < self.__capacity):
            raise IndexError("Index out of bounds.")

        if self.__arr[index] is not None:
            self.free(self.__arr[index])
        else:
            self.__size = index + 1 #!Doesn't imply there aren't unitialized strings in between

        encoded_value = value.encode("utf-8")
        str_ptr = self.malloc(len(encoded_value) + 1)
        if not str_ptr:
            raise MemoryError("Failed to allocate memory for string.")

        #*Copy string into allocated memory
        ctypes.memmove(str_ptr, encoded_value, len(encoded_value) + 1)

        #*Store pointer in the array
        self.__arr[index] = ctypes.cast(str_ptr, ctypes.POINTER(ctypes.c_char))

        #*Update size if adding a new element
        if index >= self.__size:
            self.__size = index + 1


    def __getitem__(self, index: int) -> str:
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
        if not (0 <= index < self.__capacity):
            raise IndexError("Index out of bounds.")

        if not self.__arr[index]:  #*Return empty string if it's NULL
            return ""

        return ctypes.cast(self.__arr[index], ctypes.c_char_p).value.decode("utf-8")
        

    def append(self, value: str) -> str:
        if self.__size != self.__capacity:
            self.__size[self.__size] = value
            self.__size += 1
        else:
            raise MemoryError("Not enough space in the array")


    def __len__(self) -> int:
        return self.__size


    def __iter__(self):
        for i in range(self.__size):
            if self.__arr[i] != "" and self.__arr[i] is not None:
                yield self[i]


    def __contains__(self, value: str) -> bool:
        """
        Checks if the array contains the specified value.

        Parameters
        ----------
        value : str
            The value to check for in the array.

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
        Prints the array in the conventional notation
        `[1st element, 2nd element, ..., size-th element]`
        """
        repr_str = "["
        for i in range(self.__size):
            if self.__arr[i]:  # Check if the pointer is not NULL
                str_value = ctypes.cast(self.__arr[i], ctypes.c_char_p).value.decode("utf-8")
                repr_str += f'\'{str_value}\''
            else:
                repr_str += "NULL"
            
            if i < self.__size - 1:
                repr_str += ", "

        repr_str += "]"
        return repr_str


    
    def __del__(self) -> None:
        """
        Frees all allocated memory. It iterates over all the arrays of 
        characters and frees their memory and then frees `__arr`'s memory
        """
        if self.__arr is not None:
            for i in range(self.__capacity):
                if self.__arr[i]:
                    self.free(self.__arr[i])  #*Free each string
            self.free(self.__arr)  #*Free the array itself
        self.__arr = None
