# Dynamic programming routine definitions for the Nussinov algorithm
# http://ultrastudio.org/en/Nussinov_algorithm

def load_input(args):
    input_f = open(args[0], 'r')
    input_lines = input_f.readlines()
    input_f.close()

    seq = input_lines[0].strip()

    return (seq, (len(seq), len(seq)))

def score_fn(x, y):
    if (x == 'A' and y == 'T') or \
       (x == 'T' and y == 'A') or \
       (x == 'G' and y == 'C') or \
       (x == 'C' and y == 'G'):
        return 1
    else:
        return 0

def compute_cell(i, j, table, seq):
    # This part is a little bit involved, since in the natural
    # formulation of the Nussinov algorithm, the data flows
    # from the top-right corner. Our implementation requires that
    # the data flows from the top-left corner, so some translation
    # between indiced has to be done.
    i_pos = len(seq) - i - 1
    j_pos = j
    if i_pos == j_pos:
        return 0
    elif i_pos - 1 == j_pos:
        return 0
    else:
        return reduce(max, [table[i, k_pos] + table[len(seq) - (k_pos + 1) - 1, j] \
                                for k_pos in xrange(i_pos, j_pos)],
                      table[i-1, j-1] + score_fn(seq[i_pos], seq[j_pos]))

def write_output(args, table, data):
    output_f = open(args[1], 'w')
    output_f.write('Alignment score: ' + str(table[-1,-1]) + '\n')
    output_f.close()
