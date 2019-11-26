import json
import random
import sys
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import xml.etree.ElementTree as ET
from tools import *


# Key and IV generation
key_DO_QT, iv_DO_QT = get_random_bytes(32), get_random_bytes(16)
key_DO_AT, iv_DO_AT = get_random_bytes(32), get_random_bytes(16)
key_DO_SE, iv_DO_SE = get_random_bytes(32), get_random_bytes(16)
key_U_QT, iv_U_QT = get_random_bytes(32), get_random_bytes(16)
key_U_AT, iv_U_AT = get_random_bytes(32), get_random_bytes(16)
key_QT_SE, iv_QT_SE = get_random_bytes(32), get_random_bytes(16)
key_AT_SE, iv_AT_SE = get_random_bytes(32), get_random_bytes(16)


################################## class DataOwner
class DataOwner():
	def __init__(self, key_DO_QT, iv_DO_QT, key_DO_AT, iv_DO_AT, key_DO_SE, iv_DO_SE, file_graph):
		# initialize the ciphers used to communicate with QT, AT, and SE
		self.cipher_DO_QT = AES.new(key_DO_QT, AES.MODE_CBC, iv_DO_QT)
		self.cipher_DO_AT = AES.new(key_DO_AT, AES.MODE_CBC, iv_DO_AT)
		self.cipher_DO_SE = AES.new(key_DO_SE, AES.MODE_CBC, iv_DO_SE)
	
		# read graph from file and construct sets E, V, Sigma
		self.E = list()
		self.V = set()
		self.Sigma = set()
		with open (file_graph, "r") as f:
			line = f.readline()
			while line:
				if line.startswith("@") or len(line.strip()) == 0:
					line = f.readline()
					continue
				(s, p, o) = line.strip()[:-1].split()
				self.E.append((s, p, o))
				self.V |= set([s, o])
				self.Sigma |= set([p])
				line = f.readline()


	# set_to_permute is a set of strings (can be V or sigma) for which we generate and encrypt a permutation
	# cipher is the cipher used to encrypt the generated permutation (can be cipher_DO_QT or cipher_DO_AT)
	# output : encrypted dictionary of element -> permuted value
	def generate_encrypt_permutation (self, set_to_permute, cipher):
		sigma = {}
		vals = np.random.permutation(range(len(set_to_permute)))
		i = 0
		for element in set_to_permute:
			sigma[element] = int(vals[i])
			i += 1
		
		if set_to_permute == self.V:
			self.sigma_V = sigma
		else:
			self.sigma_Sigma = sigma

		return cipher.encrypt(pad(json.dumps(sigma).encode('utf-8'), AES.block_size))


	# construct sigma_Sigma and outsource it to QT
	def send_DO_QT(self):
		return self.generate_encrypt_permutation(self.Sigma, self.cipher_DO_QT)


	# construct sigma_V and outsource it to AT
	def send_DO_AT(self):
		return self.generate_encrypt_permutation(self.V, self.cipher_DO_AT)


	# construct E_perm and outsource it to SE
	def send_DO_SE(self):
		self.E_perm = []
		for (s, p, o) in self.E:
			self.E_perm.append((self.sigma_V[s], self.sigma_Sigma[p], self.sigma_V[o]))

		return self.cipher_DO_SE.encrypt(pad(json.dumps({"E_perm":self.E_perm}).encode('utf-8'), AES.block_size))



################################## class User
class User():
	def __init__(self, key_U_QT, iv_U_QT, key_U_AT, iv_U_AT, file_query_workload):
		# initialize the ciphers used to communicate with AT and QT
		self.cipher_U_QT = AES.new(key_U_QT, AES.MODE_CBC, iv_U_QT)
		self.cipher_U_AT = AES.new(key_U_AT, AES.MODE_CBC, iv_U_AT)

		# read queries from workload file
		self.queries_xml = []
		for query in ET.parse(file_query_workload).getroot().findall("./query"):
			new_root = ET.fromstring("<queries></queries>")
			new_root.append(query)
			self.queries_xml.append(ET.tostring(new_root))

		# dict to be filled with results for each query
		self.results = {}


	# encrypt and send query i to QT
	def send_U_QT(self, i):
		self.i = i
		data = {"i" : str(i), "query_xml" : self.queries_xml[i].decode()}
		return self.cipher_U_QT.encrypt(pad(str(json.dumps(data)).encode('utf-8'), AES.block_size))


	# receive and decrypt results of query i from AT
	def receive_AT_U(self, ciphertext_AT_U):
		results = json.loads(unpad(self.cipher_U_AT.decrypt(ciphertext_AT_U), AES.block_size).decode('utf-8'))
		self.results[self.i] = results["results_perm"]



################################## class QueryTranslator
class QueryTranslator():
	# initialize the ciphers used to communicate with DO, U, and SE
	def __init__ (self, key_DO_QT, iv_DO_QT, key_U_QT, iv_U_QT, key_QT_SE, iv_QT_SE):	
		self.cipher_DO_QT = AES.new(key_DO_QT, AES.MODE_CBC, iv_DO_QT)
		self.cipher_U_QT = AES.new(key_U_QT, AES.MODE_CBC, iv_U_QT)
		self.cipher_QT_SE = AES.new(key_QT_SE, AES.MODE_CBC, iv_QT_SE)


	# receive and decrypt permutation sigma_Sigma
	def receive_DO_QT (self, encrypted_sigma_Sigma):
		self.sigma_Sigma = json.loads(unpad(self.cipher_DO_QT.decrypt(encrypted_sigma_Sigma), AES.block_size).decode('utf-8'))


	# receive the encrypted query and replace the predicates using the permutation sigma_Sigma
	def receive_U_QT (self, encrypted_query):
		data = json.loads(unpad(self.cipher_U_QT.decrypt(encrypted_query), AES.block_size).decode('utf-8'))
		self.i = data['i'] # index of the user query
		query_xml = data['query_xml'] # xml abstract representation of the user query
		self.query_xml_perm = ET.ElementTree(ET.fromstring(query_xml)) # xml abstract representation of the permuted query
		for symbol in self.query_xml_perm.getroot().iter('symbol'):
			predicate = ":"+str(symbol.text)
			if predicate in self.sigma_Sigma.keys():
				symbol.text = "l"+str(self.sigma_Sigma[":"+str(symbol.text)])
			else:
				symbol.text = "l"+str(len(self.sigma_Sigma)+1)


	# encrypt and send the permuted query
	def send_QT_SE (self):
		data = {"i" : self.i, "query_xml_perm" : ET.tostring(self.query_xml_perm.getroot()).decode()}
		return self.cipher_QT_SE.encrypt(pad(str(json.dumps(data)).encode('utf-8'), AES.block_size))



################################## class AnswersTranslator
class AnswersTranslator():
	# initialize the ciphers used to communicate with DO, U, and SE
	def __init__ (self, key_DO_AT, iv_DO_AT, key_U_AT, iv_U_AT, key_AT_SE, iv_AT_SE):	
		self.cipher_DO_AT = AES.new(key_DO_AT, AES.MODE_CBC, iv_DO_AT)
		self.cipher_U_AT = AES.new(key_U_AT, AES.MODE_CBC, iv_U_AT)
		self.cipher_AT_SE = AES.new(key_AT_SE, AES.MODE_CBC, iv_AT_SE)


	# receive and decrypt permutation sigma_V
	def receive_DO_AT(self, encrypted_sigma_V):
		self.sigma_V = json.loads(unpad(self.cipher_DO_AT.decrypt(encrypted_sigma_V), AES.block_size).decode('utf-8'))


	# replace nodes using the permutation sigma_V
	def receive_SE_AT(self, ciphertext_SE_AT):
		results_str = json.loads(unpad(self.cipher_AT_SE.decrypt(ciphertext_SE_AT), AES.block_size).decode('utf-8'))
		results_clean = extract_tuples_from_Jena_output (results_str)
		self.results_perm = []
		for result in results_clean:
			for i in range(len(result)):
				result[i] = get_key_for_val(self.sigma_V, int(result[i][1:])) # replace permutation with real node 
			self.results_perm.append(result)
		return self.results_perm


	# send encrypted result to U	
	def send_AT_U(self):
		data = {"results_perm" : self.results_perm}
		return self.cipher_U_AT.encrypt(pad(str(json.dumps(data)).encode('utf-8'), AES.block_size))




################################## class SPARQLEngine
class SPARQLEngine():
	# initialize the ciphers used to communicate with DO, QT, and AT
	def __init__ (self, key_DO_SE, iv_DO_SE, key_QT_SE, iv_QT_SE, key_AT_SE, iv_AT_SE):
		self.cipher_DO_SE = AES.new(key_DO_SE, AES.MODE_CBC, iv_DO_SE)
		self.cipher_QT_SE = AES.new(key_QT_SE, AES.MODE_CBC, iv_QT_SE)
		self.cipher_AT_SE = AES.new(key_AT_SE, AES.MODE_CBC, iv_AT_SE)


	# receive and decrypt (permuted) edges E_perm
	def receive_DO_SE(self, encrypted_E_perm, file_secure_graph, prefix):
		E_perm_aux = json.loads(unpad(self.cipher_DO_SE.decrypt(encrypted_E_perm), AES.block_size).decode('utf-8'))["E_perm"]
		self.file_secure_graph = file_secure_graph
		self.E_perm = list()
		with open(file_secure_graph, "w") as f:
			f.write(prefix + "\n\n")
			for (s, p, o) in E_perm_aux:
				self.E_perm.append((s, p, o))
				f.write(":" + str(s) + " :l" + str(p) + " :" + str(o) + ".\n")


	# translate encrypted query to SPARQL and run on encrypted graph with Apache Jena
	def receive_QT_SE(self, encrypted_query_perm, DIR_SE, sparql_translate_script, executable_sparql):
		data = json.loads(unpad(self.cipher_QT_SE.decrypt(encrypted_query_perm), AES.block_size).decode('utf-8'))
		self.i = data['i']
		self.query_xml_perm = data['query_xml_perm']
		self.file_secure_ans = DIR_SE + "secure-query-" + str(self.i) + ".sparql-ans.txt"
		with open (DIR_SE + "secure-query-" + str(self.i) + ".xml", "w") as f:
			f.write(self.query_xml_perm)
		os.system("mkdir -p " + DIR_SE + "aux")
		os.system(sparql_translate_script + " -w " + DIR_SE + "secure-query-" + str(self.i) + ".xml" + " -o " + DIR_SE + "/aux")
		os.system("mv " + DIR_SE + "aux/* " + DIR_SE + "secure-query-" + str(self.i) + ".sparql")
		os.system(executable_sparql + " --data " + self.file_secure_graph + " --query " + DIR_SE + "secure-query-" + str(self.i) + ".sparql" + " > " + self.file_secure_ans) 


	# encrypt and send (permuted) query results to AT
	def send_SE_AT(self):
		results_str = ""
		with open(self.file_secure_ans, "r") as f:
			line = f.readline()
			while line:
				results_str += line
				line = f.readline()
		return self.cipher_AT_SE.encrypt(pad(str(json.dumps({"results_str" : results_str})).encode('utf-8'), AES.block_size))

