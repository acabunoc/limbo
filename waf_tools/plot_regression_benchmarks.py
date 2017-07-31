#!/usr/bin/env python
# encoding: utf-8
#| Copyright Inria May 2015
#| This project has received funding from the European Research Council (ERC) under
#| the European Union's Horizon 2020 research and innovation programme (grant
#| agreement No 637972) - see http://www.resibots.eu
#|
#| Contributor(s):
#|   - Jean-Baptiste Mouret (jean-baptiste.mouret@inria.fr)
#|   - Antoine Cully (antoinecully@gmail.com)
#|   - Konstantinos Chatzilygeroudis (konstantinos.chatzilygeroudis@inria.fr)
#|   - Federico Allocati (fede.allocati@gmail.com)
#|   - Vaios Papaspyros (b.papaspyros@gmail.com)
#|   - Roberto Rama (bertoski@gmail.com)
#|
#| This software is a computer library whose purpose is to optimize continuous,
#| black-box functions. It mainly implements Gaussian processes and Bayesian
#| optimization.
#| Main repository: http://github.com/resibots/limbo
#| Documentation: http://www.resibots.eu/limbo
#|
#| This software is governed by the CeCILL-C license under French law and
#| abiding by the rules of distribution of free software.  You can  use,
#| modify and/ or redistribute the software under the terms of the CeCILL-C
#| license as circulated by CEA, CNRS and INRIA at the following URL
#| "http://www.cecill.info".
#|
#| As a counterpart to the access to the source code and  rights to copy,
#| modify and redistribute granted by the license, users are provided only
#| with a limited warranty  and the software's author,  the holder of the
#| economic rights,  and the successive licensors  have only  limited
#| liability.
#|
#| In this respect, the user's attention is drawn to the risks associated
#| with loading,  using,  modifying and/or developing or reproducing the
#| software by the user in light of its specific status of free software,
#| that may mean  that it is complicated to manipulate,  and  that  also
#| therefore means  that it is reserved for developers  and  experienced
#| professionals having in-depth computer knowledge. Users are therefore
#| encouraged to load and test the software's suitability as regards their
#| requirements in conditions enabling the security of their systems and/or
#| data to be ensured and,  more generally, to use and operate it in the
#| same conditions as regards security.
#|
#| The fact that you are presently reading this means that you have had
#| knowledge of the CeCILL-C license and that you accept its terms.
#|# plot the results of the Bayesian Optimization benchmarks
from glob import glob
from collections import defaultdict, OrderedDict

try:
    from waflib import Logs
    def print_log(c, s): Logs.pprint(c, s)
except: # not in waf
    def print_log(c, s): print(s)

try:
    import numpy as np
    from pylab import *
    import brewer2mpl
    bmap = brewer2mpl.get_map('Set2', 'qualitative', 8)
    colors = bmap.mpl_colors
    plot_ok = True
except:
    plot_ok = False
    Logs.pprint('YELLOW', 'WARNING: numpy/matplotlib not found: no plot of the BO benchmark results')

params = {
    'axes.labelsize' : 12,
    'text.fontsize' : 12,
    'axes.titlesize': 12,
    'legend.fontsize' : 12,
    'xtick.labelsize': 12,
    'ytick.labelsize' : 12,
    'figure.figsize' : [8, 8]
}
rcParams.update(params)

def load_data():
    files = glob("regression_benchmark_results/*/*/*.dat")
    points = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    times_learn = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    times_query = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    mses = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    for f in files:
        if 'test.dat' not in f and 'data.dat' not in f:
            fs = f.split("/")
            func, exp, bench = fs[-1][:-4], fs[-2], fs[-3]
            var = 'limbo'
            if func[-4:] == '_gpy':
                func = func[:-4]
                var = 'GPy'
            exp = exp[4:]
            # print(bench, func, var)
            # if not func in data[bench][var]:
            #     data[bench][var][func] = []
            # data[bench][var][func].append(np.loadtxt(f))
            text_file = open(f, "r")
            txt_d = text_file.readlines()
            for i in range(0, len(txt_d), 2):
                line = txt_d[i].strip().split()
                line2 = txt_d[i+1].strip().split()
                dim = int(line[0])
                pts = int(line[1])
                time_learn = float(line2[0])
                time_query = float(line2[1])
                mse = float(line2[2])
                # print(bench,var,func,dim)
                if not (var in points[bench][func][dim]):
                    points[bench][func][dim][var] = []
                    times_learn[bench][func][dim][var] = []
                    times_query[bench][func][dim][var] = []
                    mses[bench][func][dim][var] = []

                points[bench][func][dim][var].append(pts)
                times_learn[bench][func][dim][var].append(time_learn)
                times_query[bench][func][dim][var].append(time_query)
                mses[bench][func][dim][var].append(mse)
    return points,times_learn,times_query,mses

def custom_ax(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_axisbelow(True)
    ax.grid(axis='x', color="0.9", linestyle='-')

def plot(points,times_learn,times_query,mses):
    # for each benchmark configuration
    for bench in points.keys():
        # for each function
        for func in points[bench].keys():
            # for each dimension
            for dim in points[bench][func].keys():
                print('plotting for benchmark: ' + bench + ', the function: ' + func + ' for dimension: ' + str(dim))
                name = bench+'_'+func+'_'+str(dim)+'_mse'
                fig = figure()
                ax = gca()

                labels = []
                kk = 0
                # for each variant
                for var in points[bench][func][dim].keys():
                    labels.append(var)
                    # print bench,func,var
                    var_p = points[bench][func][dim][var]
                    # var_times_learn = times_learn[bench][func][var][1]
                    # var_times_query = times_query[bench][func][var][1]
                    var_mses = mses[bench][func][dim][var]

                    pp = {}

                    for i in range(len(var_p)):
                        if var_p[i] not in pp:
                            pp[var_p[i]] = []
                        pp[var_p[i]].append(var_mses[i])
                    
                    pp = OrderedDict(sorted(pp.items()))

                    x_axis = pp.keys()
                    data = pp.values()

                    y_axis = []
                    y_axis_75 = []
                    y_axis_25 = []
                    for i in range(len(data)):
                        y_axis.append(np.median(data[i]))
                        y_axis_75.append(np.percentile(data[i], 75))
                        y_axis_25.append(np.percentile(data[i], 25))

                    c_kk = colors[kk%len(colors)]
                    ax.plot(x_axis, y_axis, '-', color=c_kk, linewidth=3)
                    ax.fill_between(x_axis, y_axis_75, y_axis_25, color=c_kk, alpha=0.15, linewidth=2)
                    kk = kk + 1
                
                ax.legend(labels)
                ax.set_xlabel('Number of points')
                ax.set_ylabel('Mean Squared Error')
                custom_ax(ax)
                fig.tight_layout()
                fig.savefig(name+'.png')
                close()



def plot_all():
    if not plot_ok:
        print_log('YELLOW', "No plot")
        return
    print('loading data...')
    points,times_learn,times_query,mses = load_data()
    print('data loaded')
    plot(points,times_learn,times_query,mses)
