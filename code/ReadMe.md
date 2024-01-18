Below are all the sequential steps required to run the project with appropriate data. All these steps need to be repeated for data of each optimization level.

Step 1: Run **BIN_to_GDL.py** with below command to generate GDLs or function-level assembly codes from binaries. You need IDA-Pro to be installed in your system to run this command. 'getBBs.idc' file should be in the same directory as of BIN_to_GDL.py

    python3 BIN_to_GDL.py --input_path INPUT_FOLDER_PATH_OF_BINARIES --output_path OUTPUT_FOLDER_PATH


Step 2: Run **format_x86.py** with below command to preprocess x86 GDL files

    python3 format_x86.py --input_path INPUT_FOLDER_PATH_OF_RAW_x86_GDLs --output_path OUTPUT_FOLDER_PATH


Step 3: Run **format_ARM.py** with below command to preprocess ARM GDL files

    python3 format_ARM.py --input_path INPUT_FOLDER_PATH_OF_RAW_ARM_GDLs --output_path OUTPUT_FOLDER_PATH

Step 4: Run **move_GDLs_less_than_4_instructions_to_folder.py** with below command to filter out GDLs with less than 4 instructions as they do not contain much useful information. Do this for both x86 and ARM GDLs.

    python3 move_GDLs_less_than_4_instructions_to_folder.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLs --output_path FOLDER_WITH_TRANSFERRED_GDLs_CONTAINING_LESS_THAN_4_INSTRUCTIONS

Step 5: Run **Duplicate_FIle_Detection.py** with below command to filter out duplicate GDLs. Do this for both x86 and ARM GDLs.

    python3 Duplicate_FIle_Detection.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLs --output_path FOLDER_WITH_TRANSFERRED_DUPLICATE_GDLs

Step 6: Run **generate_BB_to_sentence_Undreamt_corpora_from_GDLs.py** with below command to generate Basic-Block-to-sentence corpora for Undreamt from GDLs. Do this for both x86 and ARM GDLs.

    python3 generate_BB_to_sentence_Undreamt_corpora_from_GDLs.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLs --output_path FOLDER_WITH_GENERATED_CORPORA --undreamt_corpora_file_name UNDREAMT_CORPORA_FILE_NAME

Step 7: Use above undreamt corpora to generate Word2Vec embeddings.

Step 8: Using Word2Vec embeddings generate cross-lingual embeddings through Vecmap

Step 9: Train Undreamt using undreamt corpora and cross-lingual embeddings

Step 10: Convert GDLs to one-basic-block-per-line format by running below command for the program **extract_instructions_from_GDLs_BB_wise.py**.

    python3 extract_instructions_from_GDLs_BB_wise.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLS --output_path OUTPUT_FOLDER_FOR_CONVERTED_GDLs

Step 11: Translate required preprocessed ARM GDLs in basic-block format to x86 using the trained undreamt model.

Step 12: Convert GDLs to one-instruction-per-line format by running below command for the program **extract_instructions_from_GDLs_instr_wise.py**. Do this for both x86 and ARM GDLs.

    python3 extract_instructions_from_GDLs_instr_wise.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLS --output_path OUTPUT_FOLDER_FOR_CONVERTED_GDLs

Step 13: Create a set of common preprocessed GDLs for ARM and x86.

Step 14: Run **get_function_embeddings_v6.py** with below command to generate function embeddings. Do this for above common GDLs.

    python3 get_function_embeddings_v6.py --input_path INPUT_FOLDER_WITH_PREPROCESSED_GDLS_IN_ONE_INSTRUCTION_PER_LINE_FORMAT --output_path OUTPUT_FOLDER_FOR_GENERATE_FUNCTION_EMBEDDINGS --output_file_name NAME_OF_OUTPUT_FILE --vecmap_embedding_path PATH_TO_CROSS_LINGUAL_EMBEDDINGS_FOR_X86_GENERATED_BY_VECMAP

Step 15: Run **calculate_accuracy_of_function_similarity_detection_from_embeddings_v6.py** with below command to calculate accuracy of function similarity detection from embeddings

    python3 calculate_accuracy_of_function_similarity_detection_from_embeddings_v6.py --input_path_x86_emb FILEPATH_FOR_X86_FUNCTION_EMBEDDINGS --input_path_ARM_emb FILEPATH_FOR_ARM_FUNCTION_EMBEDDINGS --optimization_level OPTIMIZATION_LEVEL_UNDER_CONSIDERATION

Step 16: Run **GridSVM_with_SMOTE_v6.py** with below command to calculate performance of vulnerable function discovery task. The inputs are same as step 15 except the embeddings of vulnerable functions should be replicated and at least there should be three copies of each vulnerable function embedding.

    python3 GridSVM_with_SMOTE_v6.py --input_path_x86_emb FILEPATH_FOR_X86_FUNCTION_EMBEDDINGS --input_path_ARM_emb FILEPATH_FOR_ARM_FUNCTION_EMBEDDINGS

