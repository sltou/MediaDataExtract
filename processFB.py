#!/usr/bin/python
# -*- encoding: utf8 -*-

import os
import time
import datetime
import sys
import re
import nltk
from collections import defaultdict
from nltk.text import Text

# return data structure to store all texts- a list of tuples
#[(filename, date, text)]
def importData():
    data = []
    totalChar = 0
    # a list of chars to get rid of
    punc = u'=!@#$%^&*()《》<>[]{},.!。，、⋯⋯〉〈：:＝=－、｜|〗〖'
    mapping = dict.fromkeys(map(ord,punc))
    # loop through all .txt in all directories in the file directory
    PARENT = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/gDrive/Ling447_finalPJ')
    for root, dirs, junk in os.walk(PARENT):
        #each text file
        for name in dirs[:1]:
            dirName = os.path.join(root, name)
            for text in os.listdir(dirName):
                if os.path.isfile(os.path.join(dirName, text)) and (os.path.splitext(text)[-1].lower() == '.txt'):
                    line = ''
                    first = True
                    with open(os.path.join(dirName, text), 'r') as content:
                        for line in content:
                            #the first line has to be date!
                            if first:
                                date = line
                                first = False
                                line = ''
                            posttext = ''
                            #read till the next date
                            if (len(line) < 10 ) or (not re.match('\d{4}-\d{2}-\d{2}', line[0:10])):
                                #print line
                                line =  line.decode('utf-8').translate(mapping)
                                totalChar = totalChar + len(line)
                                if not posttext == '':
                                    #print posttext.encode('utf-8')
                                    posttext = posttext + line
                                else:
                                    posttext = line
                                    
                            data.append((name, date, posttext))
                            date = line
                        #print 'this .txt has ' + str(len(data))
            print str(name) +' has ' +str(len(data)) + ' and characters ' + str(totalChar)
    return data

def tokenize(data):
    newList = []
    for item in data:
        token_list = []
        for char in item[2][0]:
            token_list.append(char.encode('utf-8'))
        newList.append((item[0], item[1], token_list))
    return newList

def sortDataByDate(data):
    data = sorted(data, key = lambda x: x[1])

'''
    modify: http://www.nltk.org/_modules/nltk/text.html
    inherent nltk ConcordanceIndex class
    will print both concordance and time stamp, and encoded in utf-8
'''
class ConcordanceIndexDate(nltk.ConcordanceIndex):
    def __init__(self, tokens, key=lambda x:x):
        """
            Construct a new concordance index.
            
            :param tokens: data [(source, date, tokens)] that this concordance index was created from.
            :param key: A function that maps each token to a normalized
            version that will be used as a key in the index.  E.g., if
            you use ``key=lambda s:s.lower()``, then the index will be
            case-insensitive.
            """
        self._tokens = tokens[2]
        """The document (list of list of tokens) that this concordance index
            was created from."""
        
        self._key = key
        """Function mapping each token to an index key (or None)."""
        
        self._offsets = defaultdict(list)
        """Dictionary mapping words (or keys) to lists of lists of offset
            indices."""
        self._date = tokens[1]
        
        # Initialize the index (self._offsets)
        for index, word in enumerate(self._tokens):
            word = self._key(word)
            self._offsets[word].append(index)


    def print_concordance(self, word, width=50, lines=25):
        half_width = (width - len(word) - 2) // 2
        context = width // 4 # approx number of words of context
        offsets = self.offsets(word)
        if offsets:
            lines = min(lines, len(offsets))
            #print("Displaying %s of %s matches:" % (lines, len(offsets)))
            for i in offsets:
                if lines <= 0:
                    break
                leftBoundry = min(context, i)
                left = (' '.join([x.decode('utf-8') for x in self._tokens[i- leftBoundry:i]]))    # was context decoded here for display purposes
                print len(self._tokens)
                rightBoundry = min(context, len(self._tokens) - i - 1)
                right = ' '.join([x.decode('utf-8') for x in self._tokens[i+1:i + rightBoundry + 1]])    # :i+context decoded here for display purposes
                left = left[-half_width:]
                right = right[:half_width]
                date = str(self._date)
                leftPadding = u'－ ' * (context - leftBoundry)
                rightPadding = u'－ ' * (context - rightBoundry)
                print rightBoundry
                print(' '.join([' ' * half_width, leftPadding, left, self._tokens[i].decode('utf-8'), right, rightPadding, date]))  # decoded here for display purposes
                lines -= 1
        else:
            print("No matches")
        return len(offsets)
'''
def showConcordance(target, data):
    concordance_index = ConcordanceIndex2([u'找'.encode('utf-8'),u'你'.encode('utf-8'),u'呀'.encode('utf-8')], key = lambda s:s.lower())    # encoded here to match an encoded text
    print concordance_index._offsets
    concordance_index.print_concordance(u'你'.encode('utf-8'))
'''

def generateConcordanceIndices(data):
    index_list = []
    for item in data:
        index_list.append(ConcordanceIndexDate(item))
    return index_list

#targets: a list of search words encoded in utf-8
def showConcordance(targets, data):
    index_list = generateConcordanceIndices(data)
    for target in targets:
        print 'now searching ' + target
        count = 0
        for index in index_list:
            count = count + index.print_concordance(target.encode('utf-8'))
        print "%d results in total" %count

if __name__ == '__main__':
    #data = importData()
    data = [(1,123,[u'找'u'你'u'呀']), (1, 234, [u'找'u'你'u'呀'u'找'u'找'u'找'u'找'u'找'u'找'])]
    data = tokenize(data)
    showConcordance([u'你'],data)

