#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

# qmail-aliasfilter

# 'qmail-aliasfilter' is a smart filter script for all qmail lovers.
# It filters aliases by the domain part of the senders email address,
# e.g. mail to nospam-.example.com@hostname.localhost will only be delivered to maildir
# if the mail comes from the *.example.com domain, otherwise the mail will be bounced or dropped.

# Here is the example content of the .qmail-nospam-default script inside your home directory (/home/jana):
# |./qmail-aliasfilter.py
# jana

# From now on, you can easily register new accounts or newsletter subscriptions with your 'nospam-...' email address
# e.g. nospam-newsletter.example.com@hostname.localhost for mailings from newsletter.example.com

# Let's see how the wildcard works. Here are some examples:
# (1) nospam-example.com@... -> example.com (the strictest, but also the best way to suppress spam)
# (2) nospam-.example.com@... -> *.example.com (and of course: example.com!)
# (3) nospam-example.@... -> example.*
# (4) nospam-.example.@... -> *.example.* (the loosest way, use only for debugging!)
# (5) nospam-example.com+newsletter.example.org@... -> a combination of the above methods

# Since 2.1 there is also the possibility to use qmail-aliasfilter in combination with maildrop
# Please take a look at the documentation (see @link) if you want to use it.

# @package		qmail-aliasfilter
# @author		originally by wibuni <github@wibuni.de>
# @copyright	Copyright (c) 2011-2012, see the @author tags
# @license		https://www.apache.org/licenses/LICENSE-2.0 Apache License 2.0
# @link			originally at https://github.com/wibuni/qmail-aliasfilter
# @link			https://github.com/panzerfahrer/qmail-aliasfilter
# @link			https://uberspace.de/dokuwiki/cool:qmail-aliasfilter
# @version		2.1.3

# Let's rock it.

import os
import sys
import time
import email

version = '2.1.3'
# see @version

raw_msg = ''.join(sys.stdin.readlines())	
msg = email.message_from_string(raw_msg)
# get the raw message from stdin and create a message object

homedir = os.getenv('HOME')
# the $HOME directory of the user, who uses qmail-aliasfilter

# initializing counters
i = 0
match_found = 0

# Any arguments passed within the call?
try:
	if sys.argv[1] == '--maildrop':
	# If you want to use qmail-aliasfilter inside maildrop, use the --maildrop argument
		redirect_spam_into_maildir = True
	else:
		redirect_spam_into_maildir = False
except:
	# catch exception if there is no argument passed
	redirect_spam_into_maildir = False

try:
	default_alias = os.getenv('DEFAULT')
	# $DEFAULT environment variable locally set by qmail, if there is a '.qmail-default',
	# so $DEFAULT will be the replacement of the 'default'-part of the '.qmail-default' file name,
	# which matches the current recipient address.
	
	if redirect_spam_into_maildir:
		default_alias = msg['X-qmail-default']	
		del msg['X-qmail-default']
	
except:
	default_alias = '$DEFAULT_not_specified'

try:
	sender_address = os.getenv('SENDER')
	# $SENDER environment variable locally set by qmail
except:
	sender_address = '$SENDER_not_specified'

try:
	recipient_address = os.getenv('RECIPIENT')
	# $RECIPIENT environment variable locally set by qmail
except:
	recipient_address = '$RECIPIENT_not_specified'
	


# debug:
# default_alias = 'test.example.com'
# sender_address = 'no-reply@another.subdomain.whatever.test.example.com'
# recipient_address = 'username@hostname.localhost'
# logfile = open('%s/qmail-aliasfilter.log' %homedir, 'a')
# print >> logfile, '[%s] [DEBUG] $DEFAULT = %s' %(time.asctime(), default_alias)
# logfile.close()

sender_hostname = str.split(sender_address, '@')	# strip the local part of the email address
amount_of_dots = str.count(sender_hostname[1], '.')	# counting the dots inside the domain part of the email address
current_alias = str.split(default_alias, '+')		# if you use example (5), we need to split and check each of the aliases

while i <= str.count(default_alias, '+'):
	# there is at least one alias, so the while loop will always be entered
	# if there are more than one alias (usage like example (5) with the plus sign), each alias will be checked

	amount_of_aliasdots = str.count(current_alias[i], '.')	# counting the dots inside the currently checked alias

	if len(str.strip(current_alias[i], '.')) == 0:
		# case: the alias contains only dots; no need to do anything else than logging and rejecting the mail.
		pass
	else:
		# case: see examples (1), (2), (3), (4) for further details
		# let's check if the hostname matches the given alias

		if sender_hostname[1] == current_alias[i]:
			# case (1): nospam-example.com@... -> accepts all incoming mail from example.com
			# nothing more to do
			match_found = match_found+1		# Yeah! We found a match.

		elif (str.find(current_alias[i], '.') == 0) and (str.rfind(current_alias[i], '.') != len(current_alias[i])-1):
			# case (2): nospam-.example.com@... -> accepts all incoming mail from *.example.com
			wildcard_alias = sender_hostname[1]
			for j in xrange(amount_of_aliasdots, amount_of_dots+1):
				# iterate and delete the subdomains until we got exactly as many dots as the alias
				wildcard_alias = str.partition(wildcard_alias, '.')
				wildcard_alias = wildcard_alias[2]
			wildcard_alias = '.'+wildcard_alias
			if wildcard_alias == current_alias[i]:
				match_found = match_found+1	# Yeah! We found a match.

		elif (str.find(current_alias[i], '.') != 0) and (str.rfind(current_alias[i], '.') == len(current_alias[i])-1):
			# case (3): nospam-example.@... -> accepts all incoming mail from example.*
			# we have to strip of the TLD part of the hostname
			wildcard_alias = str.rpartition(sender_hostname[1], '.')
			wildcard_alias = wildcard_alias[0]+wildcard_alias[1]
			if wildcard_alias == current_alias[i]:
				match_found = match_found+1	# Yeah! We found a match.

		elif (str.find(current_alias[i], '.') == 0) and (str.rfind(current_alias[i], '.') == len(current_alias[i])-1):
			# case (4): nospam-.example.@... -> accepts all incoming mail from *.example.*
			wildcard_alias = sender_hostname[1]
			for j in xrange(amount_of_aliasdots, amount_of_dots+1):
				# iterate and delete the subdomains until we got exactly as many dots as the alias
				wildcard_alias = str.partition(wildcard_alias, '.')
				wildcard_alias = wildcard_alias[2]
			wildcard_alias = '.'+wildcard_alias
			# and finally we have to strip of the TLD part of the hostname
			wildcard_alias = str.rpartition(wildcard_alias, '.')
			wildcard_alias = wildcard_alias[0]+wildcard_alias[1]
			if wildcard_alias == current_alias[i]:
				match_found = match_found+1	# Yeah! We found a match.

	i = i+1

if match_found >= 1:
	# the domain part of the senders email address matches the $DEFAULT alias of qmail

	if redirect_spam_into_maildir:
		# Add some identifier headers (to spread qmail-aliasfilter around the world!)
	
		try:
			# and add some identifier headers
			msg.replace_header('X-qmail-aliasfilter-Version', 'qmail-aliasfilter %s' %version)
		except:
			msg.add_header('X-qmail-aliasfilter-Version', 'qmail-aliasfilter %s' %version)
		try:
			msg.replace_header('X-qmail-aliasfilter-Spam-Status', 'No, tests=FROM_HOSTNAME_IN_DEFAULT_ALIAS version=%s' %version)
		except:
			msg.add_header('X-qmail-aliasfilter-Spam-Status', 'No, tests=FROM_HOSTNAME_IN_DEFAULT_ALIAS version=%s' %version)
		
		sys.stdout.writelines(msg.as_string())	# and put message back to stdout
	else:
		# Let's write this into our logfile (we don't need a logfile with the --maildrop argument, because maildrop uses own logfile)
		logfile = open('%s/qmail-aliasfilter.log' %homedir, 'a')
		print >> logfile, '[%s] [Accepted] qmail-aliasfilter accepted an email from \'%s\' to \'%s\'' %(time.asctime(), sender_address, recipient_address)
		logfile.close()

	sys.exit(0)	# everything's fine, let's deliver new mail.
else:
	# Oops, we got an error!
	
	if redirect_spam_into_maildir:
		# Don't drop the message, just add some special spam headers
	
		subj = msg['Subject']	# the original message subject
		del msg['Subject']	# now we replace the message subject
		msg['Subject'] = '[qmail-aliasfiltered] %s' %subj	# with [qmail-aliasfiltered] %Subject
	
		try:
			msg.replace_header('X-qmail-aliasfilter-Version', 'qmail-aliasfilter %s' %version)	# and add some identifier headers
		except:
			msg.add_header('X-qmail-aliasfilter-Version', 'qmail-aliasfilter %s' %version)
		try:
			msg.replace_header('X-qmail-aliasfilter-Spam-Status', 'Yes, tests=FROM_HOSTNAME_NOT_IN_DEFAULT_ALIAS version=%s' %version)
		except:	
			msg.add_header('X-qmail-aliasfilter-Spam-Status', 'Yes, tests=FROM_HOSTNAME_NOT_IN_DEFAULT_ALIAS version=%s' %version)
		try:
			msg.replace_header('X-qmail-aliasfilter-Spam-Flag', 'YES')	# and the Spam-Flag attribute header
		except:
			msg.add_header('X-qmail-aliasfilter-Spam-Flag', 'YES')
		
		sys.stdout.writelines(msg.as_string())	# and put message back to stdout
		sys.exit(0)
	else:
		# Let's write this into our logfile (we don't need a logfile with the --maildrop argument, because maildrop uses own logfile)
		logfile = open('%s/qmail-aliasfilter.log' %homedir, 'a')
		print >> logfile, '[%s] [Rejected] qmail-aliasfilter rejected an email from \'%s\' to \'%s\'' %(time.asctime(), sender_address, recipient_address)
		logfile.close()
		
		#sys.exit(99)	# silently drop message
		sys.exit(100) # or bounce message (hard error) and return message from mailer daemon
		# sys.exit(111) # or reject message temporarily (soft error). not preferable for most spam but for debbuging!

# End of file qmail-aliasfilter.py
# Location: ./qmail-aliasfilter.py
