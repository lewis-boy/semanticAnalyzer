# /P4_Optimization/cfg_construction.py

from typing import TextIO

########################################################################################################################
"""
Helper Functions:
"""

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

# END - Helper Functions
########################################################################################################################


class CFG_Node:
    """
    This class represent a single node of our control-flow graph.
    Each node in turn represents a single basic block within our 3AC.
    """
    # Class Constructor
    def __init__(self, label=None, real_start=None):

        # Identifying Data
        self.label = label      # Basic Block Index/name
        self.instructions = []  # List of TAC instructions in this block

        # Positional Data
        self.real_start = real_start
        self.leader_pos  = 0

        # Relational Data
        self.predecessors = []   # List of all predecessor nodes
        self.successors   = []   # List of successor nodes
        self.dominators   = []   # List of all nodes that dominate this node
        self.i_dominator  = None # The single immediate dominator of this node

        # Data-Flow Sets
        self.GEN  = set()
        self.KILL = set()
        self.IN   = set()
        self.OUT  = set()

    # END - Constructor
    ####################################################################################################################
    """ 
    Public Methods:
    """

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

# END - class CFG_Node:
########################################################################################################################


class ControlFlowGraph:
    """
    This class contains and manages our control-flow graph.
    """

    # Class Constructor
    def __init__(self, tac_file_path: str):

        # Node Data
        self.nodes = []          # List of all CFG nodes
        self.label_to_node = {}  # Maps Labels to Nodes
        self.leaders = {}        # List of all basic-block leaders

        # Read Input File
        self.file_name = tac_file_path
        with open(tac_file_path, 'r') as file:
            # Keep file open for all methods
            self.file = file.readlines()

        # Build the Nodes of the CFG:
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
        # Loop through all lines in the input file
        for line_number, line in enumerate(self.file, start=1):

            # Remove leading/trailing whitespace
            line = line.strip()

            # If not comment and not emtpy - Mark starting leader (rule 1)
            if line and not line.startswith("#"):
                self.leaders[line_number] = "block_1"
                break # Terminate early after finding start

        # Loop through all lines in the file
        for line_number, line in enumerate(self.file, start=1):

            # Remove leading/trailing whitespace
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Check for goto/jump instructions
            if "goto" in line or "if" in line or "ifFalse" in line:

                # Extract target line number from (n) format
                num_str = extract_jump_target(line)

                # If valid
                if num_str:

                        # Cast target to integer
                        target = int(num_str)

                        # If branch-target isnt already a leader
                        if target not in self.leaders:

                            # Mark branch-target as a leader (Rule 2)
                            self.leaders[target] = "block_" + str(len(self.leaders) + 1)

                # Find following leader if it exists (Rule 3)
                self._find_follower(line_number)

        # Sanity check
        if 0 in self.leaders:
            print("Debug: Line 0 incorrectly added as a leader. Removing.")
            self.leaders.pop(0)

        # Debugging output
        print("Debug: Leaders found:", sorted(self.leaders.keys()))
        # print("Debug: Leader blocks:", {k: v for k, v in sorted(self.leaders.items())})

    # End - _get_leaders()
    ####################################################################################################################

    def _find_follower(self, pre_leader: int):
        """
            Given a target line number this function will scan through the lines and add the first valid,
            non-comment, non-whitespace line to the leader list. But if an existing leader is encountered
            before a valid line is, then the function will terminate early.
        """
        # Grab index
        index = pre_leader # Maintains alignment

        # Loop until no lines remain
        while index < len(self.file):

            # Grab line
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

        # Loop through all sorted leaders
        for index, leader in enumerate(keys):

            # Rename with proper label
            self.leaders[leader] = "block_" + str(index + 1)

    # End - _find_follower()
    ####################################################################################################################

    def _construct_nodes(self):
        """
            This method will create the nodes representing every basic-block using the location data
            of all the leaders, it will also gather and save all instructions associated with each
            block. Operates on a single pass of the node list.
        """
        # Add Start Node
        current_node = CFG_Node("(start)")

        # Loop through every line in the file
        for line_number, line in enumerate(self.file, start=1):

            # Check If Leader
            if line_number in self.leaders:

                # Push Previous Node
                if current_node.instructions: # Has intruction
                    current_node.map_leader()
                if current_node.instructions or not self.nodes:
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

    def display_to_console(self):
        """
            This method prints the control-flow graph to the console in a limited capacity.
            Jumps are not represented. To see jumps look at the output of the display_to_pdf()
            method.
        """
        side_len = 12 # 1/2 of title bar length

        # Output title
        print("\033[1m" + "\n" + "_" * side_len + " Control Flow Graph " + "_" * side_len + "\n\n" + "\033[0m")

        # Loop through all nodes
        for node in self.nodes:
            print(f"\033[1;4mNode: {node.label}\033[0m")

            # Loop through all instructions
            for instr in node.instructions:
                print(f"    {instr}")

            # Format and display predecessors
            pred_count = len(node.predecessors)
            formatted_preds = ", ".join(f"\033[1;4m{pred.label}\033[0m" for pred in node.predecessors)
            print(f"    \033[1mPredecessors ({pred_count}):\033[0m    {formatted_preds if formatted_preds else 'None'}")

            # Format and display successors
            succ_count = len(node.successors)
            formatted_succs = ", ".join(f"\033[1;4m{succ.label}\033[0m" for succ in node.successors)
            print(f"    \033[1mSuccessors   ({succ_count}):\033[0m    {formatted_succs if formatted_succs else 'None'}")

            # Fall-through arrow to convey top-down relationships
            if node != self.nodes[-1]:
                print("\t  |\n\t  V")

    # End - display()
    ########################################################################################################################

    def _normalize_jumps_to_labels(self):
        """
            This method finds and modifies each jump instruction by replacing it's int jump target
            to the name of the block it is jumping to. So, i.e. goto(14) -> goto(block_4).
            The reason we do this is because during optimization instructions can be modified and
            relative line numbering can be lost, so its important to preserve jumps as target at blocks.
            The logic for efficiently finding these jumps is that all jumps statements will always be
            the last instruction in any block they are apart of. (because of rule 3)
        """
        # Loop through all nodes
        for basic_block in self.nodes:

            # Skip start and end nodes
            if not basic_block.instructions:
                continue

            # Seperate last instruction
            updated_instructions = basic_block.instructions[:-1]
            last_instruction = basic_block.instructions[-1]

            # save original last for debugging
            original_instruction = last_instruction
            preserved_prefix = ""

            # Preserve leading line markers
            if last_instruction.startswith("("):
                close_paren_index = last_instruction.find(")")

                # Detects a goto jump at end of line
                if close_paren_index != -1 and last_instruction[1:close_paren_index].isdigit():
                    preserved_prefix = last_instruction[:close_paren_index + 1]  # Save prefix
                    last_instruction = last_instruction[
                                       close_paren_index + 1:].strip()  # Build embedded instruction
            # Extract a jump target
            jump_target_line = extract_line_num(last_instruction)

            # If valid target
            if jump_target_line:

                # Grab label
                jump_block_label = self.leaders.get(jump_target_line)

                # If valid label
                if jump_block_label:
                    # Replace jump number with actual block name
                    last_instruction = last_instruction.replace(f"({jump_target_line})", jump_block_label)

            # Add back prefix and track changes
            final_instruction = f"{preserved_prefix} {last_instruction}".strip()
            if final_instruction != original_instruction:
                print(f"Rewriting: '{original_instruction}' → '{final_instruction}'")
            updated_instructions.append(final_instruction)

            basic_block.instructions = updated_instructions

    # End - _normalize_jumps_to_labels()
    ########################################################################################################################

    def _generate_fall_through_flow(self):
        """
            Populates successor and predecessor lists of all nodes in the path of the default fall through.
            The logic here is just to follow the default order of blocks unless there is an unconditional
            skip meaning there is absolutely dead code that is never used.
        """
        # Loop through all nodes
        for i, node in enumerate(self.nodes):

            # Skip Start and End nodes (no instructions)
            if node.label in ("(start)", "(end)") or not node.instructions:
                continue

            # Grab last instruction
            last_instr = node.instructions[-1].strip()
            is_unconditional_jump = last_instr.startswith("goto") and "if" not in last_instr

            # Skip fall-through for unconditional jumps
            if is_unconditional_jump:
                continue

            # Check if next block exists
            if i + 1 < len(self.nodes):
                # Follow fall-through
                next_node = self.nodes[i + 1]
                if next_node and next_node != node:
                    node.add_successor(next_node)

        # Manually attach start
        self.nodes[0].add_successor(self.nodes[1])

    ####################################################################################################################

    def _populate_successors(self):
        """
        Populates the successor list for each node based on jump instructions only.
        Now works on normalized block labels instead of raw line numbers.
        """
        # Loops through every node
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
        """
        This method given a line number from the input file, will return the actual instruction line
        from the basic block it is currently an attribute of. Basically it indexes a line num to
        better interface with the stored instructions set.
        """
        offset = target_line - block.real_start

        # Check if line exists in block
        if 0 <= offset < len(block.instructions):
            # Found
            return block.instructions[offset]
        else:
            # Not found
            print(f"Debug: Invalid offset {offset} in block {block.label}")
            return None

    # END - _resolve_jump_target
    ########################################################################################################################

    # Display rework
    def display_to_pdf(self, filename="cfg"):
        """
            This method uses the graphviz library to display the structure and relationships of the generated
            control-flow graph.
        """
        import os
        from graphviz import Digraph


        dot = Digraph(comment="Control Flow Graph")

        # Create title with file path
        graph_title = f"Control-Flow Graph: {self.file_name}"

        # Graph metadata and layout settings
        dot.attr(
            label=graph_title,  # Page title at the top
            labelloc='t',       # Position title at top
            fontsize='16',
            fontname='JetBrains Mono',
        rankdir='TB',       # Top-down layout
            splines='ortho',    # Right-angle elbow arrows
            ranksep='0.3',      # Vertical seperation
            nodesep='0.6',      # Horizontal seperation
            margin='0.2'        # Page Margin
        )

        # Node appearance
        dot.attr('node',
                 shape='plaintext',
                 fontname='JetBrains Mono', # might not work cuz not built-in
        fontsize='12',
                 margin='0.05'
                 )

        node_ids = []  # Used to force vertical alignment later

        # Create graph nodes with HTML tables
        for node in self.nodes:
            node_id = str(node.label).replace("(", "").replace(")", "")
            node_ids.append(node_id)

            header = f"<B>{node.label}</B>"

            # Convert TAC instructions to table rows, escaping angle brackets
            rows = "\n".join(
                f"<TR><TD ALIGN='LEFT'>{line.replace('<', '&lt;').replace('>', '&gt;')}</TD></TR>"
                for line in node.instructions
            )

            html_label = f"""< 
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                    <TR><TD ALIGN="CENTER">{header}</TD></TR>
                    {rows}
                </TABLE> 
            >""".replace("\n", "")

            dot.node(node_id, label=html_label)

        # Add invisible edges to force strict vertical alignment
        for i in range(len(node_ids) - 1):
            dot.edge(node_ids[i], node_ids[i + 1], style='invis', weight='100')

        # Add control flow edges based on successor relationships
        for node in self.nodes:
            src = str(node.label).replace("(", "").replace(")", "")
            for succ in node.successors:
                dst = str(succ.label).replace("(", "").replace(")", "")
                dot.edge(src, dst, arrowsize='0.6', penwidth='1.2')

        # Generate and render the output file (opens viewer by default)
        dot.render(f"{filename}.gv", view=True)

    # End - display_cfg_graphviz()
    ####################################################################################################################



