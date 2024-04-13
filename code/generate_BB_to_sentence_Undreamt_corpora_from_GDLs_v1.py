import argparse
import os, time

start_time = time.time()

parser = argparse.ArgumentParser(description='generate Basic-Block-to-sentence for Undreamt corpora from GDLs')
parser.add_argument('--input_path', help='input folder with preprocessed GDLs')
parser.add_argument('--output_path', help='folder with generated corpora')
parser.add_argument('--undreamt_corpora_file_name', help='Undreamt generated corpora file name with .txt extension')
args = parser.parse_args()

GDL_FOLDER_PATH = args.input_path
OUTPUT_GDL_FOLDER_PATH = args.output_path
undreamt_corpora_file_name = args.undreamt_corpora_file_name
output_filepath = os.path.join(OUTPUT_GDL_FOLDER_PATH, undreamt_corpora_file_name)

file_names = os.listdir(GDL_FOLDER_PATH)
for file in file_names:
    inst_strings = ''
    filepath = os.path.join(GDL_FOLDER_PATH, file)
    with open(filepath, "r", errors='ignore') as fp_gdl_in, open(output_filepath, "a") as fp_out:
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
            else:
                inst_strings = inst_strings + gdl_line + ' '

        inst_strings = inst_strings.strip()
        fp_out.write(inst_strings)
        fp_out.write('\n')
        fp_gdl_in.close()
        fp_out.close()
execution_time = time.time() - start_time
print("--- {} seconds ---".format(execution_time))
