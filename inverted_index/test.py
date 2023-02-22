import postings
index = {}
textList = ['the', 'in', 'the', 'be', 'to', 'from', 'to']
for i in range(len(textList)):
    if textList[i] not in index:
        index[textList[i]] = postings.Postings()
        index[textList[i]].frequs = 1
    else:
        index[textList[i]].frequs += 1
    index[textList[i]].pos.append(i)

for key in index:
    postings.printPosting(index[key])