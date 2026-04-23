"""
In search.py, you will implement Backtracking and AC3 searching algorithms
for solving Sudoku problem which is called by sudoku.py
"""

from csp import *
from copy import deepcopy
import util



def Backtracking_Search(csp):
    """
    Backtracking search initialize the initial assignment
    and calls the recursive backtrack function
    """
    # Start with an empty assignment
    assignment = {}
    # Start recursive backtracking
    return Recursive_Backtracking(assignment, csp)


def Recursive_Backtracking(assignment, csp):
    """
    The recursive function which assigns value using backtracking
    """
    # Check if assignment is complete
    if isComplete(assignment):
        return csp.values
    
    # Select an unassigned variable using MRV heuristic
    var = Select_Unassigned_Variables(assignment, csp)
    
    # Try each value in the domain for this variable
    for value in Order_Domain_Values(var, assignment, csp):
        # Check if the value is consistent with current assignment
        if isConsistent(var, value, assignment, csp):
            # Make a copy of the current state for backtracking
            old_values = deepcopy(csp.values)
            
            # Record inference for later restoration
            inferences = {}
            
            # Apply the assignment
            assignment[var] = value
            csp.values[var] = value
            
            # Forward checking: apply inferences
            inference_result = Inference(assignment, inferences, csp, var, value)
            
            # If inference didn't fail, continue recursively
            if inference_result != "FAILURE":
                result = Recursive_Backtracking(assignment, csp)
                if result != "FAILURE":
                    return result
            
            # Backtrack: restore the previous state
            del assignment[var]
            csp.values = old_values
    
    return "FAILURE"

def Inference(assignment, inferences, csp, var, value):
    """
    Forward checking using concept of Inferences
    """

    inferences[var] = value

    for neighbor in csp.peers[var]:
        if neighbor not in assignment and value in csp.values[neighbor]:
            if len(csp.values[neighbor]) == 1:
                return "FAILURE"

            remaining = csp.values[neighbor] = csp.values[neighbor].replace(value, "")

            if len(remaining) == 1:
                flag = Inference(assignment, inferences, csp, neighbor, remaining)
                if flag == "FAILURE":
                    return "FAILURE"

    return inferences

def Order_Domain_Values(var, assignment, csp):
    """
    Returns string of values of given variable
    """
    return csp.values[var]

def Select_Unassigned_Variables(assignment, csp):
    """
    Selects new variable to be assigned using minimum remaining value (MRV)
    """
    unassigned_variables = dict((squares, len(csp.values[squares])) for squares in csp.values if squares not in assignment.keys())
    mrv = min(unassigned_variables, key=unassigned_variables.get)
    return mrv

def isComplete(assignment):
    """
    Check if assignment is complete
    """
    return set(assignment.keys()) == set(squares)

def isConsistent(var, value, assignment, csp):
    """
    Check if assignment is consistent
    """
    for neighbor in csp.peers[var]:
        if neighbor in assignment.keys() and assignment[neighbor] == value:
            return False
    return True

def forward_checking(csp, assignment, var, value):
    csp.values[var] = value
    for neighbor in csp.peers[var]:
        csp.values[neighbor] = csp.values[neighbor].replace(value, '')

def revise(csp, xi, xj):
    """
    Remove inconsistent values from csp.values[xi]
    If a value x in Xi's domain cannot be satisfied by any value y in Xj's domain, remove x
    In Sudoku, values must be different (all-different constraint)
    """
    revised = False
    for x in list(csp.values[xi]):
        # For Sudoku all-different constraint, we need at least one different value in Xj
        # Check if there's any value in Xj that is compatible with x
        compatible = False
        for y in csp.values[xj]:
            if x != y:  # All-different constraint: values must be different
                compatible = True
                break
        
        # If no compatible value found, remove x from Xi's domain
        if not compatible:
            csp.values[xi] = csp.values[xi].replace(x, '')
            revised = True
    
    return revised

def AC3(csp):
    """
    AC-3 constraint propagation algorithm
    Maintains arc consistency to reduce the domain of variables
    Returns False if a contradiction is found, True otherwise
    """
    # Initialize queue with all arcs (Xi, Xj) where Xi and Xj are neighbors
    queue = []
    for var in csp.variables:
        for neighbor in csp.peers[var]:
            queue.append((var, neighbor))
    
    # Process arcs until queue is empty
    while queue:
        (xi, xj) = queue.pop(0)
        
        # Revise the domain of Xi with respect to Xj
        if revise(csp, xi, xj):
            # If Xi's domain is empty, no solution exists
            if len(csp.values[xi]) == 0:
                return False
            
            # If Xi's domain was revised, add all arcs (Xk, Xi) back to queue
            for xk in csp.peers[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    
    return True

def display(values):
    """
    Display the solved sudoku on screen
    """
    for row in rows:
        if row in 'DG':
            print("-------------------------------------------")
        for col in cols:
            if col in '47':
                print(' | ', values[row + col], ' ', end=' ')
            else:
                print(values[row + col], ' ', end=' ')
        print(end='\n')

def write(values):
    """
    Write the string output of solved sudoku to file
    """
    output = ""
    for variable in squares:
        output = output + values[variable]
    return output