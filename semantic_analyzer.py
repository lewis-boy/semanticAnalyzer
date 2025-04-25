def main():
    types = ['int', 'float', 'bool']
    symbol_table  = {}
    operators = ['+', '-', '*', '/', '&&', '||']

    def isValid(type, value):
        if type == 'int':
            return value.lstrip('-').isdigit()
        elif type == 'float':
            parts = value.lstrip('-').split('.')
            return len(parts) == 2 and all(part.isdigit() for part in parts)
        elif type == 'bool':
            return value in ['true', 'false']
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

    with open('case.txt', 'r') as source_code:
        for line in source_code:
            #line contains \n as well
            print(line, end= "$")
            processedLine = line.split("=")
            #line is either a declaration:
            #int x = 1
            #or an assignment:
            #x = 1
            if(len(processedLine) > 1):
                lhs = processedLine[0]
                rhs = processedLine[1]
                #we don't really care about the rhs for now
                processedLhs = lhs.split(" ")
                #This is a declaration
                if(len(processedLhs) > 1):
                    possibleType = processedLhs[0]
                    if(possibleType in types):
                        #we are going to assume there is only one variable name
                        #and not many seperated by commas like x,y,z
                        symbol_table[processedLhs[1]] = possibleType
                    else:
                        print(f"We reached a strange error: {processedLine}")
                #This is an assignment
                else:
                    variableName = processedLhs[0]
                    # we care about the rhs now. CHECK FOR MIX MODE 
                    #Start off easy, only worry about ints and floats and bools
                    operandsAndOperators = rhs.split("")
                    operands = getOperands(operandsAndOperators)
                    operators = getOperators(operandsAndOperators)
                    if not isValidOperand(operands, symbol_table[variableName]):
                        print(f"{line}: invalid operands. Expected operands of type {symbol_table[variableName]}")
                        break
                    if not isValidOperator(operators, symbol_table[variableName]):
                        print(f"{line}: invalid operator(s) for operands of type {symbol_table[variableName]}")
                        break
                    #We should assign value now
                    #Mix Mode DONE

                    

            #line is either an initialization:
            #int x / int main()
            #or something other statement:
            #return 0 / print() / ect
            else:
                #do something else

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