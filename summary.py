import glob
import sys
import os

# extract hoge=100 val=abc
def get_param(line, key):
    line_list = line.split(" ")
    for i in line_list:
        if key + "=" in i:
            return i.split('=')[1]


def getdirs(path):
     dirs=[]
     for item in os.listdir(path):
         if os.path.isdir(os.path.join(path,item)):
             dirs.append(item)
     return dirs


### SAMPLE ###
# Run status group 0 (all jobs):
#    READ: io=8192.0MB, aggrb=1146KB/s, minb=1146KB/s, maxb=1146KB/s, mint=7313971msec, maxt=7313971msec

# Run status group 1 (all jobs):
#    READ: io=4096.0MB, aggrb=1194KB/s, minb=1194KB/s, maxb=1194KB/s, mint=3511154msec, maxt=3511154msec
def extract_aggrb(filepath):
    ret = []
    for line in open(filepath):
        line = line.strip()
        if "aggrb=" in line:
            aggrb = get_param(line, "aggrb").rstrip("KB/s,")
            aggrb = float(aggrb) / float(1024)
            ret.append(aggrb)
    return ret


# block size must be specified KB order like 4k, 8k
def get_block_sizes(basepath):
    bsdir = getdirs(basepath)
    for i, bs in enumerate(bsdir):
        bsdir[i] = bsdir[i].replace('k','')
    bsdir.sort(cmp=lambda x,y: cmp(int(x), int(y)))
    for i, bs in enumerate(bsdir):
        bsdir[i] = bsdir[i] + 'k'
    return bsdir


def get_file_names(basepath):
    files = glob.glob(basepath + '/*.log')
    for i, f in enumerate(files):
        files[i] = f.split('/')[-1]
    return files

def print_summary(name1, throughputs1, name2, throughputs2, pattern, bs):
    diffname = "ratio" + "(%)"
    name1 = name1 + "(MB/s)"
    name2 = name2 + "(MB/s)"
    print pattern + "(" + bs + ")"
    if diff:
        print "#_of_thread\t%s\t%s\t%s" % (name1, name2, diffname)
    else:
        print "#_of_thread\t%s\t%s" % (name1, name2)

    for i, t1 in enumerate(throughputs1):
        t2 = throughputs2[i]
        num_of_thread = 2**i
        if diff:
            d = ((t2 / t1) - 1.0) * 100
            if d > 0:
                d = "+" + str(d)
            print "%s\t%s\t%s\t%s" % (num_of_thread, t1, t2, d)
        else:
            print "%s\t%s\t%s" % (num_of_thread, t1, t2)
    print
    print


if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    diff = False
    if (argc < 3):
        print '[Usage] $python %s log_path1 log_path2 (diff)' % argvs[0]
        print 'e.g.) $python %s 7.1 7.0' % argvs[0]
        quit()
    if argc == 4 and (argvs[3] == "diff"):
        diff = True

    path1 = argvs[1]
    path2 = argvs[2]
    block_sizes = get_block_sizes(path1)
    file_names = get_file_names(path1 + '/' + block_sizes[0])

    for bs in block_sizes:
        for fname in file_names:
            log1 = path1 + '/' + bs + '/' + fname
            log2 = path2 + '/' + bs + '/' + fname
            throughputs1 = extract_aggrb(log1)
            throughputs2 = extract_aggrb(log2)
            print_summary(path1, throughputs1, path2, throughputs2, fname.rstrip('.log'), bs)

        