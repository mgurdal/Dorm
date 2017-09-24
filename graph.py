import pycallgraph


from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

import main

config = Config()
config.trace_filter = GlobbingFilter(exclude=[
    'pycallgraph.*',
    'inspect*',
])

graphviz = GraphvizOutput(output_file='filter_exclude.png')

with PyCallGraph(output=graphviz, config=config):
    main.main()
