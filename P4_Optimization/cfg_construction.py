# cfg_constuctor
from typing import TextIO

########################################################################################################################
def extract_line_num(line: str):
    if not line:
        return None
    if "(" in line and ")" in line:
        start = line.find("(") + 1
        end = line.find(")")
        if start < end:
            num_str = line[start:end]
            if num_str.isdigit():
                return int(num_str)
            else:
                print(f"Debug: Invalid line reference in goto: {num_str}")
    return None
########################################################################################################################

class CFG_Node:
    """
    This class represent a single node of our control-flow graph.
    Each node in turn represents a single basic block within our 3AC.
    """
    def __init__(self, label=None):

        self.label = label      # Basic Block Index
        self.instructions = []  # List of TAC instructions in this block
        self.leader_pos  = 0
        self.start_pos   = 0

        self.predecessors = []   # List of all predecessor nodes
        self.successors   = []   # List of successor nodes

        self.dominators   = []   # List of all nodes that dominate this node
        self.i_dominator  = None # The single immediate dominator of this node

        # Data-Flow Sets
        self.GEN  = set()
        self.KILL = set()
        self.IN   = set()
        self.OUT  = set()

    #
    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def add_successor(self, node):
        if node not in self.successors:
            self.successors.append(node)

    def add_predecessor(self, node):
        if node not in self.predecessors:
            self.predecessors.append(node)

    def map_leader(self):
        if self.instructions:
            line_num = extract_line_num(self.instructions[0])
            self.leader_pos = line_num if isinstance(line_num, int) else -1
########################################################################################################################

class ControlFlowGraph:
    """
    This class will contain our control-flow graph.
    """
    # Constructor
    def __init__(self, tac_file_path: str):
        self.nodes = []             # List of all CFG nodes
        self.label_to_node = {}     # Maps Labels to Nodes

        self.leaders = {}              # List of all basic-block leaders
        self.predecessor_to_label = {} # Maps a line# to a label
        self.successor_to_label   = {} # Maps a line# to a label

        # Read Input File
        with open(tac_file_path, 'r') as file:
            self.file = file.readlines()

        # Build CFG

        self._get_leaders()
        self._rename_blocks()
        self._build_graph()

    # END - Constructor
    ####################################################################################################################

    def _get_leaders(self):
        """
        Returns an integer list, with each integer representing the line # of a Leader.
        Rules for identifying leaders:
        1. First TAC instruction is a leader
        2. Any instruction that is the target of a goto/jump is a leader
        3. Any instruction that immediately follows a goto/jump is a leader
        """
        # First, find the first non-comment line (Rule 1)
        for line_number, line in enumerate(self.file, start=1):
            line = line.strip()
            if line and not line.startswith("#"):
                self.leaders[line_number] = "block_1"
                break

        # Process the rest of the file for other leaders
        for line_number, line in enumerate(self.file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for goto/jump instructions (Rules 2 and 3)
            if "goto" in line or "if" in line or "ifFalse" in line:

                # Extract target line number from (n) format
                num_str = extract_line_num(line)

                # If valid
                if num_str:
                        # Rule 2: Target of goto is a leader
                        target = int(num_str)
                        if target not in self.leaders:
                            self.leaders[target] = "block_" + str(len(self.leaders) + 1)

                # Rule 3: Line after goto is a leader
                """_find_followers() already does this more accurately."""
                self._find_follower(line_number)
                # next_line = line_number + 1
                # if next_line <= len(self.file) and next_line not in self.leaders:
                #     self.leaders[next_line] = "block_" + str(len(self.leaders) + 1)\

        # Sanity check: remove invalid 0 line leader
        if 0 in self.leaders:
            print("Warning: Line 0 incorrectly added as a leader. Removing.")
            self.leaders.pop(0)

        print("Debug: Leaders found:", sorted(self.leaders.keys()))
        # print("Debug: Leader blocks:", {k: v for k, v in sorted(self.leaders.items())})
    # End - _get_leaders()
    ####################################################################################################################
    def _find_follower(self, pre_leader: int):
        """
            Given a target line number this function will scan through the lines and add the first valid, non-comment,
            non-whitespace line to the leader list. But if an existing leader is encountered before a valid line is,
            then the function will terminate early.
        """
        index = pre_leader  # pre_leader is 1-based, keep index aligned with line numbers

        while index < len(self.file):
            # Grab line (convert to 0-based index for list access)
            line = self.file[index].strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                index += 1
                continue

            # Terminate on Leader
            if (index + 1) in self.leaders:
                return None

            # Add Follower Leader
            self.leaders[index + 1] = "block_" + str(len(self.leaders) + 1)  # Add leader
            return

    # End - _find_follower()
    ####################################################################################################################
    def _rename_blocks(self):
        """
            This method renames all the blocks in the order in which their leaders appear.
        """
        # Sort leaders
        keys = sorted(self.leaders.keys())
        for index, leader in enumerate(keys):
            self.leaders[leader] = "block_" + str(index + 1)  # Add leader


    # End - _find_follower()
    ####################################################################################################################

    def _build_graph(self):
        """
            This method will populate the control-flow graph.
        """
        # Buffers that track node relationships
        predecessor_buffer = []
        successor_buffer   = []

        # Add Start Node
        current_node = CFG_Node("(start)")


        # Loop through every line in the file
        for line_number, line in enumerate(self.file, start=1):

            # Check If Leader
            if line_number in self.leaders:

                # Push Previous Node
                if current_node.instructions:
                    current_node.map_leader()
                    self.nodes.append(current_node)
                    self.label_to_node[current_node.label] = current_node  # map: Label -> Node

                # Create New Node
                current_node = CFG_Node(self.leaders[line_number])
                current_node.real_start = line_number

            # Strip whitespace
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Add Instructions to Current Node
            current_node.add_instruction(line)

        # END - Primary Loop
        ####################

        # Push Previous Node - (out-of-loop)
        current_node.map_leader()
        self.nodes.append(current_node)
        self.label_to_node[current_node.label] = current_node # map: Label -> Node

        # Add End Node
        current_node = CFG_Node("(end)")
        self.nodes.append(current_node)
        self.label_to_node[current_node.label] = current_node # map: Label -> Node

    # End - _build_graph()
    ####################################################################################################################

    ####################################################################################################################

    def _calculate_successors(self):
        label_map = {node.label: node for node in self.nodes if node.label}
        for node in self.nodes:
            new_successors = []
            for target_label in node.successors:
                if target_label in label_map:
                    new_successors.append(label_map[target_label])
            node.successors = new_successors

    # End - _calculate_successors()
    ####################################################################################################################

    def display(self):
        for node in self.nodes:
            print(f"Node: {node.label}")
            for instr in node.instructions:
                print(f"    {instr}")
            if node.successors:
                print(f"    Successors: {[succ.label for succ in node.successors]}")
            print("\t  |\n\t  V")

    # End - display()
    ####################################################################################################################
