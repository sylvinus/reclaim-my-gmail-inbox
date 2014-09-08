#!/usr/bin/python

import httplib2

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors
import base64
import email
import random
from lxml.html import fromstring as lxml_from_string
from unidecode import unidecode
import re
import webbrowser


UNSUBSCRIBE_MARKERS = [

  # English
  "unsub",

  # French
  "desinscription", "desinscrire", "desabonner", "desabonnement",
  "ne souhaitez plus", "ne plus recevoir", "cesser de recevoir"

]


def TrashMessage(service, user_id, msg_id):

  try:
    service.users().messages().trash(userId=user_id, id=msg_id).execute()

    return True
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

    print 'Message snippet: %s' % repr(message['snippet'])

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    mime_msg = email.message_from_string(msg_str)

    return mime_msg
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetThread(service, user_id, thread_id):
  """Get a Thread.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    thread_id: The ID of the Thread required.

  Returns:
    Thread with matching ID.
  """
  try:
    thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
    messages = thread['messages']
    print ('thread id: %s - number of messages '
           'in this thread: %d') % (thread['id'], len(messages))
    return thread
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = {"nextPageToken": None}
    messages = []

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                                 pageToken=page_token, maxResults=100).execute()
      messages.extend(response['messages'])

      print "Got %s/%s messages" % (len(messages), response.get("resultSizeEstimate"))

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetMessageSender(message):
  for header in message["payload"]["headers"]:
    if header["name"] == "From":
      return header["value"]


def GetService():

  # Path to the client_secret.json file downloaded from the Developer Console
  CLIENT_SECRET_FILE = 'client_secret.json'

  # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
  OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'

  # Location of the credentials storage file
  STORAGE = Storage('gmail.storage')

  # Start the OAuth flow to retrieve credentials
  flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
  http = httplib2.Http()

  # Try to retrieve credentials from storage or run the flow to generate them
  credentials = STORAGE.get()
  if credentials is None or credentials.invalid:
    credentials = run(flow, STORAGE, http=http)

  # Authorize the httplib2.Http object with our credentials
  http = credentials.authorize(http)

  # Build the Gmail service from discovery
  gmail_service = build('gmail', 'v1', http=http)

  return gmail_service


def ListUnread():

  gmail_service = GetService()

  all_unread_emails = ListMessagesMatchingQuery(gmail_service, "me", "is:unread")
  print
  print "*" * 50
  print "You are starting with exactly %s unread emails. Good luck!" % len(all_unread_emails)
  print

  done_senders = set()
  done_senders_tried = 0

  while done_senders_tried < 50:
    random_msg = random.choice(all_unread_emails)

    message = GetMimeMessage(gmail_service, "me", random_msg["id"])
    sender = message["from"]

    # sender = GetMessageSender(message)
    sender = re.sub("^.*<", "", sender)
    sender = re.sub(">.*?$", "", sender)

    if sender in done_senders:
      done_senders_tried += 1
      continue

    done_senders_tried = 0
    done_senders.add(sender)

    other_messages_from_this_sender = ListMessagesMatchingQuery(gmail_service, "me", "from:%s" % sender)

    print
    print "*" * 50
    print sender
    print repr(message["snippet"])
    if len(other_messages_from_this_sender) > 1:
      other_messages = random.sample(other_messages_from_this_sender, min(10, len(other_messages_from_this_sender)))
      for other_message in other_messages:
        msg = GetMessage(gmail_service, "me", other_message["id"])
        print repr(msg["snippet"])

    trash = raw_input("%s unread messages from %s. Trash them all? [y/N]" % (len(other_messages_from_this_sender), sender))

    if trash == "y":
      for other_message in other_messages_from_this_sender:
        TrashMessage(gmail_service, "me", other_message["id"])
      print "Trashed %s messages. Good riddance!" % len(other_messages_from_this_sender)

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
