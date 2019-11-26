import os
import sys
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from participants import *
from tools import *

# dict in which we log total times, per step and per participant
log = dict()
log["time_graph_outsourcing"] = {"total":0, "DO":0, "QT":0, "AT":0, "SE":0}
log["time_query_evaluation"] = {"total":0, "U":0, "QT":0, "AT":0, "SE":0}
log["time_end_to_end"] = {"total":0, "DO":0, "U":0, "QT":0, "AT":0, "SE":0}

# parse command line arguments
DIR = sys.argv[1] + "/"
id_experiment = sys.argv[2]
nb_runs = int(sys.argv[3])
run_queries = int(sys.argv[4])
mode_debug = int(sys.argv[5])
use_case, log["scaling_factor"], _ = id_experiment.split("_")

file_graph = DIR + use_case + "/graph-" + id_experiment + ".ttl"
file_secure_graph = DIR + use_case + "-secure/secure-graph-" + id_experiment + ".ttl"
file_query_workload = DIR + use_case + "/queries-" + id_experiment + ".xml"

DIR_SE = DIR + use_case + "-secure/" + id_experiment + "-SE/"
os.system("mkdir -p " + DIR_SE)

sparql_translate_script = "./gmark/src/querytranslate/test"
executable_sparql = "./apache-jena-3.13.0/bin/sparql"
prefix = os.popen("head " + file_graph + " -n 1").read().strip()


# Run nb_runs times 
for run in range(nb_runs):
	print ("\tSecure algorithm for", id_experiment, " Run", (run+1))

	# Graph outsourcing
	start = time.time()
	DO = DataOwner(key_DO_QT, iv_DO_QT, key_DO_AT, iv_DO_AT, key_DO_SE, iv_DO_SE, file_graph)
	ciphertext_DO_QT = DO.send_DO_QT()
	ciphertext_DO_AT = DO.send_DO_AT()
	ciphertext_DO_SE = DO.send_DO_SE()
	log["time_graph_outsourcing"]["DO"] += time.time() - start

	start = time.time()
	QT = QueryTranslator(key_DO_QT, iv_DO_QT, key_U_QT, iv_U_QT, key_QT_SE, iv_QT_SE)
	QT.receive_DO_QT(ciphertext_DO_QT)
	log["time_graph_outsourcing"]["QT"] += time.time() - start

	start = time.time()
	AT = AnswersTranslator(key_DO_AT, iv_DO_AT, key_U_AT, iv_U_AT, key_AT_SE, iv_AT_SE)
	AT.receive_DO_AT(ciphertext_DO_AT)
	log["time_graph_outsourcing"]["AT"] += time.time() - start

	start = time.time()
	SE = SPARQLEngine(key_DO_SE, iv_DO_SE, key_QT_SE, iv_QT_SE, key_AT_SE, iv_AT_SE)
	SE.receive_DO_SE(ciphertext_DO_SE, file_secure_graph, prefix)
	log["time_graph_outsourcing"]["SE"] += time.time() - start


	if mode_debug:
		print ("\tSanity tests for graph outsourcing")
		test_graph_outsourcing(DO, AT, QT, SE)

	if not run_queries:
		continue


	# Query evaluation
	start = time.time()
	U = User(key_U_QT, iv_U_QT, key_U_AT, iv_U_AT, file_query_workload)
	log["nb_queries"] = len(U.queries_xml)
	log["time_query_evaluation"]["U"] += (time.time() - start)

	for i in range(len(U.queries_xml)): # for each query in the workload
		print ("\t\tQuery", i)

		start = time.time()
		ciphertext_U_QT = U.send_U_QT(i) 
		log["time_query_evaluation"]["U"] += (time.time() - start)

		start = time.time()
		QT.receive_U_QT(ciphertext_U_QT) 
		ciphertext_QT_SE = QT.send_QT_SE()
		log["time_query_evaluation"]["QT"] += (time.time() - start)

		start = time.time()
		SE.receive_QT_SE(ciphertext_QT_SE, DIR_SE, sparql_translate_script, executable_sparql) 
		ciphertext_SE_AT = SE.send_SE_AT()
		log["time_query_evaluation"]["SE"] += (time.time() - start)

		start = time.time()
		AT.receive_SE_AT(ciphertext_SE_AT) 
		ciphertext_AT_U = AT.send_AT_U() 
		log["time_query_evaluation"]["AT"] += (time.time() - start)

		start = time.time()
		U.receive_AT_U(ciphertext_AT_U)
		log["time_query_evaluation"]["U"] += (time.time() - start)

	if mode_debug:		
		print("\tSanity tests for query evaluation")
		test_query_evaluation (id_experiment, U, DIR + use_case + "/")


# write running times to file
for graph_outsourcing_participant in ["DO", "QT", "AT", "SE"]:
	log["time_graph_outsourcing"][graph_outsourcing_participant] /= nb_runs
for query_evaluation_participant in ["U", "QT", "AT", "SE"]:
	log["time_query_evaluation"][query_evaluation_participant] /= nb_runs
log["time_graph_outsourcing"]["total"] = sum(log["time_graph_outsourcing"].values())
log["time_query_evaluation"]["total"] = sum(log["time_query_evaluation"].values())
log["time_end_to_end"]["total"] = log["time_graph_outsourcing"]["total"] + log["time_query_evaluation"]["total"]
log["time_end_to_end"]["DO"] = log["time_graph_outsourcing"]["DO"]
log["time_end_to_end"]["U"] = log["time_query_evaluation"]["U"]
for cloud_participant in ["QT", "AT", "SE"]:
	log["time_end_to_end"][cloud_participant] = log["time_graph_outsourcing"][cloud_participant] + log["time_query_evaluation"][cloud_participant]
if "nb_queries" in log.keys():
	log["time_query_evaluation"]["total"] /= log["nb_queries"]
	for query_evaluation_participant in ["U", "QT", "AT", "SE"]:
		log["time_query_evaluation"][query_evaluation_participant] /= log["nb_queries"]

with open(DIR + use_case + "-secure/log-" + id_experiment + ".txt", 'w') as f:
    json.dump(log, f)


