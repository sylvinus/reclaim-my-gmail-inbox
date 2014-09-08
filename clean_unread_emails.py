#!/usr/bin/python

import random
import re
import urllib
import webbrowser
from lib.gmail import GetService, ListMessagesMatchingQuery, GetMimeMessage, GetMessage, TrashMessage
from lib.unsubscribe import FindUnsubscribeLink


MIN_EMAILS_FROM_SENDER = 1


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

    # Now ask the user what to do with them!
    trash = None
    while trash in [None, "v"]:
      print
      trash = raw_input("%s total messages from %s. Trash them all? [ [y]es / [v]iew online / [N]o ]" % (len(other_messages_from_this_sender), sender))

      # View it online
      if trash == "v":
        webbrowser.open("https://mail.google.com/mail/u/0/#search/from%%3A%s" % (urllib.quote(sender_email)))

      # Trash them all
      elif trash == "y":
        for other_message in other_messages_from_this_sender:
          TrashMessage(gmail_service, "me", other_message["id"])
        print "Trashed %s messages. Bravo!" % len(other_messages_from_this_sender)

        # Find unsubscribe link if email is HTML
        unsubscribe_link, unsubscribe_links = FindUnsubscribeLink(message)

        if unsubscribe_link:
          print
          unsub = raw_input("%s looks like an unsubcribe link. Do you want to try it in your browser? [y/N]" % (unsubscribe_link[0:100]))
          if unsub == "y":
            webbrowser.open(unsubscribe_link)
        # elif len(unsubscribe_links):
        #   print "Didn't find an unsubscribe link among:"
        #   for link in unsubscribe_links:
        #     print link

  print "Seems like we can't find new senders to clean! Congrats!"

ListUnread()
