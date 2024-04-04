import os

import numpy as np
from nltk import ngrams
from collections import Counter


ARM_translated_BB_Folder_Path = '/path/to/ARM_TO_x86_translated_basic_blocks_GDL_files/'
x86_original_BB_Folder_Path = '/path/to/reference_x86_basic_blocks_GDL_files'


def closest_ref_length(translation_u, list_of_reference_u):
    """
    determine the closest reference length from translation length
    """
    len_trans = len(translation_u)
    closest_ref_idx = np.argmin([abs(len(x) - len_trans) for x in list_of_reference_u])
    return len(list_of_reference_u[closest_ref_idx])


def brevity_penalty(translation_u, list_of_reference_u):
    """
    """
    c = len(translation_u)
    r = closest_ref_length(translation_u, list_of_reference_u)

    if c > r:
        return 1
    else:
        return np.exp(1 - float(r) / c)


def count_clip_ngram(translation_u, list_of_reference_u, ngram=1):
    """
    Return
   clipped counts of the ngram for candidate and reference translation

    """
    res = dict()
    # retrieve hypothesis counts
    ct_translation_u = count_ngram(translation_u, ngram=ngram)

    # retrieve translation candidate counts
    for reference_u in list_of_reference_u:
        ct_reference_u = count_ngram(reference_u, ngram=ngram)
        for k in ct_reference_u:
            if k in res:
                res[k] = max(ct_reference_u[k], res[k])
            else:
                res[k] = ct_reference_u[k]

    return {
        k: min(ct_translation_u.get(k, 0), res.get(k, 0))
        for k in ct_translation_u
    }


def count_ngram(unigram, ngram=1):
    """
    Return
    -----
    counter: dict, containing ngram as key, and count as value
    """
    return Counter(ngrams(unigram, ngram))


def modified_precision(translation, list_of_references, ngram=1):
    """
    Return
    modified precision = clipped counts/ no. of unclipped candidate n-gram

    """
    ct_clip = count_clip_ngram(translation, list_of_references, ngram)
    ct = count_ngram(translation, ngram)

    return sum(ct_clip.values()) / float(max(sum(ct.values()), 1))


def bleu_score(translation_u, list_of_reference_u, W=[0.25 for x in range(4)]):
    bp = brevity_penalty(translation_u, list_of_reference_u)
    modified_precisions = [
        modified_precision(translation_u, list_of_reference_u, ngram=ngram)
        for ngram, _ in enumerate(W, start=1)
    ]
    score = np.sum([
        wn * np.log(modified_precisions[i]) if modified_precisions[i] != 0 else 0 for i, wn in enumerate(W)
    ])

    return bp * np.exp(score)

total_BLEU = 0
total_lines = 0
total_GDL_with_diff_line_count = 0
files = os.listdir(ARM_translated_BB_Folder_Path)
no_of_files = len(files)
for arm_file in files:
    # print('arm_file = ', arm_file)
    arm_full_path = os.path.join(ARM_translated_BB_Folder_Path, arm_file)

    arm_file_parts = arm_file.split('-ARM-')
    x86_GDL_file_name = arm_file_parts[0] + '-' + arm_file_parts[1]
    x86_file_full_path = os.path.join(x86_original_BB_Folder_Path, x86_GDL_file_name)

    with open(arm_full_path, "r", errors='ignore') as fp_arm_in, open(x86_file_full_path, "r",
                                                                      errors='ignore') as fp_x86_in:
        print('arm_file = ', arm_file)
        reference_x86_instrs = []
        translated_x86_instrs = []
        for gdl_line in fp_x86_in:
            if len(gdl_line.strip()) == 0:
                gdl_line = "MISNULL"
            reference_x86_instrs.append(gdl_line.strip())

        for gdl_line in fp_arm_in:
            if len(gdl_line.strip()) == 0:
                gdl_line = "MISNULL"
            translated_x86_instrs.append(gdl_line.strip())


        if not len(reference_x86_instrs) == len(translated_x86_instrs):
            no_of_line_difference = max(len(reference_x86_instrs),len(translated_x86_instrs)) - min(len(reference_x86_instrs),len(translated_x86_instrs))
            total_GDL_with_diff_line_count+=1

            if len(reference_x86_instrs) < len(translated_x86_instrs):
                for i in range(no_of_line_difference):
                    reference_x86_instrs.append("LENDIF")
            else:
                for i in range(no_of_line_difference):
                    translated_x86_instrs.append("LENDIF")

        # print("BLEU", bleu_score(translation, list_of_references))
        print('reference_x86_instrs = ', reference_x86_instrs)
        print('translated_x86_instrs = ', translated_x86_instrs)
        for i in range(min(len(reference_x86_instrs),len(translated_x86_instrs))):#may need to change to max
            bleu_score_val = bleu_score(translated_x86_instrs[i], reference_x86_instrs[i])
            print('i = ', i, ' bleu_score_val = ', bleu_score_val)
            total_BLEU = total_BLEU + bleu_score_val
            total_lines = total_lines + 1

        # bleu_score_val = bleu_score(translated_x86_instrs, reference_x86_instrs)
        # print('bleu_score_val = ', bleu_score_val)
        # total_BLEU = total_BLEU + bleu_score_val

# end of reading files and generating 2 arrays of texts

# # print("BLEU", bleu_score(translation, list_of_references))
# bleu_score_val = bleu_score(translated_x86_instrs, reference_x86_instrs) #
print('average BLEU for ', total_lines, ' lines is = ', total_BLEU / total_lines)
# print('average BLEU for ', total_lines, ' lines is = ', total_BLEU / max(len(reference_x86_instrs),len(translated_x86_instrs)))


print('total_GDL_with_diff_line_count = ', total_GDL_with_diff_line_count)
