# optimizer.py

from cfg_construction import *

########################################################################################################################

def optimizer(self):
    """
        We can refactor this to main later, or just leave it as is. Either way its the main function of project 4.
    """

    print("This is the optimizer :3\n")

    # Initialization
    input_file = "3AC_cases.txt"                      # Infile Directory
    control_flow_graph = ControlFlowGraph(input_file) # CFG Object

    # OUTPUT - Display Leaders
    print("\nLeaders found on the following lines.")
    print(", ".join(str(leader) for leader in sorted(control_flow_graph.leaders)))

    # OUTPUT - Display CFG
    print(".\nControl-Flow Graph:")
    control_flow_graph.display()







optimizer(None)
########################################################################################################################
