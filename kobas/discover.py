"""Find enriched pathways by frequency of terms and statistical
significance of terms."""

import os, string, csv
from sets import Set

# RPy hack, make it silent
import rpy_options
rpy_options.set_options(VERBOSE=False)
import rpy

from kobas import dbutils, exception

class Dist(dict):

    def __init__(self):
        dict.__init__(self)

    def add(self, class_, stuff): self[class_] = stuff

    def update(self, class_, iterable):
        for record in iterable:
            self.add(class_, record)

    def size(self):
        stuffs = Set()
        for rec in self.values():
            stuffs.update(rec)
        return len(stuffs)

    def get_prob(self, key):
        try:
            return float(len(self[key]))/self.size()
        except KeyError:
            return 0

    def __setitem__(self, key, val):
        if self.has_key(key):
            self[key].add(val)
        else:
            dict.__setitem__(self, key, Set((val,)))

    def __getitem__(self, key): return dict.get(self, key, Set())
            

def dist_from_annot_file(handle):
    dist = Dist()
    mykeggdb = dbutils.keggdb()
    for l in handle:
        if l[0] == '#':
            continue
        query,kos = parse_annot(l)
        if not kos: continue
        for ko in kos:
            paths = mykeggdb.get_ko3s(ko)
            for path in paths: dist[path] = query
    return dist

def dist_from_distfile(handle):
    """ parse dist file into a dict
    """
    res = Dist()
    file_reader = csv.reader(handle,dialect=csv.excel_tab)
    for term, seqs in file_reader:
        res.update(term, seqs.split(','))
    return res

def hyper(q,m,n,k, is_tail=False):
    """ check significance based on R language
    """
    if m < q: return 0
    if is_tail:
        return rpy.r.phyper(q,m,n,k)
    else:
        return 1 - rpy.r.phyper(q-1,m,n,k)

def binom(q, size, prob, is_tail=False):
    """ probability of binom distribuion.
    """
    if is_tail:
        return rpy.r.pbinom(q,size,prob)
    else:
        return 1 - rpy.r.pbinom(q-1, size, prob)

def chisq(q, df, ncp =0,is_tail=False):
    """ probability of chisquare distribution.
    """
    if is_tail:
        return rpy.pchisq(q, df, ncp)
    else:
        return 1 - rpy.r.pchisq(q, df, ncp)

def transpose(matrix):
    """matrix: [(n, m),...]
    return [[n1,n2,...], [m1,m2,...]]
    """
    res = [[],[]]
    for n, m in matrix:
        res[0].append(n)
        res[1].append(m)
    return res

def cjoin(iterable, sep=',', func=str):
    """apply function to each element before join them
    """
    return sep.join([func(i) for i in iterable])

def chisq_test(*samples):
    """do chi-square test on contingency table
    samples [(n, m),...]
    """
    data = transpose(samples)
    cmd = "chisq.test(data.frame(t=c(%s),f=c(%s)))" \
          % (cjoin(data[0]), cjoin(data[1]))
    return rpy.r(cmd)['p.value']

def qvalue(ps, method='smoother'):
    """ check qvalue (False Discovery Rate) for a list of probability.
    """
    rpy.r.library('qvalue')
    return rpy.r['qvalue'](ps)['qvalues']

class SampleTest:

    def __init__(self, *samples):
        self._samples = samples

    def get_prob(self, sample, feature):
        size = sample.size()
        count = sample.has_key(feature) and len(sample[feature]) or 0
        return float(count)/size
    
    def calc_pvalue(self,*args):
        pass

    def get_size(self, seq):
        if type(seq) == type(0):
            return seq
        else:
            return len(seq)

    def defaultTestResult(self):
        return TestResult(['Pathway', 'Sample Count', 'Sample IDs', 'Backgroud Count', 'Background IDs', 'Pvalue'])

    def __call__(self):
        pass

class TwoSampleTest(SampleTest):
    
    def __init__(self, *samples):
        if len(samples) != 2:
            raise TypeError, '%s expected 2 arguments, got %d' \
                  % (self.__class__, len(*samples))
        SampleTest.__init__(self, *samples)
        self.sample1 = self._samples[0]
        self.sample2 = self._samples[1]
        self.sample1_size = self.sample1.size()
        self.sample2_size = self.sample2.size()

class BinomTest(TwoSampleTest):

    def __init__(self, *samples):
        TwoSampleTest.__init__(self, *samples)

    def calc_pvalue(self, *args): return binom(*args)

    def __call__(self, result=None):
        if result is None: result = self.defaultTestResult()
        
        for term, seqs in self.sample1.items():
            count = len(seqs)
            bgcount = self.sample2.has_key(term) and len(self.sample2[term]) or 0
            prob = self.sample2.get_prob(term)
            result.append([term,
                           count, ','.join(seqs),
                           bgcount, ','.join(self.sample2.get(term, [])),
                           self.calc_pvalue(count, self.sample1_size, prob)])
        return result

class HyperTest(TwoSampleTest):

    def __init__(self, *samples):
        TwoSampleTest.__init__(self, *samples)

    def calc_pvalues(self, *args): return hyper(*args)

    def __call__(self, result=None):
        if self.sample1_size > self.sample2_size:
            raise exception.StatError, \
                  "Sample (%d) greater than Background (%d) in hypergeometric test" % \
                  (self.sample1_size, self.sample2_size)
        if result is None: result = self.defaultTestResult()
        for term, seqs in self.sample1.items():
            count = self.get_size(seqs)
            if self.sample2.has_key(term):
                bgcount = len(self.sample2[term])
                pvalue = hyper(count, bgcount, self.sample2_size-bgcount, self.sample1_size)
            else:
                bgcount = 0
                pvalue = 0
            result.append([term,
                           count, ','.join(seqs),
                           bgcount, ','.join(self.sample2.get(term, [])),
                           pvalue])
        return result

class ChiTest(SampleTest):

    def __init__(self, *samples):
        SampleTest.__init__(self, *samples)
        self.samples = samples
        self.sizes = []
        for sample in self.samples:
            self.sizes.append(sample.size())

    def clac_pvalues(self, *args): return chisq(*args)

    def defaultTestResult(self):
        samples = []
        for i in range(len(self.samples)):
            samples.append('Sample%d'%(i+1))
        return TestResult(['Pathway'] + samples + ['Pvalue'])

    def keys(self):
        res = Set()
        for sample in self.samples:
            res.update(sample.keys())
        return res
    
    def __call__(self, result=None):
        if result is None: result = self.defaultTestResult()
        features = self.keys()
        
        for feature in features:
            data = []
            for i in range(len(self.samples)):
                sample = self.samples[i]
                sample_size = self.sizes[i]
                feature_size = len(sample[feature])
                data.append((feature_size, sample_size-feature_size))
            pvalue = chisq_test(*data)
            result.append([feature]+data+[pvalue])
        return result

def within(x, min_=0, max_=1): return min_ <= x <= max_

def is_valid_pvalue(iterable):
    for x in iterable:
        if str(x) == "nan" or (not within(x)):
            return False
    return True
    
class TestResult:

    def __init__(self, title=None):
        if title:
            self.title = title
        else:
            self.title = []
        self.result = []
        self._keggdb = dbutils.keggdb()

    def add_title(self, title): self.title = title

    def sort(self, key=-1, order=0):
        self.result.sort(list_cmp(key))
        if order: self.result.reverse()

    def fdr(self, i=-1):
        try:
            qvalues = qvalue([i[-1] for i in self.result])
        except:
            raise
        else:
            self.add_column('Qvalue', qvalues)
    
    def add_column(self, fieldname, column):
        assert(len(self.result)==len(column))
        self.title.append(fieldname)
        for i in range(len(self.result)):
            self.result[i].append(column[i])

    def add_row(self, row):
        assert(len(row)==len(self.title))
        self.result.append(row)

    def append(self, row): self.add_row(row)

    def reverse(self): self.result.reverse()

    def __iter__(self): return iter(self.result)

    def __getitem__(self, i): return self.result[i]

    def __repr__(self):
        res = ''
        if self.title:
            res += '#%s\n' % string.join(self.title, '\t')
        for feature in self.result:
            res += string.join(map(str, feature), '\t') + '\n'
        return res

    def __str__(self): return self.__repr__()
        
    def to_text(self): return self.__repr()
    
    def add_link_to_pathway(self):
        for feature in self.result:
            feature.append(self._keggdb.ko3term2pathwayid(feature[0]))

    def to_html(self, title=None):
        from kobas import config
        from Cheetah.Template import Template
        tmpl = os.path.join(
            config.getrc()['kobas_home'], "template", "test_html.tmpl")
        self.add_link_to_pathway()
        t = Template(
            file = tmpl, searchList = [{'thead':self.title, 'result':self.result},])
        return str(t)

class list_cmp:

    def __init__(self,i):
        self.i = i

    def cmp(self, x, y):
        """ select the criteria for comparason
        """
        if x[self.i] < y[self.i]:
            return -1
        elif x[self.i] == y[self.i]:
            return 0
        else:
            return 1
    
    def __call__(self,x,y):
        return self.cmp(x,y)


def parse_annot(line):
    """ extract query and KO entries from line
    format: query\tko_id:rank:evalue:score:identitiy ...
    """
    kos = []

    l = string.split(line.strip(),'\t')
    query = l[0]

    # kos = string.split(l[1])
    if len(l) == 2:
        for annot in string.split(l[1]):
            kos.append(string.split(annot,':')[0])
    
    return (query,kos)

def annot2dist(handle):
    """ convert annotation to term distribution, besides total size
    """
    dist_dict = {}
    dist_size = 0

    mykeggdb = dbutils.keggdb()
    
    for l in handle:
        terms = []
        if l[0] == '#':
            continue
        query,kos = parse_annot(l)
        if kos:
            dist_size += 1
            [terms.extend(mykeggdb.get_ko3s(koid)) for koid in kos]
            term_freq(dist_dict, [(term,1) for term in terms])
    return (dist_dict, dist_size)
