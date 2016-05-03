#!/usr/bin/env python

"""This script implements a generic dynamic programming solver
   which distributes its workload over MPI."""

from mpi4py import MPI
from optparse import OptionParser
import numpy


# Scaffolding for some debugging
logfile = open('log.txt', 'w')
debugging = False

def logthis(expr):
    if debugging and rank == 0:
        logfile.write(expr + ' = ' + str(eval(expr)) + '\n')

starting_time = MPI.Wtime()

# Initialization
comm = MPI.COMM_WORLD

parser = OptionParser()
parser.add_option("-p", "--program", dest="program",
                  help="the .py file containing the problem definition")
parser.add_option("-d", "--division", dest="division",
                  help="the division parameter")

(options, args) = parser.parse_args()

if not options.program:
    print "Please specify the program to run, option -p."
    exit

if not options.division:
    print "Please specify the division parameter, option -d."
    exit

execfile(options.program)

p = comm.Get_size()
rank = comm.Get_rank()
d = int(options.division)

# if we have only one processor, do not use division, which would
# result in a deadlock
if p == 1:
    d = 1

# load the input data in the root...
if rank == 0:
    (data, (n,m)) = load_input(args)
else:
    data = None
    n = None
    m = None
# ... and share it with others
(data, (n,m)) = comm.bcast((data, (n,m)), root=0)

table = numpy.zeros((n, m))


def split_among(n, k):
    """Splits the range from 0 to n-1 into k blocks of equal
       length and returns an array of offsets s.t. that i-th
       goes from offset[i] to offset[i+1] (exclusive). If n
       is not divisible by k, the remainder elements go to
       the first blocks."""
    widths = []
    (per_one, leftover) = divmod(n, k)
    for i in xrange(k):
        if i < leftover:
            widths.append(per_one + 1)
        else:
            widths.append(per_one)

    offset = 0
    offsets = [offset]
    for w in widths:
        offset = offset + w
        offsets.append(offset)
        
    return offsets


n_secs = p * d
column_secs = split_among(m, n_secs)


# Logging parameters for debugging
for param in ["p", "rank", "d", "n_secs", "column_secs"]:
    logthis(param)


# Main processing loop
for c_sec in xrange(rank, n_secs, p):
    for row in xrange(n):

        # FETCH PREVIOUS ENTRIES IN ROW
        if not c_sec == 0:
            start = column_secs[max(0, c_sec - (p-1))]
            end = column_secs[c_sec]
            source = (rank - 1) % p
            tag = row
            comm.Recv(table[row, start:end], source=source, tag=tag)

        # COMPUTE THE ENTRIES IN THE COLUMN SECTION
        for col in xrange(column_secs[c_sec], column_secs[c_sec+1]):
                table[row,col] = compute_cell(row, col, table, data)

        # SEND THIS AND PREVIOUS SECTIONS IN ROW
        if not c_sec == n_secs - 1:
            start = column_secs[max(0, c_sec - (p-2))]
            end = column_secs[c_sec+1]
            dest = (rank + 1) % p
            tag = row
            comm.Send(table[row, start:end], dest=dest, tag=tag)

    if c_sec == n_secs - 1:
        write_output(args, table, data)
        
        finished_time = MPI.Wtime()
        measuring = True

        if measuring:
            time_f = open('times.txt', 'a')
            time_f.write('"%s", "%s", %d, %d, %g\n' % \
                         (options.program, args[0], p, d, \
                          (finished_time - starting_time)))
            time_f.close()

