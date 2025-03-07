
#!TEMPORARY LOCATION (@Unbo10). DO NOT CHANGE PLEASE
from src.utilities.data_structures.strArr import StrArr
from src.utilities.data_structures.dynamicArr import DArr
from src.utilities.objects.route import Route

def r16(b_route: bool = True) -> Route:
    """Returns a Route object containing the info of the K16 route"""
    station_codes: StrArr = StrArr(13)
    station_names: StrArr = StrArr(13)
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

    zones[0] = "(33)Zona B AutoNorte" #* B zone
    zones[1] = "(38)Zona E NQS Central" #* E zone central NQS 
    zones[2] = "(11)Zona K Calle 26" #* K zone

    if b_route:
        r_16: Route = Route("B16", station_codes, station_names, zones)
    else:
        r_16: Route = Route("K16", station_codes, station_names, zones)
    
    return r_16

def r23(b_route: bool = True) -> Route:
    station_codes: StrArr = StrArr(15)
    station_names: StrArr = StrArr(15)
    zones: StrArr = StrArr(3)
    station_codes[0] = "02502"
    station_names[0] = "Portal El Dorado - C.C. NUESTRO BOGOTA"
    station_codes[1] = "06100"
    station_names[1] = "Av. Rojas – UNISALESIANA"
    station_codes[2] = "06101"
    station_names[2] = "El Tiempo - Camara de Comercio de Bogota"
    station_codes[3] = "06102"
    station_names[3] = "Salitre El Greco"
    station_codes[4] = "06103"
    station_names[4] = "CAN - British Council"
    station_codes[5] = "06104"
    station_names[5] = "Gobernación"
    station_codes[6] = "06107"
    station_names[6] = "Ciudad Universitaria - Loteria de Bogota"
    station_codes[7] = "06108"
    station_names[7] = "Concejo de Bogotá"
    station_codes[8] = "09115"
    station_names[8] = "Calle 34 - Fondo Nacional de Garantias"
    station_codes[9] = "09117"
    station_names[9] = "Calle 45"
    station_codes[10] = "09119"
    station_names[10] = "Calle 57"
    station_codes[11] = "02303"
    station_names[11] = "Calle 85 - GATO DUMAS"
    station_codes[12] = "02202"
    station_names[12] = "Calle 127"
    station_codes[13] = "02201"
    station_names[13] = "Prado"
    station_codes[14] = "02200"
    station_names[14] = "Alcalá – Colegio S. Tomás Dominicos"

    zones[0] = "(33)Zona B AutoNorte" #* B zone
    zones[1] = "(36)Zona A Caracas" #* A zone
    zones[2] = "(11)Zona K Calle 26" #* K zone

    if b_route:
        r_23: Route = Route("B23", station_codes, station_names, zones)
    else:
        r_23: Route = Route("K23", station_codes, station_names, zones)

    return r_23

def joint() -> Route:
    r_23: Route = r23()
    r_16: Route = r16()
    joint_codes: DArr = DArr()
    joint_names: DArr = DArr()
    joint_zones: StrArr = StrArr(4)
    print(r_23.zone_names)

    for i in range(len(r_16.station_codes)):
        joint_codes.append(r_16.station_codes[i])
        joint_names.append(r_16.station_names[i])
    for i in range(len(r_23.station_codes)):
        if r_23.station_codes[i] not in joint_codes:
            joint_codes.append(r_23.station_codes[i])
            joint_names.append(r_23.station_names[i])

    for i in range(len(r_16.zone_names)):
        print(r_16.zone_names[i], i)
        joint_zones[i] = r_16.zone_names[i]
    for i in range(len(r_23.zone_names)):
        print(r_23.zone_names[i], i)
        if r_23.zone_names[i] not in joint_zones:
            joint_zones[3] = r_23.zone_names[i]
    
    joint_route: Route = Route("joint", joint_codes, joint_names, joint_zones)
    print(joint_names)
    return joint_route