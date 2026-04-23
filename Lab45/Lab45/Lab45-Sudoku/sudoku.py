# THE FUNCTION WHICH SOLVES ALL THE SUDOKU PROBLEMS
# IN THE INPUT FILE USING BACKTRACKING AND WRITES THE OUTPUT TO THE OUTPUT FILE

from search import *
import time
import argparse
import os

#THE MAIN FUNCTION GOES HERE
if __name__ == "__main__":
    """
    The function takes arguments from commandline as follow
    python3 sudoku.py --inputFile data/euler.txt 
    """
    argument_parser = argparse.ArgumentParser(description="Sudoku Solving Problem")
    argument_parser.add_argument("--inputFile", type=str, default="data/euler.txt", help="Sudoku Input File")
    args = argument_parser.parse_args()

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If relative path, make it relative to script directory
    if not os.path.isabs(args.inputFile):
        filename = os.path.join(script_dir, args.inputFile)
    else:
        filename = args.inputFile
    
    array = []
    with open(filename, "r") as ins:
        for line in ins:
            array.append(line)
    ins.close()
    i = 0
    boardno = 0
    start = time.time()
    f = open("output.txt", "w")
    for grid in array:
        startpuzle = time.time()
        boardno = boardno + 1
        sudoku = csp(grid=grid)
        solved = Backtracking_Search(sudoku)
        print("The board - ", boardno, " takes ", time.time() - startpuzle, " seconds")
        if solved != "FAILURE":
            print("After solving: ")
            display(solved)
            f.write(write(solved)+"\n")
            i = i + 1

    f.close()
    print ("Number of problems solved is: ", i)
    print ("Time taken to solve the puzzles is: ", time.time() - start)