#!/usr/bin/python

# Convert markdown file source files to aa_macro source files

import sys
import os
import re
from aa_macro import *

defs = """
[local tablec bgcolor="#cccccc"]  
[local oddrowc bgcolor="#ffffff"]
[local evenrowc bgcolor="#f4f4f4"]
[local hdrrowc bgcolor="#ffffff"]
[local codecolor 080]
[local c1 [v oddrowc]]  
[local c2 [v evenrowc]]  
[local c 0]  
[style a [split [co],[b]][a [urlencode [parm 1]],[parm 0]]]  
[style ac [local c [inc [v c]]][odd [v c] [v c1]][even [v c] [v c2]]]  
[style ampersand &amp;]  
[style asterisk *]  
[style b [b [b]]]  
[style blockquote <blockquote style="padding-left: 12px; border-left: 3px solid #ccc;">[nl][b][nl]</blockquote>]  
[style br <br>]  
[style codepre {nbsp}{nbsp}{nbsp}{nbsp}]
[style code [split [co],[b]][b {codewrap <pre>[parm 1]</pre>]}[comment parm 0]]  
[style fencecode [split [co],[b]][b [color [v codecolor] <pre>[parm 1]</pre>]][comment parm 0]]  
[style codewrap {nobreak {greyback &nbsp;[color [v codecolor] [b]]&nbsp;}}]  
[style comma [co]]  
[style greyback <span style="background: #dddddd;">[b]</span>]  
[style gt &gt;]  
[style h1 <h1>[b]</h1>]  
[style h2 <h2>[b]</h2>]  
[style h3 <h3>[b]</h2>]  
[style h4 <h4>[b]</h4>]  
[style h5 <h5>[b]</h5>]  
[style h6 <h6>[b]</h6>]  
[style hcell [header [b]]]  
[style hrow [row [v hdrrowc],[b]]]  
[style i [i [b]]]  
[style img [split [co],[b]][img [parm 0],[urlencode [parm 1]]]]  
[style inline [b {codewrap <tt>[b]</tt>}]]  
[style la &lt;]  
[style lb [lb]]  
[style ls [ls]]  
[style lt &lt;]  
[style lparen (]  
[style rparen )]  
[style nbsp &nbsp;]  
[style nobreak <span style="white-space: nowrap;">[b]</span>]  
[style ra &gt;]  
[style rb [rb]]  
[style ol [ol [b]]]  
[style p [p [nl][b][nl]]]  
[style quot &quot;]  
[style row [row {ac},[b]]]  
[style rs [rs]]  
[style table [table style="border-collapse: collapse; border-spacing: 0px; border-width: 1px; border-style: solid;" cellpadding=10 cellspacing=0 border=1 [v tablec]",[b]]]  
[style tcell [cell [b]]]  
[style u [u [b]]]  
[style ul [ul [b]]]  
[style underline _]  
"""

ecape = {	'[':'{lb}',']':'{rb}',
			'{':'{ls}','}':'{rs}',
		}

def fourspacedetect(s):
	det = False
	if s[:4] == '    ':
		det = True
		for c in s:
			if c == ' ':
				pass
			elif c == '*':
				det = False
				break
	return det

def cape(c):
	return ecape.get(c,c)

def escapeForHTML(c):
	if c == '<': return '{lt}'
	if c == '>': return '{gt}'
	return c

def rint(string,err=False,term='\n'):
	if err == True:
		sys.stderr.write(string+term)
	else:
		sys.stdout.write(string+term)

testfilename = "mtmtestfile.html"
canname = 'cannedstyles.txt'

def help():
	rint('()=required, |= "or", []=optional')
	rint('USE: (python|./) martomac.py [-m macroFilename][-c ][-s ][-t ][-p ][-x ]inputFilename[.md] [outputFilename]')
	rint("-c flag suppresses leading default style definitions, supply your own")
	rint("-s flag suppresses blank lines between block elements")
	rint('-t flag creates macro() processed output test file "%s"' % (testfilename))
	rint('-h flag wraps content of "%s" or stdout in basic HTML page' % (testfilename,))
	rint('-x flag suppresses printing filename report')
	rint('-o open default OS X browser on "%s"' % (testfilename,))
	rint('-p flag routes normal output to stdout')
	rint('-l flag strips terminating newlines off of list elements')
	rint('-d flag dumps canned styles to the file "%s" for your reference' % (canname,))
	rint('-m macroFileName prefixes your styles, which can override the built-ins')
	raise SystemExit

github = True
usedefs = True
maketest = False
usestdout = False
noreport = False
lnlstrip = False
wrapper = False
openit = False
whiteline = '\n'
mfilename = ''

argv = []
lookformf = False
for el in sys.argv:
	if el == '-c':
		usedefs = False
	elif el == '-o':
		openit = True
	elif el == '-l':
		lnlstrip = True
	elif el == '-p':
		usestdout = True
	elif el == '-x':
		noreport = True
	elif el == '-s':
		whiteline = ''
	elif el == '-h':
		wrapper = True
	elif el == '-d':
		try:
			fh = open(canname,'w')
			fh.write(defs)
			fh.close()
		except:
			rint('Could not write "%s" file',True)
			help()
	elif el == '-t':
		maketest = True
	elif el == '-m':
		lookformf = True
	else:
		if lookformf == False:
			argv += [el]
		else:
			lookformf = False
			mfilename = el

usemfile = False
if mfilename != '':
	try:
		fh = open(mfilename)
	except:
		rint('Cannot open macro file "%s"' % (mfilename,),True)
		help()
	else:
		fh.close()
		usemfile = True

argc = len(argv)
if argc != 2 and argc != 3:
	rint('Unexpected number of arguments: %d' % (argc-1),True)
	rint('args: %s' % (str(argv[1:])),True)
	help()

ifn = argv[1]

try:
	fh = open(ifn)
except:
	tfn = ifn+'.md'
	try:
		fh = open(tfn)
	except:
		rint('Cannot open input file "%s" or "%s"' % (ifn,tfn),True)
		help()
	else:
		ifn = tfn
fh.close()

if argc == 3:
	ofn = argv[2]
else:
	ofn = ifn.replace('.md','.txt')

if noreport == False:
	rint(' Input File: "%s"' % (ifn,))
	rint('Output File: "%s"' % (ofn,))

if usedefs == False:
	defs = ''

if usemfile == True:
	fh = open(mfilename)
	chunk = fh.read()
	fh.close()
	defs += chunk

# Markdown rules for HTML:
# ------------------------
#	entities do NOT get ampersand replacement outside of code blocks and spans
#	code blocks DO get replacement of ampersands no matter what
#	quotes turn into entities EXCEPT inside HTML tags or when an angle-link is found...
#	...might be able to punt by detecting entity/anglelink if post-this-operation...
#	...and converting quot entities back to quotes inside tags, but bleaugh
#	<> are entities EXCEPT when HTML tag is in use, and...
#	...HTML tags can only occur outside code blocks
# -------------------
def escapeHTML(line):
	return line

o = defs
to = ''
prevline = ''
blankline = False
thispara = ''

# change all underline-style header codes to #-stype header codes:
pline = ''

escBackslash = '6gg7HH8KK8fgh567'
escBTick = 'lkjUYThgfREW'
escAsterisk = 'hCpDo3Rk5EkS7'
escUnderline = 'hY9gTf8RdO1lMjB'
escLSquig = 'rFvtGbyHnuJm'
escRSquig = 'XsWCdEVfRBgT'
escLBrack = '7Y6t5R4e3W'
escRBrack = '9O8i7U6y5T4r'
escLParen = 'tskfuGFHFY'
escRParen = 'HGYJoooiUhjTgR'
escHash = '778hyFRgTcFzA'
escPlus = 'hTTgfdDDerG'
escMinus = 'iJJuGGtFFrDDwer'
escDot = 'zLcImEbWpDqL'
escXMark = 'poiASDlkjEWQ'

liveComma = '6gT8fR9mY5bG'

# Single chars to be ignored within code blocks
# and spans. They only regenerate after macro()
# ---------------------------------------------
def charCleaner(c):
	if   c == '&': c = '{ampersand}'
	elif c == '_': c = '{underline}'
	elif c == '*': c = '{asterisk}'
	elif c == '<': c = '{la}'
	elif c == '>': c = '{ra}'
	elif c == '[': c = '{lb}'
	elif c == ']': c = '{rb}'
	elif c == '(': c = '{lparen}'
	elif c == ')': c = '{rparen}'
	return c

# This sets things up so that the .md will parse successfully,
# which means that stuff that .md escapes has to pass through the
# parser without modification, as well as the link syntax. That is:
#
# 1:`stuff`       -- within backticks
# 2:    stuff,    -- subsequent to four spaces at BOL
# 3:```           -- between lines that 'fence' code with triple backticks
#   stuff
#   ```
# 4: [stuff]      -- the text for the link (not sure about this)
# 5: (stuff)      -- the links themselves
# --------------------------------------------------------------
tripleticker = False # first line enters in non-tripletick on state
def cleanthings(s):	# input is one line
	global tripleticker
	s = escapeHTML(s)
	o = ''
	dex = 0
	toff = False
	inp = False;	inpg = False
	ins = False;	insg = False
	btig = False;
	ttg = False;

	# 4 spaces gates the entire line
	# ------------------------------
	if fourspacedetect(s) == True:	iscg = True
	else:							iscg = False

	# fenced code gates lines between start-of-line ``` signals
	# ---------------------------------------------------------
	triples = False
	if line[:3] == '```':
		triples = True
		if tripleticker == True:	# if on, turn it off BEFORE we process chars
			tripleticker = False
			toff = True

	for c in s:
		dex += 1

		# backticks aren't filtered unless escaped
		# so the gate doesn't lead and lag them
		# we eat them, too, EXCEPT if this is a triple-tick
		# line, in which case, they have to remain
		# for later parsing out of language specs
		# ----------------------------------------
		cston  = False
		cstoff = False
		passthru = True	# generally, we process all characters on every line, unless:::
		if c == '`':
			if btig == False:	# turning on possible backtick code span
				btig = True
				cston = True
				if triples == False:
					passthru = False		# ::: eat single backticks not on tripletick fence lines
			else:				# turning off possible backtick code span
				btig = False
				cstoff = True
				if triples == False:
					passthru = False		# ::: eat single backticks not on tripletick fence lines

		# Square brackets:
		# ----------------
		#	* prior to a link, they are the linked text
		#   * prior to an image, they are the title and alt field content
		# ---------------------------------------------------------------
		if (btig == False and						# squares inside backticks are ignored
			tripleticker == False and				# squares inside tripletick fences are ignored
			iscg == False):							# squares on four-space lines are ignored
			if ins == True: 	insg = True			# insg lags start of squares by one
			if c == '[':   		ins  = True
			elif c == ']':
				ins = False
				insg = False						# insg ends before closing square is processed

		# Parens:
		# -------
		# These contain a link
		# ------------------------------------------------------------------
		if (btig == False and						# parens inside backticks are ignored
			tripleticker == False and				# parens inside tripletick fences are ignored
			iscg == False):							# parens on four-space lines are ignored
			if inp == True: 	inpg = True			# inpg lags start of parens by one
			if c == '(':   		inp  = True
			elif c == ')':
				inp = False
				inpg = False						# inpg ends before closing paren is processed

		# Wrap {inline } around backticks. This
		# wrap happens outside the character check
		# so it will pass through without escaping
		# ----------------------------------------
		if (        triples == False and	# not on triple tick line
			           inpg == False and	# not within parens
			           insg == False and	# not within square brackets
			           iscg == False and	# not on four-space line
			   tripleticker == False):		# not within tripletick fences
			if (btig == True and				# if in backtick zone
				cston == True):					# and it just turned on
				o += '{inline '						# THEN open {inline
			if cstoff == True:					# if it just turned off
				o += '}'							# THEN close {inline ...}

		if (inpg == True or			# if in paren zone, or
			insg == True or			# if in square bracket zone, or
			iscg == True or			# if on four-space line, or
			btig == True or 		# if within backticks, or
			tripleticker == True):	# if within triple-tick fences
			c = charCleaner(c)			# THEN escape:   &_*<>[]()

		# Although markdown provides escapes for {}, it is unclear why
		# ------------------------------------------------------------
		if c == '{':	c = '{ls}'	# escape { -- these must pass through, period
		elif c == '}':	c = '{rs}'	# escape }

		if passthru == True:		# if we're not eating this character or replacement:
			o += c						# THEN add it to the output

	# turn on code filter mode AFTER we process chars
	if (line[:3] == '```' and			# if tripletick line
			toff == False and			# and if we didn't turn off tripleticks already
			tripleticker == False): 	# and if it's off right now
				tripleticker = True			# THEN turn it on
	return o

# This runs very first thing
# --------------------------
def smartEscape(line):
	global escUnderline
	global escAsterisk
	global liveComma
	global escLParen
	global escRParen
	global escLBrack
	global escRBrack
	global escLSquig
	global escRSquig
	global escXMark
	global escBackslash
	global escHash
	global escBTick
	global escPlus
	global escMinus
	global escDot

	# An escaped character means that .md does not see it. The
	# question remaining at this time is, what does a backslash
	# escape mean within the context of a code block? Find out. TODO
	# ---------------------------------------------------------
	line = line.replace(r'\#',escHash)
	line = line.replace(r'\_',escUnderline)
	line = line.replace(r'\*',escAsterisk)
	line = line.replace(r'\(',escLParen)

	line = line.replace(r'\]',escRBrack)
	line = line.replace(r'\[',escLBrack)

	line = line.replace(r'\}',escRSquig)
	line = line.replace(r'\{',escLSquig)

	line = line.replace(r'}',escRSquig)
	line = line.replace(r'{',escLSquig)

	line = line.replace(r'\)',escRParen)
	line = line.replace(r'\(',escLParen)

	line = line.replace(r'\\',escBackslash)
	line = line.replace(r'\+',escPlus)
	line = line.replace(r'\-',escMinus)
	line = line.replace(r'\.',escDot)
	line = line.replace(r'\!',escXMark)
	line = line.replace(r'\`',escBTick)
	line = line.replace(r',',liveComma) # commas mean nothing to .md, but they mean something to mac

	line = line.replace('\t','    ')
	
	line = cleanthings(line)
	return line

# This runs after md --> mac, but prior to mac --> HTML
# -----------------------------------------------------
def smartUnEscape(s):
	global escUnderline
	global escPlus
	global escMinus
	global escDot
	global escAsterisk
	global liveComma
	global escLParen
	global escRParen
	global escLBrack
	global escRBrack
	global escLSquig
	global escBackslash
	global escRSquig
	global escXMark
	global escHash
	global escBTick
	s = s.replace(escHash,'#')
	s = s.replace(escXMark,'!')
	s = s.replace(escUnderline,	'_')
	s = s.replace(escAsterisk,	'*')
	s = s.replace(liveComma,	'{comma}')
	s = s.replace(escLParen,	'(')
	s = s.replace(escRParen,	')')
	s = s.replace(escLBrack,	'{lb}')
	s = s.replace(escRBrack,	'{rb}')
	s = s.replace(escLSquig,	'{ls}')
	s = s.replace(escRSquig,	'{rs}')
	s = s.replace(escBTick,		'`')
	s = s.replace(escBackslash, '\\')
	s = s.replace(escPlus, '+')
	s = s.replace(escMinus, '-')
	s = s.replace(escDot, '.')
	return s

ysource = []
lc = 0
try:
	ifh = open(ifn)
except:
	rint('Could not open input file "%s"' % (ifn,),True)
	help()
else:
	try:
		for line in ifh:
			lc += 1
 			try:
				line = smartEscape(line)
			except Exception,e:
				rint('blew up %s' % str(e),True)
			ysource += [line]
	except:
		rint('Could not read input file "%s" (%d lines read)' % (ifn,lc),True)
		try:
			ifh.close()
		except:
			rint('Could not close input file "%s"' % (ifn,),True)
		help()
	else:
		try:
			ifh.close()
		except:
			rint('Could not close input file "%s"' % (ifn,),True)
			help()



xsource = []
tflag = -1
killkey = 'jncfvs8jn2247y8fajn0'
for line in ysource:
	if line[:3] == '---': # this can also indicate a table header/body interspersal
		if github == True:	# then we can look for tables
			if line.find(' | ') > 0:	# we throw out table header-body lines as unneeded
				line = killkey
				xsource += [pline]
			else:
				line = '# ' + pline	# convert setex style to atx title line
				pline = ''
		else:	# not github, just do titles
			line = '# ' + pline # title line
			pline = ''
	elif line[0] == '=':
		line = '## ' + pline		# convert setex style to atx title line
		pline = ''
	else:
		if pline != killkey:
			xsource += [pline]
	pline = line

xsource += [pline]
xsource += ['\n']

# Escape all the characters that drive macro():
# ---------------------------------------------
source = []
tmode = -1
pipekey = 'nMbVc4GhItR'
prctkey = 'uHyGt9FrDeS'
for line in xsource:
	droptag = ''
	floptag = ''
	if github == True and line.find(' | ') > 0:
		tline = ''
		line = line.replace(r'\|',pipekey) 	# bury any escaped |'s
		line = line.replace(',','{comma}')	# intern commas -- we use 'em
		if tmode == -1: # header row?
			celltype = 'hcell'
			rowtype = 'hrow'
			tmode += 1	# now zero
			tline += '{table '
		else: # normal row
			celltype = 'tcell'
			rowtype = 'row'
			tmode += 1	# first line is #1 -- can pass out counter later
		celllist = line.split('|')
		tline += '{%s ' % (rowtype,)
		for cell in celllist:
			cell = cell.replace('%',prctkey)	# bury any existing %'s
			cell = cell.strip()
			asm = '{%s '+cell+'}'
			asm = asm % (celltype,)
			asm = asm.replace(prctkey,'%')		# restore % signs
			asm = asm.replace(pipekey,r'\|')	# restore escaped |'s
			tline += asm # add the cell to the line
		tline += '}' # close the row
		line = tline
	else:
		if tmode != -1: 	# were we in a table?
			tmode = -1		# then bail
			floptag += '}\n'	# close the table

	if floptag != '':
		source[-1] = source[-1] + floptag
		source += ['\n']
	source += [line]

OUTSTATE  = 0
PARASTATE = 1
QUOTESTATE = 2
BOLDSTATE = 3
ITALICSTATE = 4
UNDERLINESTATE = 5
CODESTATE = 6

# parser for header-converted lines
# ---------------------------------	
pstate = OUTSTATE
qstate = OUTSTATE
bstate = OUTSTATE
istate = OUTSTATE
ustate = OUTSTATE
cstate = OUTSTATE
wl = whiteline

urldex = 1
verbdex = 1
urlcode  = '8gYfTdRsE4'
verbcode = '3cDvFbGnH9'
urlstash = {}
verbstash = {}

tabsize = 4

fiin = False
fbin = False

def emphasis(s):
	global fiin
	global fbin
	bcmd = '7rfmnKIgf'
	icmd = '9jtGVfrDC'
	s = s.replace('**',bcmd)
	s = s.replace('__',bcmd)
	s = s.replace('*',icmd)
	s = s.replace('_',icmd)
	run = True
	while run == True:
		run = False
		if s.find(bcmd) != -1:
			run = True
			if fbin == False:
				fbin = True
				s = s.replace(bcmd,'{b ',1)
			else:
				fbin = False
				s = s.replace(bcmd,'}',1)
	run = True
	while run == True:
		run = False
		if s.find(icmd) != -1:
			run = True
			if fiin == False:
				fiin = True
				s = s.replace(icmd,'{i ',1)
			else:
				fiin = False
				s = s.replace(icmd,'}',1)
	return s

def oemphasis(s):
	reject = r'([^\s\n\t])' # anything but a space, tab or return

	if 1:
		pat = r'([^\\])\*\*' + reject	# leading **
		repl = r'\1{b \2'
		s = re.sub(pat,repl,s)

	if 1:
		pat = r'([^\\])\_\_' + reject	# leading __
		repl = r'\1{b \2'
		s = re.sub(pat,repl,s)

	if 1:
		pat = reject + r'\*\*'	# trailing **
		repl = r'\1}'
		s = re.sub(pat,repl,s)

	if 1:
		pat = reject + r'\_\_'	# trailing __
		repl = r'\1}'
		s = re.sub(pat,repl,s)

	if 1:
		pat = reject + r'\*'	# trailing *
		repl = r'\1}'
		s = re.sub(pat,repl,s)

	if 1:
		pat = reject + r'\_'	# trailing _
		repl = r'\1}'
		s = re.sub(pat,repl,s)
	if 1:
		pat = r'([^\\])\*' + reject	# leading *
		repl = r'\1{i \2'
		s = re.sub(pat,repl,s)

	if 1:
		pat = r'([^\\])\_' + reject	# leading _
		repl = r'\1{i \2'
		s = re.sub(pat,repl,s)

	return s

def checklist(line):
	tabsize = 4
	depth = 0
	mstring = ''
	listtype = None
	listmode = False
	ll = len(line)
	for i in range(0,ll):
		c = line[i]
		if c == ' ':
			depth += 1
		elif c == '\t':
			depth += tabsize
		elif c >= '0' and c <= '9':
			if line[i+1:i+3] == ') ':
				listmode = True
				listtype = 0
				mstring = c+') '
				break
		elif line[i:i+2] == '* ':
			listmode = True
			listtype = 1
			mstring = '* '
			break
		else:
			break
	return listmode,listtype,depth,mstring

def makelists(lstack):
	global lnlstrip
	lmode = -1
	lo = ''
	deep = 0
	depth = -1
	for lel in lstack:
		ltype = lel[0]
		lline = lel[1]
		ldepth= lel[2]
		lline = lline.replace(',','{comma}')
		lline = lline.lstrip()
		if lnlstrip == True:
			lline = lline.rstrip()
		if ldepth > depth:		# new list, deeper
			deep += 1
			lbreak = ''
			if deep > 1:
				lbreak = '\n'
			if ltype == 0:	lo += lbreak+'{ol ' + lline
			else:			lo += lbreak+'{ul ' + lline
		elif ldepth < depth:	# previous list, shallower
			lo += '}\n'
			deep -= 1
			lo += ','+lline
		else:					# same list
			lo += ','+lline
		depth = ldepth
	while deep > 0:
		lo += '}\n'
		deep -= 1
	return lo

def inlinecode(line):
	state = 0
	oline = ''
	trigger = 0
	ll = len(line)
	for i in range(0,ll):
		c = line[i]
		if state == 0: # not inside backticks
			if line[i:i+2] == r' `':
				trigger = 1
				oline += c
			elif c == r'`' and trigger == 1:
				trigger = 0
				oline += '{inline '
				state = 1
			else:
				trigger = 0
				oline += c
		else:			# inside backticks
			if c == r'`':
				oline += '}'
				state = 0
			else:
				c = escapeForHTML(c)
				oline += c
	return oline

def fourspacecode(line):
	consume = False
	if fourspacedetect(line) == True:
		line = line.replace('    ','{codepre}',1)
		line = '{inline '+line.rstrip()+'}\n'
		consume = True
	return consume,line

listmode = False
liststack = []
lastline4space = False

for line in source:
	llen = len(line)
	blankline = False
	consume = False
	breakpara = False
	if line.strip() == '':	# detect blank lines -- they terminate paras, quotes if open
		blankline = True
		lastline4space = False
		line = ''
	else:					# this is not a blank line
		if cstate == OUTSTATE:
			line = line.replace('  \n','{br}\n')	# auto-append line breaks
		else:
			if line[:3] != '```':
				line = '{codepre}'+line

		c,line = fourspacecode(line)
		if c == True:					# this is a fourspace line
			if lastline4space != False:	# if the previous line wasn't a fourspace, we break paras
				line = '{br}'+line
			lastline4space = True		# indicate last line state (not used again in this loop)
		else:
			lastline4space = False		# indicate last line state (not used again in this loop)

		# Handle headers
		for i in range(6,0,-1):
			if line[:i] == '#' * i:
				hc = line[i:].strip()
				h = '\n{h%d %s}\n%s' % (i,hc,wl)
				line = h
				consume = True

		if line[:2] == '> ':						# init or continue quote state
			if qstate != QUOTESTATE:
				qstate = QUOTESTATE
				line = '{blockquote %s' % (line[2:],)
				consume = True
				breakpara = True

		if github == True:		
			if line[:3] == '```':
				blankline = True
				if cstate == OUTSTATE:
					cstate = CODESTATE
					lang = line.rstrip()[3:]
					if lang == '':
						lang = 'raw'
					line = '{fencecode %s,' % (lang,)
					consume = True
					breakpara = True
				else:
					cstate = OUTSTATE
					line = '}\n'

	# Tables cannot signal begin para or quote
	# ----------------------------------------
	if line.find('{row ') >= 0:
		consume = True

	# list processing:
	# ----------------
	lmode,ltype,depth,mstring = checklist(line)
	if listmode == False:		# IF not presently in list mode
		if lmode == True:		#     IF we need to switch to list mode
			listmode = True
			line = line.replace(mstring,'',1)
			liststack += [[ltype,line,depth]]
			line = ''
			blankline = True
	else:						# ELSE already in list mode
		if lmode == True:		#    IF still in list mode
			line = line.replace(mstring,'',1)
			liststack += [[ltype,line,depth]]
			line = ''
			blankline = True
		else:					#    ELSE in, but may need to get out
			if blankline != True:
				tmp = liststack[-1]			# Get current list element
				ltype,txt,dep = tmp			# unpack
				txt = txt + line			# append the current line
				tmp = [ltype,txt,dep]		# repack
				liststack[-1] = tmp			# replace list element
				line = ''					# line consumed in list
				blankline = True			# don't process this (consume?)
			else:	# we're done
				o += makelists(liststack)
				liststack = []
				listmode = False

	line = emphasis(line)

	# Cannot trip paras when...
	#	1) table is in scope
	#   2) fenced code is in scope because uses <pre></pre>
	# -----------------------------------------------------
	if consume == False:
		if blankline == False:
			if cstate == OUTSTATE:
				if qstate == OUTSTATE:
					if pstate != PARASTATE:
						pstate = PARASTATE
						line = '{p %s' % (line,)

	if pstate == PARASTATE:
		# Paragraphs end when...
		#	1) four-space code is initiated
		#	2) a blank line is encountered
		# --------------------------------------------------------------
		if (breakpara == True or
			blankline == True):
			pstate = OUTSTATE
			if o[-1] == '\n':
				o = o[:-1]
			line += '}\n%s' % (wl,) # close para

	if qstate == QUOTESTATE:
		# Quotes end when...
		#	a blank line is encountered
		# --------------------------------------------------------------
		if (blankline == True):
			qstate = OUTSTATE
			if o[-1] == '\n':
				o = o[:-1]
			line += '}\n%s' % (wl,) # close quote

	# look for images:
	tl = ''
	escape = False
	imagestate = 0
	linkstate = 0
	verbiagestate = 0
	verb = ''
	url = ''
	for c in line:
		if 1:
			if 1:
				if c == '!':	# image introducer?
					imagestate = 1
				elif c == '[':	# verbiage introducer?
					verb = ''
					verbiagestate = 1
				elif c == ']':	# done with verbiage?
					verbiagestate = 0
				elif c == '(':	# url introducer?
					url = ''
					linkstate = 1
				elif c == ')':	# done with url?
					if url == '': # apparently, just some hanging parens
						tl += '()' # throw em back like the dead fish they are
						imagestate = 0
						linkstate = 0
					else:
						vcode = '%s%d' % (verbcode,verbdex)
						ucode = '%s%d' % (urlcode,urldex)
						verbdex += 1
						urldex += 1
						urlstash[ucode] = url
						verbstash[vcode] = verb
						if imagestate == 1:	# was this an image?
							tl += '{img %s,%s}' % (vcode,ucode)
						else:				# nope, hadda be a link
							tl += '{a %s,%s}' % (vcode,ucode)
						imagestate = 0
						linkstate = 0
				else:	# incoming!
					if linkstate == 1:
						url += c
					elif verbiagestate == 1:
						verb += c
					else:						# it's just a character
						tl += c
		line = tl

	o += line

if fiin == True:
	o += '}'
if fbin == True:
	o += '}'

# Every line read; close any open states
if cstate == CODESTATE:
	if o[-1] == '\n':
		o = o[:-1]
	o += '}\n'
	
if qstate == QUOTESTATE:
	if o[-1] == '\n':
		o = o[:-1]
	o += '}\n'

if pstate == PARASTATE:
	if o[-1] == '\n':
		o = o[:-1]
	o += '}\n'

# Here, we replace raw URLs that are floating around the document:
# ----------------------------------------------------------------
pat = r'([hH][tT][tT][pP]\:\/\/.*?)\s'
repl = '{a \\1,\\1} '
o = re.sub(pat,repl,o)

# Then we replace the url and verb codes with the actual urls and verbs
# ---------------------------------------------------------------------
for key in verbstash.keys():
	o = o.replace(key,verbstash[key])
for key in urlstash.keys():
	o = o.replace(key,urlstash[key])

# restore escaped characters
o = smartUnEscape(o)

if wrapper == True:
	o = """<HTML>
<HEAD>
<TITLE>macro() HTML test output page</TITLE>
</HEAD>
<BODY>
%s
</BODY>
</HTML>
""" % (o,)

if usestdout == True:
	rint(o)
else:
	ok = True
	try:
		ofh = open(ofn,'w')
	except:
		rint('Cannot open output file "%s"' % (ifn,),True)
		help()

	try:
		ofh.write(o)
	except:
		rint('ERROR: Could not complete write to "%s"' % (ofn,),True)
		ok = False
	try:
		ofh.close()
	except:
		rint('ERROR: Could not close "%s"' % (ofn,),True)
		ok = False

if maketest == True:
	mod = macro()
	oo = mod.do(o)
	ok = True
	try:
		fh = open(testfilename,'w')
	except:
		rint('ERROR: Could not open "%s"' % (testfilename,),True)
		ok = False
	else:
		try:
			fh.write(oo)
		except:
			rint('ERROR: Could not complete write to "%s"' % (testfilename,),True)
			ok = False
		try:
			fh.close()
		except:
			rint('ERROR: Could not close "%s"' % (tetsfilename,),True)
			ok = False
		if ok == True:
			if openit == True:
				cmd = 'open %s' % (testfilename)
				os.system(cmd)
