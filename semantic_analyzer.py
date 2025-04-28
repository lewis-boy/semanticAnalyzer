def main():
    types = ['int', 'float', 'bool']
    symbol_table  = {}
    stack = []
    operators = ['+', '-', '*', '/', '&&', '||']


    # TODO turn the right side of the OR statement into its own function with proper error message.
    def isValid(type, value):
        if type == 'int':
            return value.lstrip('-').isdigit() or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'int')
        elif type == 'float':
            parts = value.lstrip('-').split('.')
            return (len(parts) == 2 and all(part.isdigit() for part in parts)) or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'float')
        elif type == 'bool':
            return value in ['true', 'false'] or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'bool')
        return False

    def getOperands(rhs):
        operands = []
        for element in rhs:
            if element not in operators:
                operands.append(element)
        return operands
    
    def getOperators(rhs):
        operators = []
        for element in rhs:
            if element in operators:
                operators.append(element)
        return operators
    
    def isValidOperand(operands, type):
        for operand in operands:
            if not isValid(type, operand):
                return False
        return True
    
    def isValidOperator(operatorsArray, type):
        for operator in operatorsArray:
            if type == "int" or type == "float":
                if operator not in ["+", "-", "*", "/"]:
                    return False
            else:
                if operator not in ["&&" or "||"]: 
                    return False
        return True
    
    def hadEqualSign(array):
        return len(array) > 1
    
    def areInitializing(array):
        return len(array) > 1
    
    def hasMoreThanOneToken(array):
        return len(array) > 1
    
    def isInSymbolTable(name):
        return name in symbol_table
    
    def firstTokenIsTypeKeyword(token):
        return token in types
    
    def isReturnStatement(token):
        return token == "return"
    
    def hasValidRhs(rhs, name, statement):
        operandsAndOperators = rhs.split()
        operands = getOperands(operandsAndOperators)
        operators = getOperators(operandsAndOperators)
        if not isValidOperand(operands, symbol_table[name]["type"]):
            print(f"{statement}: invalid operands. Expected operands of type {symbol_table[name]["type"]}")
            return False
        if not isValidOperator(operators, symbol_table[name]["type"]):
            print(f"{statement}: invalid operator(s) for operands of type {symbol_table[name]["type"]}")
            return False
        return True

    with open('case.txt', 'r') as source_code:
        for line in source_code:
            line = line.strip(";\n")
            print(line, end= "$\n")
            lineWithEqualsRemoved = line.split("=")
            if hadEqualSign(lineWithEqualsRemoved):
                lhs = lineWithEqualsRemoved[0]
                rhs = lineWithEqualsRemoved[1]
                lhs = lhs.split()
                if areInitializing(lhs):
                    possibleType = lhs[0]
                    possibleName = lhs[1]
                    if isInSymbolTable(possibleName):
                        print(f"Error! {possibleName} is already initialized. Use a different name!")
                    if possibleType not in types:
                        print(f"Error! {possibleType} is not a valid type. Please use valid typing!")
                    varType = possibleType
                    name = possibleName
                    symbol_table[name] = {}
                    symbol_table[name]["type"] = varType
                    symbol_table[name]["hasValue"] = False
                    if not hasValidRhs(rhs, name, line):
                        break
                    symbol_table[name]["hasValue"] = True


                else:
                    #we are assigning
                    name = lhs[0]
                    if not isInSymbolTable(name):
                        print(f"Error! {name} has not been initialized yet. Please initialize!")
                    if not hasValidRhs(rhs, name, line):
                        break
                    symbol_table[name]["hasValue"] = True

            #it did not contain an equals sign
            else:
                line = line.split()
                if hasMoreThanOneToken(line):
                    if firstTokenIsTypeKeyword(line[0]):
                        # we are declaring
                        varType = line[0]
                        name = line[1]
                        if name.endswith("()"):
                            name = name.strip("()")
                            if isInSymbolTable(name):
                                print(f"Error! {name} is already initialized. Use a different name!")
                                break
                            symbol_table[name] = {}
                            symbol_table[name]["type"] = varType
                            symbol_table[name]["hasValue"] = False
                            stack.append(name)
                        else:
                            if isInSymbolTable(name):
                                print(f"Error! {name} is already initialized. Use a different name!")
                                break
                            symbol_table[name] = {}
                            symbol_table[name]["type"] = varType
                            symbol_table[name]["hasValue"] = False
                    #check if the first token is a return keyword
                    elif isReturnStatement(line[0]):
                        if not stack:
                            print("Error! You can't use return statements here")
                            break
                        name = stack[-1]
                        value = line[1]
                        if not isValid(symbol_table[name]["type"], value):
                            print(f"Error! {line}: invalid operand. Expected operand of type {symbol_table[name]["type"]}")
                            break
                        symbol_table[name]["hasValue"] = True










    return 0
    #     #line = file.readline()
    #     word = read_word(file, skip_whitespace(file))
    #     while word != '\n':
    #         # Skip whitespace to find the start of a line
    #         char = skip_whitespace(file)

    #         if not char:
    #             break

    #         # Check if line starts with a type (keyword)
    #         if char.isalpha():
    #             word, next_char = read_word(file, char)

    #             if word in types:
    #                 var_type = word
            
    #                 # Skip whitespace after type
    #                 while next_char in [' ', '\t']:
    #                     next_char = file.read(1)

    #                 # Read variable name
    #                 if not (next_char.isalpha() or next_char == '_'):
    #                     print("Invalid variable name start.")
    #                     continue
    #                 var_name, next_char = read_word(file, next_char)
    #                 if(var_name[-2:].strip() == "()"):
    #                     print(f"'{var_name}' is a function")
    #                 #Assignment
    #                 else:
    #                       # Skip whitespace before =
    #                     while next_char in [' ', '\t']:
    #                         next_char = file.read(1)

    #                     if next_char != '=':
    #                         print(f"Expected '=' after variable name '{var_name}'")
    #                         continue
    #                     # Skip whitespace after =
    #                     next_char = skip_whitespace(file)

    #                     # Read value
    #                     value = read_value(file, next_char)
    #                     # Validate
    #                     if is_valid_value(var_type, value):
    #                         symbol_table[var_name] = var_type
    #                         print(f"Valid: {var_type} {var_name} = {value}")
    #                     else:
    #                         print(f"Invalid assignment: {var_type} {var_name} = {value}")
                    
    #             else:
    #                 # Not a type declaration — skip rest of line (usage, etc.)
    #                 file.readline()
    #                 continue
    #         else:
    #             # Skip non-type lines
    #             file.readline()

    # print("\nCollected Variables:")
    # for var in symbol_table:
    #     print(var)


if __name__ == "__main__":
    main()