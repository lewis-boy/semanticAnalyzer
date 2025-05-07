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
    print(lastUsed)
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

def getReg(varName):
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
    jumpCheckpoints = [int(x) for x in jumpCheckpointsStrings]
    print(jumpCheckpoints)    
    return jumpCheckpoints


def main():
    jumpCheckpoints = findCheckpoints()
    lastUsed = findLastUsed()
    updateRegs(lineNumber, lastUsed)
    # with open(FILE, 'r') as tacFile:
    #     for line in tacFile:
    #         lineNumber, code = line.split(None, 1)
    #         # print(lineNumber, end=" ")
    #         # print(code)



if __name__ == "__main__":
    main()