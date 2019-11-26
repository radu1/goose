import os
from participants import *


# return the key that corresponds to a given value in a dict
def get_key_for_val(d, val_to_search):
	for k, v in d.items():
		if v == val_to_search:
			return k


# return a list of tuples extracted from a Jena output
def extract_tuples_from_Jena_output(results_str):
	results = results_str["results_str"].split("\n")
	results = results[3:-2] # remove format lines at the beginning and end
	results_clean = []
	for result in results:
		result = result[1:-1].split("|") # [1:-1] to remove the | at the beginning and end of line
		for i in range(len(result)):
			result[i] = result[i].strip()
		if len(result[0]) > 0:
			results_clean.append(result)
	return results_clean


# return a sorted list of strings based on data; if data is a dict, then each element in the result is a key value pair
def to_str_list(data, is_dict):
	if is_dict:
		return sorted(map(lambda key : str(key) + " " + str(data[key]), data.keys()))
	else:
		return sorted(map(lambda element : str(element), data))


# assert that two lists are identical
def test_equal_lists(l1, l2):
	for i in range(len(l1)):
		assert (l1[i] == l2[i])


# sanity tests for graph outsourcing
def test_graph_outsourcing(DO, AT, QT, SE):
	# test correct encryption/decryption of each exchange between DO and a cloud node
	test_equal_lists(to_str_list (DO.sigma_Sigma, True), to_str_list (QT.sigma_Sigma, True))
	test_equal_lists(to_str_list (DO.sigma_V, True), to_str_list (AT.sigma_V, True))
	test_equal_lists(to_str_list (DO.E_perm, False), to_str_list (SE.E_perm, False))

	# test graph reconstruction by cloud nodes
	cloud_E = list()
	for (x, y, z) in SE.E_perm:
		cloud_E.append((get_key_for_val(AT.sigma_V, x), get_key_for_val(QT.sigma_Sigma, y), get_key_for_val(AT.sigma_V, z)))
	test_equal_lists(to_str_list (DO.E, False), to_str_list (cloud_E, False))


# sanity tests for query answering i.e., if the user receives exactly the "gold" results (as for standard no-secure Jena)
def test_query_evaluation(id_experiment, U, DIR):
	for i in range(U.i + 1):
		# results received by the user for query i
		l1 = to_str_list(U.results[i], False)

		# read gold results from file
		gold_results_str = ""
		with open(DIR + "SPARQL-" + id_experiment + "/query-" + str(i) + ".sparql-ans.txt", "r") as f:
			line = f.readline()
			while line:
				gold_results_str += line
				line = f.readline()
		l2 = to_str_list(extract_tuples_from_Jena_output ({"results_str" : gold_results_str}), False)
		test_equal_lists(l1, l2)


