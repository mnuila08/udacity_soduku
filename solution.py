
# Global variables:
rows = 'ABCDEFGHI'
cols = '123456789'
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [ a +b for a in A for b in B]


# Assign global values: (used in regular sodoku)
boxes = cross(rows, cols)
unitlist = \
([cross(rows, c) for c in cols] + [cross(r, cols) for r in rows] + [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs
                                                                   in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

assignments = []


def assign_value(values, box, value):
    """
        Please use this function to update your values dictionary!
        Assigns a value to a given box. If it updates the board record it.
        """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def find_naked_twins_unit(values, unit):
    naked_twins = []
    # Find all instances of naked twins
    for box in unit:
        # if only two values in the box, continue:
        if len(values[box]) == 2:
            for peer in peers[box]:
                if values[peer] == values[peer] and box != peer:  # check it's not the same box
                    naked_twins.append([box, peer])
    return naked_twins if len(naked_twins) > 0 else False


def remove_naked_twins_unit(values, naked_twins):
    for twins in naked_twins:
        peers_tw1 = set(peers[twins[0]])
        peers_tw2 = set(peers[twins[1]])
        peers_12 = set(peers_tw1).intersection(peers_tw2)  # want the peers that exist in both (intersection)
        for pbox in peers_12:
            # check if pbox is not one of the twins and its values are more than 2:
            if pbox != twins[0] and pbox != twins[1] and len(values[pbox]) > 2:
                values = assign_value(values, pbox, values[pbox].replace(values[twins[0]][0], ''))
                values = assign_value(values, pbox, values[pbox].replace(values[twins[0]][1], ''))
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
        Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

        Returns:
        the values dictionary with the naked twins eliminated from peers.
        """

    naked_twins = []
    for unit in unitlist:
        naked_twins = find_naked_twins_unit(values, unit)
        if naked_twins and len(naked_twins) > 0:
            for value in naked_twins:
                values = remove_naked_twins_unit(value, naked_twins)

    return values


# ----------------------------------------------------------------------------------------------------------------#
# Problem 2:



# Create our diagonals:
diagonal1 = [rows[i] + cols[i] for i in range(len(rows))]  # A1, B2, ...I9
reverse_cols = cols[::-1]
diagonal2 = [rows[i] + reverse_cols[i] for i in range(len(rows))]  # A9, B8, ..., I1
diag_unitlist = [diagonal1 + diagonal2] + unitlist
diag_units = [[r+c for r,c in zip(rows, cols)], [r+c for r,c in zip(rows, cols[::-1])]]  # create our dictionary of all units (including diagonal)
diag_peers = dict((s, set(sum(diag_units[s], [])) - set([s])) for s in boxes)  # create our peers with diagonal entries


def grid_values(grid):
    """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Args:
        grid(string) - A grid in string form.
        Returns:
        A grid in dictionary form
        Keys: The boxes, e.g., 'A1'
        Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))


def display(values):
    """
        Display the values as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
        Iterates through all values boxes. If the box only has 1 value,
        it removes that value from all the diagonal peers of this box as well.
        """
    solved = [b for b in values.keys() if len(values[b]) == 1]
    for b in solved:
        d = values[b]
        for peer in diag_peers[b]:
            values[peer] = values[peer].replace(d, '')
            
    return values


def only_choice(values):
    """
        Iterates through the diagonal unit lists. If a unit has a certain value d
        for only one box, the box is assigned the value d
        """
    for unit in diag_unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """
        Continuously uses only_choice function and eliminate to reduce the puzzle
        until the sudoku stays the same during an iteration.
        """
    stalled = False
    while not stalled:
        # how many were solved before the reduction:
        solved_before = len([box for box in values.keys() if len(values[box]) == 1])
        # solve using eliminate strategy
        values = eliminate(values)
        # solve using only_choice strategy
        values = only_choice(values)
        #reduce using naked_twins
        values = naked_twins(values)
        # find out how many are solved now:
        solved_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_before == solved_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False  # Failed earlier
    if all(len(values[s] == 1 for s in boxes)):
        return values  # Solved
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
        Find the solution to a Sudoku grid.
        Args:
        grid(string): a string representing a sudoku grid.
        Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
        """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
