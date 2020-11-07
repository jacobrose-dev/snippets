"""This module holds a single function that generates an A1 Style Grid.
The author does not known if it can be done in a more Pythonic way,
  but this method gets the job done for any size grid.
width is an integer defining how many columns will be created.
height is an integer defining how many rows will be created."""

def generate_cells(width, height):
    """Generates cell-names for an 'A1 Reference Style' grid,
        and places them into a dictionary with empty values.
    width and height parameters are both = integer > zero"""
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' # explicit to avoid import
    empty_grid = {}
    for column in range(1, width+1):
    
        bijective_hexavigesimal = []
        while column: # repetitiously reduce unit with divmod()
            column, remainder = divmod(column - 1, 26)
            bijective_hexavigesimal[:0] = alphabet[remainder]
            
        column = ''.join(bijective_hexavigesimal)
        
        for row in range(1, height+1):
            cell = column + str(row)
            empty_grid[cell] = ''
                 
    return empty_grid

if __name__ == "__main__":
    grid = generate_cells(8, 8) # You can make these numbers arbitrarily large
    print(grid)
