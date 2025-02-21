
#!TEMPORARY LOCATION (@Unbo10). DO NOT CHANGE PLEASE
from src.utilities.data_structures.strArr import StrArr
from src.utilities.objects.route import Route

def k16() -> Route:
    """Returns a Route object containing the info of the K16 route"""
    station_codes: StrArr = StrArr(15)
    station_names: StrArr = StrArr(15)
    zones: StrArr = StrArr(3)
    station_codes[0] = "02502"
    station_names[0] = "Portal El Dorado - C.C. NUESTRO BOGOTA"
    station_codes[1] = "06001"
    station_names[1] = "Modelia"
    station_codes[2] = "06100"
    station_names[2] = "Av. Rojas – UNISALESIANA" #! The dash looks weird
    station_codes[3] = "06101"
    station_names[3] = "El Tiempo - Camara de Comercio de Bogota"
    station_codes[4] = "06102"
    station_names[4] = "Salitre El Greco"
    station_codes[5] = "06103"
    station_names[5] = "CAN - British Council"
    station_codes[6] = "06105"
    station_names[6] = "Quinta Paredes"
    station_codes[7] = "07108" #! No info about Corferias
    station_names[7] = "Av. El Dorado"
    station_codes[8] = "07103"
    station_names[8] = "AV. CHILE"
    station_codes[9] = "02204"
    station_names[9] = "Pepe Sierra"
    station_codes[10] = "02200" #! The dash looks weird
    station_names[10] = "Alcalá – Colegio S. Tomás Dominicos"
    station_codes[11] = "02101"
    station_names[11] = "Toberin - Foundever"
    station_codes[12] = "02502" #! No info about Calle 187
    station_names[12] = "Terminal"

    zones[0] = "33" #* B zone
    zones[1] = "38" #* E zone central NQS 
    zones[2] = "11" #* K zone

    k_16: Route = Route("K16", station_codes, station_names, zones)
    
    return k_16