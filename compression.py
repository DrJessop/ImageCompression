def predictiveEncrypt(img, channels):
    preprocess = []
    if channels > 1: 
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                for c in range(img.shape[2]):
                    if x == 0: 
                        preprocess.append(int(img[y, x, c]))
                    else: 
                        preprocess.append(int(img[y, x, c]) - int(img[y, x - 1, c]) + 255)
    
    else: 
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                if x == 0: 
                    preprocess.append(img[int(y), int(x)])
                else: 
                    preprocess.append(int(img[y, x]) - int(img[y, x - 1]) + 255)
    return preprocess

def predictiveDecrypt(array, channels, xdim, ydim):
    original = []
    if channels > 1:
        for y in range(ydim):
            row = []
            for x in range(xdim): 
                channel = []
                for c in range(channels):
                    indx = y * xdim * channels + x * channels + c
                    if x == 0: 
                        channel.append(array[indx])
                    else:
                        channel.append(row[-1][c] + array[indx] - 255)
                row.append(channel)
            original.append(row)
    else: 
        for y in range(ydim):
            row = []
            for x in range(xdim):
                indx = y * xdim + x
                if x == 0: 
                    row.append(array[indx])
                else: 
                    row.append(row[-1] + array[indx] - 255)
            original.append(row)
    return original

def splitHexIntoBytes(x):
    assert x < 65536
    x = hex(x)
    if len(x) <= 4:
        return (int('0x00', 16), int(x, 16))
    elif len(x) == 5:
        return (int(x[:3], 16), int('0x'+x[3:5], 16))
    return (int(x[:4], 16), int('0x'+x[4:6], 16))

# Compress an image
def LZWEncryption(flattenedArray):
    lzwDict = {str(i):i for i in range(511)}
    maxCode = 510
    code = bytearray()
    currArray = []
    for i in range(len(flattenedArray)):
        if len(lzwDict) > 65535:
            lzwDict = {str(j):j for j in range(511)}
            maxCode = 510
        currArray.append(str(flattenedArray[i]))
        currString = ','.join(currArray)
        if currString not in lzwDict:
            maxCode += 1
            lzwDict[currString] = maxCode
            data4Bytes = lzwDict[','.join(currArray[:-1])]
            data2BytesA, data2BytesB = splitHexIntoBytes(data4Bytes)
            code.append(data2BytesA)
            code.append(data2BytesB)
            currArray = [str(flattenedArray[i])]
    data2BytesA, data2BytesB = splitHexIntoBytes(lzwDict[','.join(currArray)])
    code.append(data2BytesA)
    code.append(data2BytesB)
    return code

def getFirst(string):
    endPosition = 0
    while endPosition != len(string) and string[endPosition] != ',':
        endPosition += 1
    if endPosition == len(string):
        return string
    else:
        return string[:endPosition]

def LZWDecryption(encryptedCode):
    decodingDict = {i:str(i) for i in range(511)}
    maxKey = 510
    key = (encryptedCode[0] << 8) + encryptedCode[1]
    decryptedCode = [int(decodingDict[key])]
    currentString = ''
    previous = getFirst(decodingDict[key])
    stringToInt = lambda x: int(x)
    for i in range(2, len(encryptedCode), 2):
        if len(decodingDict) > 65535:
            decodingDict = {j:str(j) for j in range(511)}
            maxKey = 510
        key = (encryptedCode[i] << 8) + encryptedCode[i + 1]
        if key not in decodingDict:
            decryptedCode.extend(list(map(stringToInt, previous.split(','))))
            decryptedCode.append(int(getFirst(previous)))
            previous = previous + ',' + getFirst(previous)
            maxKey += 1
            decodingDict[maxKey] = previous
        else:
            currentString = decodingDict[key]
            decryptedCode.extend(list(map(stringToInt, currentString.split(','))))
            maxKey += 1
            decodingDict[maxKey] = previous + ',' + getFirst(currentString)
            previous = currentString
    return decryptedCode
