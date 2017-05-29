import os
import sys

from alize.log import Log
from alize.exception import *

try :
    from slacker import Slacker
except Exception as e:
    print(str(e))

L = Log("Slack.Library.ALIZE")

class Slack(object):
    def __init__(self, token):
        try:
            self.slack = Slacker(token)
        except Exception as e:
            L.warning(str(e))
            raise SlackError("%s is not exists." % token)

    def message(self, message, channels):
        try:
            result = self.slack.chat.post_message(
                channels,
                message,
                as_user=True)
            if result.successful:
                return result.body
            else:
                L.warning("Slack Error : %s" % result.error)
                raise SlackError(result.error)
        except Exception as e:
            L.warning(str(e))
            raise SlackError("%s is not exists." % channels)


    def upload(self, filepath, channels,
               content=None,
               filetype=None,
               filename=None,
               title=None,
               initial_comment=None):
        try:
            result = self.slack.files.upload(
                filepath,
                content=content,
                filetype=filetype,
                filename=filename,
                title=title,
                initial_comment=initial_comment,
                channels=channels)
            if result.successful:
                return result.body
            else:
                L.warning("Slack Error : %s" % result.error)
                raise SlackError(result.error)
        except Exception as e:
            L.warning(str(e))
            raise SlackError("%s is not exists." % channels)
