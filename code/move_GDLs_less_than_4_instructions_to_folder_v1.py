import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Filter out GDLs with less than 4 instructions as they do not contain much useful information')
parser.add_argument('--input_path', help='input folder with preprocessed GDLs')
parser.add_argument('--output_path', help='folder with transferred GDLs containing less than 4 instructions')
args = parser.parse_args()

dirpath = args.input_path
destDirectory = args.output_path

filenames = os.listdir(dirpath)
for fname in filenames:
    srcpath = os.path.join(dirpath, fname)

    with open(srcpath, 'r') as fp:
        line_count = 0
        for count, line in enumerate(fp):
            if line.startswith('node: '):
                continue
            if line.startswith('{'):
                continue
            if line.startswith('}'):
                continue
            if line.startswith('\n'):
                continue
            if line.startswith('0}'):
                continue
            if line.startswith('0'):
                continue
            if len(line.strip()) == 0:
                continue
            if line.startswith('edge: '):
                continue

            line_count = line_count + 1

    if line_count < 4:
        shutil.move(srcpath, destDirectory)
