# optimizer.py

from cfg_construction import *
from data_flow_analysis import Data_Flow_Analyzer

########################################################################################################################

def optimizer(): # mnain function for project 4
    # Read input file
    input_file = "./P4_Optimization/test_case_3.txt"  # Using relative path with explicit current directory
    
    # Build Control Flow Graph
    cfg = ControlFlowGraph(input_file)
    
    # Display leaders
    print("\nLeaders line #s:", [pos for pos in (node.leader_pos for node in cfg.nodes) if pos > 0])

    # Display Console CFG
    cfg.display_to_console()

    # Prompt User Input
    response = input("\n"
                     "Would you like to generate PDF that displays the "
                     "Control-Flow Graph with Graphviz? (Y/N): ").strip().upper()
    if response == ("Y"):
        print("Great! Your PDF is generating.\n")
        # Display graphviz CFG
        cfg.display_to_pdf()
    else:
        print("Okay. The PDF generation will be skipped.\n")

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
