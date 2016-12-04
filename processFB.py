#!/usr/bin/python
# -*- encoding: utf8 -*-

import os
import time
import datetime
import sys
import re

# data structure to store all texts- a list of tuples
#[(filename, date, text)]
data = []
totalChar = 0
# a list of chars to get rid of
punc = u'=!@#$%^&*()《》<>[]{},.!。，、⋯⋯〉〈：:＝=－、｜|〗〖'
mapping = dict.fromkeys(map(ord,punc))
# loop through all .txt in all directories in the file directory
PARENT = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/gDrive/Ling447_finalPJ')
for root, dirs, junk in os.walk(PARENT):
    #each text file
    for name in dirs:
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
