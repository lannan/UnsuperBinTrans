import ast, json, os, pickle, re, time
from os.path import expanduser
from collections import defaultdict


def handle_filename_too_long(long_name):
    long_name = long_name.split(".gdl")[0:]
    long_name = long_name[0]
    before_at_1 = long_name.split("@")[0]
    after_at_1 = long_name.split("@")[1]
    new_name = before_at_1 + "@" + after_at_1[:30] + after_at_1[-30:] + '_funcGNN_formatted.txt'

    return new_name


def find_max(string):
    result = [e for e in re.split("[^0-9]", string) if e != '']

    # list 'result' elements are strings: ['3', '17', '14'], so we use map(int, list) to get integers
    return max(map(int, result))


# connect the line with ~
def write_line(line):
    out_line = ''
    for i, token in enumerate(line):
        if i > 0 and out_line[-1] != ',':
            out_line += '~'
        out_line += token.upper()
    return out_line


def check_segment_reg_offset_len(temp):
    if temp.strip().endswith(']'):
        if len(temp.strip()) <= 12:
            return True

    if temp.strip().endswith('h') or temp.strip().endswith('H'):
        if not len(temp.strip()) > 5:
            return True

    return False


# replace labels and tags
def replace_labels(arch, line, function_names):
    if arch == 'x86':
        # call + function_name
        if line[0] == 'call':
            pass

        # replace function names with <FOO>
        if not line[0].startswith('call'):
            for i, token in enumerate(line):
                if token == '=':
                    if i == 0:
                        return None
                    line.remove(token)
                    continue

                # replace string data type
                if token.startswith('_STR_'):
                    if i == 0:
                        return None
                    line[i] = '<STRING>'
                    continue

                # replace function names in the air
                if token.startswith('__') or token.startswith('_'):
                    if i == 0:
                        return None
                    continue

                # replace arg_abc types
                if token.startswith('arg_'):
                    if i == 0:
                        return None
                    line[i] = '<ARG>'
                    continue

                # replace var_abc types
                if token.startswith('var_'):
                    if i == 0:
                        return None
                    line[i] = '<VAR>'
                    continue

                # replace offset
                if token == 'offset':
                    line[i] = 'OFFSET'
                    continue

                if token == 'short':
                    line[i] = 'SHORT'
                    continue

                if token == 'jmp':
                    line[i] = 'JMP'
                    continue

                if token == 'leave':
                    line[i] = 'LEAVE'
                    continue

                if token == 'proc':
                    return None

                if token == 'near':
                    return None

                if token == 'endp':
                    return None

                if i != 0 and (re.sub('\A[0-9A-Fa-f.-]+\Z', '0', token) == '0' or re.sub('[0-9A-Fa-f.-]+h', '0',
                                                                                         token) == '0'):
                    if len(line[i].strip()) > 5:
                        line[i] = '<CONST>'
                    continue

                # replace segment registers
                # "segment register : offset register"; A segment register is one of CS, DS, ES, FS, GS, or SS)
                if token.startswith('cs:'):
                    if i == 0:
                        return None
                    temp = token[3:]

                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'cs:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('ds:'):
                    if i == 0:
                        return None
                    temp = token[3:]
                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'ds:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('es:'):
                    print('token.startswith(es:) = ', token)

                    if i == 0:
                        return None
                    temp = token[3:]


                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'es:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('fs:'):
                    if i == 0:
                        return None
                    temp = token[3:]

                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'fs:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('gs:'):
                    if i == 0:
                        return None
                    temp = token[3:]

                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'gs:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('ss:'):
                    if i == 0:
                        return None
                    temp = token[3:]

                    if check_segment_reg_offset_len(temp):
                        if token[-1] == ',':
                            line[i] += ','
                        continue

                    if temp.startswith('dword_'):
                        temp = 'dword_<ADDR>'
                    elif temp.startswith('qword_'):
                        temp = 'qword_<ADDR>'
                    else:
                        temp = '<ADDR>'
                    line[i] = 'ss:' + temp
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                # replace data types
                if token == '<XMMWORD_PTR>':
                    if i == 0:
                        return None
                    continue

                if token == '<DWORD_PTR>':
                    if i == 0:
                        return None
                    continue

                if token == '<QWORD_PTR>':
                    if i == 0:
                        return None
                    continue

                if token == '<TBYTE_PTR>':
                    if i == 0:
                        return None
                    continue

                if token == '<BYTE_PTR>':
                    if i == 0:
                        return None
                    continue

                if token == '<WORD_PTR>':
                    if i == 0:
                        return None
                    continue

                # replace dummy name prefixes from ida
                # this has to be the last step of the whole filtering process
                # refer to https://hex-rays.com/blog/igors-tip-of-the-week-34-dummy-names/
                if token.startswith('sub_'):
                    print('req_token_sub_ = ', token)

                    if i == 0:
                        return None
                    continue

                if token.startswith('def_'):
                    print('token.startswith(def_) = ', token)
                    if i == 0:
                        return None
                    line[i] = 'DEF_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('locret_'):
                    if i == 0:
                        return None
                    line[i] = 'locret_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','

                    continue

                if token.startswith('loc_'):
                    if i == 0:
                        return None

                    line[i] = 'loc_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','

                    continue

                if token.startswith('off_'):
                    print('token.startswith(off_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'off_<OFFSET>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('seg_'):
                    print('token.startswith(seg_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'seg_<ADDR>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('asc_'):
                    print('token.startswith(asc_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'asc_<STR>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('byte_'):
                    print('token.startswith(byte_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'byte_<BYTE>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('word_'):
                    print('token.startswith(word_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'word_<WORD>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('dword_'):
                    print('token.startswith(dword_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'DWORD_<WORD>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('qword_'):
                    print('token.startswith(qword_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'qword_<WORD>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('byte3_'):
                    print('token.startswith(byte3_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'byte3_<BYTE>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('xmmword_'):
                    print('token.startswith(xmmword_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'xmmword_<WORD>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('ymmword_'):
                    if i == 0:
                        return None
                    line[i] = 'ymmword_<WORD>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('packreal_'):
                    if i == 0:
                        return None
                    line[i] = 'packreal_<BIT>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('flt_'):
                    if i == 0:
                        return None
                    line[i] = 'flt_<BIT>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('dbl_'):
                    if i == 0:
                        return None
                    line[i] = 'dbl_<BIT>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('tbyte_'):
                    if i == 0:
                        return None
                    line[i] = 'tbyte_<BYTE>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('stru_'):
                    if i == 0:
                        return None
                    line[i] = 'stru_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('custdata_'):
                    if i == 0:
                        return None
                    line[i] = 'custdata_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('algn_'):
                    if i == 0:
                        return None
                    line[i] = 'algn_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                if token.startswith('unk_'):
                    print('token.startswith(unk_) = ', token)

                    if i == 0:
                        return None
                    line[i] = 'unk_<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
                    continue

                # starting with opcode
                if i == 0:
                    continue

                if token in x86_regi_set:
                    continue

                if token in x86_reg_re:
                    continue

                # random missed opcodes
                if token in missed_opcodes:
                    continue

                # [rax + 8]
                if token[0] == '[':
                    if token[-1] == ',':
                        comma = True
                        token = token[:-1]
                    else:
                        comma = False
                    # remove the '[]'
                    temp = token[1: -1]

                    # mark the punctuation
                    symbol = '+'
                    if '-' in temp:
                        symbol = '-'

                    # split by symbol
                    items = temp.split(symbol)
                    for idx, item in enumerate(items):
                        # search for asterisk *
                        if '*' in item:
                            sub_items = item.split('*')

                            for idx_s, s in enumerate(sub_items):
                                sub_items[idx_s] = token_helper(s, function_names)

                            items[idx] = '*'.join(sub_items)
                            continue

                        items[idx] = token_helper(item, function_names)

                    line[i] = '[' + symbol.join(items) + ']'
                    if comma:
                        line[i] += ','
                    continue

                # NO MATCH. Shouldn't be there
                else:
                    line[i] = '<TAG>'
                    if token[-1] == ',':
                        line[i] += ','
    return line


def token_helper(token, function_names):
    if token.startswith('var_'):
        return '<VAR>'

    if token.startswith('arg_'):
        return '<ARG>'

    if re.sub('\A[0-9A-Fa-f.-]+\Z', '0', token) == '0' or re.sub('[0-9A-Fa-f.-]+h', '0', token) == '0':
        if len(token.strip()) > 5:
            return '<CONST>'
        else:
            return token

    else:
        return token


def write_to_file(instruction_list, file_path):
    with open(file_path, 'w') as fp_out:
        for inst in instruction_list:
            fp_out.write(inst + '\n')
    fp_out.close()


def run_gdl_processing(input_file, output_file, output_file_gdl):
    with open(input_file, 'r') as fp_in, open(output_file, 'w') as fp_out, open(output_file_gdl, 'w') as fp_out_gdl:
        print('input_file = ', input_file)
        lines = fp_in.readlines()
        for i, line in enumerate(lines):
            ori = line

            if i > 10:
                last_line = lines[-1]
                if line != last_line:
                    next_line = lines[i + 1]
                    if line.startswith('node:') and next_line.startswith('// node 0'):
                        fp_out.write('\n0')
                        fp_out_gdl.write('\n0')

                        continue
                    if line.startswith('node:') and next_line.startswith('node:'):
                        fp_out.write('\n0')
                        fp_out_gdl.write('\n0')

                        continue
                    if line.startswith('// node 0'):
                        fp_out.write('\n')
                        fp_out_gdl.write('}\n')
                        continue

                if line.startswith('colorentry'):
                    continue
                if line.startswith('endbr64'):
                    continue
                if line.startswith('}'):
                    continue
                if line.startswith('node'):
                    fp_out.write('\n')
                    if 'title: "0"' in line:
                        fp_out_gdl.write(line.replace("\n", "") + ' @BB\n')
                    else:
                        fp_out_gdl.write("}\n" + line.replace("\n", "") + ' @BB\n')

                    continue
                elif line.startswith('edge'):
                    fp_out_gdl.write(line)
                    line = line.replace('"', '')
                    res = [int(number) for number in line.split() if number.isdigit()]
                    fp_out.write(str(res) + " ")
                    continue
                elif line.startswith('// node 0'):
                    fp_out.write("\n")
                    fp_out_gdl.write("\n")

                    continue
                elif line.startswith('// node'):
                    continue
                if '"' in line:
                    line = line.split('"')
                    line = line[0]
                if ';' in line:
                    line = line.split(';')
                    line = line[0]

                if 'xmmword ptr' in line:
                    line = line.replace('xmmword ptr', '<XMMWORD_PTR>')
                if 'qword ptr' in line:
                    line = line.replace('qword ptr', '<QWORD_PTR>')
                if 'dword ptr' in line:
                    line = line.replace('dword ptr', '<DWORD_PTR>')
                if 'tbyte ptr' in line:
                    line = line.replace('tbyte ptr', '<TBYTE_PTR>')
                if 'byte ptr' in line:
                    line = line.replace('byte ptr', '<BYTE_PTR>')
                if 'word ptr' in line:
                    line = line.replace('word ptr', '<WORD_PTR>')

                line = line.split()
                if line[0] == 'endbr64':
                    continue

                if not line:
                    continue

                if 'retn' in line[0]:
                    line = ['retn']

                line = replace_labels(architecture, line, function_names)
                line = write_line(line)
                fp_out.write(line + ' ')
                fp_out_gdl.write(line + '\n')
                unique_instructions.add(line)
                instruction_mapping[line].add(ori)

        fp_in.close()
        fp_out.close()
        fp_out_gdl.close()

        with open(output_file, "r") as inp:
            lines = inp.readlines()
            if lines[0] == '\n':
                lines = lines[1:]
            count = len(lines)
            # count = len(open(output_file).readlines())
            new_file_lines = []
            current_line = [None] * count
            for i, line in enumerate(lines):
                current_line[i] = line.strip()
            if len(current_line) > 2 and not re.search('[a-zA-Z]', current_line[-1]):
                new_file_lines.append(current_line[:len(current_line) - 1])
                new_file_lines[0] = list(filter(None, new_file_lines[0]))
                new_file_lines.append(current_line[len(current_line) - 1:])
            else:
                new_file_lines.append(current_line)
                new_file_lines[0] = list(filter(None, new_file_lines[0]))

        with open(output_file, "w") as outfile:

            if len(new_file_lines) > 1:
                for line in new_file_lines[:-1]:
                    outfile.write("labels_ ")
                    jd = json.dumps(line)
                    print(jd, end="\n", file=outfile)
                for line in new_file_lines[1:]:
                    line = str(line)
                    line = re.sub(r"\]\s", "], ", line)
                    line = ast.literal_eval(line)
                    outfile.write("graph_ [" + line[0] + "]")
            else:
                for line in new_file_lines:
                    outfile.write("labels_ ")
                    jd = json.dumps(line)
                    print(jd, end="\n", file=outfile)
                    outfile.write("graph_ [[0, 0]]")

        with open((output_file), 'r') as input:
            lines = input.readlines()
            labels = lines[0].split("_ ")
            labels = ast.literal_eval(labels[1])
            graph_length = len(labels) - 1
            graph = lines[1].split("_ ")
            graph = graph[1]
            graph_max = find_max(graph)

            while graph_max > graph_length:
                labels.append('0')
                graph_length = len(labels) - 1

            with open(output_file, "w") as outfile:
                outfile.write("labels_ ")
                jd = json.dumps(labels)
                print(jd, end="\n", file=outfile)
                outfile.write("graph_ " + str(graph))


############### HERE IS MAIN FUNCTION ################################
def preprocessing(input_file, output_file):
    with open(input_file, 'r') as fp_in, open(output_file, 'w') as fp_out:
        lines = fp_in.readlines()

        for line in lines:
            ori = line
            if 'xmmword ptr' in line:
                line = line.replace('xmmword ptr', '<XMMWORD_PTR>')
            if 'qword ptr' in line:
                line = line.replace('qword ptr', '<QWORD_PTR>')
            if 'dword ptr' in line:
                line = line.replace('dword ptr', '<DWORD_PTR>')
            if 'tbyte ptr' in line:
                line = line.replace('tbyte ptr', '<TBYTE_PTR>')
            if 'byte ptr' in line:
                line = line.replace('byte ptr', '<BYTE_PTR>')
            if 'word ptr' in line:
                line = line.replace('word ptr', '<WORD_PTR>')

            line = line.split()
            if line[0] == 'endbr64' or line[0] == 'dq':
                continue
            line = replace_labels(architecture, line, function_names)

            if not line:
                continue

            line = write_line(line)
            fp_out.write(line + '\n')
        fp_in.close()
        fp_out.close()


# ref https://en.wikibooks.org/wiki/X86_Assembly/X86_Architecture
x86_reg_re = ("rip,?|rax,?|rbx,?|rcx,?|rdx,?|rsp,?|rbp,?|rsi,?|rdi,?|eax,?|ecx,?|edx,?|ebx,?|"
              "esp,?|ebp,?|esi,?|edi,?|ax,?|cx,?|dx,?|bx,?|sp,?|bp,?|di,?|si,?|"
              "ah,?|al,?|ch,?|cl,?|dh,?|dl,?|bh,?|bl,?|spl,?|bpl,?|sil,?|dil,?|st,?|")

# ref https://blog.yossarian.net/2020/11/30/How-many-registers-does-an-x86-64-cpu-have
bounds_regi = set(
    ['bnd0', 'bnd0,', 'bnd1', 'bnd1,', 'bnd2', 'bnd2,', 'bnd3', 'bnd3,', 'bndcfg', 'bndcfg,', 'bndcfu', 'bndcfu,',
     'bndstatus', 'bndstatus,'])
debug_regi = set(['dr' + str(i) for i in range(8)] + ['dr' + str(i) + ',' for i in range(8)])
control_regi = set(['cr' + str(i) for i in range(16)] + ['cr,' + str(i) for i in range(16)])
stack_regi = set(['st(' + str(i) + ')' for i in range(8)] + ['st(' + str(i) + '),' for i in range(8)])
sse_regi = set(['xmm' + str(i) for i in range(32)] + ['xmm' + str(i) + ',' for i in range(32)])
avx_regi = set(['zmm' + str(i) for i in range(32)] + ['zmm' + str(i) + ',' for i in range(32)])
av2_regi = set(['ymm' + str(i) for i in range(32)] + ['ymm' + str(i) + ',' for i in range(32)])
gen_regi = set(['r' + str(i) for i in range(8, 16)] + ['r' + str(i) + ',' for i in range(8, 16)])
# https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/x64-architecture
gen2_regi = set(['r' + str(i) + 'b' for i in range(8, 16)] + ['r' + str(i) + 'b,' for i in range(8, 16)])
gen3_regi = set(['r' + str(i) + 'd' for i in range(8, 16)] + ['r' + str(i) + 'd,' for i in range(8, 16)])
gen4_regi = set(['r' + str(i) + 'w' for i in range(8, 16)] + ['r' + str(i) + 'w,' for i in range(8, 16)])
x86_regi_set = set()
x86_regi_set = set.union(bounds_regi, debug_regi, control_regi, stack_regi, sse_regi, avx_regi, av2_regi, gen_regi,
                         gen2_regi, gen3_regi, gen4_regi)

missed_opcodes = set(
    ['cmpxchg', 'cmpxchg,', 'xadd', 'xadd,', 'movsq', 'movsq,', 'stosq', 'stosq,', 'scasb', 'scasb,', 'stosd', 'stosd,',
     'cmpsb', 'cmpsb,', 'sub', 'sub,'])

HOME = expanduser("~")
architecture = 'x86'
folder_names = ['coreutils', 'diffutils', 'findutils', 'libgcrypt', 'libgpg-error', 'openssl', 'cmake']

# FILE TYPE
gdl = True

start_time = time.time()

instruction_mapping = defaultdict(set)
unique_instructions = set()
unknown_opcodes = set()

# UBUNTU
input_path = '/path/to_RAW_x86_GDL_files/'
output_path = '/path/to_temporary_logs/'
output_path_GDL_files = '/path/to/preprocessed/x86/GDL_files'
if not os.path.exists(output_path):
    os.makedirs(output_path)

if not os.path.exists(output_path):
    os.makedirs(output_path)

# get all .txt file names
file_names = os.listdir(input_path)

function_names = {}
for file in file_names:
    input_file = input_path + '/' + file
    output_file = output_path + '/' + file.split('.gdl')[0] + '_funcGNN_formatted.txt'
    output_file_gdl = output_path_GDL_files + '/' + file  # .split('.gdl')[0] + '_funcGNN_formatted.txt'

    if gdl:
        try:
            run_gdl_processing(input_file, output_file, output_file_gdl)
        except OSError as exc:
            if exc.errno == 36:
                new_name = handle_filename_too_long(file)
                new_file = output_path + '/' + new_name
                new_file_gdl = output_path_GDL_files + '/' + new_name

                run_gdl_processing(input_file, new_file, new_file_gdl)
        except:
            continue
    else:
        try:
            preprocessing(input_file, output_file)
        except:
            continue

execution_time = time.time() - start_time
print("--- {} seconds ---".format(execution_time))
