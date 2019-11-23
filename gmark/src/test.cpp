#include <unistd.h>
#include <fstream>
#include <chrono>
#include <thread>

#include "config.h"
#include "gmark.h"
#include "configparser.h"
#include "workload.h"
#include "workload2.h"
#include "report.h"
#include "randomgen.h"


int main(int argc, char ** argv) {
	string conf_file;
	string graph_file;
	string workload_file;
	int c;
	config::config conf;

	while ((c = getopt(argc, argv, "c:g:w:an:")) != -1) {
		switch(c) {
			case 'c':
				conf_file = optarg;
				break;
			case 'g':
				graph_file = optarg;
				break;
			case 'w':
				workload_file = optarg;
				break;
			case 'a':
				conf.print_alias = true;
				break;
			case 'n':
				conf.nb_nodes.push_back(stoi(optarg)); 
				conf.nb_graphs = 1;
			break;
		}
	}
  
	configparser::parse_config(conf_file, conf);
	conf.complete_config();

	report::report rep1;
	ofstream graph_stream;
	string fileName = graph_file;
	graph_stream.open(fileName);

	graph_stream << "@prefix : <http://example.org/gmark/> .\n\n" ;
	graph::ntriple_graph_writer writer(graph_stream);
	writer.build_graph(conf, rep1, 0);
	graph_stream.close();

        report::workload_report rep2;
        ofstream workload_stream;
        workload_stream.open(workload_file);
        workload::workload wl;
	workload2::generate_workload(conf, wl, rep2);
        workload::write_xml(wl, workload_stream, conf);
        workload_stream.close();

	cout << rep1.nb_nodes << " " << rep1.nb_edges << " " << conf.workloads[0].size << endl;

}

