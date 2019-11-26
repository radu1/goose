#!/bin/bash

# compile gMark: graph/query generator
cd gmark/src
make all

# compile gMark: query translator
cd querytranslate
make
cd ../../..

# directory where all files should be generated
DIR='data'
rm -rf $DIR
mkdir -p $DIR


nb_graphs_per_scaling_factor_query_evaluation=200
nb_graphs_per_scaling_factor_graph_outsourcing=10
min_scaling_factor=1000
max_scaling_factor_query_evaluation=10000
max_scaling_factor_graph_outsourcing=10000000
nb_runs=3
mode_debug=0 # if 1, also do sanity tests

declare -a use_cases=("bib" "uniprot" "social-network" "shop")

for use_case in ${use_cases[@]}; do
	mkdir -p $DIR/${use_case}
	mkdir -p $DIR/${use_case}-secure
done

for i in `seq 1 $nb_graphs_per_scaling_factor_query_evaluation`; do
	for use_case in ${use_cases[@]}; do
		scaling_factor=$min_scaling_factor
		run_queries=1
		while [ $scaling_factor -le $max_scaling_factor_graph_outsourcing ]; do
			id="${use_case}_${scaling_factor}_${i}"
			echo $id

			# gMark: graph and query generation
			./gmark/src/test -a -n $scaling_factor -c gmark/use-cases/${use_case}.xml -g $DIR/${use_case}/graph-$id.ttl -w $DIR/${use_case}/queries-$id.xml >> $DIR/${use_case}/log_${use_case}.txt

			# Directory where to store SPARQL translations
			mkdir -p $DIR/${use_case}/SPARQL-$id

			# gMark: query translation in SPARQL
			./gmark/src/querytranslate/test -w $DIR/${use_case}/queries-$id.xml -o $DIR/${use_case}/SPARQL-$id

			# Run Apache Jena nb_runs times for each query, only if current scaling factor is below max_scaling_factor_query_evaluation
			if [ $scaling_factor -gt $max_scaling_factor_query_evaluation ]
			then
				run_queries=0
			else
				for query in `ls $DIR/${use_case}/SPARQL-$id/*sparql`; do
					echo -e "\tStandard algorithm for $query"
					t_start=$(date +%s.%N)
					for j in `seq 1 $nb_runs`; do
						echo -e "\t\tRun $j";
						./apache-jena-3.13.0/bin/sparql --query $query --data $DIR/${use_case}/graph-$id.ttl > $query-ans.txt;
					done
					t_end=$(date +%s.%N)
					time=$(echo "($t_end-$t_start)/$nb_runs" | bc -l)
					nb_ans=$(echo "$(wc -l $query-ans.txt | cut -d" " -f 1) - 4" | bc)
					echo $scaling_factor $i $nb_ans $time >> ./data/${use_case}/times.txt
				done
			fi

			# Secure algorithm: do nb_runs times Graph outsourcing and run each query 
			python3 ./secure-algorithm/main.py $DIR $id $nb_runs $run_queries $mode_debug

			scaling_factor="$(($scaling_factor*10))"
		done
	done

	# Generate plots
	python3 ./script-plot.py $DIR $max_scaling_factor_query_evaluation

	# Once we have enough runs for graph outsourcing, we focus only on query evaluation
	if [ $i == $nb_graphs_per_scaling_factor_graph_outsourcing ]
	then
		max_scaling_factor_graph_outsourcing=$max_scaling_factor_query_evaluation
	fi
done


