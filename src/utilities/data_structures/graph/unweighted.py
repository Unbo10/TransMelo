"""Dictionary-based implementation of an undirected and unweighted graph"""

from src.utilities.data_structures.dictionary import Dictionary
from src.utilities.data_structures.lList import LList

class Graph: #! Change name
    def __init__(self, node_capacity: int = 20) -> None:
        """
        Initialize an unweighted graph.

        This constructor creates a new unweighted graph with an adjacency list
        representation.

        Parameters
        ----------
        node_capacity : int, optional
            The initial capacity for the number of nodes in the graph. Defaults
            to 20.
        """
        self._adj_list: Dictionary = Dictionary(node_capacity) 

    def add_node(self, node: str) -> None:
        """
        Adds a new node to the graph if it doesn't already exist.
        
        The node is added to the adjacency list with an empty linked list 
        as its value, representing that it has no adjacent nodes initially.
        
        Parameters:
        -----------
        node : str
            The identifier of the node to be added to the graph.
        
        Returns:
        --------
        None
        
        Notes:
        ------
        If the node already exists in the graph, this method does nothing.
        """
        #*Node is a key
        if node not in self._adj_list:
            self._adj_list[node] = LList()

    def add_edge(self, node1: str, node2: str) -> None:
        """
        Adds an undirected edge between two nodes.

        Parameters
        ----------
        node1 : str
            The first node.
        node2 : str
            The second node.
        """
        if node1 not in self._adj_list:
            self.add_node(node1)
        if node2 not in self._adj_list:
            self.add_node(node2)

        self._adj_list[node1].append(node2)
        self._adj_list[node2].append(node1)


    def remove_edge(self, node1: str, node2: str) -> None:
        """
        Removes one or two edges connecting two nodes.

        Parameters
        ----------
        node1 : str
            The first node.
        node2 : str
            The second node.
        """
        if node1 in self._adj_list and node2 in self._adj_list[node1]:
            self._adj_list[node1].remove(node2)
        if node2 in self._adj_list and node1 in self._adj_list[node2]:
            self._adj_list[node2].remove(node1)


    def remove_node(self, node: str) -> None:
        """
        Removes a node and all its edges from the graph.

        Parameters
        ----------
        node : str
            The node to remove.
        """
        if node in self._adj_list:
            for neighbour in self._adj_list[node]:
                self._adj_list[neighbour].remove(node)
            self._adj_list.remove(node)


    def get_neighbours(self, node: str) -> LList:
        """
        Returns the neighbors of a node.

        Parameters
        ----------
        node : str
            The node whose neighbors are needed.

        Returns
        -------
        LList
            A linked list of neighboring nodes.
        """
        if node in self._adj_list:
            return self._adj_list[node]
        return LList()

    def __repr__(self):
        repr: str = ""
        if len(self._adj_list) == 0:
            repr += "[]"
        else:
            #*Key, value
            for node, neighbours in self._adj_list.items():
                repr += f"{node}: {neighbours}\n"
            repr = repr[0: len(repr) - 1] #* To eliminate the last line break
        return repr