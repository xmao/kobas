import getopt

def getdopt(args, shortopts, longopts=[]):
    opts, args = getopt.getopt(args, shortopts, longopts)
    return dict(opts), args
