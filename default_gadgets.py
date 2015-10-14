#!/usr/bin/python
# -*- coding: utf-8 -*-
# (C) eranroz
#
# Distributed under the terms of the MIT license.

import re
import pywikibot
from pywikibot.exceptions import NoPage
import time

def extract_defaults(wikitext):
	default_re = re.compile('\*\s*([^\|]+?)[\|\[].*default\s*[\|\]]')
	match_lines = [default_re.match(line) for line in wikitext.split('\n')]
	return [m.group(1) for m in match_lines if m]

def family_default_gadgets(family='wikipedia'):
	site = pywikibot.getSite('en', family)
	family_sites = [pywikibot.getSite(lang, family) for lang in site.languages()]
	gadgets_dict = dict()  # key - gadget name, value - wikipedias listi
	print('going over %i wikies'%len(family_sites))
	for wiki_i, wiki in enumerate(family_sites):
		if wiki_i%25==0:
			time.sleep(1)  # sleep between
		print('%i: %s' % (wiki_i, wiki.code))
		gadgets_def = pywikibot.Page(wiki, 'MediaWiki:Gadgets-definition')
		try:
			wikitext = gadgets_def.get()
			default_gadgets = extract_defaults(wikitext)
			for gadget in default_gadgets:
				gadget = gadget.replace('<!--', '').replace('-->', '')
				gadget_item = '[[:%s:%s:MediaWiki:Gadget-%s|%s]]'%(family,wiki.code, gadget, wiki.code)
				if gadget not in gadgets_dict:
					gadgets_dict[gadget] = [ gadget_item ]
				else:
					gadgets_dict[gadget].append( gadget_item )
		except NoPage:
			continue
	output = [('| [[Gadgets/%s|%s]] || %s || %i'%(k, k, ', '.join(v), len(v)), len(v)) for k,v in gadgets_dict.items()]
	output.sort(key=lambda x:-x[1])  # sort by popularity
	output = """Default gadgets in project %s.
{| class="wikitable sortable plainlinks"
! Gadget !! languages !! #
|-
%s
|}
"""%( family, '\n|-\n'.join(map(lambda x:x[0], output)))
	print(output)
	meta_wiki = pywikibot.getSite('en', 'meta')
	meta_page = pywikibot.Page(meta_wiki, 'Gadgets/%s/default'%(family))
	meta_page.put(output, 'Default gadgets in %s'%family)

if __name__ == '__main__':
	families = ['wikipedia', 'wikibooks', 'wiktionary','wikiquote', 'wikinews', 'wikisource', 'wikivoyage', 'wikiversity']
	for fam in families:
		family_default_gadgets(fam)
