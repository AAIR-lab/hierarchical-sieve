import glob
import os
import graphs
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
# import pygraphviz as pgv
import IPython
import graph_utils as gu
import random
import sys

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    DETermined = False
    sieved = False
    while (not DETermined) or sieved:
        #cleanup output area
        ofiles = glob.glob("output/o_*.*")
        for file in ofiles:
            os.remove(file)

        print("\n\n\n\n\n\n\n\n -------Generating new graph-------- \n\n\n\n\n\n")
        #gu.generate_input_graph(fname="input/T_rand.txt",n=12,v=7)
        seed = random.randrange(sys.maxsize)
        seed = 3389602175065137929
        random.seed(seed)
        #random.seed()

        f = graphs.FMP()
        f.initialize("input/T_phi8_10q_7vars.txt")
        #f.initialize("input/T_rand.txt")


        DETermined = f.get_dec_vars_for_G()
        if DETermined:
            print("DETerminator asserts termination")
        else:
            print("DETerminator cannot assert termination")
        sieved = gu.global_sieve(f.G_pristine)
        if sieved:
            print("       Sieve asserts termination")
        else:
            print("       Sieve cannot assert termination")

        print("seed " + repr(seed))
        #DETermined = True




