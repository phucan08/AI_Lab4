# CLASS DESCRIPTION FOR CONSTRAINT SATISFACTION PROBLEM (CSP)

from util import *

class csp:

    # INITIALIZING THE CSP
    def __init__(self, domain=digits, grid=""):
        """
        Unitlist consists of the 27 lists of peers
        Units is a dictionary consisting of the keys and the corresponding lists of peers
        Peers is a dictionary consisting of the 81 keys and the corresponding set of 27 peers
        Constraints denote the various all-different constraints between the variables
        """
        self.domain = domain
        self.variables = squares
        
        # Create unitlist: 27 units total (9 rows, 9 columns, 9 3x3 boxes)
        self.unitlist = (
            # 9 rows
            [cross(r, cols) for r in rows] +
            # 9 columns
            [cross(rows, c) for c in cols] +
            # 9 3x3 boxes
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
        )
        
        # Create units dictionary: for each square, which units does it belong to
        self.units = dict((s, [u for u in self.unitlist if s in u]) for s in self.variables)
        
        # Create peers dictionary: for each square, who are its peers
        self.peers = dict((s, set(sum(self.units[s], [])) - set([s])) for s in self.variables)
        
        # Initialize values from grid if provided
        if grid:
            self.values = self.getDict(grid)
        else:
            # Initialize with full domains for all variables
            self.values = dict((s, domain) for s in self.variables)



    def getDict(self, grid=""):
        """
        Getting the string as input and returning the corresponding dictionary
        """
        i = 0
        values = dict()
        for cell in self.variables:
            if grid[i] != '0':
                values[cell] = grid[i]
            else:
                values[cell] = digits
            i = i + 1
        return values