
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors
import base64
import email
import httplib2


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

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    mime_msg = email.message_from_string(msg_str)

    return mime_msg, message
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


def ListMessagesMatchingQuery(service, user_id, query='', debug=False):
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
    page_index = 1

    while 'nextPageToken' in response:

      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                                 pageToken=page_token, maxResults=100).execute()
      messages.extend(response['messages'])

      if debug:
        print "Fetched messages %s/%s" % (page_index * 100, response.get("resultSizeEstimate"))

      page_index += 1

      for m in messages:
        yield m

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
