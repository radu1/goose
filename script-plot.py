import sys
import os
import json
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter("ignore")

DIR = sys.argv[1]
max_scaling_factor_query_evaluation = int(sys.argv[2])

use_cases = ["uniprot", "social-network", "bib", "shop"]
participants = ["DO", "U", "QT", "SE", "AT"]

lists_go = {} # dict used to plot Scalability of graph outsourcing
lists_qe = {} # dict used to plot Scalability of query evaluation
lists_zoom = {} # dict used to plot Zoom on end-to-end solution

# parse log files for each use_case
for use_case in use_cases:

	# read times for secure algorithm
	list_log_files = os.popen("ls " + DIR + "/" + use_case + "-secure/log*").read().strip().split("\n")
	agr_time_secure = dict()
	cnt_time_secure = dict()
	list_scaling_factors = []
	for log_file in list_log_files:
		with open(log_file) as f:
			log = json.load(f)
			scaling_factor = int(log["scaling_factor"])
			if scaling_factor in cnt_time_secure.keys():
				cnt_time_secure[scaling_factor] += 1
				for k1 in ["time_graph_outsourcing", "time_query_evaluation", "time_end_to_end"]:
					for k2 in log[k1].keys():
						agr_time_secure[scaling_factor][k1][k2] += log[k1][k2]
			else:
				list_scaling_factors.append(scaling_factor)
				cnt_time_secure[scaling_factor] = 1
				agr_time_secure[scaling_factor] = dict()
				for k1 in ["time_graph_outsourcing", "time_query_evaluation", "time_end_to_end"]:
					agr_time_secure[scaling_factor][k1] = dict()
					for k2 in log[k1].keys():
						agr_time_secure[scaling_factor][k1][k2] = log[k1][k2]
	for scaling_factor in agr_time_secure.keys():
		for k1 in agr_time_secure[scaling_factor].keys():
			for k2 in agr_time_secure[scaling_factor][k1].keys():
				agr_time_secure[scaling_factor][k1][k2] /= cnt_time_secure[scaling_factor]

	list_scaling_factors = sorted(list_scaling_factors)
	list_scaling_factors_run_sparql = list(filter(lambda x: x <= max_scaling_factor_query_evaluation, list_scaling_factors))
	list_t_qe = [agr_time_secure[scaling_factor]["time_query_evaluation"]["total"] for scaling_factor in list_scaling_factors_run_sparql]
	lists_go[use_case] = [agr_time_secure[scaling_factor]["time_graph_outsourcing"]["total"] for scaling_factor in list_scaling_factors]
	lists_zoom[use_case] = [agr_time_secure[max_scaling_factor_query_evaluation]["time_end_to_end"][participant] for participant in participants]

	# read times for standard algorithm
	agr_time_standard = {scaling_factor:0 for scaling_factor in list_scaling_factors}
	cnt_time_standard = {scaling_factor:0 for scaling_factor in list_scaling_factors}
	with open(DIR + "/" + use_case + "/times.txt") as f:
		line = f.readline()
		while line :
			scaling_factor, _, _, time = line.strip().split()
			agr_time_standard[int(scaling_factor)] += float(time)
			cnt_time_standard[int(scaling_factor)] += 1
			line = f.readline()
	agr_time_standard = [agr_time_standard[scaling_factor]/cnt_time_standard[scaling_factor] for scaling_factor in list_scaling_factors_run_sparql]
	overhead = [(list_t_qe[i] - agr_time_standard[i])/agr_time_standard[i]*100 for i in range(len(list_scaling_factors_run_sparql))]
	lists_qe[use_case] = (agr_time_standard, list_t_qe, overhead)




############ plot Scalability of graph outsourcing
plt.figure(figsize=(7, 5))
plt.rcParams.update({'font.size':14})
plt.xlabel("Scaling factor")
plt.ylabel("Time (seconds)")
plt.xscale('log')
plt.yscale('log')
markers = ["o", "s", "*", "v"]
for i in range(len(use_cases)):
	plt.plot(list_scaling_factors, lists_go[use_cases[i]], marker=markers[i])
plt.legend(loc="upper left", labels=use_cases)
plt.savefig(DIR + "/scalability-graph-outsourcing.pdf")



############ plot Size of graphs in dataset
plt.figure(figsize=(7, 5))
plt.rcParams.update({'font.size':14})
plt.xlabel("Number of nodes |V|")
plt.ylabel("Number of edges |E|")
plt.xscale('log')
plt.yscale('log')
for i in range(len(use_cases)):
	list_size_V = []
	list_size_E = []
	sum_size_V = {}
	cnt_size_V = {}
	with open(DIR + "/" + use_cases[i] + "/log_" + use_cases[i] + ".txt") as f:
		line = f.readline()
		while line:
			size_V, size_E, _ = line.strip().split()
			size_V = int(size_V)		
			if size_V not in list_size_V:
				list_size_V.append(size_V)
				sum_size_V[size_V] = int(size_E)
				cnt_size_V[size_V] = 1
			else:
				sum_size_V[size_V] += int(size_E)
				cnt_size_V[size_V] += 1
			line = f.readline()
	for size_V in list_size_V:
		list_size_E.append(sum_size_V[size_V]/cnt_size_V[size_V])
	plt.plot(list_size_V, list_size_E, marker=markers[i])
plt.legend(loc="upper left", labels=use_cases)
plt.savefig(DIR + "/size-graphs-dataset.pdf")



############ plot Scalability of query evaluation, and comparison standard vs secure algorithm
plt.figure(figsize=(14, 5))
plt.rcParams.update({'font.size':12.75})
for i in range(len(use_cases)):
	use_case = use_cases[i]
	plt.subplot(1, 7, i*2+1)
	plt.title(use_cases[i])
	plt.xlabel("Scaling factor")
	plt.ylabel("Time (seconds)")
	plt.xscale('log')
	plt.yscale('log')
	plt.ylim(0.1, 100)
	plt.plot(list_scaling_factors_run_sparql, lists_qe[use_case][0], marker=">", label='Standard', color="purple")
	plt.plot(list_scaling_factors_run_sparql, lists_qe[use_case][1], marker="d", label='GOOSE', color="olive")
	if i == 0:
		plt.legend(bbox_to_anchor=(2., 1.3), ncol=2)
	ax2 = plt.twinx()
	ax2.plot(list_scaling_factors_run_sparql, lists_qe[use_case][2], marker="x", label="Overhead", color="darkblue")
	if i == 0:
		ax2.legend(bbox_to_anchor=(3.4, 1.3))
	ax2.set_ylim(0,100)
	ax2.set_ylabel("Overhead (%)")
	plt.subplots_adjust(left=0.07, bottom=0.2, right=0.87, top=0.8, wspace=0, hspace=0)
plt.savefig(DIR + "/scalability-query-evaluation.pdf")



############ plot Zoom on end-to-end solution i.e., graph outsourcing and query evaluation
plt.figure(figsize=(14, 2.5))
plt.rcParams.update({'font.size':14})
for i in range(len(use_cases)):
	use_case = use_cases[i]
	plt.subplot(1, 4, i+1)
	plt.title(use_cases[i])
	plt.pie(lists_zoom[use_case], colors = ["chartreuse", "red", "blue", "gray",  "pink"])
	if i==0:
		 plt.legend(labels=participants, bbox_to_anchor=(-0.25, 0.95))
plt.savefig(DIR + "/zoom-end-to-end-solution.pdf")


