
import argparse
import os


def is_cleanup(name):
	return name.endswith('.i64') or name.endswith('.idb') or name.endswith('.id0') or name.endswith('.id1')or name.endswith('.nam') or name.endswith('.til')

def main():

	parser = argparse.ArgumentParser(description='Generate GDLs/Function level assembly code from binaries')
	parser.add_argument('--input_path', help='the input folder with binaries')
	parser.add_argument('--output_path', help='the output folder where GDLs are generated')

	args = parser.parse_args()

	input_path = args.input_path
	output_path = args.output_path

	if not os.path.exists(output_path):
		os.makedirs(output_path)
	input_names = os.listdir(input_path)

	#run script against all files
	for name in input_names:
		target_file = input_path+"/"+name
		os.system("ida64 -c -A -SgetBBs.idc " + target_file)
		#os.system("ida64 -c -A -SgetBBs.idc " + target_file)

	# housekeeping
	# Delete ida database files and move the .gdl to raw_BB directory
	output_names = os.listdir(input_path)
	for name in output_names:
		if is_cleanup(name):
			target_file = input_path+"/"+name
			os.remove(target_file)
		elif name.endswith('.gdl'):
			move_from = input_path+"/"+name
			move_to = output_path+"/"+name
			os.rename(move_from, move_to)

if __name__ == "__main__":
	main()
