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
from random import shuffle
import io

# return data structure to store all texts- a list of tuples
#[(filename, date, text)]
def importData(i):
    data = []
    totalChar = 0
    posttext = ''
    # a list of chars to get rid of
    #mystring = '不 如 你 都 係 肥 返 啦 好 嗎 …'
    punc = u'=!@#$%^&*()《》<>[]{},.!。，、⋯⋯〉〈：:＝=－、｜|〗〖… ?\n」「'
    mapping = dict.fromkeys(map(ord,punc))
    fileName = ''
    #mystring = mystring.decode('utf-8').translate(mapping)
    #print mystring
    # loop through all .txt in all directories in the file directory
    PARENT = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/gDrive/Ling447_finalPJ')
    for root, dirs, junk in os.walk(PARENT):
        #each text file
        for name in dirs[i:i+1]:
            fileName = name
            dirName = os.path.join(root, name)
            allFiles = os.listdir(dirName)
            shuffle(allFiles)
            #randomly look at 1000 posts
            for text in allFiles[:min(len(allFiles), 1000)]:
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
    return data, fileName

def tokenize(data):
    newList = []
    for item in data:
        token_list = []
        for char in item[2]:
            char = char.lower()
            token_list.append(char.encode('utf-8'))
        newList.append((item[0], item[1], token_list))
    return newList

def sortDataByDate(data):
    data = sorted(data, key = lambda x: x[1])

'''
    modify: http://www.nltk.org/_modules/nltk/text.html
    inherent nltk ConcordanceIndex class
    will print both concordance and time stamp, and encoded in utf-8
    only one word, faster
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
    def __init__(self, tokens, slangs, key=lambda x:x):
        """
            Construct a new concordance index.
            
            :param tokens: data [(source, date, tokens)] that this concordance index was created from.
        """
        self._tokens = tokens[2]
        self._key = key
        self._offsets = defaultdict(list)
        self._date = tokens[1]
        
        '''
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
         '''
    # building ngrams are too slow for this amount of data. just build the grams for slangs because this is all we need
        for slang in slangs:
            #print slang
            #print self._tokens
            num = len(slang)
            slang = slang.encode('utf-8')
            for index, word in enumerate(self._tokens):
                if index < len(self._tokens) - num:
                    #check if matching the slang
                    pont = "".join(self._tokens[index:index + num])
                    #print pont
                    if pont == slang:
                        slang = self._key(slang)
                        self._offsets[slang].append(index)
        #print self._offsets

    # will print at most 100 randomized occurences  of concordance
    def print_concordance(self, word, file, width=50, lines=100):
        out = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/concordance/%s%s' %(file,word))
        file = io.open('%s.txt'%out, 'a', encoding = 'utf-8')
        context = 10 # window = +- 10
        wordUTF = word.decode('utf-8')
        num = len(wordUTF)
        #print num
        offsets = self.offsets(word)
        if offsets:
            if len(offsets) > 100:
                shuffle(offsets)
            lines = min(lines, len(offsets))
            #print("Displaying %s of %s matches:" % (lines, len(offsets)))
            for i in offsets:
                if lines <= 0:
                    break
                leftBoundry = min(context, i)
                left = (''.join([x.decode('utf-8') for x in self._tokens[i- leftBoundry:i]]))    # was context decoded here for display purposes
                #print len(self._tokens)
                rightBoundry = min(context, len(self._tokens) - (i + num))
                right = ''.join([x.decode('utf-8') for x in self._tokens[i+num:i + rightBoundry + 1]])    # :i+context decoded here for display purposes
                #print self._date
                date = str(self._date)
                #leftPadding = u'－ ' * (context - leftBoundry)
                #rightPadding = u'－ ' * (context - rightBoundry)
                #print rightBoundry
                file.write((' '.join([left, wordUTF, right, date])))  # decoded here for display purposes
                lines -= 1
        file.close()
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

def generateConcordanceIndices(data, slangs):
    index_list = []
    for item in data:
        index_list.append(ConcordanceMultiIndexDate(item, slangs, key=lambda s:s.lower())) #old version ConcordanceIndexDate(item)
        #print 'generated 1'
        #sys.stdout.flush()
    #for index in index_list:
        #print index._offsets
    return index_list

def occurenceAtTime(targets, data,file):
    out = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/occurence/%s' %file)
    file = open('%s.txt'%out, 'w')
    for target in targets:
        months = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        occurs = {2006:copy.deepcopy(months), 2007:copy.deepcopy(months), 2008:copy.deepcopy(months), 2009:copy.deepcopy(months), 2010:copy.deepcopy(months), 2011:copy.deepcopy(months), 2012:copy.deepcopy(months), 2013:copy.deepcopy(months), 2014:copy.deepcopy(months), 2015:copy.deepcopy(months), 2016:copy.deepcopy(months)}
        num = len(target)
        target = target.encode('utf-8')
        for item in data:
            newTime = time.strptime(item[1][:7], '%Y-%m')
            for index, word in enumerate(item[2]):
                if index <= len(item[2]) - num:
                    #check if matching the slang
                    pont = ("".join(item[2][index:index + num]))
                    #print type(pont)
                    if pont == target:
                        occurs[newTime.tm_year][newTime.tm_mon] = occurs[newTime.tm_year][newTime.tm_mon] + 1
        print 'Looking for %s' %target
        file.write(target)
        file.write('\n')
        for year in occurs.keys():
            for month in occurs[year].keys():
                file.write("%d %d %d\n" %(year, month, occurs[year][month]))
    file.close()
#sys.stdout.flush()


#targets: a list of search words encoded in utf-8
def showConcordance(targets, data, slangs, fileName):
    index_list = generateConcordanceIndices(data, slangs)
    for target in targets:
        print 'now searching ' + target
        count = 0
        for index in index_list:
            count = count + index.print_concordance(target.encode('utf-8'), fileName)
        print "%d results in total" %count

if __name__ == '__main__':
    slangs = [u'玻璃心', u'一地玻璃', u'做兵', u'收兵', u'屈蛇', u'關公災難', u'李氏力場', u'689', u'有請小凰姐', u'廢青', u'方丈', u'tree根', u'厚多士', u'囧', u'到嘔', u'你識條春咩', u'你識條鐵咩', u'JER數', u'誠實豆沙包', u'on9', u'扒房', u'燉冬菇', u'n無', u'綠帽', u'sevenhead', u'語癌', u'小學雞', u'中學雞', u'中學鴨', u'undingable', u'海k', u'膠', u'串', u'動l', u'草泥馬', u'重口味', u'重口味', u'狗衝', u'昂坪360', u'十卜', u'抽水', u'河蟹', u'金翅仆街鳥', u'玩撚猿', u'神馬', u'orz', u'1999', u'粉腸', u'飛釘', u'爆seed', u'腦細', u'sorrysir', u'割禾青', u'仆街', u'賣飛佛', u'吹水', u'射住', u'收皮', u'淆底', u'升呢', u'步兵', u'認真你就輸了', u'耶青', u'抄牌', u'到無朋友', u'到冇朋友', u'殺很大', u'頹', u'秒殺', u'軍糧', u'宅男', u'出pool', u'講呢啲', u'爛grade', u'好似係', u'回水', u'潮', u'大閘蟹', u'炮友', u'搬龍門', u'o嘴', u'omouth', u'潛水', u'屈機', u'噴飯', u'扮蟹', u'等埋發叔', u'倒抽一口涼氣', u'倒抽一口梁氣', u'我爸是梁特', u'kai', u'hea', u'chok', u'chur', u'charm', u'hehe', u'全部都係雞', u'條女', u'你的樣子如何', u'賓賓', u'阿叉', u'摺', u'左膠', u'threecmeet', u'goodest']
    #print len(slangs)
    '''
    data = [(1,'2016-09-30T00:28:22+0000',u'我愛你Jeffery'), (1, '2016-09-30T00:28:22+0000', u'你寫完作業了沒有')] #dummydata
    data = tokenize(data)
    showConcordance([u'你j'],data,[u'你j', u'你寫'])
    '''
    for file in range(12):
        data, fileName = importData(file)
        data = tokenize(data)
        #dataDistribution(data)
        #print data
        showConcordance(slangs,data,slangs, fileName)
        #ngrams = generateConcordanceIndices(data, slangs)
        #occurenceAtTime(slangs, data, fileName)

