import os
import time
import random
import graphs
import graph_utils

def hierarchical_sieve(fmp_filepath, output_dir, seed=None, k=10):

    assert output_dir is not None
    DETermined = False
    sieved = False
    if seed is None:
        seed = int(time.time())

    for iteration in range(1, k + 1):

        k_dir = "%s/run-%u" % (output_dir, iteration)
        os.makedirs(k_dir, exist_ok=True)
        with open("%s/seed.txt" % (k_dir), "w") as fh:
            fh.write(str(seed))

        random.seed(seed)

        f = graphs.FMP()
        f.initialize(fmp_filepath)  

        # Increase the seed by 1
        seed += 1

        DETermined = f.get_dec_vars_for_G(k_dir)
        sieved = graph_utils.global_sieve(f.G_pristine)

        if DETermined or sieved:
            break

    return DETermined, sieved, iteration
