What this does
==============

Starting this project I had 40.000+ unread emails in my gmail inbox. That's a lot. I started missing a couple important emails and decided to take action.

This command-line tool browses through the list of unread emails and tries to delete emails from recurring undesired senders as well as unsubscribing from their mailing lists when possible.

In the end this should help reducing the number of emails you get everyday.

How to install
==============

Follow the first steps of https://developers.google.com/gmail/api/quickstart/quickstart-python and download the client_secret_xxx.json file into this folder as client_secret.json

In "REDIRECT URIS", enter "http://localhost:8080/oauth2callback". Then go to "Consent screen" and choose an email address and enter a product name. You have to wait a few minutes for it to be taken into account.

Install the local dependencies:

```
virtualenv venv
source venv/bin/activate
export CFLAGS=-Qunused-arguments
export CPPFLAGS=-Qunused-arguments
STATIC_DEPS=true pip install -r requirements.txt
```


How to use
==========

Run from your command line:

```
python clean_unread_emails.py
```

You will have a series of prompts asking you for each sender if you want to trash all the emails they ever sent you.

No destructive action will be taken by default, you have to answer "y" for anything to be done.


Sample output
=============

```
*************************************************
SlideShare <donotreply@slidesharemail.com>

u'The world&#39;s largest community for sharing presentations. Start sharing! Hello Sylvain Zimmer!'
u'Combined performance summary of all your uploads. as of 15 Jul, 2013 Total Stats + Weekly change'
u'You have a new follower on SlideShare Hello Sylvain Zimmer, Good news! John Royle has started'
u'Your SlideShare stats from last week as of 09 Feb, 2014 Total Stats + Weekly change Total views 47K +'
u'Your weekly roundup of the best presentations, infographics and documents on SlideShare SlideShare'
u'You have new followers on SlideShare. Stay up-to-date with your network Hello Sylvain, Follow Denis'
u'New posts from your SlideShare network today New content from your network today Hello Sylvain,'
u'You have new followers on SlideShare. Stay up-to-date with your network Hello Sylvain, Good news!'
u'Look back on your year on SlideShare: View your 2013 stats summary. Sylvain Congratulations, Sylvain!'
u'You have new followers on SlideShare. Stay up-to-date with your network Hello Sylvain, Follow Soohyun'

550 total messages from SlideShare <donotreply@slidesharemail.com>. Trash them all? [ [y]es / [v]iew online / [N]o ]y

Trashed 550 messages. Good riddance!

http://slidesharemail.com/wf/click?upn=jezcwfmnhu88p3q140orkr6xzeryg8dh3oygnlzq7mjpkakdegbolfp0mdica looks like an unsubcribe link. Do you want to try it in your browser? [y/N]y

```

TODO
====

 - Compare read/unread ratios
 - More robust unsubscribe link detection
 - Prettier output
 - getopts
