class TreeNode:
    def __init__(self, val="", children=None):
        self.val = val
        self.children = children if children is not None else []

def printTree(parseTree, prefix="", isLast=True):
    if parseTree.val == "i":
        parseTree.val = "id"
    branch = "└── " if isLast else "├── "
    print(prefix + branch + parseTree.val)

    new_prefix = prefix + ("    " if isLast else "│   ")
    branchCount = len(parseTree.children)

    for i, child in enumerate(parseTree.children):
        isLastChild = (i == branchCount - 1)
        printTree(child, new_prefix, isLastChild)




def main():
    productions = {
        "1": {"lhs":"E","rhs":"E+T"},
        "2": {"lhs":"E","rhs":"E-T"},
        "3": {"lhs":"E","rhs":"T"},
        "4": {"lhs":"T","rhs":"T*F"},
        "5": {"lhs":"T","rhs":"T/F"},
        "6": {"lhs":"T","rhs":"F"},
        "7": {"lhs":"F","rhs":"(E)"},
        "8": {"lhs":"F","rhs":"i"},
    }

    table = {
        "0": {"i":"S5","(":"S4","E":"1","T":"2","F":"3"},
        "1": {"+":"S6","-":"S7","$":"ACC"},
        "2": {"+":"R3","-":"R3","*":"S8","/":"S9",")":"R3","$":"R3"},
        "3": {"+":"R6","-":"R6","*":"R6","/":"R6",")":"R6","$":"R6"},
        "4": {"i":"S5","(":"S4","E":"10","T":"2","F":"3"},
        "5": {"+":"R8","-":"R8","*":"R8","/":"R8",")":"R8","$":"R8"},
        "6": {"i":"S5","(":"S4","T":"11","F":"3"},
        "7": {"i":"S5","(":"S4","T":"12","F":"3"},
        "8": {"i":"S5","(":"S4","F":"13"},
        "9": {"i":"S5","(":"S4","F":"14"},
        "10": {"+":"S6","-":"S7",")":"S15"},
        "11": {"+":"R1","-":"R1","*":"S8","/":"S9",")":"R1","$":"R1"},
        "12": {"+":"R2","-":"R2","*":"S8","/":"S9",")":"R2","$":"R2"},
        "13": {"+":"R4","-":"R4","*":"R4","/":"R4",")":"R4","$":"R4"},
        "14": {"+":"R5","-":"R5","*":"R5","/":"R5",")":"R5","$":"R5"},
        "15": {"+":"R7","-":"R7","*":"R7","/":"R7",")":"R7","$":"R7"},
    }

    errorTable = {
        "5":{"i":"Missing operator"},
        "1":{"E":"Missing left parentheses"},
        "6":{"+":"Missing operand"},
        "4":{"(":"Missing expression"},
        "10": {"E":"Missing right parentheses"}
    }
    
    symbolList = ("i", "+", "-", "*", "/", "(", ")", "$", "E", "T", "F")

    foundError = False

    with open("case.txt", "r") as textFile:
        case = textFile.readline().strip() + '$'
        while case != "$":
            print("\n" + case)
            stack = []
            stack.append(TreeNode("0"))
            i = 0
            while i < len(case):
                symbol = case[i]
                #skip whitespace
                if symbol in (' ', '\t'):
                    i += 1
                    continue
                #handle id tokens
                #look up action/goto command in table
                if(symbol in table[stack[-1].val]):
                    action = table[stack[-1].val][symbol]
                else:
                    errorCodeState = stack[-1].val
                    if errorCodeState == "0":
                        print("Cannot start with an operator. Please start with an operand or a left parentheses.")
                        break
                    errorCodeSymbol = stack[-2].val
                    if errorCodeState in errorTable and errorCodeSymbol in errorTable[errorCodeState]:
                        print(errorTable[errorCodeState][errorCodeSymbol])
                    else:
                        print("Error Not Found")
                    foundError = True
                    break
                #It is an action
                if action == "ACC":
                    break
                if action[0] in ("S", "R"):
                    #We must shift
                    if action[0] == "S":
                        stack.append(TreeNode(symbol))
                        stack.append(TreeNode(action[1:]))
                        i += 2 if symbol == "i" else 1
                    #We must reduce
                    elif action[0] == "R":
                        if action[1:] in productions:
                            prod = productions[action[1:]]
                            newTree = TreeNode(prod["lhs"])
                            while(stack[-1].val != prod["rhs"][0]):
                                element = stack.pop()
                                if element.val in symbolList:
                                    newTree.children.append(element)
                            newTree.children.append(stack.pop())
                            goto = table[stack[-1].val][prod["lhs"]]
                            stack.append(newTree)
                            #I am praying that this will never has an S or an R. If it does, an error occurred
                            stack.append(TreeNode(goto))    
                #It is a goto without reduction
                else:
                    print("BIG ERROR, table was initialized wrong somehow!!!")
                    break
            if stack[-1].val == "0":
                print("No tree to print")
            else:
                if not foundError:
                    print("About to print tree")
                    stack.pop()
                    printTree(stack.pop())
            case = textFile.readline().strip() + '$'
    return
if __name__ == "__main__":
    main()