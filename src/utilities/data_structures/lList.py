"""Module that stores a LinkedList DS."""


class Node:
    def __init__(self, value: any = None) -> None:
        """
        Initializes a new instance of a Node.

        Parameters
        ----------
        value : any, optional
            The value to be stored in the node. Default is None.
        """
        self.value: any = value
        self.next: Node = None


class LList:
    def __init__(self) -> None:
        """
        Initializes a new instance of a linked list.

        The linked list is initially empty with no nodes, and a size of 0.
        """
        self.__head: Node = None
        self.__tail: Node = None
        self.__size: int = 0


    def append(self, value) -> None:
        """
        Appends a value to the end of the linked list.

        Parameters
        ----------
        value : Any
            The value to append to the linked list.
        """
        new_node: Node = Node(value)
        if self.__tail is not None:
            self.__tail.next = new_node
        else:
            self.__head = new_node
        self.__size += 1
        self.__tail = new_node


    def remove(self, index: int) -> None:
        """
        Removes the element at the specified index from the linked list.

        Parameters
        ----------
        index : int
            The index of the element to remove.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        if not 0 <= index < self.__size:
            raise IndexError("Index out of range")

        current = self.__head
        previous = None

        #*Traverse to the node at the given index
        for _ in range(index):
            previous = current
            current = current.next

        #*If deleting the head, update its pointer
        if previous is None:
            self.__head = current.next
        else:
            previous.next = current.next

        #*If deleting the tail, update its pointer
        if current == self.__tail:
            self.__tail = previous

        self.__size -= 1


    def __getitem__(self, index: int) -> any:
        """
        Retrieves the value at the specified index in the linked list.

        Parameters
        ----------
        index : int
            The index of the value to retrieve.

        Returns
        -------
        any
            The value at the specified index.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        current: Node = self.__head
        if 0 <= index < self.__size:
            for _ in range(index):
                current = current.next
        return current.value


    def __setitem__(self, index: int, value: any) -> None:
        """
        Sets the value at the specified index in the linked list.

        Parameters
        ----------
        index : int
            The index of the value to set.
        value : any
            The new value to assign.

        Raises
        ------
        IndexError
            If the index is out of bounds.
        """
        current: Node = self.__head
        if 0 <= index < self.__size:
            for _ in range(index):
                current = current.next
            current.value = value
        else:
            raise IndexError("Index out of range")

    def __len__(self) -> str:
        return self.__size

    def __repr__(self) -> str:
        """
        Returns a string representation of the linked list.
        Returns a string with the format `[value1 -> value2 -> ... -> valueN]`, where 
        each value is an element of the linked list, and the arrow (->) indicates 
        the connection to the next element.

        Returns
        -------
        str
            A string representation of the linked list.
        """
        repr: str = "["
        current: Node = self.__head
        while current != self.__tail and current is not None:
            repr += f"{current.value} -> "
            current = current.next
        if self.__tail is not None:
            repr += f"{self.__tail.value}"
        repr += "]"
        return repr

    def __iter__(self) -> any:
        """
        Iterates over the elements of the linked list instance.

        Yields
        ------
        any
            The value of each node in the linked list, starting from the head and proceeding to the tail.
        """
        current: Node = self.__head
        while current:
            yield current.value
            current = current.next
