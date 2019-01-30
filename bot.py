import logging
import getpass
from optparse import OptionParser

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

import os, sys



name = "mk-chat_bot"
version = "0.0.5"
designation = "do nothing"
master = "musickiller@dismail.de"


help_message = f"""
Hello, this is {name}@{version}.

Designed, designated and tasked to {designation}.

Posible uses include:

/help -- view this help message

/bot exit -- Shutdown
    connection, and quit the program.
    
/bot restart -- restart the bot.
    Yes, you can edit the code,
    issue restart and continue 
    doing all the stuff with
    a minimal downtime!

TODO:
0. MAKE ID CHECK ASAP!!
1. make helpfile using optparse?
2. have fun
"""


class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        logging.info("Ready to receive messages!")
        
        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            # print ("Received message from %(from)s" % msg)
            # print (msg['body'])
            logging.info("Received new message!\n\
                From: %(from)s\n\
                Text: %(body)s" % msg
                )
            
            if msg['body'] == '/bot exit':
                if msg['from'[:len(master)]] == master:
                    msg.reply("Received exit message. Quitting now.").send()
                    logging.info("Received exit message. Quitting now.")
                    self.disconnect(wait=True)
                else:
                    logging.warning("Received exit message from\
                        an unauthorized user!")
                    msg.reply("Sorry, but you are not authorized.").send()
            elif msg['body'] == '/bot restart':
                if msg['from'[:len(master)]] == master:
                    answ = "Received restart message. Restarting now."
                    msg.reply(answ).send()
                    logging.info(answ)
                    self.disconnect(wait=True)
                    os.execl(sys.executable, sys.executable, * sys.argv)
                else:
                    sender = msg['from'[:len(master)]]
                    logging.warning("Received restart message from " +
                        "an unauthorized user!")
                    msg.reply(f"Sorry, but you are not authorized.\n" +
                        f"You are {sender},\n" +
                        f"You have to be {master}").send()
            else:
                logging.info("Received gibberish message." +
                    "Replying with a help file.")
                msg.reply(help_message).send()


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')


    xmpp = EchoBot(xmpp_login, getpass.getpass())
    xmpp.connect()
    xmpp.process(block=True)
