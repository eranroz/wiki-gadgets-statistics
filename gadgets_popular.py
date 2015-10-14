#!/usr/bin/python
# -*- coding: utf-8 -*-
# (C) eranroz
#
# Distributed under the terms of the MIT license.! /usr/bin/env python

import datetime
import MySQLdb
import pywikibot

familyGadgets = dict()  # family -> (gadget -> [(lang, users)])

def fillStatsForCluster(host, dbList):
    clusterHost = cluster
    conn = MySQLdb.connect(host=host,
                   read_default_file='~/replica.my.cnf')
    cursor = conn.cursor()
    for db, lang, family in dbList:
        print 'Querying ',db
        if family not in familyGadgets:
            familyGadgets[family] = dict()
        gadgetsDict = familyGadgets[family]
        cursor.execute('USE `%s_p`'%db)
        try:
            cursor.execute('''
    /* gadgets_popular.py SLOW_OK */
    SELECT
    up_property,
    COUNT(*)
    FROM %s_p.user_properties_anon
    WHERE up_property LIKE 'gadget-%%'
    AND up_value = 1
    GROUP BY up_property;
    '''%db)
        except:
            continue
        for row in cursor.fetchall():
            gadgetName = row[0].split('gadget-', 1)[1]
            if gadgetName not in gadgetsDict:
                gadgetsDict[gadgetName]=[]
            langLink = '[[:%s:%s:MediaWiki:%s|%s]]' % (family,lang,row[0], lang)
            count = row[1]
            gadgetsDict[gadgetName].append((langLink,count))
    cursor.close()
    conn.close()


report_template = u'''\
Cross-project gadgets preferences statistics.

'''
report_family_template= u'''
Gagets statistics for %s projects as of %s.
----
{| class="wikitable sortable plainlinks" style="width:85%%; margin:auto;"
|- style="white-space:nowrap;"
! Gadget
! wikis (number of users)
! total number of users
|-
%s
|}
'''

conn = MySQLdb.connect(host='enwiki.labsdb',
                       db='meta_p',
                       read_default_file='~/replica.my.cnf')
cursor = conn.cursor()
cursor.execute('''
		select slice,dbname,lang,family from meta_p.wiki
		where is_closed=0
		and family in ('wikibooks','wikipedia','wiktionary','wikiquote','wikisource','wikinews','wikiversity','wikivoyage')
        and dbname not like 'test%'
''')
servers,dbnames,wikiLangs,wikiFamilies = zip(*cursor.fetchall())
nameToCluster=dict()
for clus, db, lang, family in zip(servers,dbnames,wikiLangs,wikiFamilies):
    if clus not in nameToCluster:
        nameToCluster[clus]=[]
    nameToCluster[clus].append((db,lang,family))

for cluster, wikisMetaData in nameToCluster.iteritems():
    print 'Filling data from cluster ', cluster
    fillStatsForCluster(cluster, wikisMetaData)

report_text = report_template
for family, gadgets in familyGadgets.iteritems():
    gadgetsDetails = [(gadgetName,', '.join([u'%s (%s)'%(link,str(count)) for link, count in langData]), sum([count for link,count in langData])) for gadgetName, langData in gadgets.iteritems()]
    gadgetsDetails.sort(key=lambda x:x[2], reverse=True)
	
    gadgetsInfo = [u'| [[Gadgets/%s]] || %s || %i'%(gadgetName, langData, totalCount) for gadgetName, langData, totalCount in gadgetsDetails]
    family_report = report_family_template % (family, datetime.datetime.now().strftime('%B %Y'), '\n|-\n'.join(gadgetsInfo))
    meta_wiki = pywikibot.getSite('meta', 'meta')
    meta_page = pywikibot.Page(meta_wiki, 'Gadgets/%s'%(family))
    meta_page.put(family_report, 'Update')
    report_text = report_text+'\n'+ family_report
try:
    resFile = file('gadgetsData.wikitext','w')
    print>>resFile,report_text
    resFile.close()
except:
    pass
print report_text
cursor.close()
conn.close()

