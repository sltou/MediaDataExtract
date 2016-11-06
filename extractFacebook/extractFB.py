'''
    Get all posts with timestamps and their comments with timestamps from a list of Facebook public pages
    For each page, a folder with the name of the page is created in the home directory
    A txt document with name = post_id is created for each post with format:
        first line: post content
        second line: creation date
        3rd - : comment, creation date. each comment one line
'''

import facebook
import urllib
import urlparse
import subprocess
import warnings
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
FACEBOOK_PROFILE_ID = 'dryclubhk'


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
try:
    fb_response = facebook_graph.get_object(id = FACEBOOK_PROFILE_ID, fields = 'posts')
    for post in fb_response['posts']['data']:
        time = post['created_time']
        content = post['message']
        postid = post['id']
        try:
            comments = facebook_graph.get_connections(id = postid, connection_name = 'comments')
            for comment in comments['data']:
                time = comment['created_time']
                content = comment['message']
                print content
        except facebook.GraphAPIError as e:
            print 'error in getting comments', e.type, e.message

#print fb_response
except facebook.GraphAPIError as e:
    print 'Something went wrong:', e.type, e.message