import string

def str_gen(cnt):
    res = ""
    ci = cnt - 1
    index = ci//26
    if index>0:
        res += str_gen(index)
    res += string.ascii_lowercase[ci % 26]
    return res

def prefix_str_gen(MAX_CNT):
    prefix = ""
    cnt = 1
    while cnt<MAX_CNT:
        prefix = str_gen(cnt)
        cnt+=1
        yield prefix