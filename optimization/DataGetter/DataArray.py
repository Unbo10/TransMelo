from optimization.DS.objArr import ObjArr
from optimization.DS.intArr import IntArr

def create_data_array(file_name: str) -> ObjArr:
    #*For now, it will just retrieve the info of the "Terminal" station
    with open(file_name, mode="r") as file:
        #*Group all the data into a single string to avoid using lists
        content: str = file.read() #!Can we use built-in strings?

    EOF_reached: bool = False
    row: int = 1 #*Current row number
    row_start: int = 89
    row_end: int = 0
    comma_count: int = 0
    #? Are we counting rows or columns?
    #? We may need a linked list to store the indices of each line to know
    #? how long the arrays need to be
    # time_arr: ObjArr: ObjArr()
    while not EOF_reached:
        try:
            while content[row_end] != "\n":
                if row_end > 1000:
                    EOF_reached = True
                    break
                row_end += 1
            
            print(content[row_start:row_end], end= "A\n")
        except IndexError:
            print("Reached EOF")
            EOF_reached = True
        row_start = row_end + 1
        row_end += 50 #*We can safely say each row will have more than 50 chrs


if __name__ == "__main__":
    create_data_array(file_name="optimization/DataGetter/20250211.csv")

