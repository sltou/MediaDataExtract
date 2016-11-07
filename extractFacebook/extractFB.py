'''
    ADD IN README: need to explore with limit! Looks like it is different in each webpage
    Get all posts with timestamps and their comments with timestamps from a list of Facebook public pages
    For each page, a folder with the name of the page is created in the home directory
    A txt document with name = post_id is created for each post with format:
        first line: creation date
        second line: post content
        3rd - : creation date of comment, comment. each comment: one line time, next line content
'''

import facebook
import urllib
import urlparse
import subprocess
import warnings
import os
import time
import datetime
from utf8Encode import *

#import app ID, app secret, and profile ID
from JennySecrets import *

'''
    SECTION: Facebook login
    code from http://stackoverflow.com/questions/3058723/programmatically-getting-an-access-token-for-using-the-facebook-graph-api
'''
# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)


# Parameters of your app and the id of the profile you want to mess with.
FACEBOOK_APP_ID     = JennyFBAppID  #change it to your app id!
FACEBOOK_APP_SECRET = JennyFBAppSecret #change it to your app secret!
FACEBOOK_PROFILE_ID = 'hk.nextmedia'


# Trying to get an access token. Very awkward.
oauth_args = dict(client_id     = FACEBOOK_APP_ID,
                  client_secret = FACEBOOK_APP_SECRET,
                  grant_type    = 'client_credentials')
oauth_curl_cmd = ['curl',
                  'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
oauth_response = subprocess.Popen(oauth_curl_cmd,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE).communicate()[0]

try:
    oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
except KeyError:
    print('Unable to grab an access token!')
    exit()

'''
    SECTION: create a facebook graph object
'''
facebook_graph = facebook.GraphAPI(oauth_access_token)


'''
    SECTION: Get the data!
'''
#directory to save the files
directory = os.path.abspath('/Users/jennytou/Desktop/Umich/Fall2016/ling447/finalPJ/gDrive/Ling447_finalPJ/appleDaily')
#start date 01/11/2016
startDate = 1403049600 #1477958400
until = startDate
#end date 01/11/2006
endDate = 1162339200
#first time request object, do not need to check paging
firstTime = True
lastPostDate = startDate
while (firstTime or lastPostDate >= endDate and 'paging' in object['posts'].keys() and 'next' in object['posts']['paging'].keys() and object['posts']['paging']['next']):
    if not (firstTime):
        nextUrl = object['posts']['paging']['next']
        parsed = urlparse.urlparse(nextUrl)
        until = int(urlparse.parse_qs(parsed.query)['until'][0])
    try:
        object = facebook_graph.get_object(id = FACEBOOK_PROFILE_ID, fields = 'posts.since(%s).limit(25).until(%s){created_time, message, id, comments}' %(endDate, until))
        #print object
        for post in object['posts']['data']:
            try:
                firstTime = False
                postID = post['id']
                postContent = post['message']
                postTime = post['created_time']
                #create a file for the post
                file = open(directory + '/' + postID + '.txt', 'w')
                #write content, time
                file.write(postTime.encode('utf-8') + '\n' + postContent.encode('utf-8') + '\n')
                #if no comment on the post, pass and go to the next post
                comments = post['comments']
                for comment in comments['data']:
                    commenttime = comment['created_time']
                    content = comment['message']
                    file.write(commenttime.encode('utf-8') + '\n' + content.encode('utf-8') + '\n')
                file.close()
            except KeyError as e:
                print e.message
                pass
            

        #can only do 100 posts a request, so keep requesting until end
        lastPostDate = time.mktime(time.strptime(postTime[:10], '%Y-%m-%d'))


    except facebook.GraphAPIError as e:
        print 'Something went wrong:', e.type, e.message
        
    except requests.ConnectionError:
        '''
            SECTION: get another token if exceeds max!
            code from http://stackoverflow.com/questions/3058723/programmatically-getting-an-access-token-for-using-the-facebook-graph-api
            '''
        # Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
        warnings.filterwarnings('ignore', category=DeprecationWarning)


        # Parameters of your app and the id of the profile you want to mess with.
        FACEBOOK_APP_ID     = JennyFBAppID  #change it to your app id!
        FACEBOOK_APP_SECRET = JennyFBAppSecret #change it to your app secret!
        FACEBOOK_PROFILE_ID = 'hk.nextmedia'


        # Trying to get an access token. Very awkward.
        oauth_args = dict(client_id     = FACEBOOK_APP_ID,
                          client_secret = FACEBOOK_APP_SECRET,
                          grant_type    = 'client_credentials')
        oauth_curl_cmd = ['curl',
                          'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
        oauth_response = subprocess.Popen(oauth_curl_cmd,
                                          stdout = subprocess.PIPE,
                                          stderr = subprocess.PIPE).communicate()[0]

        try:
            oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
        except KeyError:
            print('Unable to grab an access token!')
            exit()

        '''
            SECTION: create a facebook graph object
            '''
        facebook_graph = facebook.GraphAPI(oauth_access_token)

        pass



