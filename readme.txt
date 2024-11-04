Sudoku Solver readme submission

My sudoku solver makes use of dancing links, popularised by Donald Knuth. Sudoku can be looked at as an exact cover problem where the 9x9 grid is represented as a large binary table of possible moves (rows) that can be made, against the game's constraints (columns). If a possibility satisfies a constraint, this is shown as a 1 in the table. The columns can then be 'covered.' If any rows in this column have a 1 value, the entire row is also covered. 

This is done using Knuth's Algorithm X. This is a brute force method with backtracking that Knuth designed to solve this problem quickly. Itis a depth-first approach so it is guaranteed to find a solution, but not necessarily the most optimal solution. It is intended to find and return every possible solution to a problem of this type, however since in this case we only need one solution I added functionality that forces the algorithm to return only the first solution it finds (or stop searching if no solution exists). During my research, I found no other algorithm that could match its speed so in spite of its complexity it was clearly the one to work on.

As a basic example of how the algorithm works, let's say we have an arbitrary game with 5 possible moves that can be made, labelled 1 to 5 and 5 constraints rules labelled A to E. We can represent the relationship between possibilities and constraints with sets. These vary depending on the problem. For the sake of example, our relationships will be as follows:

A {1,5}
B {2,4}
C {1,3,5}
D {1,2,3}
E {2,3}

The exact cover table for these sets is as such:


H   A   B   C   D   E
  ______________________
 |                      |
1|  1   0   1   1   0   |
 |                      |
2|  0   1   0   1   1   |
 |                      |
3|  0   0   1   1   1   |
 |                      |
4|  0   1   0   0   0   |
 |                      |
5|  1   0   1   0   0   |
 |______________________|


I will be referring to the possibilities, 1 to 5 as 'moves':
We know the table is not empty so we proceed with Algorithm X. We look at the column with the minimum number of 1s that is closest to the head (at the top left corner) which in this case is A. This is selected deterministically in my approach with the S heuristic created by Knuth (discussed later). The rows for move 1 and 5 are then selected nondeterministically. The row for move 1 is added to the first level 1 branch of partial solution (which will be an empty list at this point). 

In the row for move 1, columns A, C and D have a value of 1. We therefore cover over these columns to reduce the table. This also means that any rows in these columns with 1s are also covered. In our example, rows 1, 2, 3 and 5 must be covered.


H   B   E
  __________
 |          |
4|  1   0   |
 |__________|


Only the row for move 4 remains. The table cannot be reduced any further but the lowest number of 1s in zero so this solution is incomplete and the branch must terminate so we backtrack to the row for move 5 as the next level 1 branch.

We use the same principle used with row 1. Columns A and C must be covered. Row 1 is added to our partial solution. Rows 1, 3 and 5 have 1s in these columns and must be covered also. This leaves us with another reduced matrix.


H   B   C   E
  ______________
 |              |
2|  1   0   1   |
 |              |
4|  1   0   0   |
 |______________|


The lowest number of 1s in a column here is in E. We move down to level 2 of this branch and add Row 2 to our partial solution but again, we can see there will still be at least one 0 in our reduced solution so the algorithm terminates this branch.
Backtracking back to our original table, there are no more 1s to explore in column A: 


H   A   B   C   D   E
  ______________________
 |                      |
1|  1   0   1   1   0   |
 |                      |
2|  0   1   0   1   1   |
 |                      |
3|  0   0   1   1   1   |
 |                      |
4|  0   1   0   0   0   |
 |                      |
5|  1   0   1   0   0   |
 |______________________|
 

We move on to the next minimum column which is B. We will reduce this, selecting row 2 as the next branch at level 1. This time, our reduction is successful. If we focus on column B and row 2, adding the latter to our partial solution, we get the following reduced matrix:


H   A   C
  __________
 |          |
5|  1   1   |
 |__________|
 

There are only 1s remaining so the table is deemed empty. Row 5 still exists and is added to the partial solution. This is considered a successful solution and the algorithm either terminates or tries to find more solutions depending on the application.

With the above, we can say the exact cover is S* = {Move 2, Move 5}. 

If we look back at the relationships between possibilities and constraints, each of these successful moves is only present in constraints A to E once: 

Move 2 {B,D,E}
Move 5 {A,C}

In the context of the game, if moves 2 and 5 are played, you win.

Naturally, the table for sudoku is significantly bigger than this example. You need to reduce the table such that there are 81 values added to the partial solution. These will be the row numbers that correlate to a specific value in a specific cell of the sudoku grid. For instance, the possibility of the cell in column 2, row 3 of the sudoku grid (index of 20) having a value 5 would be row 185 in the cover table (20 * 9 + 5)

With Knuth's dancing links, this table is shown as a circular doubly linked list. The column header nodes are linked together by left-right pointers but also have pointers to the row nodes above/below them. They have to be unlinked when covering - not removed - so you can backtrack. The nodes also need a numerical designator for the row and one for the column, although this should be stored as the actual column header node rather than a number so links can be made more easily. For the nodes we make specifically used as column headers, I keep track of the column size as the covering process is reliant on this. These principles are difficult to show in a text file so this image from Jonathan Chu at Berkeley may better explain it [Ref 1]:
https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/Knuth-figure-3.png

There are 81 cells on a 9x9 sudoku grid. We can put one of nine values in each cell. This means there are 81 x 9 = 729 possible moves you can make and therefore 729 rows. Constraints are not as straight forward. There are four rules in sudoku we need to consider:

Cell rule: You cannot place one number in a column, then another number in a row where the column and row intersect. In other words, you aren't allowed to put two numbers in one box. There are 81 places where a column and row intersect (81 cells) so there are 81 constraints.

Row rule: You can only have one number from 1 - 9 represented in each row. You cannot have the number 5 appear twice in any row for example. There are 9 cells in any row with 9 possible values that can occupy any cell. There are therefore 81 constraints to work with here.

Column rule: Identical in principle to the row rule but for columns. 9 cells with 9 possible values, thus 81 constraints.

3x3 Box rule: The 3x3 boxes in the corners, middle and mid-edges of the sudoku grid work in the same way as the columns and rows. Again, 9 cells, 9 possible values so 81 constraints.

There are 324 constraints in total. So, the table for an EMPTY sudoku grid will be 729 x 324. When implementing, it was imperative to be able to make the whole table as an input problem could have any number of the cells filled in or empty. 

There exists a text based representation of the entire table created by R. Hanson of stolaf.edu [Ref 2]:
https://www.stolaf.edu/people/hansonr/sudoku/exactcovermatrix.htm

This resource was instrumental in my implementation as it allowed me to see which parts of the table should be a 0 and which a 1 then recognise patterns so it can be quickly created in code with functions. I did not want to make the table manually - this would take far too much time as it would mean tediously linking every node and adding coordinates, then painstakingly cutting the table down to account for cells that are already filled in.

For any row, there is a single 1 for each constraint rule. I found that I needed to translate a single index and the cell value into 4 separate values ranging from 1 to 324 to satisfy the constraints match Hanson's table. The process for creating the equations by recognising the patterns in the table was arduous. Therefore, as to not add an additional few pages to this file, I recorded my testing and thought process for this in a document that can be accessed with this link:
https://docs.google.com/document/d/1Oun9dEATxTCuPAPn8dRHqgRnc20kivpUTHAvRA6qd3Q/edit?usp=sharing

With these equations, creating the four nodes per row is as easy as knowing the index in the sudoku grid we're looking at and the value that is / can possibly be in the cell. We set the row number based on both of these parameters, and the equations give us the column number for each node - this also means that storing column header nodes in a global list for easy access is important. Once the four nodes are made, they must be circularly linked to eachother, so node 1 is linked to both node 2 and node 4:

                ________       ________       ________       ________
To Node 4  <-- |        | <-- |        | <-- |        | <-- |        | <-- From Node 1   
               | Node 1 |     | Node 2 |     | Node 3 |     | Node 4 |
From Node 4--> |________| --> |________| --> |________| --> |________| --> To Node 1


Because each new set of nodes will be created at the current bottom of the table and the vertical links are also circular, linking above and below is as easy as pointing down at the column header and up at current lowest node in their respective column (which the column header is currently pointing up at and can be accessed as columnheader.above).


                 |    ^
                 |    |
                 v    |
                ________                          
To Header  <-- |        | <--   
               |ColNode1|       ...etc
From Header--> |________| -->  

                 |    ^
                 |    |
                 v    |
                ________       ________       ________       ________
To Node 4  <-- |        | <-- |        | <-- |        | <-- |        | <-- From Node 1   
               | Node 1 |     | Node 2 |     | Node 3 |     | Node 4 |
From Node 4--> |________| --> |________| --> |________| --> |________| --> To Node 1

                 |    ^
                 |    |
                 v    |


Now that the table is complete, the sudoku can be solved by throwing it through Algorithm X. I made use of the extensive documentation that exists to make the algorithm. Mattias Harrysson and Hjalmar Laestander of the Swedish KTH Institute of Technology, in their report on the use of dancing links for solving exact cover problems [Ref 3], created helpful pseudocode for the searching, covering and uncovering that I made use of when developing. The search method is recursive and continuously covers columns then backtracks until a solution is found/not found. A boolean variable must be added (that they refer to as 'h') that is returned as positive if the puzzle is solved and checked for each loop of the recursion. Because of this h variable, we can easily tell if a solution was found at the end of a branch - if it comes back false, we can keep going until all branches are explored and then assume outputting the array of -1s is the correct course of action. 

Covering columns, as shown in my example, relies on the length of the columns. As Donald Knuth himself found [Ref 4], if time is a factor you cannot iterate through every column header breadth-wise as this enlarges the algorithm's branching factor. Instead he created his S Heuristic using a constantly updating size parameter s to find the minimum sized column quickly. Because an exact cover problem could be infinitely large, it is advised to set this variable as infinity - I do not know how to do this in Python so I used the max possible column size of 729 + 1 = 730. Another publication by Jan Magne Tjensvold about a generic implementation of AlgorithmX had useful pseudocode that I used as a basis when making my method for the S Heuristic [Ref 5].

As far as the input sudoku grid is concerned, I found it far easier to make the cover table when the sudoku is flattened out row-wise into a 1x81 array. Knuth himself used an 81 character string as his format in a 2005 programming competition to solve a similar problem. This makes indexing far easier as if we were to add nodes for the value of 5 in row 9, column 9 of the sudoku grid, we can simply multiply the index of 81 by 9, then add 5 which gives us an exact row number. Using an unedited 9x9 grid would mean performing unnecessary conversions and mathematics to achieve the desired results. The 1x81 grid has to be restructured into the 9x9 grid once the solution is found which can be done easily using numpy.


----------------------------------------------------------- REFERENCES ---------------------------------------------------------------


[Ref 1] 2006, Chu, J., Dancing Links Algorithm Figure [Online]
Available from: https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/Knuth-figure-3.png
[Accessed 04/03/21]

[Ref 2] Hanson, R., Sudoku Exact Cover Matrix [Online]
Available from: https://www.stolaf.edu/people/hansonr/sudoku/exactcovermatrix.htm
[Accessed 11/02/21]

[Ref 3] 2014, Harrysson, M. & Laestander, H., Solving Sudoku Efficiently with Dancing Links [Online]
Available from: https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf
[Accessed 19/02/21]

[Ref 4] 2000, Knuth, D. E., Dancing Links Report [Online]
Available from: https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/0011047.pdf
[Accessed 18/02/21]

[Ref 5] 2007, Tjensvold, J. M., Generic Distributed Exact Cover Solver Report [Online]
Available from: https://janmagnet.files.wordpress.com/2008/07/decs-report-draft-02.pdf
[Accessed 16/02/21]


Other references from the comments of my code:

[Additional Ref 1] 2021, Berry, J., Solving Sudoku with Dancing Links [Online]
Available from: https://taeric.github.io/Sudoku.html
[Accessed 11/02/21]

[Additional Ref 2] 2020, Wikipedia, Knuth's Algorithm X [Online]
Available from: https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X
[Accessed 19/02/21]
