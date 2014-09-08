from lxml.html import fromstring as lxml_from_string
from unidecode import unidecode


UNSUBSCRIBE_MARKERS = [

  # English
  "unsub", "blacklist", "opt-out", "opt out", "removealert", "removeme",

  # French
  "desinscription", "desinscrire", "desabonner", "desabonnement",
  "ne souhaitez plus", "ne plus recevoir", "cesser de recevoir",

  # German
  "abbestellen", "abmelden",

  # Spanish
  "borrarse", "cancelar", "anular",

]


def FindUnsubscribeLink(message):

  unsubscribe_link = None
  unsubscribe_links = []

  for part in message.walk():
    if part.get_content_type() == 'text/html':
      html = part.get_payload(decode=True)

      doc = lxml_from_string(html)

      for element, attribute, link, pos in doc.iterlinks():
        link_content = unidecode(element.text_content()).lower()

        unsubscribe_links.append((repr(link_content)[0:100], link[0:100]))
        for pattern in UNSUBSCRIBE_MARKERS:
          if (pattern in link_content) or (pattern in link.lower()):
            unsubscribe_link = link

  return unsubscribe_link, unsubscribe_links
