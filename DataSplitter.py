class DataSplitter:
    def __init__(self, f = open('output.txt', 'a', encoding='utf8')):
        self.f = f

    def fileReader(self, myList):
        if " || " in myList:
            #print(myList[0])
            partAbbr = myList.split("&")
            #print(partAbbr)
            aloneAbbr = list(partAbbr[0].split(" || "))
            #print(aloneAbbr[0])
            for j in range(0, len(aloneAbbr)):
                self.f.write(aloneAbbr[j] + " & " +
                        partAbbr[1] + " & " +
                        partAbbr[2] + '\n')
        else:
            self.f.write(myList + '\n')
        return