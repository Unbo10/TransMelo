import ctypes

class DArr:
    def __init__(self):
        self.size = 0  # Number of elements in the list
        self.capacity = 1  # Default capacity
        self.array = self._make_array(self.capacity)
    
    def _make_array(self, capacity):
        """Creates a new array with the given capacity using ctypes."""
        return (capacity * ctypes.py_object)()
    
    def append(self, item):
        """Adds an element to the end of the list, resizing if necessary."""
        if self.size == self.capacity:
            self._resize(2 * self.capacity)  # Double capacity
        
        self.array[self.size] = item
        self.size += 1
    
    def insert(self, index, item):
        """Inserts an element at the specified index, shifting elements if needed."""
        if not 0 <= index <= self.size:
            raise IndexError("Index out of range")
        
        if self.size == self.capacity:
            self._resize(2 * self.capacity)
        
        for i in range(self.size, index, -1):  # Shift elements right
            self.array[i] = self.array[i - 1]
        
        self.array[index] = item
        self.size += 1

    def remove(self, value):
        """Removes the first occurrence of the specified value."""
        for i in range(self.size):
            if self.array[i] == value:
                self.pop(i)
                return
        raise ValueError("Value not found in list")
    
    def pop(self, index=None):
        """Removes and returns an item at a given index (or the last item by default)."""
        if self.size == 0:
            raise IndexError("Pop from empty list")

        if index is None:
            index = self.size - 1  # Default to last element
        
        if index < 0:  
            index += self.size  # Convert negative index to positive
        
        if not 0 <= index < self.size:
            raise IndexError("Index out of range")

        item = self.array[index]

        # Shift elements left to fill the gap
        for i in range(index, self.size - 1):
            self.array[i] = self.array[i + 1]

        self.array[self.size - 1] = None  # Avoid memory leak
        self.size -= 1

        # Shrink capacity if needed
        if self.size > 0 and self.size == self.capacity // 4:
            self._resize(self.capacity // 2)

        return item
    
    def clear(self):
        """Removes all elements from the list."""
        self.size = 0
        self.capacity = 1
        self.array = self._make_array(self.capacity)

    def _resize(self, new_capacity):
        """Resizes internal array to a new capacity."""
        new_array = self._make_array(new_capacity)
        
        for i in range(self.size):
            new_array[i] = self.array[i]
        
        self.array = new_array
        self.capacity = new_capacity

    def __iter__(self):
        """Returns an iterator over the elements in the list."""
        for i in range(self.size):
            yield self.array[i]
    
    def __len__(self):
        """Returns the number of elements in the list."""
        return self.size
    
    def __getitem__(self, index):
        """Retrieves an item at a given index."""
        if not 0 <= index < self.size:
            raise IndexError("Index out of range")
        return self.array[index]
    
    def __setitem__(self, index, value):
        """Sets an item at a given index."""
        if index < 0:
            index += self.size
            if index < 0:
                raise IndexError("Index out of range")
                
        if index >= self.size:
            while index >= self.capacity:
                self._resize(self.capacity * 2)
            self.size = index + 1
            
        self.array[index] = value
    
    def __repr__(self):
        """String representation of the list."""
        result = "["
        for i in range(self.size):
            try:
                if i > 0:
                    result += ", "
                result += repr(self.array[i])
            except (TypeError, ValueError):
                if i > 0:
                    result += ", "
                result += 'None'
        result += "]"
        return result