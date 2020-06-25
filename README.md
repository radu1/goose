# GOOSE 
## (a secure framework for Graph OutsOurcing and Sparql Evaluation)

This repository contains the open-source code of GOOSE and scripts that allow to reproduce the experimental results from our paper.
If you use this code, please cite:

    @inproceedings{CL20,
      author    = {Ciucanu, R. and Lafourcade, P.},
      title     = {{GOOSE: A Secure Framework for Graph Outsourcing and SPARQL Evaluation}},
      booktitle = {DBSec},
      year      = {2020},
      pages     = {347--366}
    }


GOOSE is written in Python, and uses [Apache Jena](https://jena.apache.org/) (written in Java) for SPARQL evaluation and [gMark](https://github.com/graphMark/gmark) (written in C++) for graph and query workload generation.
The script `install-libraries.sh` installs the necessary libraries for running GOOSE.

The script `script-complete-workflow.sh` reproduces the complete workflow of the large-scale experimental study reported in the paper. This includes graph and query workload generation with gMark, graph outsourcing with GOOSE, and query evaluation (with GOOSE vs standard SPARQL evaluation), for 8000 queries.
As reported in the paper, it took 8 days for us to run this complete workflow. The entire generated data (graphs, queries, and query answers) takes 46GB.
