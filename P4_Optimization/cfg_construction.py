# cfg_constuctor
from typing import TextIO

###################################################################################################

class CFG_Node:
    """
    This class represent a single node of our control-flow graph.
    Each node in turn represents a single basic block within our 3AC.
    """
    def __init__(self, label=None):

        self.label = label      # Basic Block Index
        self.instructions = []  # List of TAC instructions in this block

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

########################################################################################################################

class ControlFlowGraph:
    """
    This class will contain our control-flow graph.
    """
    # Constructor
    def __init__(self, tac_file_path: str):
        self.nodes = []             # List of all CFG nodes
        self.label_to_node = {}     # Maps Labels to Nodes

        self.leaders = {}           # List of all basic-block leaders

        # Read Input File
        with open(tac_file_path, 'r') as file:
            self.file = file.readlines()

        # Build CFG
        self._get_leaders()
        self._build_graph()

    # END - Constructor
    ####################################################################################################################

    def _get_leaders(self):
        """
        Returns an integer list, with each integer representing the line # of a Leader.
        """
        # Rules for identifying headers
        # 1. Start of the program.            -- line 0
        # 2. At the "target" of any branch.   -- line lead to by a "goto"
        # 3. Immediately after any branch.    -- any line following a conditional.

        # Remove
        if True:
            # Loop through every line in the file
            for line_number, line in enumerate(self.file, start=1):

                # Strip whitespace
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Mark Starting Leader  (condition 1.)
                if len(self.leaders) == 0:
                    self.leaders[line_number] = "block_" + str(len(self.leaders)+1) # Add leader

                    # Mark Branch-Target Following Leader (condition 3.)
                    self._find_follower(1)
                    continue

                # Mark Branch-Target Leader (condition 2.)
                if "if " in line and "goto " in line:
                    start = line.find("goto ") + len("goto ")
                    num_str = ""
                    # Gather Digits After GOTO
                    while start < len(line) and line[start].isdigit():
                        num_str += line[start]
                        start += 1

                    # If Valid Target
                    if num_str:
                        # Convert Branch-Target to int
                        target = int(num_str)
                    else:
                        # Catch Error
                        print("Debug:", " Invalid GOTO / Jump Destination.")
                        continue

                    # Check if Branch-Target is already a Leader
                    if target not in self.leaders:
                        self.leaders[target] = "block_" + str(len(self.leaders) + 1)  # Add leader

                        # Mark Branch Following Leader (condition 3.)
                        self._find_follower(line_number)

        print("Debug:", "Finished getting leaders.")
    # End - _get_leaders()
    ####################################################################################################################

    def _find_follower(self, pre_leader: int):
        """
            Given a target line number this function will scan through the lines and add the first valid, non-comment,
            non-whitespace line to the leader list. But if an existing leader is encountered before a valid line is,
            then the function will terminate early.
        """
        index = pre_leader + 1
        while index < len(self.file):

            # Grab line
            line = self.file[index]

            # Strip leading/trailing whitespace
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):

                # Increment Line
                index += 1
                continue

            # Terminate on Leader
            if index in self.leaders:
                return None

            # Add Follower Leader
            self.leaders[index] = "block_" + str(len(self.leaders) + 1)  # Add leader

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
                self.nodes.append(current_node)
                self.label_to_node[current_node.label] = current_node  # map: Label -> Node

                # Create New Node
                current_node = CFG_Node(self.leaders[line_number])

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
        self.nodes.append(current_node)
        self.label_to_node[current_node.label] = current_node # map: Label -> Node

        # Add End Node
        current_node = CFG_Node("(end)")
        self.nodes.append(current_node)
        self.label_to_node[current_node.label] = current_node # map: Label -> Node

    # End - _build_graph()
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
            print()

    # End - display()
    ####################################################################################################################