# GOOSE 
## (a framework for encrypted Graph OutsOurcing and SPARQL Evaluation)

This repository contains the open-source code of GOOSE and scripts that allow to reproduce the experimental results from our paper.

GOOSE is written in Python, and uses [Apache Jena](https://jena.apache.org/) (written in Java) for SPARQL evaluation and [gMark](https://github.com/graphMark/gmark) (written in C++) for graph and query workload generation.

The script `install-libraries.sh` installs the necessary libraries for running GOOSE.

The script `script-complete-workflow.sh` reproduces the complete workflow of the large-scale experimental study reported in the paper. This includes graph and query workload generation with gMark, graph outsourcing with GOOSE, and query evaluation (with GOOSE vs standard SPARQL evaluation), for 8000 queries.
As reported in the paper, it took eight days for us to run this complete workflow.

The entire data that we used (graphs, queries, and query answers) takes 46GB and includes many large files, hence we were not able to add it on GitHub, but nonetheless we make it available at a different URL.
Thus, to reproduce the plots from the paper, you can download an archive (11GB) of the data, uncompress, and run only the script plot (the two parameters indicate data directory and graph scaling factor on which to zoom for the time shares of the participants)
```
wget http://sancy.univ-bpclermont.fr/~lafourcade/95BQR75_CL19/data.tgz
tar -xvf data.tgz
python3 script-plot.py data 10000
```
