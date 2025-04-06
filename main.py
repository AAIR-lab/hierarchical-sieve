import os
import argparse
from hierarchical_sieve import hierarchical_sieve

# Press the green button in the gutter to run the script.
if __name__ == '__main__':


    import shutil
    import pathlib    
    ROOT_DIR = pathlib.Path(__file__).parent.as_posix()
    DEFAULT_FMP_FILEPATH = "%s/input/T_phi8_10q_7vars.txt" % (ROOT_DIR)
    DEFAULT_OUTPUT_DIR = "%s/output" % (ROOT_DIR)

    parser = argparse.ArgumentParser()
    parser.add_argument("--fmp-filepath", type=str,
        default=DEFAULT_FMP_FILEPATH)
    parser.add_argument("--output-dir", type=str,
        default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--k", type=int, default=1,
        help="The number of iterations to run for")
    parser.add_argument("--clean", action="store_true", default=False,
        help="Clean the output dir before executing")


    args = parser.parse_args()
    if args.clean:
        shutil.rmtree(args.output_dir, ignore_errors=True)
    
    os.makedirs(args.output_dir, exist_ok=True)    
    DETermined, sieved, num_iter = hierarchical_sieve(args.fmp_filepath,
        args.output_dir, args.k)

    if DETermined:
        print("DETerminator asserts termination")
    else:
        print("DETerminator cannot assert termination")

    if sieved:
        print("Sieve asserts termination")
    else:
        print("Sieve cannot assert termination")





