# irrad_balancer.py
# 5/20/19 by Eric Graves

# GOALS:
# -- Recreate results of https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6317197
# -- Use Python logging to make testable and deployable code
# -- Create robustly-testable script and then optimize it later

#TODO:
# -- Keep track of transformations to map original layout to switching layout

# Use Irradiance Equalization Principle to sort solar cells to optimize
# irradiance of individual cells in a switched-array
# =============================================================================

# Imports
import numpy as np
import logging
import math

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Testing logging")

# =============================================================================
# ======================= USER CONTROLS FOR TESTING ===========================
input_rows = 4 # rows
input_cols = 15 # cols
# =============================================================================
# ==== Function to sort array elements and flip every other row ===============
def sort_and_flip(test_array):

    # Input array [n by m], get shape for robustness
    [n,m] = test_array.shape # rows, cols
    test_array_out = np.zeros((n,m))

    # Sort array elements in descending order
    # -- Flatten into single row
    test_array_flat = test_array.flatten()
    logging.debug(test_array_flat.shape)
    # -- Sort elements
    test_array_flat_sorted = np.sort(test_array_flat, axis=None) # ascending elements
    test_array_flat_sorted[::-1].sort() # reverse in place -> now descending
    logging.debug(test_array_flat_sorted)
    # -- Fix array shape
    test_array_sorted = np.reshape(test_array_flat_sorted, (n,m))
    # logging.debug("Sorted Descending Array:")
    # logging.debug(test_array_sorted)

    # Flip even rows
    # -- For each row in the array
    FLIP_ROW = False # Starts false because we never flip the first row

    # logging.debug("Flip Tests:")
    # logging.debug("Number of elements: " + str(n*m))
    # logging.debug("Output array: " + str(test_array_out.shape))

    for i in range(0,n): # doesnt matter if array continues past n, the last row will just be padding
        # -- Read a row of m elements
        row = test_array_flat_sorted[i*m : (i+1)*m]
        #logging.debug("i= " + str(i))
        #logging.debug("Elements " + str(i) + " " + str((i + 1)*m - 1))
        #logging.debug(row)
        # -- If this is an even row (n = 1,3,5,...), reverse the elements
        if FLIP_ROW:
            row = np.flip(row)
            #logging.debug(row)
            #logging.debug("Elements in row " + str(i) + " were flipped")
        FLIP_ROW = not FLIP_ROW
        # -- Save to output array
        test_array_out[i] = row

    # logging.debug("Sorting Input array:")
    # logging.debug(test_array_sorted)
    # logging.debug("Sorting/Flipping Output array:")
    # logging.debug(test_array_out)

    return test_array_out
# =============================================================================
# ========== Function to sum adjacent odd and even row elements ===============
def sum_adj_rows(test_array):
    # Add every two rows
    # -- (i.e. 1+2, 3+4, 5+6), to make a new array [n/2 by m]
    # -- if odd number of rows, add a padding row of all zeros
    # -- Assume input array has even number of rows
    [n,m] = test_array.shape # rows, cols
    num_rows = int(n/2) # number of rows in sum array (1/2 the rows of input)

    test_array_summed = np.zeros((num_rows, m))
    # logging.debug("Sum array:")
    # logging.debug(test_array_summed)

    for i in range(0,n, 2):
        sum_array = np.add(test_array[i], test_array[i+1])
        test_array_summed[int(i/2)] = sum_array

    # logging.debug("Sum output array:")
    # logging.debug(test_array_summed)

    return test_array_summed
# =============================================================================

# Continue Code Body

# Generate test array with random integer values in correct range (0-200)
test_array = np.random.randint(0, high=200, size=(input_rows, input_cols))
logging.debug("Testing with a " + str(input_rows) + " by " + str(input_cols) + " array:")
logging.debug(test_array) # prints with first row on debug message line

# Input array [n by m], get array shape for robustness
[n,m] = test_array.shape # rows, cols

# Calculate the number of times the array will be sorted, flipped, summed
# -- from the number of rows. Each loop, the number of rows halves (rounded up),
# -- and repeats until number of rows = 1. This is repeated division by 2
num_loops = 0;
if n < 1:
    logging.debug("Array has less than 1 row")
else:
    while n > 1:
        n = math.ceil(n/2)
        num_loops += 1
    logging.debug("This array will take " + str(num_loops))

# Run the operations the correct number of times on the test array
for i in range(0,num_loops):

    [r,c] = test_array.shape # Number of rows changes size with each loop

    # Sort the array and flip every other row
    test_array = sort_and_flip(test_array)

    # Add padding row if needed (if odd number of rows)
    if r%2 != 0:
        new_row = np.zeros((1,m))
        test_array = np.concatenate((test_array, new_row), axis=0)
        [r,c] = test_array.shape
        logging.debug("Padding Added:")
        logging.debug(test_array)

    # Sum adjacent odd and even rows
    test_array = sum_adj_rows(test_array)
    logging.debug("Final array:")
    logging.debug(test_array)

    logging.debug("++++++++++++++++++++++++++++++") # Pad output for readability
    logging.debug("++++++++++++++++++++++++++++++\n")


# The final array should have elements which are close in magnitude to one
# -- another. From the operations done here, the switches can be set to optimize
# -- the irradiance spread over the cells.
