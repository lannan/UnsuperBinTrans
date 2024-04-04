import ast, json, os, pickle, re, time
from os.path import expanduser
from collections import defaultdict, deque


# gdl formatting addition
def find_max(string):
    result = [e for e in re.split("[^0-9]", string) if e != '']

    # list 'result' elements are strings: ['3', '17', '14'], so we use map(int, list) to get integers
    return max(map(int, result))


# end gdl addition
def handle_filename_too_long(long_name):
    long_name = long_name.split(".gdl")[0:]
    long_name = long_name[0]
    before_at_1 = long_name.split("@")[0]
    after_at_1 = long_name.split("@")[1]
    new_name = before_at_1 + "@" + after_at_1[:30] + after_at_1[-30:] + '_funcGNN_formatted.txt'

    return new_name


def write_to_file(instruction_list, file_path):
    with open(file_path, 'w') as fp_out:
        for inst in instruction_list:
            fp_out.write(inst + '\n')
    fp_out.close()


def replace_dummy(token):
    # replace dummy name prefixes from ida
    # this has to be the last step of the whole filtering process
    # refer to https://hex-rays.com/blog/igors-tip-of-the-week-34-dummy-names/

    # replace string data type
    if token.startswith('_STR_'):
        return '<STRING>'

    if token.startswith('sub_'):
        return 'sub_<FOO>'

    if token.startswith('locret_'):
        return 'locret_<TAG>'

    if token.startswith('def_'):
        return 'def_<TAG>'

    if token.startswith('loc_'):
        return 'loc_<TAG>'

    if token.startswith('off_'):
        return 'off_<OFFSET>'

    if token.startswith('seg_'):
        return 'seg_<ADDR>'

    if token.startswith('asc_'):
        return 'asc_<STR>'

    if token.startswith('byte_'):
        return 'byte_<BYTE>'

    if token.startswith('word_'):
        return 'word_<WORD>'

    if token.startswith('dword_'):
        return 'DWORD_<WORD>'

    if token.startswith('qword_'):
        return 'qword_<WORD>'

    if token.startswith('byte3_'):
        return 'byte3_<BYTE>'

    if token.startswith('xmmword_'):
        return 'xmmword_<WORD>'

    if token.startswith('ymmword_'):
        return 'ymmword_<WORD>'

    if token.startswith('packreal_'):
        return 'packreal_<BIT>'

    if token.startswith('flt_'):
        return 'flt_<BIT>'

    if token.startswith('dbl_'):
        return 'dbl_<BIT>'

    if token.startswith('tbyte_'):
        return 'tbyte_<BYTE>'

    if token.startswith('stru_'):
        return 'stru_<TAG>'

    if token.startswith('custdata_'):
        return 'custdata_<TAG>'

    if token.startswith('algn_'):
        return 'algn_<TAG>'

    if token.startswith('unk_'):
        return 'unk_<TAG>'

    return None


def helper(cur_token, function_names):
    print('cur_token = ', cur_token)
    res = ''
    zero = False
    cur_puncs = deque()
    for ch in cur_token:
        if ch == '+':
            cur_puncs.append('+')
        elif ch == '-':
            cur_puncs.append('-')
    subs = re.split('\+|\-', cur_token)  # <ADDR>  -  cfbd

    for sub in subs:
        sub = sub.strip()
        if sub.startswith('#'):
            sub = sub[1:]

        if sub.startswith('('):
            par = True
            sub = sub[1:]
        else:
            par = False
        if sub.isdigit() or sub.startswith('0x'):
            if sub.isdigit():
                if len(sub) > 4:
                    res += '0'
                else:
                    res += sub
            elif sub.startswith('0x'):
                if len(sub) > 6:
                    res += '0'
                else:
                    res += sub
            zero = True
        elif sub in function_names:
            res += '<FOO>'
        elif sub in arm_addrs:
            res += '<ADDR>'
        elif sub.startswith('var_'):
            res += '<VAR>'
        elif sub.startswith('arg_'):
            res += '<ARG>'
        elif replace_dummy(sub):
            res += replace_dummy(sub)
        elif zero:
            print('elif zero:')
            res += sub

        elif sub.startswith('<CONST>'):
            res += '<CONST>'
        elif sub.startswith('<ADDR>'):
            res += '<ADDR>'
        else:
            res += '<TAG>'
        if cur_puncs:
            res += cur_puncs.popleft()
    if par:
        res += ')'

    return res

def replace_labels(line, function_names):
    print('start of replace_labels , line = ', line)
    IF_THIS_INSTRUCTION_A_FUNCTION = False
    first_opcode = line[0]
    if first_opcode == 'BLX' or first_opcode == 'BL' or first_opcode == 'BX':
        IF_THIS_INSTRUCTION_A_FUNCTION = True
    # this is function call in ARM equivalent to 'call' in x86

    for i, token in enumerate(line):
        print('@replace_labels token = ', token)

        if token == '=':
            if i == 0:
                return None
            continue

        # tag the comma
        if token[-1] == ',':
            token = token[:-1]
            comma = True
        else:
            comma = False

        if token[0] == '#':
            if i == 0:
                return None
            token = token[1:]

        # # replace '#-' with '$'
        print('token_of_interest token = ', token)

        # this below replacement covers on of the form #0X6545AD.. or #646AD...
        token_parts = re.split('\+|\-|\,', token)
        # print('token_parts = ', token_parts)
        if len(token_parts) > 1 and token_parts[1].startswith('#'):
            if len(token_parts[1].strip()) <= 7:
                pass
            else:
                token = re.sub('#(0x[0-9a-fA-F ]+)', '<CONST>', token)  # '0' #original
                token = re.sub('#-(0x[0-9a-fA-F ]+)', '$', token)
                token = re.sub('#([0-9a-fA-F ]+)', '<CONST>', token)  # '0'
                token = re.sub('#-([0-9a-fA-F ]+)', '$', token)
        else:
            token = re.sub('#(0x[0-9a-fA-F ]+)', '0', token)
            token = re.sub('#-(0x[0-9a-fA-F ]+)', '$', token)
            token = re.sub('#([0-9a-fA-F ]+)', '0', token)
            token = re.sub('#-([0-9a-fA-F ]+)', '$', token)


        if token[0] == '=':
            equal_sign = True
            token = token[1:]
        else:
            equal_sign = False

        if token[0] == '-':
            minus_sign = True
            token = token[1:]
        else:
            minus_sign = False

        # conditional operators
        # https://developer.arm.com/documentation/dui0068/b/ARM-Instruction-Reference/Conditional-execution
        if token == 'EQ' or token == 'NE' or token == 'CS' or token == 'HS' or token == 'CC':
            continue
        if token == 'LO' or token == 'MI' or token == 'PL' or token == 'VS' or token == 'VC':
            continue
        if token == 'HI' or token == 'LS' or token == 'GE' or token == 'LT' or token == 'GT':
            continue
        if token == 'LE' or token == 'AL':
            continue

        if token in arm_directives:
            return None


        # replace function names:
        if token.startswith('_STR_'):
            if i == 0:
                return None
            line[i] = "<STRING>"
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        # :upper16: or :lower16:

        if token.startswith(':upper16:'):
            if i == 0:
                return None
            line[i] = 'UPPER<ADDR>'
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue


        if token.startswith(':lower16:'):
            if i == 0:
                return None
            line[i] = 'LOWER<ADDR>'
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue


        if token.startswith("arg_"):
            if i == 0:
                return None
            line[i] = '<ARG>'
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if token.startswith("var_"):
            if i == 0:
                return None
            line[i] = '<VAR>'
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if token.startswith('jpt_'):
            if i == 0:
                return None
            line[i] = 'JPT<ADDR>'
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        # dummy generated by IDA
        dummy = replace_dummy(token)
        print('@replace_labels 3rd after dummy token = ', token)

        if dummy:
            if i == 0:
                return None
            line[i] = dummy
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue
        print('@replace_labels 3rd after if dummy token = ', token, ' line[i] = ', line[i])

        # immediate operands
        if token.isdigit() or token.startswith('0x'):
            if i == 0:
                return None

            if len(line[i].strip()) > 7:

                line[i] = '<CONST>'

            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if token[0] == '(' and token[-1] == ')':
            if i == 0:
                return None
            item = token[1:-1]
            if '+' or '-' in item:
                line[i] = helper(item, function_names)
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if token[0] == '[':
            if i == 0:
                return None
            exclamation = False
            suffix = None
            if token[-1] == '!':
                items = token[1:-2].split(',')
                exclamation = True
            elif token[-1] == ']':
                items = token[1:-1].split(',')
            else:
                items = token[1:].split(']')[0].split(',')
                suffix = token[1:].split(']')[1]
            cur = '['
            for item in items:
                if item in arm_regi_set:
                    cur += item
                elif item[0] == '-' and item[1:] in arm_regi_set:
                    cur += item
                elif item == '0':
                    cur += '0'
                elif item == '$':
                    cur += '$'
                elif '+' in item or '-' in item:
                    cur += helper(item, function_names)
                    print('after helper cur = ', cur)
                elif item.startswith('#'):
                    if len(item) > 7:
                        cur += '0'
                    else:
                        cur += item
                elif '0' in item or '$' in item:
                    cur += item
                elif '<CONST>' in item:
                    cur += item
                elif '<ADDR>' in item:
                    cur += item
                else:
                    cur += '<TAG>'
                cur += ','

            cur = cur[:-1]
            if exclamation:
                cur += ']!'
            else:
                cur += ']'
            line[i] = cur
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if suffix:
                line[i] += suffix
            if comma:
                line[i] += ','

            continue

        # registers
        if token in arm_regi_set:
            continue

        if token[0] == '-1' and token[1:] in arm_regi_set:
            continue

        if i == 0:
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if ',' in token:
            line[i] = token
            if equal_sign:
                line[i] = "=" + line[i]
            if minus_sign:
                line[i] = '-' + line[i]
            if comma:
                line[i] += ','
            continue

        if '#' in token:
            idx = token.index('#')
            line[i] = token[:idx] + '0'

        else:
            if IF_THIS_INSTRUCTION_A_FUNCTION:
                pass

            else:
                line[i] = '<TAG>'

        if equal_sign:
            line[i] = "=" + line[i]
        if minus_sign:
            line[i] = '-' + line[i]
        if comma:
            line[i] += ','

    print('final line = ', line)
    return line


# connect the line with ~
def write_line(line):
    out_line = ''
    for i, token in enumerate(line):

        if i > 0 and out_line[-1] != ',':
            out_line += '~'
        out_line += token.upper()

    out_line = re.sub('0RG_[0-9a-zA-Z]+', '<ARG>', out_line)
    out_line = out_line.replace("$", "-0")
    return out_line


def split_registers(token):
    # POP.W {R4-R8,PC}
    cur_registers = token.split(',')
    register_list = []
    for cur_regi in cur_registers:
        if '-' in cur_regi:
            cur_range = cur_regi.split('-')
            # replace sp, lr, pc with r13 - r15
            for cur_idx, cur_item in enumerate(cur_range):
                if cur_item in map_regi:
                    cur_range[cur_idx] = map_regi[cur_item]

            # R4-R11; D0-D5
            char_regi = cur_range[0][0]
            start, end = int(cur_range[0][1:]), int(cur_range[1][1:])
            for val in range(start, end + 1):
                register_list.append(char_regi + str(val))
        else:
            register_list.append(cur_regi)
    return register_list


def stack_operation(line):
    opcode = line[0]
    if line[1][-2] == '!':
        exclamation = '!'
    else:
        exclamation = ''
    sec = line[1][:-1].replace('!', '')

    # stack operation on ARM: 
    # https://www.cnblogs.com/goodhacker/p/3206405.html 
    punc = '+'
    if opcode.startswith('S'):
        punc = '-'
    elif opcode.startswith('L'):
        punc = '+'
    else:
        unknown_opcodes.add(opcode)

    register_list = []
    result = []

    # LDMDB R11, {R4-R11,SP,PC}
    cur_registers = line[2][1:-1].split(',')
    for cur_regi in cur_registers:
        if '-' in cur_regi:
            cur_range = cur_regi.split('-')

            # replace sp, lr, pc with r13 - r15
            # e.g., LDMFD SP, {SP-PC}     
            for cur_idx, cur_item in enumerate(cur_range):
                if cur_item in map_regi:
                    cur_range[cur_idx] = map_regi[cur_item]

            # R4-R11
            char_regi = cur_range[0][0]
            start, end = int(cur_range[0][1:]), int(cur_range[1][1:])
            for val in range(start, end + 1):
                register_list.append(char_regi + str(val))
        else:
            register_list.append(cur_regi)

    if punc == '-':
        register_list = register_list[::-1]  # reverse

    for regi_item in register_list:
        result.append("{}~[{}{}0]{},{}".format(opcode, sec, punc, exclamation, regi_item))

    return result


def replace_range(line, fp_out, fp_out_gdl):
    ori = line
    line = line.split()
    opcode = line[0]

    if opcode.startswith('PUSH'):
        rev = True
    else:
        rev = False
    if len(line) == 2:
        # POP.W {R4-R8,PC}
        # LDM R5, {R9,R10}
        register_list = split_registers(line[1][1:-1])
        if rev:
            register_list.reverse()

        for regi_item in register_list:
            written_line = line[0] + '~' + regi_item.upper()
            written_line = re.sub('0RG_[0-9a-zA-Z]+', '<ARG>', written_line)
            written_line = written_line.replace('$', '-0')
            fp_out.write(written_line + ' ')
            fp_out_gdl.write(written_line + '\n')

            unique_instructions.add(written_line)
            instruction_mapping[written_line].add(ori)

    elif len(line) == 3:
        # LDM R5!, {R0-R3}  
        # LDMDB R11, {R4-R11,SP,PC}
        cur_lines = stack_operation(line)

        for cur_line in cur_lines:
            written_line = cur_line.upper()
            written_line = re.sub('0RG_[0-9a-zA-Z]+', '<ARG>', written_line)
            written_line = written_line.replace('$', '-0')
            fp_out.write(written_line + ' ')
            fp_out_gdl.write(written_line + '\n')

            unique_instructions.add(written_line)
            instruction_mapping[written_line].add(ori)

    elif len(line) == 4 and line[2].startswith('{'):
        # VTBL.8 D6, {D22-D23}, D24
        idx_end = line[2].index('}')
        cur_remain = line[2][idx_end + 1:]

        register_list = split_registers(line[2][1:idx_end])
        for regi_item in register_list:
            written_line = line[0] + '~' + line[1] + regi_item.upper() + cur_remain + line[3]
            written_line = re.sub('0RG_[0-9a-zA-Z]+', '<ARG>', written_line)
            written_line = written_line.replace('$', '-0')
            fp_out.write(written_line + ' ')
            fp_out_gdl.write(written_line + '\n')

            unique_instructions.add(written_line)
            instruction_mapping[written_line].add(ori)
    else:
        with open(HOME + '/Desktop/length_does_not_match.txt', 'w') as f:
            f.write("LENGTH DOES NOT MATCH:   " + ori + "\n\n")
    return None


def gdl_preprocessing(input_file, output_file, output_file_gdl):
    with open(input_file, 'r') as fp_in, open(output_file, 'w') as fp_out, open(output_file_gdl, 'w') as fp_out_gdl:
        lines = fp_in.readlines()
        for i, line in enumerate(lines):
            if " = " in line or "%" in line:
                continue
            ori = line

            # gdl formatting additions
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

                    if 'title: "0"' in line:  # 1st node
                        fp_out_gdl.write(line.replace("\n", "") + ' @BB\n')
                    else:
                        fp_out_gdl.write("}\n" + line.replace("\n", "") + ' @BB\n')

                    continue
                if line.startswith('edge'):
                    fp_out_gdl.write(line)

                    line = line.replace('"', '')
                    res = [int(number) for number in line.split() if number.isdigit()]
                    fp_out.write(str(res) + " ")
                    continue
                if line.startswith('// node 0'):
                    fp_out.write("\n")
                    fp_out_gdl.write("\n")

                    continue
                if line.startswith('// node '):
                    continue
                if '"' in line:
                    line = line.split('"')
                    line = line[0]
                if ';' in line:
                    line = line.split(';')
                    line = line[0]
            else:
                continue

            if '{' in line:
                replace_range(line, fp_out, fp_out_gdl)

            else:
                # replace " - " with '-'
                line = line.replace(" - ", '-')
                line = line.split()
                if len(line) == 1:
                    continue

                # ignore directives
                if line[0] in arm_directives:
                    continue

                formatted_line = replace_labels(line, function_names)
                if not formatted_line:
                    continue
                written_line = write_line(formatted_line)
                print('FINALLLL written_line = ', written_line, "\n\n")
                fp_out.write(written_line + " ")
                fp_out_gdl.write(written_line + "\n")


                unique_instructions.add(written_line)
                instruction_mapping[written_line].add(ori)

        fp_in.close()
        fp_out.close()
        fp_out_gdl.close()

        # gdl formatting additions
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


# ref: 
# https://developer.arm.com/documentation/dui0473/i/CJAJBFHC
# https://www.keil.com/support/man/docs/armasm/armasm_dom1359731136117.htm
arm_directives = set(['CODE16', 'CODE32', 'EXPORT', 'ALIGN', 'DCD', 'nptr', 'DCB'])
arm_addrs = set(['errnum', 'name', 's'])
gen_regi = set(['R' + str(i) for i in range(0, 16)] + ['R' + str(i) + '!' for i in range(0, 16)])
map_regi = {'SP': 'R13', 'LR': 'R14', 'PC': 'R15'}
var_regi = set(['V' + str(i) for i in range(1, 9)])
arg_regi = set(['A' + str(i) for i in range(1, 5)])

# floating point registers:  https://blog.csdn.net/notbaron/article/details/106577545 
float_regi = set(['D' + str(i) for i in range(0, 16)] + ['d' + str(i) for i in range(0, 16)] + ['S' + str(i) for i in
                                                                                                range(0, 32)] + [
                     's' + str(i) for i in range(0, 32)])

# https://blog.51cto.com/u_14592069/2591169
cp15_regi = set(['C' + str(i) for i in range(0, 16)] + ['P' + str(i) for i in range(0, 16)] + ['c' + str(i) for i in
                                                                                               range(0, 16)] + [
                    'p' + str(i) for i in range(0, 16)])

# https://developer.arm.com/documentation/den0024/a/ARMv8-Registers/NEON-and-floating-point-registers/Scalar-register-sizes
scalar_regi = set(['B' + str(i) for i in range(0, 32)] + ['b' + str(i) for i in range(0, 32)] + ['D' + str(i) for i in
                                                                                                 range(0, 32)] + [
                      'd' + str(i) for i in range(0, 32)])
scalar_regi2 = set(['H' + str(i) for i in range(0, 32)] + ['h' + str(i) for i in range(0, 32)] + ['Q' + str(i) for i in
                                                                                                  range(0, 32)] + [
                       'q' + str(i) for i in range(0, 32)])

program_regi = set(['CPSR', 'SPSR'])
other_regi = set(['SB', 'IP', 'SP', 'LR', 'PC', 'FP'])

arm_regi_set = set.union(gen_regi, var_regi, arg_regi, float_regi, cp15_regi, program_regi, other_regi, scalar_regi,
                         scalar_regi2)

##########  MAIN  ##########

HOME = expanduser("~")
architecture = 'arm'
folder_names = ['coreutils', 'diffutils', 'findutils', 'libgcrypt', 'libgpg-error', 'openssl', 'cmake']

# FILE TYPE
gdl = True

start_time = time.time()

instruction_mapping = defaultdict(set)
unique_instructions = set()
unknown_opcodes = set()

# UBUNTU
input_path = '/path/to_RAW_ARM_GDL_files/'
output_path = '/path/to_temporary_logs/'
output_path_GDL_files = '/path/to/preprocessed/ARM/GDL_files'
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
            gdl_preprocessing(input_file, output_file, output_file_gdl)
        except OSError as exc:
            if exc.errno == 36:
                new_name = handle_filename_too_long(file)
                new_file = output_path + '/' + new_name
                new_file_gdl = output_path_GDL_files + '/' + new_name

                gdl_preprocessing(input_file, new_file, new_file_gdl)
        except:
            continue

execution_time = time.time() - start_time
print("--- {} seconds ---".format(execution_time))
