

from src.utilities.data_structures.graph.weighted import Weighted as Graph
from src.utilities.data_structures.objArr import ObjArr

class SystemGraph(Graph):
    def __init__(self, node_capacity = 22):
        super().__init__(node_capacity)
        average_speed: int = 30 / 60 #* Km/min
        approximation_factor: int = 1 #* Ceiling or floor function
        weights: ObjArr = ObjArr(2) #*[time (min), distance (km)]
        weights[0] = 0
        weights[1] = 0.76
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Portal El Dorado - C.C. NUESTRO BOGOTA', 'Modelia', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.87
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Modelia', 'Av. Rojas – UNISALESIANA', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 0.58
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Av. Rojas – UNISALESIANA', 'El Tiempo - Camara de Comercio de Bogota', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 0.86
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('El Tiempo - Camara de Comercio de Bogota', 'Salitre El Greco', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 0.57
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Salitre El Greco', 'CAN - British Council', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 0.58
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('CAN - British Council', 'Gobernación', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.70
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.45
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Gobernación', 'Quinta Paredes', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.45
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Quinta Paredes', 'Ciudad Universitaria - Loteria de Bogota', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 3.45
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Ciudad Universitaria - Loteria de Bogota', 'Av. El Dorado', weights)

        #* 26 - NQS
        weights: ObjArr = ObjArr(2)
        weights[1] = 4.40
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Av. El Dorado', 'AV. CHILE', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 4.40
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('AV. CHILE', 'Pepe Sierra', weights)


        #* 26 - Caracas
        weights: ObjArr = ObjArr(2)
        weights[1] = 0.70
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Ciudad Universitaria - Loteria de Bogota', 'Concejo de Bogotá', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 2.30
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Concejo de Bogotá', 'Calle 34 - Fondo Nacional de Garantias', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.11
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Calle 34 - Fondo Nacional de Garantias', 'Calle 45', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.20
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Calle 45', 'Calle 57', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 3.20
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Calle 57', 'Calle 85 - GATO DUMAS', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 3.70
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Calle 85 - GATO DUMAS', 'Calle 127', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.10
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Calle 127', 'Prado', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 3.18
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Pepe Sierra', 'Alcalá – Colegio S. Tomás Dominicos', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 1.10
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Prado', 'Alcalá – Colegio S. Tomás Dominicos', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 2.64
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor
        self.add_edge('Alcalá – Colegio S. Tomás Dominicos', 'Toberin - Foundever', weights)
        weights: ObjArr = ObjArr(2)
        weights[1] = 2.61
        weights[0] = 0
        weights[0] = int(weights[1] * average_speed) + approximation_factor

        #! CHECK EDGES


if __name__ == "__main__":
    graph = SystemGraph()
    print(graph)