# data_flow_analysis.py
# Project 4 - Machine Independent Optimization
# Implements data flow analysis for compiler opt.

from cfg_construction import ControlFlowGraph, CFG_Node

class Data_Flow_Analyzer: # class performs variable specific dfa on a given cfg
    def __init__(self, cfg: ControlFlowGraph):
        self.cfg = cfg
        self.analysis_type = "ReachingDefinitions"
        self.definitions = set()

    def compute_data_sets(self): # decides which analysis to run (RD or LV)
        if self.analysis_type == "ReachingDefinitions":
            self._do_reaching_definitions()
        else:
            self._do_live_variables()

    def _do_reaching_definitions(self): # runs reaching definitions analysis
        self._find_definitions()
        self._setup_gen_kill()
        self._init_in_out()
        self._run_forward_analysis()

    def _do_live_variables(self): # runs live variables analysis
        self._setup_use_def()
        self._init_in_out()
        self._run_backward_analysis()

    def _find_definitions(self): # finds all variable definitions in the program
        for block in self.cfg.nodes:
            for instr in block.instructions:
                if '=' in instr:
                    var = instr.split('=')[0].strip()
                    self.definitions.add(var)

    def _setup_gen_kill(self): # sets up gen and kill sets for each block
        for block in self.cfg.nodes:
            block.GEN = set()
            block.KILL = set()
            
            for instr in block.instructions:
                if '=' in instr:
                    var = instr.split('=')[0].strip()
                    block.GEN.add(var)
                    
                    for other_def in self.definitions:
                        if other_def != var:
                            var_base = var.split('[')[0] if '[' in var else var
                            if other_def.startswith(var_base):
                                block.KILL.add(other_def)

    def _setup_use_def(self): # sets up use and def sets for each block
        for block in self.cfg.nodes:
            block.USE = set()
            block.DEF = set()
            
            for instr in block.instructions:
                # Handle assignment statements
                if '=' in instr:
                    def_var = instr.split('=')[0].strip()
                    block.DEF.add(def_var)
                    
                    # Get the right-hand side expression
                    expr = instr.split('=')[1].strip()
                    
                    # Handle array accesses
                    if '[' in expr and ']' in expr:
                        # Extract the index expression
                        start = expr.find('[') + 1
                        end = expr.find(']')
                        index_expr = expr[start:end]
                        # Add any variables in the index expression
                        for var in self.definitions:
                            if var in index_expr and var not in block.DEF:
                                block.USE.add(var)
                    
                    # Handle regular variables in expressions
                    # instead of set() operations everywhere
                    block.OUT = list(block.GEN)
                    for var in block.IN:
                        if var not in block.KILL:
                            block.OUT.append(var)
                    block.OUT = set(block.OUT)  # i dont think it's optimal LOL - brian

                
                # Handle if statements and conditions
                elif 'if' in instr:
                    # Extract the condition part
                    if 'then' in instr:
                        condition = instr.split('then')[0].replace('if', '').strip()
                    else:
                        condition = instr.replace('if', '').strip()
                    
                    # Add variables used in the condition
                    for var in self.definitions:
                        if var in condition and var not in block.DEF:
                            block.USE.add(var)

    def _init_in_out(self): # initializes the IN and OUT sets to empty
        for block in self.cfg.nodes:
            block.IN = set()
            block.OUT = set()

    def _run_forward_analysis(self): # runs the forward analysis until it stabilizes
        changed = True
        iteration = 0
        
        while changed:
            changed = False
            iteration += 1
            
            print(f"\nIteration {iteration}:")
            
            for block in self.cfg.nodes:
                old_in = block.IN.copy()
                old_out = block.OUT.copy()
                
                block.IN = set()
                for pred in block.predecessors:
                    block.IN.update(pred.OUT)
                
                block.OUT = block.GEN.union(block.IN - block.KILL)
                
                if old_in != block.IN or old_out != block.OUT:
                    changed = True
                
                self._print_state(block)
            
            print("\n" + "="*50)

    def _run_backward_analysis(self): # runs te backward analysis until it stabilizes
        changed = True
        iteration = 0
        
        while changed:
            changed = False
            iteration += 1
            
            print(f"\nIteration {iteration}:")
            
            for block in self.cfg.nodes:
                old_in = block.IN.copy()
                old_out = block.OUT.copy()
                
                block.OUT = set()
                for succ in block.successors:
                    block.OUT.update(succ.IN)
                
                block.IN = block.USE.union(block.OUT - block.DEF)
                
                if old_in != block.IN or old_out != block.OUT:
                    changed = True
                
                self._print_state(block)
            
            print("\n" + "="*50)

    def _print_state(self, block: CFG_Node): # function prints the current state of a block
        print(f"\nBlock {block.label}:")
        print(f"IN: {sorted(block.IN)}")
        print(f"OUT: {sorted(block.OUT)}")
        if self.analysis_type == "ReachingDefinitions":
            print(f"GEN: {sorted(block.GEN)}")
            print(f"KILL: {sorted(block.KILL)}")
        else:
            print(f"USE: {sorted(block.USE)}")
            print(f"DEF: {sorted(block.DEF)}")
