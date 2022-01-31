# GOOSE 
## (a secure framework for Graph OutsOurcing and Sparql Evaluation)

This repository contains the open-source code of GOOSE and scripts that allow to reproduce the running example and the experimental results from our paper.

GOOSE is written in Python, and uses [Apache Jena](https://jena.apache.org/) (written in Java) for SPARQL evaluation and [gMark](https://github.com/graphMark/gmark) (written in C++) for graph and query workload generation.
The script `install-libraries.sh` installs the necessary libraries for running GOOSE.

The script `example.sh` from the directory `running-example` reproduces the running example that we used in our [DBSec paper](https://link.springer.com/chapter/10.1007%2F978-3-030-49669-2_20) and in our [DBSec talk](https://www.youtube.com/watch?v=ZhtpulFf3rs).

The script `script-complete-workflow.sh` reproduces the complete workflow of the large-scale scalability study reported in the paper. This includes graph and query workload generation with gMark, graph outsourcing with GOOSE, and query evaluation (with GOOSE vs standard SPARQL evaluation), for 8000 queries.
To run smaller (and quicker) scalability experiments, you should set to smaller values the scaling factors specified in the script.


If you use this code, please cite:

    @inproceedings{CL20,
      author    = {Ciucanu, R. and Lafourcade, P.},
      title     = {{GOOSE: A Secure Framework for Graph Outsourcing and SPARQL Evaluation}},
      booktitle = {IFIP WG 11.3 Conference on Data and Applications Security and Privacy (DBSec)},
      year      = {2020},
      pages     = {347--366}
    }
    
    @inproceedings{CL20demo,
      author    = {Ciucanu, R. and Lafourcade, P.},
      title     = {{Demonstration of GOOSE: A Secure Framework for Graph Outsourcing and SPARQL Evaluation}},
      booktitle = {International Semantic Web Conference (ISWC) -- Demo},
      year      = {2020}
    }



