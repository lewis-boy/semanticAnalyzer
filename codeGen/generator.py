FILE = "tac1.txt"
keywords = ['goto', 'return', 'if', 'then']
regs = {
    "$s0": {"isFree": False, "val": ""},
    "$s1": {"isFree": False, "val": ""},
    "$s2": {"isFree": False, "val": ""},
    "$s3": {"isFree": False, "val": ""},
    "$s4": {"isFree": False, "val": ""},
    "$s5": {"isFree": False, "val": ""},
    "$s6": {"isFree": False, "val": ""},
}
tempRegs = {
    "$t0": {"isFree": False, "val": ""},
    "$t1": {"isFree": False, "val": ""},
    "$t2": {"isFree": False, "val": ""},
    "$t3": {"isFree": False, "val": ""},
    "$t4": {"isFree": False, "val": ""},
    "$t5": {"isFree": False, "val": ""},
    "$t6": {"isFree": False, "val": ""},
}

def isInReg(A):
    for reg, contents in regs:
        if contents["val"] == A:
            return True
    for reg, contents in tempRegs: 
        if contents["val"] == A:
            return True
    return False

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
            lineNumber = number[1:-1]
            for word in code.split():
                if word[0].isalpha() and word not in keywords:
                    word1, word2 = scanForArray(word)
                    lastUsed[word1] = lineNumber
                    if word2:
                        lastUsed[word2] = lineNumber
    # print(lastUsed)
    return lastUsed

def updateRegs(lineNumber, lastUsed):
    for reg, contents in regs:
        varName = contents["val"]
        if varName == "":
            continue
        if lastUsed[varName] < lineNumber:
            regs[reg]["isFree"] = True
    for reg, contents in tempRegs:
        varName = contents["val"]
        if varName == "":
            continue
        if lastUsed[varName] < lineNumber:
            tempRegs[reg]["isFree"] = True

def getReg(varName, type="norm"):
    freeRegs = []
    for reg,contents in regs:
        if contents["val"] == varName:
            return reg
        if contents["isFree"]:
            freeRegs.append(reg)
    if len(freeRegs) > 0:
        print(f"LW {freeRegs[0]}, {varName}")
        return freeRegs[0]
    print("--------------------------NO REGS AVAILABLE---------------------------")
    return None
def getTempReg(varName):
    freeRegs = []
    for reg,contents in tempRegs:
        if contents["val"] == varName:
            return reg
        if contents["isFree"]:
            freeRegs.append(reg)
    if len(freeRegs) > 0:
        return freeRegs[0]
    print("--------------------------NO TEMP REGS AVAILABLE---------------------------")
    return None


def findCheckpoints():
    jumpCheckpointsStrings = []
    with open(FILE, 'r') as tac:
        for line in tac:
            i = 0
            for word in line.split():
                if word.startswith("(") and i != 0:
                    jumpCheckpointsStrings.append(word[1:-1])
                i += 1
    # jumpCheckpoints = [int(x) for x in jumpCheckpointsStrings]
    # print(jumpCheckpoints)    
    return jumpCheckpointsStrings

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



def main():
    #used to add labels
    jumpCheckpoints = findCheckpoints()

    #used to know whether C dies on this line or not
    lastUsed = findLastUsed()

    
    # updateRegs(lineNumber, lastUsed)
    with open(FILE, 'r') as tacFile:
        for line in tacFile:
            line = line.rstrip()
            lineNumber, code = line.split(None, 1)
            # print(lineNumber[1:-1])
            if lineNumber[1:-1] in jumpCheckpoints:
                print(f"L{lineNumber[1:-1]}:")
            quad = turnIntoQuad(code)
            if quad[0] in ["BRANCH", "JUMP", "RETURN"]:
                continue
            op = quad[0]
            b = quad[1]
            c = quad[2]
            a = quad[3]
            reg = ""
            if isInReg(a):
                reg = getReg(a)
                #emit MOVE b
            else:
                reg = getReg(b, "temp" if a[0].lower() == "t" else "norm")
                


            



if __name__ == "__main__":
    main()