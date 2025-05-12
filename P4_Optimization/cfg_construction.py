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

def extract_jump_target(line: str):
    if "goto" in line:
        start = line.find("goto")
        open_paren = line.find("(", start)
        close_paren = line.find(")", open_paren)
        if open_paren != -1 and close_paren != -1:
            num_str = line[open_paren + 1:close_paren]
            if num_str.isdigit():
                return int(num_str)
    return None
########################################################################################################################

class CFG_Node:
    """
    This class represent a single node of our control-flow graph.
    Each node in turn represents a single basic block within our 3AC.
    """
    def __init__(self, label=None, real_start=None):

        self.label = label      # Basic Block Index
        self.real_start = real_start

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

        # Build the Nodes of the CFG
        self._get_leaders()
        self._rename_blocks()
        self._construct_nodes()
        self._normalize_jumps_to_labels() # rename goto targets to blocks

        # Construct Predecessor & Successor Sets:
        self._populate_successors()        # Calculates jump successors
        self._generate_fall_through_flow() # Skips rely on jumps
        self._populate_predecessors()      # Relies on successor set being accurate


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
                num_str = extract_jump_target(line)

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

    def _construct_nodes(self):
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

    ################ - OLD CODE - ###########################################
    #
    # def _calculate_successors(self):
    #     label_map = {node.label: node for node in self.nodes if node.label}
    #     for node in self.nodes:
    #         new_successors = []
    #         for target_label in node.successors:
    #             if target_label in label_map:
    #                 new_successors.append(label_map[target_label])
    #         node.successors = new_successors
    ###########################################################################

    # End - _calculate_successors()
    ####################################################################################################################

    def display(self):
        side_len = 12
        print("\033[1m" + "\n" + "_" * side_len + " Control Flow Graph " + "_" * side_len + "\n\n" + "\033[0m")
        for node in self.nodes:
            print(f"\033[1;4mNode: {node.label}\033[0m")
            for instr in node.instructions:
                print(f"    {instr}")

            # Format Predecessors
            pred_count = len(node.predecessors)
            formatted_preds = ", ".join(f"\033[1;4m{pred.label}\033[0m" for pred in node.predecessors)
            print(f"    \033[1mPredecessors ({pred_count}):\033[0m    {formatted_preds if formatted_preds else 'None'}")

            # Format Successors
            succ_count = len(node.successors)
            formatted_succs = ", ".join(f"\033[1;4m{succ.label}\033[0m" for succ in node.successors)
            print(f"    \033[1mSuccessors   ({succ_count}):\033[0m    {formatted_succs if formatted_succs else 'None'}")

            # Arrow
            print("\t  |\n\t  V")

    # End - display()
    ####################################################################################################################
    def _normalize_jumps_to_labels(self):
        """
        Rewrites jump targets (e.g., goto (N)) to use block labels (e.g., goto block_X),
        while preserving the original line number marker (e.g., (2)) at the beginning of the instruction.
        """
        for node in self.nodes:
            new_instructions = []
            for instr in node.instructions:
                original = instr  # keep for debugging
                prefix = ""

                # Preserve the original line number marker, e.g., (2)
                if instr.startswith("("):
                    end_idx = instr.find(")")
                    if end_idx != -1 and instr[1:end_idx].isdigit():
                        prefix = instr[:end_idx + 1]
                        instr = instr[end_idx + 1:].strip()

                # Attempt to extract a jump target (e.g., from "goto (32)")
                target_line = extract_line_num(instr)
                if target_line:
                    label = self.leaders.get(target_line)
                    if label:
                        # Replace (N) anywhere in the *remaining* instruction with block_X
                        instr = instr.replace(f"({target_line})", label)

                # Recombine with preserved prefix
                full_instr = f"{prefix} {instr}".strip()
                if full_instr != original:
                    print(f"Rewriting: '{original}' → '{full_instr}'")
                new_instructions.append(full_instr)

            node.instructions = new_instructions

    ####################################################################################################################
    def _generate_fall_through_flow(self):
        """
            Populates successor and predecessor lists of all nodes in the path of the default fall through.
        """
        # Loop through all nodes
        for i, node in enumerate(self.nodes):
            if node.label in ("(start)", "(end)") or not node.instructions:
                continue

            last_instr = node.instructions[-1].strip()
            is_unconditional_jump = last_instr.startswith("goto") and "if" not in last_instr

            # Skip fall-through for unconditional jumps
            if is_unconditional_jump:
                continue

            # Add fall-through to next block if it exists
            if i + 1 < len(self.nodes):
                next_node = self.nodes[i + 1]
                if next_node and next_node != node:
                    node.add_successor(next_node)

    ####################################################################################################################
    def _populate_successors(self):
        """
        Populates the successor list for each node based on jump instructions only.
        Now works on normalized block labels instead of raw line numbers.
        """
        for node in self.nodes:
            if not node.instructions or node.label in ("(start)", "(end)"):
                continue

            last_instr = node.instructions[-1].strip()

            # Look for any target in the form "goto block_X" or "if ... goto block_X"
            if "goto" not in last_instr:
                continue

            # Find block label after 'goto'
            parts = last_instr.split("goto")
            if len(parts) < 2:
                continue  # malformed

            jump_target = parts[1].strip().split()[0]  # gets block_X
            if jump_target in self.label_to_node:
                target_node = self.label_to_node[jump_target]
                if target_node and target_node != node:
                    print(f"Debug: {node.label} jumps to {target_node.label}")
                    node.add_successor(target_node)

    # End - populate_successors()
    ####################################################################################################################

    def _populate_predecessors(self):
        """
            Populates the predecessor list for each node based on existing successor links.
        """
        for node in self.nodes:
            for succ in node.successors:
                succ.add_predecessor(node)

    # End - populate_predecessors()
    ####################################################################################################################
    def _resolve_jump_target(self, block: CFG_Node, target_line: int):
        offset = target_line - block.real_start
        if 0 <= offset < len(block.instructions):
            return block.instructions[offset]
        print(f"Debug: Invalid offset {offset} in block {block.label}")
        return None
