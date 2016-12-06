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
import copy

# return data structure to store all texts- a list of tuples
#[(filename, date, text)]
def importData():
    data = []
    totalChar = 0
    posttext = ''
    # a list of chars to get rid of
    #mystring = '不 如 你 都 係 肥 返 啦 好 嗎 …'
    punc = u'=!@#$%^&*()《》<>[]{},.!。，、⋯⋯〉〈：:＝=－、｜|〗〖… ?\n」「'
    mapping = dict.fromkeys(map(ord,punc))
    #mystring = mystring.decode('utf-8').translate(mapping)
    #print mystring
    # loop through all .txt in all directories in the file directory
    PARENT = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/gDrive/Ling447_finalPJ')
    for root, dirs, junk in os.walk(PARENT):
        #each text file
        for name in dirs[:1]:
            dirName = os.path.join(root, name)
            for text in os.listdir(dirName)[:20]:
                #print text
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
                            else:
                                data.append((name, date, posttext))
                                date = line
                                posttext = ''
                        #print 'this .txt has ' + str(len(data))
            print str(name) +' has ' +str(len(data)) + ' and characters ' + str(totalChar)
    return data

def tokenize(data):
    newList = []
    for item in data:
        token_list = []
        for char in item[2]:
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


    def print_concordance(self, word, width=50, lines=50):
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
                #print len(self._tokens)
                rightBoundry = min(context, len(self._tokens) - i - 1)
                right = ' '.join([x.decode('utf-8') for x in self._tokens[i+1:i + rightBoundry + 1]])    # :i+context decoded here for display purposes
                left = left[-half_width:]
                right = right[:half_width]
                #print self._date
                date = str(self._date)
                leftPadding = u'－ ' * (context - leftBoundry)
                rightPadding = u'－ ' * (context - rightBoundry)
                #print rightBoundry
                print(' '.join([leftPadding, left, self._tokens[i].decode('utf-8'), right, rightPadding, date]))  # decoded here for display purposes
                lines -= 1
        return len(offsets)


'''
    modify: http://www.nltk.org/_modules/nltk/tesxt.html
    inherent nltk ConcordanceIndex class
    will print both concordance and time stamp, and encoded in utf-8, and can look for concordance for phrases of length 1-10
    '''
class ConcordanceMultiIndexDate(nltk.ConcordanceIndex):
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
            START indices."""
        self._date = tokens[1]
        
        # Initialize the index (self._offsets) 1 to 10 gram
        for gram in range(10):
            for index, word in enumerate(self._tokens):
                #keep generate n-gram
                if index < len(self._tokens) - gram:
                    #build the gram
                    gramWord = word
                    for i in range(1,gram + 1):
                        gramWord = gramWord + self._tokens[index + i]
                    gramWord = self._key(gramWord)
                    self._offsets[gramWord].append(index)

    #to do: modify for multiple
    def print_concordance(self, word, width=50, lines=50):
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
                #print len(self._tokens)
                rightBoundry = min(context, len(self._tokens) - i - 1)
                right = ' '.join([x.decode('utf-8') for x in self._tokens[i+1:i + rightBoundry + 1]])    # :i+context decoded here for display purposes
                left = left[-half_width:]
                right = right[:half_width]
                #print self._date
                date = str(self._date)
                leftPadding = u'－ ' * (context - leftBoundry)
                rightPadding = u'－ ' * (context - rightBoundry)
                #print rightBoundry
                print(' '.join([leftPadding, left, self._tokens[i].decode('utf-8'), right, rightPadding, date]))  # decoded here for display purposes
                lines -= 1
        return len(offsets)

def dataDistribution(data):
    #create bin of dates, dict (key year) of dict (key month)
    months = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
    posts = {2006:copy.deepcopy(months), 2007:copy.deepcopy(months), 2008:copy.deepcopy(months), 2009:copy.deepcopy(months), 2010:copy.deepcopy(months), 2011:copy.deepcopy(months), 2012:copy.deepcopy(months), 2013:copy.deepcopy(months), 2014:copy.deepcopy(months), 2015:copy.deepcopy(months), 2016:copy.deepcopy(months)}
    characters = {2006:copy.deepcopy(months), 2007:copy.deepcopy(months), 2008:copy.deepcopy(months), 2009:copy.deepcopy(months), 2010:copy.deepcopy(months), 2011:copy.deepcopy(months), 2012:copy.deepcopy(months), 2013:copy.deepcopy(months), 2014:copy.deepcopy(months), 2015:copy.deepcopy(months), 2016:copy.deepcopy(months)}
    for item in data:
        newTime = time.strptime(item[1][:7], '%Y-%m')
        posts[newTime.tm_year][newTime.tm_mon] = posts[newTime.tm_year][newTime.tm_mon] + 1
        characters[newTime.tm_year][newTime.tm_mon] = characters[newTime.tm_year][newTime.tm_mon] + len(item[2])
    for year in posts.keys():
        for month in posts[year].keys():
            print "%d %d %d" %(year, month, posts[year][month])
    for year in characters.keys():
        for month in characters[year].keys():
            print "%d %d %d" %(year, month, characters[year][month])

def generateConcordanceIndices(data):
    index_list = []
    for item in data:
        index_list.append(ConcordanceMultiIndexDate(item)) #old version ConcordanceIndexDate(item)
    #for index in index_list:
        #print index._offsets
    return index_list

def occurenceAtTime(targets, ngramsTime):
    for target in targets:
        months = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        occurs = {2006:copy.deepcopy(months), 2007:copy.deepcopy(months), 2008:copy.deepcopy(months), 2009:copy.deepcopy(months), 2010:copy.deepcopy(months), 2011:copy.deepcopy(months), 2012:copy.deepcopy(months), 2013:copy.deepcopy(months), 2014:copy.deepcopy(months), 2015:copy.deepcopy(months), 2016:copy.deepcopy(months)}
        for ngram in ngramsTime:
            occurence = len(ngram._offsets[target.encode('utf-8')])
            #print occurence
            newTime = time.strptime(ngram._date[:7], '%Y-%m')
            occurs[newTime.tm_year][newTime.tm_mon] = occurs[newTime.tm_year][newTime.tm_mon] + occurence
        print 'Looking for %s' %target
        for year in occurs.keys():
            for month in occurs[year].keys():
                print "%d %d %d" %(year, month, occurs[year][month])


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
    slangs = [u'玻璃心', u'一地玻璃', u'做兵', u'收兵', u'屈蛇', u'關公災難', u'李氏力場', u'689']
    #data = [(1,'2016-09-30T00:28:22+0000',u'我愛你'), (1, '2016-09-30T00:28:22+0000', u'你寫完作業了沒有')] #dummydata
    data = importData()
    data = tokenize(data)
    #dataDistribution(data)
    #print data
    #showConcordance([u'你'],data)
    ngrams = generateConcordanceIndices(data)
    occurenceAtTime([u'玻璃心', u'加油'], ngrams)

