class BaseCJK(object):
    cjkCore = int("4E00", 16) #CJK Unified Ideographs range: [U+4E00, U+9FFF]
    lenCore = int("9FFF", 16) - cjkCore + 1 #20992
    cjkExtA = int("3400", 16) #CJK Unified Ideographs Extension A range: [U+3400, U+4DBF]
    lenExtA = int("4DBF", 16) - cjkExtA + 1 #6592
    cjkExtB = int("20000", 16) #CJK Unified Ideographs Extension B range: [U+20000, U+2A6DF]
    lenExtB = int("2A6DF", 16) - cjkExtB + 1 #42720

    def chunk(self, data, length):
        return [data[i:i+length] for i in range(0, len(data), length)]

    def encode(self, bInput):
        padding = 0
        if len(bInput) % 2 != 0:
            padding = 1
            bInput += b"\x00"
        trunks = self.chunk(bInput, 2)

        binStr = ""
        for chunk in trunks:
            for x in chunk:
                binStr += "{:0>8}".format(bin(x)[2:])
        chunk16 = self.chunk(binStr, 16)

        outStr = ""
        for bin16 in chunk16:
            int2 = int(bin16, 2)
            if(int2 < self.lenCore):
                c = chr( self.cjkCore + int2)
            elif((int2 - self.lenCore) < self.lenExtA):
                c = chr( self.cjkExtA + (int2 - self.lenCore))
            else:
                c = chr( self.cjkExtB + (int2 - self.lenCore - self.lenExtA))
            outStr += c
        
        if(padding):
            outStr += "="
        return outStr

    def decode(self, sInput):
        padding = sInput.count("=")
        sInput = sInput.replace("=", "")
        
        binStr = ""
        for char in sInput:
            code = ord(char)
            if((code >= self.cjkCore) and ((code - self.cjkCore) < self.lenCore)):
                index = code - self.cjkCore
            elif((code >= self.cjkExtA) and ((code - self.cjkExtA) < self.lenExtA)):
                index = self.lenCore + code - self.cjkExtA
            elif((code >= self.cjkExtB) and ((code - self.cjkExtB) < self.lenExtB)):
                index = self.lenCore + self.lenExtA + code - self.cjkExtB
            else:
                raise ValueError('not a valid baseCJK string')
            binStr += "{:0>16b}".format(index)

        chunk8 = self.chunk(binStr, 8)
        if(padding):
            chunk8.pop()
        
        outbytes = b""
        for chunk in chunk8:
            outbytes += bytes([int(chunk, 2)])

        return outbytes

if __name__ == "__main__":
    bCJK = BaseCJK()
    print(bCJK.decode(bCJK.encode(b"Hello, world.")))
