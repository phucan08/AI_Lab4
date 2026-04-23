#!/usr/bin/env python3
"""
Sudoku GUI Solver with Interactive Solving and Hints
Features:
- 3 difficulty levels (Easy, Normal, Hard)
- Interactive puzzle solving
- Hint system using CSP algorithms
- Visual solving process
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
from csp import csp
from search import Backtracking_Search, AC3
from util import digits, rows, cols, cross, squares

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver - Interactive")
        self.root.geometry("800x900")

        # Game state
        self.current_puzzle = None
        self.solution = None
        self.user_entries = {}
        self.hints_used = 0

        # Create GUI elements
        self.create_widgets()

        # Generate initial puzzle
        self.new_game("Normal")

    def create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_label = tk.Label(self.root, text="Sudoku Solver", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)

        # Difficulty selection
        difficulty_frame = tk.Frame(self.root)
        difficulty_frame.pack(pady=5)

        tk.Label(difficulty_frame, text="Difficulty:", font=("Arial", 12)).pack(side=tk.LEFT)

        self.difficulty_var = tk.StringVar(value="Normal")
        difficulties = ["Easy", "Normal", "Hard"]

        for diff in difficulties:
            tk.Radiobutton(difficulty_frame, text=diff, variable=self.difficulty_var,
                          value=diff, command=self.change_difficulty).pack(side=tk.LEFT, padx=10)

        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="New Game", command=lambda: self.new_game(self.difficulty_var.get()),
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Solve Step-by-Step", command=self.solve_step_by_step,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Get Hint", command=self.get_hint,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Check Solution", command=self.check_solution,
                 bg="#9C27B0", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Reset", command=self.reset_puzzle,
                 bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # Stats frame
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(pady=5)

        self.stats_label = tk.Label(stats_frame, text="Hints used: 0 | Cells filled: 0/81",
                                   font=("Arial", 10))
        self.stats_label.pack()

        # Sudoku grid
        self.create_grid()

        # Status label
        self.status_label = tk.Label(self.root, text="Ready to play!", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def create_grid(self):
        """Create the 9x9 Sudoku grid"""
        grid_frame = tk.Frame(self.root, bd=2, relief="solid")
        grid_frame.pack(pady=10)

        self.cells = {}

        for i in range(9):
            for j in range(9):
                # Determine cell position and styling
                cell_name = rows[i] + cols[j]

                # Create frame for 3x3 box borders
                cell_frame = tk.Frame(grid_frame, bd=1, relief="solid",
                                    width=50, height=50)

                # Thicker borders for 3x3 box boundaries
                if i % 3 == 0 and i != 0:
                    cell_frame.config(bd=3)
                if j % 3 == 0 and j != 0:
                    cell_frame.config(bd=3)

                cell_frame.grid(row=i, column=j, sticky="nsew")
                cell_frame.grid_propagate(False)

                # Create entry widget
                entry = tk.Entry(cell_frame, font=("Arial", 16, "bold"), justify="center",
                               width=2, bd=0)
                entry.pack(expand=True, fill="both")

                # Bind events
                entry.bind('<KeyRelease>', lambda e, cell=cell_name: self.on_cell_change(cell))
                entry.bind('<FocusIn>', lambda e, cell=cell_name: self.on_cell_focus(cell))

                self.cells[cell_name] = entry

        # Configure grid weights
        for i in range(9):
            grid_frame.grid_rowconfigure(i, weight=1)
            grid_frame.grid_columnconfigure(i, weight=1)

    def generate_puzzle(self, difficulty):
        """Generate a new puzzle with given difficulty"""

        # Start with a solved puzzle
        solved_puzzle = self.generate_solved_puzzle()

        # Remove cells based on difficulty
        cells_to_remove = {
            "Easy": 30,    # Remove 30 cells (51 clues)
            "Normal": 45,  # Remove 45 cells (36 clues)
            "Hard": 55     # Remove 55 cells (26 clues)
        }

        puzzle = solved_puzzle.copy()
        cells = list(squares)
        random.shuffle(cells)

        for cell in cells[:cells_to_remove[difficulty]]:
            puzzle[cell] = '0'

        return puzzle, solved_puzzle

    def generate_solved_puzzle(self):
        """Generate a random solved Sudoku puzzle"""
        # Create empty puzzle
        puzzle = dict((s, '0') for s in squares)

        # Fill diagonal 3x3 boxes first (they don't constrain each other)
        self.fill_diagonal_boxes(puzzle)

        # Solve the rest using backtracking
        sudoku_csp = csp(grid=''.join([puzzle[s] for s in squares]))
        solved = Backtracking_Search(sudoku_csp)

        if solved == "FAILURE":
            return self.generate_solved_puzzle()  # Try again

        return solved

    def fill_diagonal_boxes(self, puzzle):
        """Fill the three diagonal 3x3 boxes"""
        boxes = [
            [rows[i] + cols[j] for i in range(3) for j in range(3)],  # Top-left
            [rows[i] + cols[j] for i in range(3,6) for j in range(3,6)],  # Center
            [rows[i] + cols[j] for i in range(6,9) for j in range(6,9)]   # Bottom-right
        ]

        for box in boxes:
            nums = list(digits)
            random.shuffle(nums)
            for cell, num in zip(box, nums):
                puzzle[cell] = num

    def new_game(self, difficulty):
        """Start a new game with given difficulty"""
        self.current_puzzle, self.solution = self.generate_puzzle(difficulty)
        self.user_entries = {}
        self.hints_used = 0
        self.update_display()
        self.update_stats()
        self.status_label.config(text=f"New {difficulty} game started!")

    def change_difficulty(self):
        """Change difficulty and start new game"""
        self.new_game(self.difficulty_var.get())

    def update_display(self):
        """Update the grid display"""
        for cell in squares:
            entry = self.cells[cell]
            value = self.current_puzzle[cell]

            if value != '0':
                entry.delete(0, tk.END)
                entry.insert(0, value)
                entry.config(state="disabled", bg="#E8E8E8")  # Clue cells
            else:
                entry.config(state="normal", bg="white")
                if cell in self.user_entries:
                    entry.delete(0, tk.END)
                    entry.insert(0, self.user_entries[cell])

    def on_cell_change(self, cell):
        """Handle cell value changes"""
        entry = self.cells[cell]
        value = entry.get().strip()

        # Validate input
        if value and (len(value) != 1 or value not in digits):
            entry.delete(0, tk.END)
            return

        # Update user entries
        if value:
            self.user_entries[cell] = value
        elif cell in self.user_entries:
            del self.user_entries[cell]

        self.update_stats()

    def on_cell_focus(self, cell):
        """Handle cell focus events"""
        # Highlight related cells (same row, column, box)
        self.highlight_related_cells(cell)

    def highlight_related_cells(self, cell):
        """Highlight cells in same row, column, and box"""
        related = set(self.get_related_cells(cell))

        for c in squares:
            if c in related:
                self.cells[c].config(bg="#FFFACD")  # Light yellow
            else:
                # Reset to appropriate color
                if self.current_puzzle[c] != '0':
                    self.cells[c].config(bg="#E8E8E8")  # Clue
                else:
                    self.cells[c].config(bg="white")  # Empty

    def get_related_cells(self, cell):
        """Get cells in same row, column, and box"""
        sudoku_csp = csp()
        return sudoku_csp.peers[cell]

    def get_hint(self):
        """Provide a hint for the next move"""
        if not self.solution:
            messagebox.showinfo("No Puzzle", "Start a new game first!")
            return

        # Find empty cells
        empty_cells = [cell for cell in squares
                      if self.current_puzzle[cell] == '0' and cell not in self.user_entries]

        if not empty_cells:
            messagebox.showinfo("Complete", "Puzzle is already complete!")
            return

        # Use MRV heuristic to find most constrained cell
        sudoku_csp = csp()
        sudoku_csp.values = self.get_current_values()

        # Apply AC-3 to reduce domains
        AC3(sudoku_csp)

        # Find cell with smallest domain
        min_domain_size = float('inf')
        best_cell = None

        for cell in empty_cells:
            domain_size = len(sudoku_csp.values[cell])
            if domain_size < min_domain_size:
                min_domain_size = domain_size
                best_cell = cell

        if best_cell:
            correct_value = self.solution[best_cell]
            possible_values = list(sudoku_csp.values[best_cell])

            if len(possible_values) == 1:
                hint = f"Cell {best_cell}: Must be {possible_values[0]} (only possibility)"
            else:
                hint = f"Cell {best_cell}: Try {correct_value} (one of {len(possible_values)} possibilities: {''.join(sorted(possible_values))})"

            self.hints_used += 1
            self.update_stats()
            self.status_label.config(text=hint)

            # Highlight the suggested cell
            self.cells[best_cell].config(bg="#90EE90")  # Light green
            self.root.after(2000, lambda: self.reset_cell_colors())  # Reset after 2 seconds
        else:
            self.status_label.config(text="No hints available!")

    def reset_cell_colors(self):
        """Reset cell background colors"""
        for cell in squares:
            if self.current_puzzle[cell] != '0':
                self.cells[cell].config(bg="#E8E8E8")
            else:
                self.cells[cell].config(bg="white")

    def solve_step_by_step(self):
        """Solve the puzzle step by step"""
        if not self.solution:
            messagebox.showinfo("No Puzzle", "Start a new game first!")
            return

        # Get current state
        current_values = self.get_current_values()

        # Find next move using backtracking
        sudoku_csp = csp()
        sudoku_csp.values = current_values.copy()

        # Apply AC-3 to reduce domains before looking for steps
        AC3(sudoku_csp)

        # Try to find one solution step
        assignment = {}
        for cell in squares:
            cell_value = current_values[cell]
            if isinstance(cell_value, str) and len(cell_value) == 1 and cell_value != '0':
                assignment[cell] = cell_value

        # Use the solver to find next logical step
        result = self.find_next_step(sudoku_csp, assignment)

        if result:
            cell, value = result
            self.user_entries[cell] = value
            self.update_display()
            self.update_stats()
            self.status_label.config(text=f"Step: Cell {cell} = {value}")

            # Highlight the filled cell
            self.cells[cell].config(bg="#90EE90")
            self.root.after(1000, lambda: self.reset_cell_colors())
        else:
            self.status_label.config(text="No more steps available!")

    def find_next_step(self, csp_obj, assignment):
        """Find the next logical step in solving"""
        # Look for naked singles (cells with only one possibility)
        for cell in squares:
            if cell not in assignment:
                cell_values = csp_obj.values[cell]
                if isinstance(cell_values, str) and len(cell_values) == 1:
                    return (cell, cell_values)

        # Look for cells that can only have one value in their unit
        for unit in csp_obj.unitlist:
            for digit in digits:
                possible_cells = [cell for cell in unit
                                if cell not in assignment and digit in str(csp_obj.values[cell])]
                if len(possible_cells) == 1:
                    return (possible_cells[0], digit)

        return None

    def check_solution(self):
        """Check if current solution is correct"""
        if not self.solution:
            messagebox.showinfo("No Puzzle", "Start a new game first!")
            return

        correct = True
        errors = []

        for cell in squares:
            user_value = self.user_entries.get(cell, '')
            correct_value = self.solution[cell]

            if user_value != correct_value:
                correct = False
                errors.append(cell)
                self.cells[cell].config(bg="#FFB6C1")  # Light red for errors

        if correct:
            messagebox.showinfo("Congratulations!", "Puzzle solved correctly! 🎉")
            self.status_label.config(text="Puzzle solved correctly!")
        else:
            self.status_label.config(text=f"Errors in {len(errors)} cells. Try again!")
            self.root.after(3000, lambda: self.reset_cell_colors())

    def reset_puzzle(self):
        """Reset puzzle to initial state"""
        self.user_entries = {}
        self.hints_used = 0
        self.update_display()
        self.update_stats()
        self.status_label.config(text="Puzzle reset!")

    def get_current_values(self):
        """Get current values including user entries in CSP format"""
        values = {}
        for cell in squares:
            if cell in self.user_entries:
                # User has entered a value
                values[cell] = self.user_entries[cell]
            elif self.current_puzzle[cell] != '0':
                # Clue cell
                values[cell] = self.current_puzzle[cell]
            else:
                # Empty cell - full domain
                values[cell] = digits
        return values

    def update_stats(self):
        """Update statistics display"""
        filled_cells = len(self.user_entries)
        self.stats_label.config(text=f"Hints used: {self.hints_used} | Cells filled: {filled_cells}/81")

def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()