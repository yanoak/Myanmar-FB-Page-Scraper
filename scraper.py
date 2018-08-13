
# import some Python dependencies
import urllib2
#import requests
import json
import datetime
import csv
import time
import sys
from converter import zg12uni51
from uni_ecoder import UnicodeWriter

##### Facebook app id + secret

app_id = ""
app_secret = "" # DO NOT SHARE WITH ANYONE!
 
access_token = app_id + "|" + app_secret

##### Get JSON from FB Graph API request untill successcful

def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print e
            time.sleep(5)
            
            print "Error for URL %s: %s" % (url, datetime.datetime.now())

    return response.read()


#-----------------------------------------------------------------
####################### POSTS ####################################
#-----------------------------------------------------------------


##### Use request_until_succeed() to get particular FB page's JSON data

def getFacebookPageFeedData(page_id, access_token, num_statuses):
    
    # construct the URL string
    base = "https://graph.facebook.com"
    node = "/" + page_id + "/feed" 
    # parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(1).summary(true),"
    # parameters += "comments.limit(1).summary(true),shares&until=1405296000&limit=%s&access_token=%s" % (num_statuses, access_token) # changed

    parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(1).summary(true),"
    parameters += "reactions.limit(1).summary(true),"
    parameters += "comments.limit(1).summary(true),shares&limit=%s&access_token=%s" % (num_statuses, access_token) # changed
    url = base + node + parameters
    
    # retrieve data
    data = json.loads(request_until_succeed(url))
    
    return data


##### Process data from getFacebookPageFeedData() into array

def processFacebookPageFeedStatus(status):
    
    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.
    
    # Additionally, some items may not always exist,
    # so must check for existence first
    try: 
        status_id = status['id']
        status_message = '' if 'message' not in status.keys() else zg12uni51(status['message']).encode('utf-8').replace('"', r'\"')
        #status_message = '' if 'message' not in status.keys() else status['message'].encode('utf-8')
        link_name = '' if 'name' not in status.keys() else status['name'].encode('utf-8')
        status_type = status['type']
        status_link = '' if 'link' not in status.keys() else status['link'].encode('utf-8')
        
        
        # Time needs special care since a) it's in UTC and
        # b) it's not easy to use in statistical programs.
        
        status_published = datetime.datetime.strptime(status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
        status_published = status_published + datetime.timedelta(hours=-5) # EST
        status_published = status_published.strftime('%Y-%m-%d %H:%M:%S') # best time format for spreadsheet programs
        
        # Nested items require chaining dictionary keys.
        #print status['likes']
        #num_likes = 0 if 'likes' not in status.keys() else status['likes']['summary']['total_count']

        num_likes = 0
        if 'likes' in status.keys(): 
            if 'summary' in status['likes']: 
                if 'total_count' in status['likes']['summary']: 
                    num_likes = status['likes']['summary']['total_count']
        num_reactions = 0
        if 'reactions' in status.keys(): 
            if 'summary' in status['reactions']: 
                if 'total_count' in status['reactions']['summary']: 
                    num_reactions = status['reactions']['summary']['total_count']
        num_comments = 0
        if 'comments' in status.keys(): 
            if 'summary' in status['comments']: 
                if 'total_count' in status['comments']['summary']: 
                    num_comments = status['comments']['summary']['total_count']
        #comment_1 = "" if 'comments' not in status.keys() else status['comments']['data'][0]['message']
        #comment_2 = "" if 'comments' not in status.keys() else status['comments']['data'][1]['message']
        num_shares = 0 if 'shares' not in status.keys() else status['shares']['count']
    except Exception, e:
        print e
        print "Error for status %s" % (status)

    
    # return a tuple of all processed data
    return (status_id, status_message, link_name, status_type, status_link,
           status_published, num_likes, num_reactions, num_comments, num_shares)
#     return utf_8_encoder( (status_id, status_message, link_name, status_type, status_link,
#           status_published, num_likes, num_comments, num_shares) )


##### Write data from processFacebookPageFeedStatus() into CSV file

def scrapeFacebookPageFeedStatusWriteCSV(page_id, access_token):
    
    with open('%s_facebook_statuses.csv' % page_id, 'wb') as file:
        #w = csv.writer(file)
        uni_writer = UnicodeWriter(file)
        uni_writer.writerow(["status_id", "status_message", "link_name", "status_type", "status_link",
           "status_published", "num_likes", "num_reactions", "num_comments", "num_shares"])
        #w.writerow(["status_id", "status_message", "link_name", "status_type", "status_link",
        #   "status_published", "num_likes", "num_comments", "num_shares"])
        
        
        has_next_page = True
        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()
        
        print "Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime)
        
        statuses = getFacebookPageFeedData(page_id, access_token, 100)
        
        while has_next_page:
            for status in statuses['data']:
                
                row = processFacebookPageFeedStatus(status)
                #print(row)
                uni_writer.writerow(row)
                #w.writerow(row)
                
                #print "%s \n" % (row) 
                
                # output progress occasionally to make sure code is not stalling
                num_processed += 1
                if num_processed % 1000 == 0:
                    print "%s Statuses Processed: %s" % (num_processed, datetime.datetime.now())
                    
            # if there is no next page, we're done.
            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(statuses['paging']['next']))
            else:
                has_next_page = False
                
        
        print "\nDone!\n%s Statuses Processed in %s" % (num_processed, datetime.datetime.now() - scrape_starttime)



#-----------------------------------------------------------------
####################### COMMENTS #################################
#-----------------------------------------------------------------

##### Use request_until_succeed() to get particular FB posts' JSON data for comments

def getPostsCommentData(page_id, access_token, num_statuses):
    
    # construct the URL string
    base = "https://graph.facebook.com"
    node = "/" + post_id + "/comments" 
    # parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(1).summary(true),"
    # parameters += "comments.limit(1).summary(true),shares&until=1405296000&limit=%s&access_token=%s" % (num_statuses, access_token) # changed

    parameters = "/?fields=id,message,from,like_count,comment_count,message_tags,parent,created_time,comments.limit(1).summary(true),likes.limit(1).summary(true),reactions.limit(1).summary(true)&"
    parameters += "limit=%s&access_token=%s" % (num_comments, access_token) # changed
    url = base + node + parameters
    
    # retrieve data
    data = json.loads(request_until_succeed(url))
    
    return data


##### Function to be called from an external script to get post data from a page

def scrapeFacebookPage(page_id):
    #statuses = getFacebookPageFeedData(page_id, access_token, 100)
    #print statuses
    scrapeFacebookPageFeedStatusWriteCSV(page_id,access_token)

