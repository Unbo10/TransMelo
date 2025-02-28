from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.lList import LList

class Dictionary:
    def __init__(self, capacity: int = 0):
        """
        Initializes a new instance of a dictionary with a specified size.

        Parameters
        ----------
        size : int
            The number of buckets in the hash table. Default is 0.

        Notes
        -----
        The dictionary is implemented as a hash table using separate chaining
        for collision resolution. Each bucket contains a linked list to store
        multiple key-value pairs that hash to the same location.
        """
        self.__capacity: int = capacity
        self.__size: int = 0
        self.__table: ObjArr = ObjArr(capacity)
        for i in range(capacity):
            self.__table[i] = LList()


    def __hash(self, key: str) -> int:
        """
        Computes a hash value for the provided key using polynomial rolling hash function.

        This method implements a simple polynomial hash function with a prime number to
        reduce collisions. It maps a string key to an integer index within the dictionary's
        internal array size.

        Parameters
        ----------
        key : str
            The string key to hash.

        Returns
        -------
        int
            The computed hash index, which is in the range [0, self.__capacity - 1].

        Notes
        -----
        The hash function uses 31 as the prime multiplier since it's effective for 
        string hashing with a relatively small number of entries (around 30 stations).
        """
        hash_index: int = 0
        #*To reduce collisions (since there will be no more than 30 stations,
        #*31 is a good number)
        prime: int = 31
        for char in key:
            #*Convert to ASCII and compute modulo capacity
            hash_index = (hash_index * prime + ord(char)) % self.__capacity
        return hash_index  


    def insert(self, key: str, value: any) -> None:
        """
        Inserts a key-value pair into the dictionary.
        Parameters
        ----------
        key : str
            The key to insert into the dictionary.
        value : any
            The value associated with the key.
        Notes
        -----
        If the key already exists in the dictionary, the existing value will be
        replaced with the new value. If the key doesn't exist, a new key-value
        pair will be created and added to the appropriate chain in the hash table.
        """
        index: int = self.__hash(key)
        chain: LList = self.__table[index]
        key_in_chain: bool = False

        for pair in chain:
            if pair[0] == key:
                pair[1] = value
                key_in_chain = True
        
        if key_in_chain == False:
            #?Values may need to be converted to integers
            pair: ObjArr = ObjArr(2)
            pair[0] = key
            pair[1] = value
            self.__size += 1
            chain.append(pair) #*Insert new key-value pair


    def remove(self, key: str) -> bool:
        """
        Removes a key-value pair from the dictionary.

        Parameters
        ----------
        key : Any
            The key to remove from the dictionary.

        Returns
        -------
        bool
            True if the key was found and removed.

        Raises
        ------
        KeyError
            If the key was not found in the dictionary.

        Notes
        -----
        This method uses the hash function to locate the chain where the key might be stored,
        then iterates through that chain to find and remove the key-value pair.
        """
        index = self.__hash(key)
        chain: LList = self.__table[index]
        index_to_remove: int = -1

        i: int = 0
        for pair in chain:
            if pair[0] == key:
                index_to_remove = i
                self.__size -= 1
                break
            i += 1
        if index_to_remove >= 0:
            chain.remove(index_to_remove) #*Removes the entire chain
            return True
        else:
            raise KeyError("Key not found")  #*Key not found


    def get(self, key: str) -> any:
        """
        Retrieves the value associated with the specified key in the dictionary.
        
        Parameters
        ----------
        key
            The key for which to retrieve the associated value.
        
        Returns
        -------
        any
            The value associated with the specified key if the key exists in the dictionary,
            None otherwise.

        Raises
        ------
        KeyError
            If the key was not found in the dictionary.
        
        Notes
        -----
        This method uses the hash function to locate the appropriate chain,
        then searches through the chain for the specified key.
        """
        index = self.__hash(key)
        chain = self.__table[index]

        for pair in chain:
            if pair[0] == key:
                return pair[1]
        raise KeyError("Key not found")  #*Key not found


    def __setitem__(self, key: str, value: any) -> None:
        self.insert(key, value)


    def __getitem__(self, key: str) -> any:
        return self.get(key)


    def items(self):
        """
        Enables iteration over all key-value pairs in the dictionary.

        Yields
        ------
        ObjArr
            An array containing [key, value] for each entry in the dictionary.
        """
        for chain in self.__table:
            for pair in chain:
                yield pair


    def __repr__(self) -> str:
        """
        Returns a string representation of the Dictionary object.
        The output format is:
        Key 0: [Array of key-value pairs at this index]
        Key 1: [Array of key-value pairs at this index]
        ...
        Key n: [Array of key-value pairs at this index]

        Each key represents a hash bucket (chain) in the dictionary, and each bucket
        shows the key-value pairs stored there. Empty buckets are represented as [].

        Returns
        -------
        str
            A string representation of the dictionary showing hash table contents.
        """
        i: int = 0
        j: int = 0
        repr: str = ""

        for chain in self.__table:
            if chain:
                repr += f"Key {i}: "
                j = 0
                for pair in chain:
                    repr += f"Index {j}: {pair}"
                    if 0 <= j < len(chain) - 1:
                        repr += " - "
                    j += 1
            else:
                repr += f"Key {i}: []"  # Explicitly print empty list
            repr += "\n"
            i += 1
        return repr


    def __len__(self) -> int:
        return self.__size


    def __contains__(self, key: str) -> any:
        """
        Check if a key is present in the dictionary.

        This method implements the 'in' operator for the dictionary. It allows for checking
        whether a key exists in the dictionary using the syntax 'key in dictionary'.

        Parameters
        ----------
        key : str
            The key to check for existence in the dictionary.

        Returns
        -------
        bool
            True if the key exists in the dictionary, False otherwise.
        """
        try:
            self.get(key)
            return True
        except KeyError:
            return False


    def __iter__(self) -> any:
        """
        Return an iterator over the keys in the dictionary.
        
        This method allows the dictionary to be used in for loops and other contexts
        requiring iteration, providing only the keys similar to Python's built-in
        dictionary behavior.
        
        Returns
        -------
        iterator
            An iterator yielding all keys in the dictionary.
        """
        for chain in self.__table:
            for pair in chain:
                yield pair[0]  # ✅ Yields only the key

            