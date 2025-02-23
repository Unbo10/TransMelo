"""Module that stores a LinkedList DS."""


class Node:
    def __init__(self, value: any = None):
        self.value: any = value
        self.next: Node = None


class LList:
    def __init__(self):
        self.__head: Node = None
        self.__tail: Node = None
        self.__size: int = 0


    def add(self, value):
        new_node: Node = Node(value)
        if self.__tail is not None:
            self.__tail.next = new_node
        else:
            self.__head = new_node
        self.__tail = new_node
        self.__size += 1


    def __getitem__(self, index: int) -> any:
        current = self.__head
        if 0 <= index < self.__size:
            for _ in range(index):
                current = current.next
        return current.value


    def __setitem__(self, index, value) -> None:
        current = self.__head
        if 0 <= index < self.__size:
            for _ in range(index):
                current = current.next
            current.value = value
        else:
            raise IndexError("Index out of range")


    def __len__(self):
        return self.__size


    def __repr__(self):
        repr: str = "["
        current: Node = self.__head
        while current != self.__tail and current is not None:
            repr += f"{current.value} -> "
            current = current.next
        if self.__tail is not None:
            repr += f"{self.__tail.value}"
        repr += "]"
        return repr

    def __iter__(self):
        current = self.__head
        while current:
            yield current.value
            current = current.next