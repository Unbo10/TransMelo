import unittest
from src.utilities.data_structures.intArr import IntArr
from src.utilities.data_structures.graph.weighted import Weighted

class TestWeightedGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Weighted()
    
    def test_add_node(self):
        self.graph.add_node("Station A")
        self.assertEqual(str(self.graph), "Station A: []")
        
    def test_add_edge(self):
        # Create weight array with distance and time
        weights: IntArr = IntArr(2)
        weights[0] = 5  # distance in km
        weights[1] = 10  # time in minutes
        
        self.graph.add_edge("Station A", "Station B", weights)
        self.assertTrue("Station B" in str(self.graph))
        self.assertTrue("Station A" in str(self.graph))
    
    def test_multiple_weighted_edges(self):
        # Create weight arrays for different connections
        weights_ab: IntArr = IntArr(2)
        weights_ab[0] = 5  # distance in km
        weights_ab[1] = 12  # time in minutes
        
        weights_ac: IntArr = IntArr(2)
        weights_ac[0] = 8  # distance in km
        weights_ac[1] = 20  # time in minutes
        
        weights_bc: IntArr = IntArr(2)
        weights_bc[0] = 3  # distance in km
        weights_bc[1] = 7  # time in minutes
        
        # Add edges with multiple weights
        self.graph.add_edge("Station A", "Station B", weights_ab)
        self.graph.add_edge("Station A", "Station C", weights_ac)
        self.graph.add_edge("Station B", "Station C", weights_bc)
        
        # Get neighbors and check weights
        neighbors_a = self.graph.get_neighbours("Station A")
        neighbors_b = self.graph.get_neighbours("Station B")
        neighbors_c = self.graph.get_neighbours("Station C")
        
        # Check if each station has the correct number of neighbors
        self.assertEqual(len(neighbors_a), 2)
        self.assertEqual(len(neighbors_b), 2)
        self.assertEqual(len(neighbors_c), 2)
        
        # Check if Station A's neighbors have correct weights
        for edge in neighbors_a:
            if edge[0] == "Station B":
                self.assertEqual(edge[1][0], 5)  # distance
                self.assertEqual(edge[1][1], 12)  # time
            elif edge[0] == "Station C":
                self.assertEqual(edge[1][0], 8)  # distance
                self.assertEqual(edge[1][1], 20)  # time
        
        # Check if Station B's neighbors have correct weights
        for edge in neighbors_b:
            if edge[0] == "Station A":
                self.assertEqual(edge[1][0], 5)  # distance
                self.assertEqual(edge[1][1], 12)  # time
            elif edge[0] == "Station C":
                self.assertEqual(edge[1][0], 3)  # distance
                self.assertEqual(edge[1][1], 7)  # time
        
        # Check if Station C's neighbors have correct weights
        for edge in neighbors_c:
            if edge[0] == "Station A":
                self.assertEqual(edge[1][0], 8)  # distance
                self.assertEqual(edge[1][1], 20)  # time
            elif edge[0] == "Station B":
                self.assertEqual(edge[1][0], 3)  # distance
                self.assertEqual(edge[1][1], 7)  # time

    def test_remove_node(self):
        # Create weight arrays for different connections
        weights_ab: IntArr = IntArr(2)
        weights_ab[0] = 5  # distance in km
        weights_ab[1] = 12  # time in minutes
        
        weights_ac: IntArr = IntArr(2)
        weights_ac[0] = 8  # distance in km
        weights_ac[1] = 20  # time in minutes
        
        # Add edges with weights
        self.graph.add_edge("Station A", "Station B", weights_ab)
        self.graph.add_edge("Station A", "Station C", weights_ac)
        

        # Remove node B and verify it's gone
        self.graph.remove_node("Station B")
        print("Updated\n", self.graph)
        self.assertFalse("Station B" in str(self.graph))

        
        # Check that B is no longer a neighbor of A
        neighbors_a = self.graph.get_neighbours("Station A")
        self.assertEqual(len(neighbors_a), 1)
        self.assertEqual(neighbors_a[0][0], "Station C")
        
        # Remove node C and verify A has no neighbors
        self.graph.remove_node("Station C")
        neighbors_a = self.graph.get_neighbours("Station A")
        self.assertEqual(len(neighbors_a), 0)

    def test_add_and_remove_edges(self):
        # Create weight arrays
        weights1: IntArr = IntArr(2)
        weights1[0] = 5
        weights1[1] = 10
        
        weights2: IntArr = IntArr(2)
        weights2[0] = 7
        weights2[1] = 15
        
        # Add edges
        self.graph.add_edge("Station X", "Station Y", weights1)
        self.graph.add_edge("Station X", "Station Z", weights2)
        
        # Verify edges exist
        neighbors_x = self.graph.get_neighbours("Station X")
        self.assertEqual(len(neighbors_x), 2)
        
        # Remove edge
        self.graph.remove_edge("Station X", "Station Y")
        print(self.graph)
        
        # Verify edge was removed
        updated_neighbors = self.graph.get_neighbours("Station X")
        self.assertEqual(len(updated_neighbors), 1)
        self.assertEqual(updated_neighbors[0][0], "Station Z")

if __name__ == '__main__':
    unittest.main()