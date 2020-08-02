#!/bin/bash

id=example_0_0
mkdir -p example/SPARQL-$id
mkdir -p example-secure

############################
echo "Standard query evaluation, without any security"

# Translate the UCRPQ in SPARQL using gMark
../gmark/src/querytranslate/test -w example/queries-$id.xml -o example/SPARQL-$id

# Run the SPARQL query on the .ttl graph and output the query answers in a .txt file
../apache-jena-3.13.0/bin/sparql --query example/SPARQL-$id/query-0.sparql --data example/graph-$id.ttl > ./example/SPARQL-$id/query-0.sparql-ans.txt


############################
echo "GOOSE"
cd ..
python3 secure-algorithm/main.py running-example $id 1 1 0
# All generated files are in "running-example/example-secure"
