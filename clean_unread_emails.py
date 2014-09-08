#!/usr/bin/python

import random
from lxml.html import fromstring as lxml_from_string
from unidecode import unidecode
import re
import urllib
import webbrowser
from lib.gmail import GetService, ListMessagesMatchingQuery, GetMimeMessage, GetMessage, TrashMessage


UNSUBSCRIBE_MARKERS = [

  # English
  "unsub",

  # French
  "desinscription", "desinscrire", "desabonner", "desabonnement",
  "ne souhaitez plus", "ne plus recevoir", "cesser de recevoir"

]

MIN_EMAILS_FROM_SENDER = 10


def ListUnread():

  gmail_service = GetService()

  done_senders = set()

  # List unread messages ordered by date desc
  for message in ListMessagesMatchingQuery(gmail_service, "me", "is:unread", debug=True):

    # Get more info about the message
    message, gmail_message = GetMimeMessage(gmail_service, "me", message["id"])
    sender = message["from"]

    sender_email = re.sub("^.*<", "", sender)
    sender_email = re.sub(">.*?$", "", sender_email)

    if sender_email in done_senders:
      continue

    done_senders.add(sender_email)

    other_messages_from_this_sender = list(ListMessagesMatchingQuery(gmail_service, "me", "from:%s" % sender_email))

    # Not enough emails to care about this sender.
    if MIN_EMAILS_FROM_SENDER and len(other_messages_from_this_sender) < MIN_EMAILS_FROM_SENDER:
      continue

    print
    print "*" * 50
    print sender
    print repr(gmail_message["snippet"])
    if len(other_messages_from_this_sender) > 1:
      other_messages = random.sample(other_messages_from_this_sender, min(10, len(other_messages_from_this_sender)))
      for other_message in other_messages:
        msg = GetMessage(gmail_service, "me", other_message["id"])
        print repr(msg["snippet"])

    trash = None
    while trash in [None, "v"]:
      trash = raw_input("%s total messages from %s. Trash them all? [ [y]es / [v]iew online / [N]o ]" % (len(other_messages_from_this_sender), sender))

      if trash == "y":
        for other_message in other_messages_from_this_sender:
          TrashMessage(gmail_service, "me", other_message["id"])
        print "Trashed %s messages. Good riddance!" % len(other_messages_from_this_sender)
      elif trash == "v":
        webbrowser.open("https://mail.google.com/mail/u/0/#search/from%%3A%s" % (urllib.quote(sender_email)))

    # Find unsubscribe link if email is HTML
    unsubscribe_link = None
    unsubscribe_links = []

    for part in message.walk():
      if part.get_content_type() == 'text/html':
        html = part.get_payload(decode=True)

        doc = lxml_from_string(html)

        for element, attribute, link, pos in doc.iterlinks():
          link_content = unidecode(element.text_content()).lower()
          link = link.lower()

          unsubscribe_links.append((repr(link_content)[0:100], link[0:100]))
          for pattern in UNSUBSCRIBE_MARKERS:
            if (pattern in link_content) or (pattern in link):
              unsubscribe_link = link

    if unsubscribe_link:
      unsub = raw_input("%s looks like an unsubcribe link. Do you want to try it in your browser? [y/N]" % (unsubscribe_link[0:100]))
      if unsub == "y":
        webbrowser.open(unsubscribe_link)
    # elif len(unsubscribe_links):
    #   print "Didn't find an unsubscribe link among:"
    #   for link in unsubscribe_links:
    #     print link

  print "Seems like we can't find new senders to clean! Congrats!"

ListUnread()
