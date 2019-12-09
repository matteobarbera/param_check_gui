import re


def read_critical_parameters():
    file_name = ".//avy_parameter_check_list.h"
    with open(file_name, 'r') as f:
        params = dict()
        list_begin_found = False
        for line in f:
            if not list_begin_found:
                if re.search(r"#define PCHK_CRIT_PARAM_LIST", line):
                    list_begin_found = True
            if list_begin_found:  # So that the first element is not skipped
                pattern = r"(?:.*{)(.*)(?:}.*)"
                try:
                    match = re.match(pattern, line)[1].split(',')
                    match[0] = match[0][12:].strip("\") ")
                    params[match[0]] = match[1:]
                except TypeError:
                    break
        return params


if __name__ == "__main__":
    print(read_critical_parameters())
