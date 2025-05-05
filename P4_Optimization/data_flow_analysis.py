# data_flow_analysis.py

from cfg_construction import ControlFlowGraph

########################################################################################################################
class Data_Flow_Analyzer:
    """
    This class performs variable specific data-flow analysis on a given control-flow graph.
    """
    def __init__(self, cfg: ControlFlowGraph):
        self.flow_graph = cfg
        self.direction  = "Forward"
        self.path_use   = "Any"

    def compute_data_sets(self):

    def apply_optimizations(self):

    def set_direction(self, dir_param: str):
        self.__setattr__('direction', dir_param)
    def set_path(self,  path_param: str):
        self.__setattr__('path', path_param)
########################################################################################################################


########################################################################################################################
