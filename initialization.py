''' 
initializing task including
crawling initializing, database connector, translator etc.
'''

# from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
import re
import warnings
import json
import mechanize
import cookielib
import urllib, urllib2
import sys
import pprint
import datetime
import pdb

def crawling_init(qurl):
    """query qurl and return corresponding html code, 
    if cannot open browser or not found, return none """   
    print 'qurl = ', qurl

    #Browser
    br = mechanize.Browser()
    
    #Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    
    #Browser options
    br.set_handle_equiv(True)
    #br.set_handel_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    
    #Debugging messages
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)
    
    #User-Agent
    br.addheaders = [('User-agent','Mozilla/5.0')]
    # br.addheaders = [('user-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')]
    try:
        # open url
        response = br.open(qurl)
        
        # get page content
        html = response.read()
        return html
        
    except: # otherwise, return empty data
        return {}

def db_connection():
"""config mysqldb connection"""

    db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost
        user="usr", # your username
        passwd="pwd", # your password
        db="db_name",
        use_unicode=True,
        charset="utf8") # name of the data base
    return db

def write_to_dictionary(file_name):
    db = None
    data = {}
    try:
        db = db_connection()
        cur = db.cursor()
        try:
            with codecs.open(file_name, 'r') as reader:
                for eachline in reader:
                    content = eachline.split(':')[1].split(' ### ')
                    en_kw = content[0].strip()
                    ch_kw = content[1].strip()

                    '''check if the keyword is already in the db to avoid duplication'''
                    query = "SELECT * FROM Dictionary WHERE en_kw='%s'" % (en_kw)
                    cur.execute(query)
                    result = cur.fetchone()
                    if result:
                        pass
                    else:
                        insert_clause = "INSERT INTO Dictionary VALUES (default, %s, %s);" % (k_id,en_kw, ch_kw)
                        try:
                            cur.execute(insert_clause)
                        except Exception as e:
                            print 'error info:', e                        
        except:
            print 'open file eror'
    except:
        print 'database accessing error occurred.'



def translate(keyword):
    """given an English word, find its corresponding Chinese version 
    return all information about this word, including 
    its id, English spelling and Chinese spelling.
    If error or no match result found, return None. """

    db = None
    data={}
    try:
        db = db_connection()
        cur = db.cursor()
        query = "SELECT * FROM Dictionary WHERE en_kw=%s;" % (keyword)
        cur.execute(query)
        result = cur.fetchone()

        if result:
            data['id'] = result[0]
            data['english'] = result[1]
            data['chinese'] = result[2]
    except:
        print 'database accessing error occurred.'

    finally:
        if db:
            db.commit()
            db.close()
        return data

def get_market_trend(keyword,date_start, date_end):
    '''given an product name, begin date and end date, get all supply and demand index from taobao and aliz
    return the data in dictionary form to ease future processing and presenting'''

    db = None
    data= {}
    start_date = date_start
    end_date = date_end

    product = translate(keyword)
    if product:
        try:
            db = db_connection()
            cur = db.cursor()
            query = "SELECT * FROM market_trend WHERE (%s>= %s AND %s<= %s) ORDER BY 'date' ASC;" % ('date','date', start_date, end_date)
            cur.execute(query)
            results = cursor.fetchall()

            if results:    
                data= { 'purchase_index1688': {}, 
                        'purchase_indexTb': {}, 
                        'supply_index': {}, 
                        'date': {},
                        'keyword':{keyword},
                        }

                for row in results: 
                    """check before run if the row[index]/ db design is in right order with this code"""
                    data['purchase_index1688'].append(row[1])
                    data['purchase_indexTb'].append(row[2])
                    data['supply_index'].append(row[3])
                    data['date'].append(row[4])
        except:
            print 'database accessing error occurred.' 
    if db:
        db.commit()
        db.close()
    return data





