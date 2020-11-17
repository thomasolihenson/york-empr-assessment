from PIL import Image
import numpy as np

### Importing from Files ###

def getQrFromFile(_fileQrName):
    """ This function for loading a perfect QR code from an image. I.e. an image exactly 21 x 21. The rounding for brightness causes errors. """
    _imQrArray = np.array(Image.open(r"qrCodes\\" + str(_fileQrName) + ".png").convert("L"))
    return cleanResizeImage(_imQrArray)

def cleanResizeImage(_imQrArray):
    """ Takes a numpy array from an imported image, then resizes the image to 21x21 and cleans up the pixels so that they are only either 255 or 0. """
    _imQrArray = Image.fromarray(_imQrArray)
    _imQrArray = _imQrArray.resize(size = (21,21),resample = Image.NEAREST)
    _imQrArray = np.array(_imQrArray)
    _imQrAvgBrightness = np.mean(_imQrArray)
    _imQrSize = isQrSquare(_imQrArray)
    for _row in range(_imQrSize):
        for _column in range(_imQrSize):
            if _imQrArray[_row][_column] > (_imQrAvgBrightness*1.2):
                _imQrArray[_row][_column] = 255
            else:
                _imQrArray[_row][_column] = 0
    return _imQrArray

### Frequently Called ###

def toBinQrArray(_imQrArray):
    """ Takes an array of white and black values of 255 and 0, then changes the black values to a logic 1 and white to a logic 0. """
    _imQrSize = isQrSquare(_imQrArray)
    for _row in range(_imQrSize):
        for _column in range(_imQrSize):
            if (_imQrArray[_row][_column] == 0):
                _imQrArray[_row][_column] = 1
            else:
                _imQrArray[_row][_column] = 0
    return _imQrArray

def toImQrArray(_binQrArray):
    """ Takes a binary array of white and black values of 0 and 1, then changes the black values to 0 and white to 255. """
    _binQrSize = isQrSquare(_binQrArray)
    for _row in range(_binQrSize):
        for _column in range(_binQrSize):
            if (_binQrArray[_row][_column] == 0):
                _binQrArray[_row][_column] = 255
            else:
                _binQrArray[_row][_column] = 0
    return _binQrArray

def isQrSquare(_anyQrArray):
    """ Takes a given array, either an image or binary, and returns it's dimensions if it is square, otherwise it returns False. """
    if (_anyQrArray.shape[0] == _anyQrArray.shape[1]):
        return _anyQrArray.shape[0]
    else:
        return False

def isImQrArray(_anyQrArray):
    """ Checks whether a given array is an image array or a binary array. """
    if (_anyQrArray[0][0] == 1):
        return False
    else:
        return True

def showQrCode(_anyQrArray):
    """ Takes a QR image array and displays it """
    if (isImQrArray(_anyQrArray) == True):
        _imQrArray = _anyQrArray
        _printQrImage = Image.fromarray(_imQrArray)
        _printQrImage.show()
    else:
        _imQrArray = toImQrArray(_anyQrArray)
        _printQrImage = Image.fromarray(_imQrArray)
        _printQrImage.show()

## Other Functions ###

def getQrData(_binQrArray):
    """ Main function for decoding QR code, containing sub functions required to decode the QR code. """
    _binQrSize = isQrSquare(_binQrArray)

    def getApplyQrMask(_binQrArray):
        """ Reads the bits for the bitmask, loads the bitmask from a file, then applies the bitmask to the given binary, and returns a QR array with the data in its raw form. """
        _bitMaskQr = ""
        for _column in range(2,5):
            _bitMaskQr += str(_binQrArray[8][_column])
        _bitMaskQrArray = np.array(Image.open(r"qrMasks\\qrMask"+_bitMaskQr+".png").convert("L"))
        for _row in range(_binQrSize):
            for _column in range(_binQrSize):
                if (_binQrArray[_row][_column] ^ (_bitMaskQrArray[_row][_column] == 255)):
                    _binQrArray[_row][_column] = 0
                else:
                    _binQrArray[_row][_column] = 1
        return _binQrArray

    def getQrData(_binMaskedQrArray):
        """ Iterates through the array of QR code data and adds it all to a binary string. """
        _binQrDataArray = []
        _loopDataArray = [[20,8,-1,20,18,-1],[9,21,1,18,16,-1],[20,8,-1,16,14,-1],[9,21,1,14,12,-1],[20,6,-1,12,10,-1],[5,-1,-1,12,10,-1],[0,6,1,10,8,-1],[7,21,1,10,8,-1],
                          [12,8,-1,8,6,-1],[9,13,1,5,3,-1],[12,8,1,3,1,-1],[9,13,1,1,-1,-1]]
        for _loopDataItem in _loopDataArray:
            for _row in range(_loopDataItem[0],_loopDataItem[1],_loopDataItem[2]):
                for _column in range(_loopDataItem[3],_loopDataItem[4],_loopDataItem[5]):
                    _binQrDataArray.append(_binMaskedQrArray[_row][_column])
        return _binQrDataArray

    def getQrEncoding(_binQrDataArray):
        """ Gets the encoding of the qr code by reading the first 4 bits of the binary data array, then returns the integer value representing the encoding. """
        _binQrEncodingList = _binQrDataArray[0:4]
        _binQrEncoding = ""
        for _item in _binQrEncodingList:
            _binQrEncoding += str(_item)
        return int(_binQrEncoding,base=2)

    def readQrData(_binQrDataArray):
        """ Reads the decoded data from the qr code and returns the text or other contents of the code. """
        _binQrEncoding = getQrEncoding(_binQrDataArray)

        def getQrLength(_binQrDataArray,_bitsQrLength):
            """ Given the number of bits used to store the length of the string, it reads these values from the start of the binary data array, from directly after the encoding values, and returns the integer
                value for the length of the data. """
            _binQrLengthList = _binQrDataArray[4:(4+_bitsQrLength)]
            _binQrLength = ""
            for _item in _binQrLengthList:
                _binQrLength += str(_item)
            return int(_binQrLength,base=2)

        def readQrDataByte(_binQrDataArray):
            """ This is called when the data is identified as ascii/8 bits. It iterates through the binary data array, reading sections of 8 bits, and then adding the character that each byte represents. """
            _binQrLength = getQrLength(_binQrDataArray,8)
            _binQrTextDataList = ""
            _binQrTextData = ""
            for _item in _binQrDataArray[12:(12+(8*_binQrLength))]:
                _binQrTextDataList += str(_item)
            for _loopChar in range(0,(8*_binQrLength),8):
                _binText = _binQrTextDataList[_loopChar:(_loopChar+8)]
                _binQrTextData += chr(int(_binText,base=2))
            return _binQrTextData

        def decodeAlphanumeric(_binAlphanumeric):
            """ Takes an integer representing two alphanumeric characters and uses a lookup dictionary to return the two letters. """
            _outputText = ""
            alphanumericLookup = {0:"0",1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"A",11:"B",12:"C",13:"D",14:"E",15:"F",16:"G",17:"H",18:"I",19:"J",20:"K",21:"L",22:"M",23:"N",24:"O",25:"P",
                                  26:"Q",27:"R",28:"S",29:"T",30:"U",31:"V",32:"W",33:"X",34:"Y",35:"Z",36:" ",37:"$",38:"%",39:"*",40:"+",41:"–",42:".",43:"/",44:":"}
            for _char1 in range(0,45):
                for _char2 in range(0,45):
                    if ((_char1 * 45) + _char2) == _binAlphanumeric:
                        _outputText += alphanumericLookup[_char1]
                        _outputText += alphanumericLookup[_char2]
            return _outputText


        def readQrDataAlphanumeric(_binQrDataArray):
            """ This is called when the data is identified as alphanumeric. It iterates through the binary data array, reading sections of 10 bits, and then calls another function to decode the characters, and
                returns them as a string. """
            if ((getQrLength(_binQrDataArray,9) // 2) * 2) == getQrLength(_binQrDataArray,9):
                _binQrLength = (getQrLength(_binQrDataArray,9) // 2)
            else:
                _binQrLength = ((getQrLength(_binQrDataArray,9) // 2) + 1)
            _binQrAlphanumberDataList = ""
            _binQrAlphanumberData = ""
            for _item in _binQrDataArray[13:(13+(11*_binQrLength))]:
                _binQrAlphanumberDataList += str(_item)
            for _loopChar in range(0,(11*_binQrLength),11):
                _binNum = str(_binQrAlphanumberDataList[_loopChar:(_loopChar+11)])
                _binQrAlphanumberData += decodeAlphanumeric(int(_binNum,base=2))
            return _binQrAlphanumberData

        def readQrDataNumeric(_binQrDataArray):
            """ This is called when the data is identified as numeric. It iterates through the binary data array, reading sections of 10 bits, and then working out the numbers that the bits represent. It then
                returns these as a string. """
            if ((getQrLength(_binQrDataArray,10) // 3) * 3) == getQrLength(_binQrDataArray,10):
                _binQrLength = (getQrLength(_binQrDataArray,10) // 3)
            else:
                _binQrLength = ((getQrLength(_binQrDataArray,10) // 3) + 1)
            _binQrNumberDataList = ""
            _binQrNumberData = ""
            for _item in _binQrDataArray[14:(14+(10*_binQrLength))]:
                _binQrNumberDataList += str(_item)
            for _loopChar in range(0,(10*_binQrLength),10):
                _binNum = str(int(_binQrNumberDataList[_loopChar:(_loopChar+10)],base=2))
                if len(_binNum) == 1:
                    _binNum = str(00) + _binNum
                elif len(_binNum) == 2:
                    _binNum = str(0) + _binNum
                _binQrNumberData += _binNum
            return _binQrNumberData

        if (getQrEncoding(_binQrDataArray) == 1): # Numeric
            return readQrDataNumeric(_binQrDataArray)
        elif (getQrEncoding(_binQrDataArray) == 2): # Alphanumeric
            return readQrDataAlphanumeric(_binQrDataArray)
        elif (getQrEncoding(_binQrDataArray) == 4): # Byte
            return readQrDataByte(_binQrDataArray)
        else:
            return ("Unknown Encoding -",getQrEncoding(_binQrDataArray))

    return readQrData(getQrData(getApplyQrMask(_binQrArray)))

### Main ###

def main():
    """ To showcase the decoder I use 2 real qr codes, scanned from our EMPR scanner, as well as 9 test codes, 3 of each type of qr code. For each code the program prints the filename being scanned, the data
        read, and whether this data is correct. This will only accent Version 1 QR codes as the differences with each version are significant. """

    _qrCodesArray = ["ScannedQrOne Edited","ScannedQrTwo Edited", # These are the real scanned codes, edited to make them easier to scan
                     "TestByteQr21x21","TestByteQr250x250Blurry","TestByteQr42x42", # These are the test 8 bit ascii codes
                     "TestNumericQr21x21","TestNumericQr21x21Blurry","TestNumericQr300x300", # These are the test numeric codes
                     "TestAlphanumericQr231x231","TestAlphanumericQr48x48Blurry","TestAlphanumericQrNew21x21"] # These are the test alphanumeric codes
    _qrCodesData = ["123012","12345",
                    "QR Code Demo","QR Code Demo","EMPR QR Code",
                    "123012","123012","11032020",
                    "ALPHANUMERICTEST","ALPHANUMERICTEST","WWW.YORK.AC.UK",]
    _qrCodesCount = 0
    _qrCorrectlyRead = 0
    _qrIncorrectlyRead = 0
    for _qrCode in _qrCodesArray:
        _qrCodeName = ""
        for _qrCodeLetter in _qrCode:
            _qrCodeName += str(_qrCodeLetter)
        print("QR Code Filename: " + str(_qrCodeName) + str(".png\nQR Code Data: "),end="")
        imQrArray = getQrFromFile(_qrCode)
        binQrArray = toBinQrArray(imQrArray)
        qrData = getQrData(binQrArray)
        print(qrData)
        try:
            assert (qrData==_qrCodesData[_qrCodesCount])
            print("QR Code Accurate: Correctly Read\n")
            _qrCorrectlyRead += 1
        except AssertionError:
            print("QR Code Accurate: Incorrectly Read")
            print("QR Code Correct Data:",_qrCodesData[_qrCodesCount],"\n")
            _qrIncorrectlyRead += 1
        _qrCodesCount += 1
    print("QR Codes Correctly Scanned:",str(_qrCorrectlyRead)+"/"+str(_qrCorrectlyRead+_qrIncorrectlyRead),"\n")

if (__name__ == "__main__"):
    main()