# optimizer.py

from cfg_construction import *
from data_flow_analysis import Data_Flow_Analyzer

########################################################################################################################

def optimizer(): # mnain function for project 4
    # Read input file
    input_file = "./P4_Optimization/test_case_1.txt"  # Using relative path with explicit current directory
    
    # Build Control Flow Graph
    cfg = ControlFlowGraph(input_file)
    
    # Display leaders
    print("\nLeaders line #s:", [pos for pos in (node.leader_pos for node in cfg.nodes) if pos > 0])

    # Display CFG
    cfg.display()
    
    # Run Reaching Definitions Analysis
    print("\nReaching Definitions Analysis:")
    analyzer = Data_Flow_Analyzer(cfg)
    analyzer.compute_data_sets()
    
    # Run Live Variables Analysis
    print("\nLive Variables Analysis:")
    analyzer.analysis_type = "LiveVariables"
    analyzer.compute_data_sets()

optimizer()
########################################################################################################################
