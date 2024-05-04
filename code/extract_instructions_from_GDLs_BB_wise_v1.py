import argparse
import os, time

start_time = time.time()

parser = argparse.ArgumentParser(description='Convert GDLs to one-basic-block-per-line format')
parser.add_argument('--input_path', help='input folder with preprocessed GDLs')
parser.add_argument('--output_path', help='output folder for converted GDLs')
args = parser.parse_args()

GDL_FOLDER_PATH = args.input_path
OUTPUT_GDL_FOLDER_PATH = args.output_path

file_names = os.listdir(GDL_FOLDER_PATH)
for file in file_names:
    inst_strings = ''
    filepath = os.path.join(GDL_FOLDER_PATH, file)
    output_filepath = os.path.join(OUTPUT_GDL_FOLDER_PATH, file)
    with open(filepath, "r", errors='ignore') as fp_gdl_in:
        for gdl_line in fp_gdl_in:
            gdl_line = gdl_line.strip()
            if gdl_line.startswith('node: {'):
                continue
            elif gdl_line.startswith('{'):
                continue
            elif gdl_line.startswith('}'):
                inst_strings = inst_strings.strip() + '\n'
                continue
            elif gdl_line.startswith('edge: {'):
                continue
            elif gdl_line == '\n':
                continue
            elif gdl_line == '0}':
                continue
            elif gdl_line == '0':
                continue
            elif len(gdl_line.strip()) == 0:
                continue
            else:
                inst_strings = inst_strings + gdl_line + ' '

        inst_strings = inst_strings.strip()
        fp_gdl_in.close()
    with open(output_filepath, "w") as fp_out:
        fp_out.write(inst_strings)
        fp_out.close()
execution_time = time.time() - start_time
print("--- {} seconds ---".format(execution_time))
