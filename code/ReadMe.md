Below are all the sequential steps required to run the project with appropriate data. All these steps need to be repeated for data of each optimization level.

Step 1: Run **BIN_to_GDL_v1.py** as per instructions in commit message


Step 2: Run **format_x86_v1.py** as per instructions in commit message

Step 3: Run **format_ARM_v1.py** as per instructions in commit message

Step 4: Run **move_GDLs_less_than_4_instructions_to_folder_v1.py** as per instructions in commit message

Step 5: Run **Duplicate_FIle_Detection_v1.py** as per instructions in commit message

Step 6: Run **generate_BB_to_sentence_Undreamt_corpora_from_GDLs_v1.py** as per instructions in commit message

Step 7: Use the above undreamt corpora to generate Word2Vec embeddings.

Step 8: Using Word2Vec embeddings generate cross-lingual embeddings through Vecmap

Step 9: Train Undreamt using undreamt corpora and cross-lingual embeddings

Step 10: Run **extract_instructions_from_GDLs_BB_wise_v1.py**.as per instructions in commit message


Step 11: Translate required preprocessed ARM GDLs in basic-block format to x86 using the trained undreamt model.

Step 12: Run **extract_instructions_from_GDLs_instr_wise_v1.py**. as per instructions in commit message


Step 13: Create a set of common preprocessed GDLs for ARM and x86.

Step 14: Run **get_function_embeddings_v1.py** as per instructions in commit message

Step 15: Run **calculate_accuracy_of_function_similarity_detection_from_embeddings_v1.py** as per instructions in commit message to perform the function similarity detection task

Step 16: Run **GridSVM_with_SMOTE_v1.py** as per instructions in commit message to perform the vulnerability detection task

Step 17: Run **BLEU_Calculation_v1.py** as per instructions in commit message to calculate BLEU scores for the translation.

