import argparse

from scipy import spatial
import math
import matplotlib.pyplot as plt
import random
from sklearn import metrics
import datetime


parser = argparse.ArgumentParser(description='Calculate accuracy of function similarity detection from embeddings')
parser.add_argument('--input_path_x86_emb', help='filepath for x86 function embeddings')
parser.add_argument('--input_path_ARM_emb', help='filepath for ARM function embeddings')
parser.add_argument('--optimization_level', help='optimization level under consideration')

args = parser.parse_args()

ARM_Emb_File = args.input_path_ARM_emb
x86_Emb_File = args.input_path_x86_emb
OPT_Level = '_'+args.optimization_level+'_'
curve_title = 'Cosine_Similarity'
x86_emb_dict = {}
ARM_emb_dict = {}

current_metric = 1
cosine_sim = 1


with open(x86_Emb_File, 'r') as x86_file:
    for x86_line in x86_file:
        x86_line_details = x86_line.split(' ', 1)
        x86_file_name = x86_line_details[0]
        x86_emb = x86_line_details[1]
        x86_emb_dict[x86_file_name] = x86_emb

with open(ARM_Emb_File, 'r') as ARM_file:
    for ARM_line in ARM_file:
        ARM_line_details = ARM_line.split(' ', 1)
        ARM_file_name = ARM_line_details[0]
        modified_ARM_file_name = ARM_file_name.replace('-ARM-',
                                                       '-')
        ARM_emb = ARM_line_details[1]
        ARM_emb_dict[modified_ARM_file_name] = ARM_emb

def get_formatted_timestamp():
    ct = datetime.datetime.now()
    ct = str(ct)
    ct = ct.replace('-', '_')
    ct = ct.replace(' ', '_')
    ct = ct.replace(':', '_')
    ct = ct.split('.')[0]
    return ct

def do_main_calculation():
    # below for similar functions
    sim_cosine_vals_X = []
    sim_cosine_vals = []
    count = 0
    for file_name in x86_emb_dict:
        if file_name in ARM_emb_dict:
            x86_list = [float(i) for i in x86_emb_dict[file_name].split()]
            ARM_list = [float(i) for i in ARM_emb_dict[file_name].split()]
            if current_metric == cosine_sim:
                result = 1 - spatial.distance.cosine(x86_list, ARM_list)

            sim_cosine_vals.append(result)
            count += 1
            sim_cosine_vals_X.append(count)
    sim_cosine_vals = sorted(sim_cosine_vals, key=float)

    # below for dissimilar functions
    dissim_count = 0
    dissim_cosine_vals_X = []
    dissim_cosine_vals = []
    x86_keys = list(x86_emb_dict.keys())
    random.shuffle(x86_keys)
    for x86_key_filename in x86_keys:
        ARM_keys = list(ARM_emb_dict.keys())
        random.shuffle(ARM_keys)

        for ARM_key_filename in ARM_keys:
            if not x86_key_filename == ARM_key_filename:
                x86_list = [float(i) for i in x86_emb_dict[x86_key_filename].split()]
                ARM_list = [float(i) for i in ARM_emb_dict[ARM_key_filename].split()]
                if current_metric == cosine_sim:
                    result = 1 - spatial.distance.cosine(x86_list, ARM_list)
                dissim_cosine_vals.append(result)
                dissim_count += 1
                dissim_cosine_vals_X.append(dissim_count)
                break

    dissim_cosine_vals = sorted(dissim_cosine_vals, key=float)
    y_test, y_pred_proba = [], []
    if current_metric == cosine_sim:
        dissimilar_val_default = 0
        similar_val_default = 1

    for val in dissim_cosine_vals:
        if math.isnan(val):
            pass
        elif math.isinf(val):
            pass
        else:
            y_test.append(dissimilar_val_default)
            y_pred_proba.append(val)

    for val in sim_cosine_vals:
        if math.isnan(val):
            pass
        elif math.isinf(val):
            pass
        else:
            y_test.append(similar_val_default)
            y_pred_proba.append(val)

    curve_title_fig = curve_title.replace('_', ' ')
    fpr, tpr, _ = metrics.roc_curve(y_test, y_pred_proba)
    roc_auc = metrics.auc(fpr, tpr) * 100
    roc_auc = "{:.2f}".format(roc_auc)
    plt.plot(fpr, tpr, label="AUC=" + str(roc_auc) + '%')
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.title(curve_title_fig)
    plt.legend(loc=4)
def main():
    do_main_calculation()
    plt.savefig(curve_title + OPT_Level + get_formatted_timestamp() + ".pdf", format="pdf", bbox_inches="tight")

if __name__ == "__main__":
    main()

