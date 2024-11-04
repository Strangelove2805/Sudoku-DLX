import numpy as np


class Node:                                 # Class for creating nodes representing valid states in the cover table
    def __init__(self, row, column):        # Takes inputs for the row and column - 729 x 324 at the greatest
        self.above = self                   # Pointer to the node directly above a node
        self.below = self                   # Pointer to the node directly below a node
        self.left = self                    # Pointer to the node directly to the left of a node
        self.right = self                   # Pointer to the node directly to the right of a node
        self.row = row                      # Numerical parameter for the row a given node is in
        self.column = column                # Node type parameter for the column a given node is in
        self.size = 0                       # The number of nodes in a column (only applied for the column headers)
        # Saving the size of a column makes using Knuth's S heuristic (finding the smallest column) far easier


class AlgorithmX:                   # Class for creating the sudoku cover table and applying Donald Knuth's Algorithm X

    def __init__(self):
        self.head = Node(0, self)   # Create a head node designator for the linked list of the column headers

    # Method for constructing the exact cover table
    # This takes a flattened 1x81 version of the sudoku grid - this was suggested by Donald Knuth himself to make
    # indexing for both the cover table and search algorithm easier. He's a clever man... I took his word for it.
    # (He suggested structuring it as a string [Ref 1] but I found an array easier to work with and understand)
    # We aren't constructing the entire table, but a cut down version based on the specific puzzle we're solving.
    def exact_cover_table(self, sudoku):

        # Create a list of every column header node starting with the table head
        # Having this list available is extremely important for constructing the table as it allows us to find the
        # column header we're looking for when adding above pointers to a new node using nothing more than a single
        # index, removing the need of a for-loop that sequentially searches through the linked list
        column_list = [self.head]

        for column_number in range(1, 325):             # There are 324 constraints, create 324 column headers

            column_header = Node(column_number, -1)     # Create a column head at index i. Its row mustn't be 0 - 729
            column_header.right = self.head             # Point the right pointer of the new node at the head
            column_header.left = self.head.left         # Point the left pointer of the new node at left of the head

            # These lines shift the head marker of the doubly linked list across for each new column header added
            self.head.left.right = column_header
            self.head.left = column_header

            column_list.append(column_header)       # Add the new node to the list of column headers

        # Method for calculating which column a new node should be placed in
        # The numbers 1-4 designate which quarter (i.e which constraint) of the table we should be focussing on
        # The thought process behind these equations can be found in readme.
        # I cannot stress the importance of how instrumental the visualisation of the cover table by R. Hanson
        # of stolaf.edu [Ref 2] was in helping to figure this out
        def find_position(index, value, constraint_type):
            switch = {                                                      # Serves as a switch case
                1: index + 1,                                               # Equation for constraint 1, cell
                2: index // 9 * 9 + value + 81,                             # Equation for constraint 2, row
                3: (index % 9) * 9 + value + 162,                           # Equation for constraint 3, column
                4: (index % 9) // 3 * 9 + index // 27 * 27 + value + 243,   # Equation for constraint 4, 3x3 box
            }
            return switch.get(constraint_type)

        def add_vertical_pointers(new_node):    # Method for adding above/below pointers to a new node

            column = new_node.column            # This designates which column we should be adding to

            column.size += 1                    # The column size must be increased by 1 to indicate the node's addition

            # It is important to remember that the doubly linked list is circular, so in any given column the highest
            # node's above parameter points to the lowest node and vice versa. We can use this to add new nodes easily
            new_node.below = column
            new_node.above = column.above

            # The existing nodes' pointers also must be adjusted
            column.above.below = new_node
            column.above = new_node

        # Method for adding the left/right circular pointers to a new set of nodes in a given row
        # This method creates all of the nodes for a certain possibility based on a single cell and its value. For all
        # of the 729 possible actions there are 4 nodes, 1 for each different constraint type
        def add_horizontal_pointers(index, value):

            row = index * 9 + value     # Calculation for the row number (from 1-729) based on the cell and value in it

            # Create the first node for this row. This one is for the cell constraint where a row and column intersect.
            # It exists to prevent two values being put into the same cell which is obviously an illegal move in sudoku.
            # Parameters are the current row and the column header whose number is based on the cell constraint equation
            constraint_1_node = Node(row, column_list[find_position(index, value, 1)])

            # Create the second node for this row. This one is for the row constraint to ensure each number from 1-9
            # is only represented once in each sudoku row
            constraint_2_node = Node(row, column_list[find_position(index, value, 2)])

            # Create the third node for this row. This one is for the column constraint to ensure each number from 1-9
            # is only represented once in each sudoku column
            constraint_3_node = Node(row, column_list[find_position(index, value, 3)])

            # Create the third node for this row. This one is for the 3x3 grid constraint to ensure each number from 1-9
            # is only represented once in each of the 9 3x3 squares
            constraint_4_node = Node(row, column_list[find_position(index, value, 4)])

            # The new nodes are all part of the same row and must be linked together in the same fashion as the column
            # headers, creating a circular linkage
            constraint_1_node.right = constraint_2_node
            constraint_2_node.right = constraint_3_node
            constraint_3_node.right = constraint_4_node
            constraint_4_node.right = constraint_1_node

            # This takes effect in both directions. It is a doubly linked list, after all
            constraint_1_node.left = constraint_4_node
            constraint_2_node.left = constraint_1_node
            constraint_3_node.left = constraint_2_node
            constraint_4_node.left = constraint_3_node

            # The new nodes need to be linked up to their column headers and/or nodes above/below them
            add_vertical_pointers(constraint_1_node)
            add_vertical_pointers(constraint_2_node)
            add_vertical_pointers(constraint_3_node)
            add_vertical_pointers(constraint_4_node)

        # Technically, we don't want to create the whole cover table. Since some of the numbers will already be filled
        # in, we can have a single row for these particular cells. For instance, if the cell at row 3 column 2 has a
        # value of 6, we can settle for one row for row 3 column 2, value 6. There are no other possible moves. If a
        # cell is empty, however, we have to make rows for all 9 possible values of this cell
        for index, cell_value in enumerate(sudoku):

            # If this particular cell isn't empty, simply create one set of row nodes using both its index and value
            if cell_value != 0:

                add_horizontal_pointers(index, cell_value)

            # If it is empty, add the row nodes for every possible value the cell can take (1-9)
            else:

                # range(1,10) is from 1 to 9, i.e all possible values a cell can have
                for possible_value in range(1, 10):

                    add_horizontal_pointers(index, possible_value)

    # We are using Donald Knuth's S Heuristic which allows us to quickly find the column with the least number of nodes
    # in it. This is vital when covering nodes in AlgoX as it minimises the number of branches when searching
    # I want to be very clear that this method is adapted from pseudocode created by Jan Magne Tjensvold in their
    # report on a generic exact cover solving implementation [Ref 3]
    def s_heuristic(self):

        column = None
        header = self.head
        column_to_test = self.head.right

        # In the pseudocode this number is infinity since in general there can be infinite possibilities in a cover
        # problem but since there are only 729 in sudoku (and I don't know how to make infinity in Python) I can safely
        # put it at any number higher than this, i.e there can only be 729 nodes in a column
        size = 730

        # This will search through the columns, constantly updating 'size' with the size of the smallest column found
        while column_to_test != header:

            if column_to_test.size < size:

                column = column_to_test
                size = column_to_test.size

            column_to_test = column_to_test.right

        return column

    # Method for covering a column in the table. As per Knuth's discussion of how dancing links should be handled
    # [Ref 4], any rows with nodes in the column to be covered up are also covered.
    # The three methods below are adapted from pseudocode created by Mattias Harrysson and Hjalmar Laestander
    # of KTH Computer Science in their report on using Dancing Links for sudoku [Ref 5]
    @staticmethod
    def cover(column_header):

        column_header.right.left = column_header.left
        column_header.left.right = column_header.right

        i = column_header.below                 # The current node we are looking at in the column

        # Iterate through the nodes in the column until you circle back to the header
        while i != column_header:

            j = i.right                         # The row nodes in line with the current node i

            # Iterate until all nodes in the row are covered
            while j != i:

                # Unlink, decrease the row size then move over in the row
                j.below.above = j.above
                j.above.below = j.below
                j.column.size -= 1
                j = j.right

            i = i.below

    # Method to revert any changes made in the cover operation. Any covered columns and their rows are re-linked to the
    # rest of the table. The process is identical to the cover method, albeit inverted.
    @staticmethod
    def uncover(column):

        i = column.above                        # The current node we are looking at in the column

        while i != column:

            j = i.left                          # The row nodes in line with the current node i

            # Iterate until all nodes in the row are uncovered
            while j != i:

                # Relink, increase the row size then move over in the row
                j.below.above = j
                j.above.below = j
                j.column.size += 1
                j = j.left

            i = i.above

        column.right.left = column
        column.left.right = column

    # Method to recursively search the cover table and cover columns until a solution is generated, adding rows to the
    # partial solution for each new depth of a branch.
    # The search algorithm is adapted from aforementioned pseudocode with alterations made using the worded description
    # of Algorithm X from Wikipedia [Ref 6]
    def search(self, h, solution):

        # If there are no columns left to search so the table can be considered empty, you can assume a solution has
        # been found
        if self.head == self.head.left:

            return True, solution

        # We need to find the column with the least nodes in it and cover it (and any rows that cross it)
        column = self.s_heuristic()
        self.cover(column)

        row = column.below                              # As defined by Wikipedia, "Choose a row r such that r,c = 1"

        while row != column:                            # For each column

            solution.append(row)                        # Add the row number to the partial solution
            j = row.right

            while j != row:                             # For each row...

                self.cover(j.column)                    # Delete row i, column j from the matrix
                j = j.right

            # Repeat the process recursively on the table until a solution exists
            h, solution = self.search(h, solution)

            if h:

                return True, solution

            # If a solution is not found, backtrack and uncover any columns that were covered along the way
            row = solution.pop()
            column = row.column
            j = row.left

            while j != row:

                self.uncover(j.column)
                j = j.left

            row = row.below

        self.uncover(column)
        return False, solution                      # A solution has not been generated (and likely doesn't exist)


# Method to solve an input sudoku puzzle
def sudoku_solver(sudoku):

    # Donald Knuth suggested a single string of values as an input for easy indexing but flattening the 9x9 grid into
    # a 1x81 grid works just as well
    flattened_sudoku = sudoku.flatten()

    solve = AlgorithmX()                            # Initialise the Knuth Algorithm X class, creating the header node
    solve.exact_cover_table(flattened_sudoku)       # Create the cover table based on the input sudoku

    # Search the cover table and cut it down to find a solution. For each level of a branch, each new row for a partial
    # solution is appended to an empty array
    h, solved = solve.search(False, [])

    # We'll be overwriting the values of a 1x81 array of zeroes
    solution = np.array([0] * 81)

    # If the solution doesn't exist, print the array of -1s
    if not h:

        fail = (solution - 1).reshape(9, 9)
        return fail

    # If the solution has been found, adjust the row numbers of the solution to find their cell value
    for i in solved:

        cell_value = i.row % 9
        solution[(i.row - 1) // 9] = cell_value

    # Because 9 % 9 = 0, any cells with value 9 will be 0. We have to change these to 9s before reshaping and returning
    solved_sudoku = np.where(solution == 0, 9, solution).reshape(9, 9)

    return solved_sudoku


# -------------------------------------------------------------------------------------
#                               REFERENCES
#                      (Can also be found in readme)
# -------------------------------------------------------------------------------------

# [Ref 1] 2021, Berry, J., Solving Sudoku with Dancing Links [Online]
# Available from: https://taeric.github.io/Sudoku.html
# [Accessed 11/02/21]

# [Ref 2] Hanson, R., Sudoku Exact Cover Matrix
# Available from: https://www.stolaf.edu/people/hansonr/sudoku/exactcovermatrix.htm
# [Accessed 11/02/21]

# [Ref 3] 2007, Tjensvold, J. M., Generic Distributed Exact Cover Solver Report
# Available from: https://janmagnet.files.wordpress.com/2008/07/decs-report-draft-02.pdf
# [Accessed 16/02/21]

# [Ref 4] 2000, Knuth, D. E., Dancing Links Report
# Available from: https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/0011047.pdf
# [Accessed 18/02/21]

# [Ref 5] 2014, Harrysson, M. & Laestander, H., Solving Sudoku Efficiently with Dancing Links
# Available from: https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf
# [Accessed 19/02/21]

# [Ref 6] 2020, Wikipedia, Knuth's Algorithm X
# Available from: https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X
# [Accessed 19/02/21]


if __name__ == "__main__":

    test_grid = np.array([[9, 0, 7, 0, 0, 0, 6, 5, 1],
                          [1, 0, 5, 0, 9, 0, 0, 8, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 5, 0, 4, 0, 0, 0, 0, 0],
                          [0, 2, 0, 0, 0, 0, 0, 4, 0],
                          [0, 0, 1, 0, 0, 6, 0, 0, 0],
                          [0, 0, 8, 6, 0, 0, 0, 3, 0],
                          [0, 0, 4, 1, 0, 0, 9, 0, 0],
                          [0, 0, 9, 0, 5, 0, 0, 6, 0]])

    out = sudoku_solver(test_grid)
    print(out)

