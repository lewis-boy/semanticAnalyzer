
def main():
    types = ['int', 'float', 'bool']
    symbol_table  = {}
    stack = []
    operators = ['+', '-', '*', '/', '&&', '||']
    foundError = False
    lineNumber = 0


    # TODO turn the right side of the OR statement into its own function with proper error message.

    # def scanSymbolTable(type, value):
    #     if value not in symbol_table:
    #         print(f"{value} has not been initialized")
    #         return False
    #     if not symbol_table[value]["hasValue"]:
    #         print(f"{value} has only been initialized but does not have an initial value")
    #         return False
    #     if symbol_table[value]["type"] != type:
    #         print(f"{value} should be of type -> {type}")
    #         return False
    #     return True

    def isValid(type, value):
        if type == 'int':
            result = value.lstrip('-').isdigit() or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'int')
        elif type == 'float':
            parts = value.lstrip('-').split('.')
            result = (len(parts) == 2 and all(part.isdigit() for part in parts)) or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'float')
        elif type == 'bool':
            result = value in ['true', 'false'] or (value in symbol_table and symbol_table[value]["hasValue"] and symbol_table[value]["type"] == 'bool')
        if not result:
            print(f"This operand -> {value} does not match the intended {type} type.")
        return result

    # def isValid(type, value):
    #     if type == 'int':
    #         return value.lstrip('-').isdigit() or scanSymbolTable(type, value)
    #     elif type == 'float':
    #         parts = value.lstrip('-').split('.')
    #         return (len(parts) == 2 and all(part.isdigit() for part in parts)) or scanSymbolTable(type, value)
    #     elif type == 'bool':
    #         return value in ['true', 'false'] or scanSymbolTable(type, value)
    #     return False

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
            print(f"Error on line {lineNumber}! {statement}: invalid operands. Please check that your operands {operands} are of type {symbol_table[name]["type"]}\nIf operands are variables, check if they have been correctly initialized.")
            return False
        if not isValidOperator(operators, symbol_table[name]["type"]):
            print(f"Error on line {lineNumber}! {statement}: invalid operator(s) for operands of type {symbol_table[name]["type"]}")
            return False
        return True

    with open('case.txt', 'r') as source_code:

        for line in source_code:
            lineNumber += 1
            line = line.strip(";\n")
            # print(line, end= "$\n")
            lineWithEqualsRemoved = line.split("=")
            if hadEqualSign(lineWithEqualsRemoved):
                lhs = lineWithEqualsRemoved[0]
                rhs = lineWithEqualsRemoved[1]
                lhs = lhs.split()
                if areInitializing(lhs):
                    possibleType = lhs[0]
                    possibleName = lhs[1]
                    if isInSymbolTable(possibleName):
                        foundError = True
                        print(f"Error on line {lineNumber}! {possibleName} is already initialized. Use a different name!")
                        break
                    if possibleType not in types:
                        foundError = True
                        print(f"Error on line {lineNumber}! {possibleType} is not a valid type. Please use valid typing!")
                        break
                    varType = possibleType
                    name = possibleName
                    symbol_table[name] = {}
                    symbol_table[name]["type"] = varType
                    symbol_table[name]["hasValue"] = False
                    if not hasValidRhs(rhs, name, line):
                        foundError = True
                        break
                    symbol_table[name]["hasValue"] = True


                else:
                    #we are assigning
                    name = lhs[0]
                    if not isInSymbolTable(name):
                        foundError = True
                        print(f"Error on line {lineNumber}! {name} has not been initialized yet. Please initialize!")
                        break
                    if not hasValidRhs(rhs, name, line):
                        foundError = True
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
                                foundError = True
                                print(f"Error on line {lineNumber}! {name} is already initialized. Use a different name!")
                                break
                            symbol_table[name] = {}
                            symbol_table[name]["type"] = varType
                            symbol_table[name]["hasValue"] = False
                            stack.append(name)
                        else:
                            if isInSymbolTable(name):
                                foundError = True
                                print(f"Error on line {lineNumber}! {name} is already initialized. Use a different name!")
                                break
                            symbol_table[name] = {}
                            symbol_table[name]["type"] = varType
                            symbol_table[name]["hasValue"] = False
                    #check if the first token is a return keyword
                    elif isReturnStatement(line[0]):
                        if not stack:
                            foundError = True
                            print(f"Error on line {lineNumber}! You can't use return statements here")
                            break
                        name = stack[-1]
                        value = line[1]
                        if not isValid(symbol_table[name]["type"], value):
                            foundError = True
                            print(f"Error on line {lineNumber}! ({line[1]}) Invalid return value. Expected return type of {symbol_table[name]["type"]}")
                            break
                        symbol_table[name]["hasValue"] = True
    if not foundError:
        print("No semantic errors found. Code is semantically correct! Congratulations!")
    
    return True

if __name__ == "__main__":
    main()