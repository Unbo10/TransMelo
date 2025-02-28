"""Dictionary-based implementation of an undirected and unweighted graph"""

from src.utilities.data_structures.intArr import IntArr
from src.utilities.data_structures.lList import LList
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.graph.unweighted import Graph

class Weighted(Graph):
    def __init__(self, node_capacity: int = 20):
        """
        Initialize a new weighted graph.

        This constructor extends the base Graph class initialization.

        Parameters
        ----------
        node_capacity : int, optional
            The initial capacity for nodes in the graph. Defaults to 20.
        """
        super().__init__(node_capacity)
    
    def add_edge(self, node1: str, node2: str, weights: IntArr) -> None:
        """
        Adds a weighted edge between two nodes.

        Parameters
        ----------
        node1 : str
            The first node.
        node2 : str
            The second node.
        weights : IntArr
            The weight of the edge.
        """
        if node1 not in self._adj_list:
            self.add_node(node1)
        if node2 not in self._adj_list:
            self.add_node(node2)

        edge: ObjArr = ObjArr(2)
        edge[0] = node2
        edge[1] = weights
        self._adj_list[node1].append(edge)

        edge = ObjArr(2) #* To avoid passing a reference to the previous one
        edge[0] = node1
        edge[1] = weights
        self._adj_list[node2].append(edge)


    def remove_edge(self, node1: str, node2: str) -> None:
        """
        Removes one or two weighted edges connecting two nodes.

        Parameters
        ----------
        node1 : str
            The first node.
        node2 : str
            The second node.
        """
        if node1 in self._adj_list:
            edge_index = -1
            for i, edge in enumerate(self._adj_list[node1]):
                if edge[0] == node2:
                    edge_index = i
                    break
                    
            if edge_index >= 0:
                self._adj_list[node1].remove(edge_index)
        
        if node2 in self._adj_list:
            edge_index = -1
            for i, edge in enumerate(self._adj_list[node2]):
                if edge[0] == node1:
                    edge_index = i
                    break
                    
            if edge_index >= 0:
                self._adj_list[node2].remove(edge_index)


    def remove_node(self, node: str) -> None:
        """
        Removes a node from the graph.
        This method removes a node from the graph as well as all edges that are connected to it.
        It first identifies all adjacent nodes that have an edge to the node being removed,
        then removes those edges, and finally removes the node itself from the adjacency list.
        Parameters
        ----------
        node : str
            The node to be removed from the graph.
        Returns
        -------
        None
            The method doesn't return anything, it modifies the graph in-place.
        """
        nodes_to_update: LList = LList()
        for adj_node in self._adj_list:
            if adj_node != node:
                #*Check if this node has the node-to-be-removed as a neighbor
                for i, edge in enumerate(self._adj_list[adj_node]):
                    if edge[0] == node:
                        nodes_to_update.append(adj_node)
                        break
        for adj_node in nodes_to_update:
            self.remove_edge(adj_node, node)
    
        # Finally remove the node itself
        self._adj_list.remove(node)


    def get_neighbours(self, node: str) -> ObjArr:
        """
        Retrieves all neighbours of a node along with their edge weights.

        Parameters
        ----------
        node : str
            The node whose neighbours are to be retrieved.

        Returns
        -------
        ObjArr
            An array of [neighbour, weights] pairs.
        """
        if node not in self._adj_list:
            return ObjArr(0)
        neighbours: ObjArr = ObjArr(len(self._adj_list[node]))
        i: int = 0
        for neighb_and_weights in self._adj_list[node]:
            neighbours[i] = neighb_and_weights
            i += 1
        return neighbours