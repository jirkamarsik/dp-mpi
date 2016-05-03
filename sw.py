# Dynamic programming routine definitions for the Smith-Waterman
# algorithm
# http://ultrastudio.org/en/Smith_%26_Waterman

def load_input(args):
    input_f = open(args[0], 'r')
    input_lines = input_f.readlines()
    input_f.close()

    seqA = input_lines[0].strip()
    seqB = input_lines[1].strip()

    return ((seqA, seqB), (len(seqA) + 1, len(seqB) + 1))

# The score assignments I use here are of no consequence,
# choice of numbers does not affect the performance on the benchmarks.
def score_fn(x, y):
    if y == '-':
        # deletion
        return -1
    elif x == '-':
        # insertion
        return -1
    elif x != y:
        # mismatch
        return -1
    else:
        # match
        return +2

def compute_cell(i, j, table, data):
    if i == 0 or j == 0:
        return 0
    (seqA, seqB) = data
    return max(0,
               table[i-1, j-1] + score_fn(seqA[i-1], seqB[j-1]),
               table[i-1, j] + score_fn(seqA[i-1], '-'),
               table[i, j-1] + score_fn('-', seqB[j-1]))

def write_output(args, table, data):
    output_f = open(args[1], 'w')
    output_f.write('Alignment score: ' + str(table[-1,-1]) + '\n')
    # recreating the local alignment from the DP table is irrelevant
    # to our project...
    output_f.close()
    
