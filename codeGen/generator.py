FILE = "tac1.txt"
keywords = ['goto', 'return', 'if', 'then']
regs = {
    "$s0": {"isFree": True, "val": []},
    "$s1": {"isFree": True, "val": []},
    "$s2": {"isFree": True, "val": []},
    "$s3": {"isFree": True, "val": []},
    "$s4": {"isFree": True, "val": []},
    "$s5": {"isFree": True, "val": []},
    "$s6": {"isFree": True, "val": []},
}
tempRegs = {
    "$t0": {"isFree": True, "val": []},
    "$t1": {"isFree": True, "val": []},
    "$t2": {"isFree": True, "val": []},
    "$t3": {"isFree": True, "val": []},
    "$t4": {"isFree": True, "val": []},
    "$t5": {"isFree": True, "val": []},
    "$t6": {"isFree": True, "val": []},
}

def prettyPrintRegs():
    for reg, contents in regs.items():
        print(f"{reg} : {contents}")
    for reg, contents in tempRegs.items():
        print(f"{reg} : {contents}")

def scanForArray(word):
    word = word.split("[")
    if len(word) == 1:
        return (word[0], None)
    else:
        return (word[0], word[1][:-1])



def findLastUsed():
    lastUsed = {}
    with open(FILE, 'r') as tac:
        for line in tac:
            number, code = line.split(None, 1)
            lineNumber = int(number[1:-1])
            for word in code.split():
                if word[0].isalpha() and word not in keywords:
                    word1, word2 = scanForArray(word)
                    lastUsed[word1] = lineNumber
                    if word2:
                        lastUsed[word2] = lineNumber
    # print(lastUsed)
    return lastUsed

lastUsed = findLastUsed()



def freeReg(varName):
    for reg, contents in regs.items():
        if varName in contents["val"]:
            if len(contents["val"]) == 1:
                contents["isFree"] = True
            contents["val"].remove(varName)
    for reg, contents in tempRegs.items():
        if varName in contents["val"]:
            if len(contents["val"]) == 1:
                contents["isFree"] = True
            contents["val"].remove(varName)

def updateRegs(regToUpdate, varName):
    for reg, contents in regs.items():
        if reg == regToUpdate and varName not in contents["val"]:
            contents["val"].append(varName)
            contents["isFree"] = False
    for reg, contents in tempRegs.items():
        if reg == regToUpdate and varName not in contents["val"]:
            contents["val"].append(varName)
            contents["isFree"] = False
        
def contentsAreStale(contents, lineNumber):
    if len(contents) > 1:
        return False
    return lineNumber > lastUsed[contents[0]]

def loadArray(varName):
    for reg, contents in regs.items():
        if contents["isFree"]:
            print(f"\tLW {reg}, {varName}")
            contents["val"] = []
            contents["val"].append(varName)
            contents["isFree"] = False
            return



def getReg(varName, lineNumber, type="norm"):
    registerTable = regs if type == "norm" else tempRegs
    freeRegs = []
    occupiedRegister = ""
    for reg, contents in  registerTable.items():
        if varName in contents["val"]:
            occupiedRegister = reg
            if len(contents["val"]) == 1 and lineNumber >= lastUsed[varName]:
                contents["val"] = []
                contents["isFree"] = True
                return reg
        elif contents["isFree"]:
            freeRegs.append(reg)
    if len(freeRegs) > 0:
        if occupiedRegister == "":
            if isIntermediate(varName):
                print(f"\tLI {freeRegs[0]}, {varName}")
            else:
                print(f"\tLW {freeRegs[0]}, {varName}")
        else:
            print(f"\tMOVE {freeRegs[0]}, {occupiedRegister}")
        return freeRegs[0]
    else:
        #Look for stale reg:
        if type == "norm":
            for reg, contents in regs.items():
                if contentsAreStale(contents["val"], lineNumber):
                    contents["val"] = []
                    return reg
        else:
            for reg, contents in tempRegs.items():
                if contentsAreStale(contents["val"], lineNumber):
                    contents["val"] = []
                    return reg
    
    print("--------------------------NO REGS AVAILABLE---------------------------")
    return None
    
def getAssignmentReg(varName, type="norm"):
    registerTable = regs if type == "norm" else tempRegs
    freeRegs = []
    for reg, contents in  registerTable.items():
        if varName in contents["val"]:
            return reg
        elif contents["isFree"]:
            freeRegs.append(reg)
    if len(freeRegs) > 0:
        if isIntermediate(varName):
            print(f"\tLI {freeRegs[0]}, {varName}")
        else:
            print(f"\tLW {freeRegs[0]}, {varName}")
        return freeRegs[0]
    print("--------------------------NO REGS AVAILABLE---------------------------")
    # return None

def getArrayReg(varName):
    occupiedReg = ""
    for reg, contents in regs.items():
        if varName in contents["val"]:
            occupiedReg = reg
            break
    for reg, contents in tempRegs.items():
        if contents["isFree"]:
            print(f"\tMOVE {reg}, {occupiedReg}")
            return reg
            



def findCheckpoints():
    jumpCheckpointsStrings = []
    with open(FILE, 'r') as tac:
        for line in tac:
            i = 0
            for word in line.split():
                if word.startswith("(") and i != 0:
                    jumpCheckpointsStrings.append(word[1:-1])
                i += 1
    jumpCheckpoints = [int(x) for x in jumpCheckpointsStrings]
    # print(jumpCheckpoints)    
    return jumpCheckpoints

def parseBranch(tac):
    tac = tac.rstrip()
    tac = tac.split(None, 1)[1]
    tac = tac.split(" then goto ")
    # print(tac)
    return ("BRANCH", tac[0], tac[1][1:-1], None)

def getOp(operator):
    match operator:
        case "*":
            op = "MULT"
        case "+":
            op = "ADD"
        case "-":
            op = "SUB"
        case _:
            op = "DEFAULT"
    return op

def turnIntoQuad(tac):
    tacSplit = tac.split()
    firstToken = tacSplit[0]
    if firstToken == "if":
        return parseBranch(tac)
    elif firstToken == "goto":
        return ("JUMP", tacSplit[1][1:-1], None, None)
    elif firstToken == "return":
        return ("RETURN", None, None, None)
    else:
        tac = tac.split(" = ")
        lhs = tac[0]
        rhs = tac[1]
        if len(lhs.split("[")) > 1:
            lhs = lhs.split("[")
            return ("ARRAYASSIGN", lhs[1][:-1], rhs, lhs[0])
        else:
            if len(rhs.split()) > 1:
                rhs = rhs.split()
                return (getOp(rhs[1]),rhs[0], rhs[2], lhs)
            else:
                if len(rhs.split("[")) > 1:
                    rhs = rhs.split("[")
                    return ("ASSIGNELEMENT", rhs[0], rhs[1][:-1], lhs)
                else:
                    return("ASSIGN", rhs, None, lhs)
                
def isIntermediate(src):
    return src[0].isdigit()

def inReg(varName):
    for reg, contents in regs.items():
        if varName in contents["val"]:
            return True
    return False


def emitOperation(quad, targetReg, lineNumber):
    c = quad[2]
    match quad[0]:
        case "ADD":
            print(f"\t{"ADDI" if isIntermediate(c) else "ADD"}, {targetReg}, {targetReg}, {c if isIntermediate(c) else getReg(c, lineNumber, "temp" if c[0].lower() == "t" else "norm")}")
        case "MULT":
            print(f"\t{"MULTI" if isIntermediate(c) else "MULT"}, {targetReg}, {targetReg}, {c if isIntermediate(c) else getReg(c, lineNumber, "temp" if c[0].lower() == "t" else "norm")}")
        case "SUB":
            print(f"\t{"SUBI" if isIntermediate(c) else "SUB"}, {targetReg}, {targetReg}, {c if isIntermediate(c) else getReg(c, lineNumber, "temp" if c[0].lower() == "t" else "norm")}")

def getRelation(rel):
    match rel:
        case "=":
            return "BEQ"
        case ">":
            return "BGT"
        case "<":
            return "BLT"
        case ">=":
            return "BGE"
        case "<=":
            return "BLE"
        case "!=":
            return "BNE"

def main():
    #used to add labels
    jumpCheckpoints = findCheckpoints()
    # print(lastUsed)

    # updateRegs(lineNumber, lastUsed)
    with open(FILE, 'r') as tacFile:
        for line in tacFile:
            line = line.rstrip()
            lineNumber, code = line.split(None, 1)
            lineNumber = int(lineNumber[1:-1])
            # print(lineNumber)
            if lineNumber in jumpCheckpoints:
                print(f"L{lineNumber}:")
            quad = turnIntoQuad(code)
            op = quad[0]
            b = quad[1]
            c = quad[2]
            a = quad[3]

            if op == "ASSIGN":
                regB = getAssignmentReg(b, "temp" if a[0].lower() == "t" else "norm")
                freeReg(a)
                updateRegs(regB, a)
                if not isIntermediate(b):
                    updateRegs(regB, b)
                # prettyPrintRegs()
                continue

            elif op == "ASSIGNELEMENT":
                if not inReg(b):
                    loadArray(b)
                regB = getAssignmentReg(b, "temp" if a[0].lower() == "t" else "norm")
                print(f"\t{"ADDI" if isIntermediate(c) else "ADD"}, {regB}, {regB}, {c if isIntermediate(c) else getReg(c, lineNumber, "temp" if c[0].lower() == "t" else "norm")}")
                
                freeReg(a)
                if not isIntermediate(c) and lineNumber >= lastUsed[c]:
                    freeReg(c)
                updateRegs(regB, a)
                # prettyPrintRegs()
                continue

            elif op == "ARRAYASSIGN":
                # print(quad)
                if not inReg(a):
                    loadArray(a)
                regA = getArrayReg(a)
                print(f"\t{"ADDI" if isIntermediate(b) else "ADD"}, {regA}, {regA}, {b if isIntermediate(b) else getReg(b, lineNumber, "temp" if b[0].lower() == "t" else "norm")}")

                print(f"\tSW {regA}, ({a}[{b}])")
                continue

            elif op == "JUMP":
                # print(quad)
                print(f"\tJAL L{b}")
                continue

            elif op == "RETURN":
                for reg, content in regs.items():
                    for varName in content["val"]:
                        print(f"\tSW {reg}, ({varName})")
                continue
            
            elif op == "BRANCH":
                # print(quad)
                goto = quad[2]
                quadOne = quad[1].split()
                left = quadOne[0]
                relation = quadOne[1]
                right = quadOne[2]
                relation = getRelation(relation)

                print(f"\t{relation} {left}, {right}, L{goto}")
                continue

            regB = getReg(b, lineNumber, "temp" if a[0].lower() == "t" else "norm")
            emitOperation(quad ,regB, lineNumber)
            freeReg(a)
            if not isIntermediate(c) and lineNumber >= lastUsed[c]:
                freeReg(c)
            updateRegs(regB, a)
            # prettyPrintRegs()

if __name__ == "__main__":
    main()