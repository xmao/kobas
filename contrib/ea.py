import sys

# RPy hack, make it silent
import rpy_options
rpy_options.set_options(VERBOSE=False)
import rpy

class Test(object):

    methods = []

    def register(cls, callable, name, desc, type_=2):
        cls.methods.append((callable, name.strip(), desc.strip(), type_))
    
    register = classmethod(register)

    def __call__(self, method, *args, **kargs):
        for i in self.methods:
            if i[1] == method.strip():
                return i[0](*args, **kargs)
        raise KeyError, 'Unsupported statistic test method, %s' % method


def hyper(m1, n1, m2, n2, is_tail=False, **kargs):
    """ check significance based on R language
    """
    q, m, n, k = m1, m2, n2-m2, n1
    if m < q: return 0
    if is_tail:
        if q == 0:
            return 0
        else:
            return rpy.r.phyper(q,m,n,k)
    else:
        if q == 0:
            return 1
        else:
            return 1 - rpy.r.phyper(q-1,m,n,k)

Test.register(hyper, hyper.__name__, 'Hyper geometric statistic test')


def binom(m1, n1, m2, n2, **kargs):
    """do chi-square test on contingency table
    samples [(n, m),...]
    """
    p = float(m2)/n2
    alternative = kargs.get('alternative', 'greater')
    cmd = 'binom.test(c(%d, %d), p=%f, alternative="%s")' \
          % (m1, n1-m1, p, alternative)
    return rpy.r(cmd)['p.value']

Test.register(binom, binom.__name__, 'Binomal statistic test')


def chisq(m1, n1, m2, n2, **kargs):
    """do chi-square test on contingency table
    samples [(n, m),...]
    """
    cmd = "chisq.test(matrix(c(%d, %d, %d, %d), nc=2))" \
          % (m1, n1-m1, m2, n2-m2)
    return rpy.r(cmd)['p.value']

Test.register(chisq, chisq.__name__, 'Chi Square statistic test')


def xchisq(m1, n1, m2, n2, **kargs):
    # Automatically invoke Fisher Exact Test when sample frequencies < 5
    #  _______________
    # | m1      m2    |
    # | n1-m2   n2-m2 |
    #  ---------------
        max_e = 5
        s1r,s2r,s1c,s2c, t = m1+m2, (n1+n2-m1-m2), n1, n2, float(n1+n2)
        es = (s1r*s1c/t, s1r*s2c/t, s2r*s1c/t, s2r*s2c/t)
        for e in es:
            if e < max_e:
                return fisher_test(m1, n1, m2, n2, **kargs)
        return chisq_test(m1, n1, m2, n2, **kargs)

Test.register(xchisq, xchisq.__name__, 'Extended chi-square test, applying Fisher Exact Test when sample frequencies < 5')


def fisher(m1, n1, m2, n2, **kargs):
        """do chi-square test on contingency table
        samples [(n, m),...]
        """
        alternative = kargs.get('alternative', 'greater')
        cmd = 'fisher.test(matrix(c(%d, %d, %d, %d), nc=2), alternative="%s")' \
              % (m1, n1-m1, m2, n2-m2, alternative)
        return rpy.r(cmd)['p.value']

Test.register(fisher, fisher.__name__, 'Fisher exact statistic test')


def qvalue_by_qvalue(ps, method='smoother'):
    """ check qvalue (False Discovery Rate) for a list of probability.
    """
    rpy.r.library('qvalue')
    return rpy.r['qvalue'](ps)['qvalues']


def qvalue_by_genets(ps, method=1.0):
    """ check fdr (False Discovery Rate) for a list of probability
    """
    assert isinstance(ps,list)

    if len(ps) <= 1 :
        raise exception.StatError, \
              'Cannot do FDR correction for _%d_ pvalue' % len(ps)
    
    if not is_valid_pvalue(ps):
        raise exception.StatError, "Invalid pvalue in %s" % str(ps)

    rpy.r.library('GeneTS')
    
    if issubclass(type(method), basestring) \
            and method in ("conservative", "adaptive", "bootstrap", "smoother"):
        eta0 = rpy.r['fdr.estimate.eta0'](ps, method=method)
        print 'eta0 = %g' % eta0
    elif type(method) in (int, float):
        assert 0 <= method <= 1
        eta0 = method
    else:
        raise ValueError, '''eta0 should be a float number
or a string in (conservative, adaptive, bootstrap, smoother), not %s''' % str(eta0)
    
    return rpy.r['fdr.control'](ps, eta0 = eta0)['qvalues']

def help():
    return '''ea.py [options] FILE
-m statistic method (%s), default is hyper
-q qvalue implementation (qvalue or genets), default is qvalue package''' % ', '.join([ '%s - %s' % (i[1], i[2]) for i in Test.methods ])

if __name__ == '__main__':
    import getopt, sys
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:q:')
    except:
        print help()
        sys.exit(1)
    else:
        dopts = dict(opts)

    if '-h' in dopts:
        print help()
        sys.exit(0)

    method = ('-m' in dopts) and dopts['-m'] or 'hyper'
    qvalue = ('-q' in dopts) and dopts['-q'] or 'qvalue'

    ret,test = [], Test()

    for l in file(args[0]):
        if not l.startswith('#') and l.strip():
            category, m, M, n, N = l.split('\t')[:5]
            ret.append(
                [category, int(m), int(M), int(n), int(N), test(method, *[ int(i) for i in [m, M, n, N]])])
   
    if qvalue != 'no':
        qvalues = vars()['qvalue_by_%s' % qvalue]([ i[-1] for i in ret ])

    for i in range(len(ret)):
        if qvalue == 'no':
            print '\t'.join([ str(j) for j in ret[i] ])
        else:
            print '\t'.join([ str(j) for j in ret[i] ]), '\t', qvalues[i]

