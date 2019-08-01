import logging
import getpass
from optparse import OptionParser

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

import os, sys



class EchoBot(ClientXMPP):
    
    name = "mk-chat_bot"
    version = "1.0.1"
    designation = "do nothing"
    config="config.txt"
    
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
        1. make the bot do something usefull
        3. may be add some OMEMO?
        2. have fun"""

    sorry_message = f"""
        I'm sorry to inform you, but you
        are not authorized to access this
        function. Try something simpler!"""
    
    bot_cmds = {
        "exit":"stop_bot",
        "restart":"restart_script"
        }
    
    
    def __init__(self, jid, password):
        self.load_config()
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

    def load_config(self, log_level=logging.DEBUG,
                    log_format='%(levelname)-8s %(message)s'):
                    
        logging.basicConfig(level=log_level, format=log_format)

        logging.info("Loading chat bot main configuration...")


        params = {}
        params["masters"] = []
        config_file = open(config)
        for line in config_file:
            line = line.rstrip('\n')
            array = line.split("=",maxsplit=1)
            if len(array) == 2:
                if array[0] == "add_master":
                    logging.info("New master found!")
                    logging.info(array[1])
                    params["masters"] += [array[1]]
                else:
                    # uncommenting this will reveal password to stdout
                    # logging.info('New parameter "' + str(array[0]) + '" is set to "' + str(array[1]) + '"')
                    params[array[0]] = array[1]
        config_file.close()
        '''
        get(key[, default]
        Return the value for key if key is in the dictionary, else default. If default is not given, it defaults to None, so that this method never raises a KeyError.
        '''
        login = params.get("login")
        logging.debug("CONF:\tLogin is set to " + login)
        password = params.get("password")
        # logging.debug("CONF:\tPassword is set to " + password)
        masters = params.get("masters", ["NO MASTER SET!"])
        logging.debug("CONF:\tmasters are set to " + str(masters))

        # check:
        if masters == []: logging.error("MASTER DEVICE NOT SET!!!")

        logging.info("Configuration is loaded.")
        
        
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
            logging.info(
                """
----------------------------
|Received new message!
|From: %(from)s
|Text: %(body)s
----------------------------""" % msg
                )
            
            cmdarray = msg["body"].split(maxsplit=1)
            if len(cmdarray) == 0:
                cmd_source = "ERR: NO COMMAND SOURCE"
                cmd = "ERR: NO COMMAND"
            elif len(cmdarray) == 1:
                if cmdarray[0][0] == "/":
                    cmd_source = cmdarray[0]
                    cmd = "ERR: NO COMMAND"
                else:
                    cmd_source = "ERR: NO COMMAND SOURCE"
                    cmd = cmdarray[0]
            else:
                if cmdarray[0][0] == "/":
                    cmd_source = cmdarray[0]
                    cmd = cmdarray[1]
                else:
                    cmd_source = "ERR: NO COMMAND SOURCE"
                    cmd = msg["body"]
            
            sender = msg['from']
            
            if self.check_cmd_auth(
                    sender, cmd_source, cmd,
                    self.check_master(sender, masters)
                    ) == "true":
                self.run_cmd(msg, cmd_source, cmd)
            else:
                msg.reply(sorry_message).send()

    def check_master(self, sender, masters):
        logging.debug("FUN:\tChecking user ID")
        # sender = msg['from'].split("/",1)[0]
        # print (sender)
        # print (masters)
        if sender in masters:
            return "true"
        else: return "false"
        
    def check_cmd_auth(self, sender="user", cmd_source="NO SOURCE",
                       cmd="NO COMMAND", is_master="false"):
        
        logging.debug("FUN:\tChecking whether user is authorized to run the command")
        master_source = ["/bot"]
        
        logging.debug(f"""
            User: {sender}
            Command source: {cmd_source}
            Command: {cmd}
            Is master: {is_master}""")
        
        if cmd_source not in master_source or is_master=="true":
            logging.info(f"Authorized {sender} to run {cmd_source} {cmd}")
            return "true"
        else:
            logging.info(f"Denied authorization for {sender} to run " +
                "{cmd_source} {cmd}")
            return "false"
        
    def run_cmd(self, msg, source, cmd):
        logging.debug("FUN:\tAttempting to run commmand.")
        if source == "/bot":
            if cmd in self.bot_cmds:
                # now need to decide what is it that I want to run...
                # getattr(x, 'foobar') is equivalent to x.foobar
                # then if I need to get self.$cmd(msg), I do next:
                getattr(self, self.bot_cmds[cmd])(msg)
            else:
                self.cmd_unknown(msg)
        else:
            self.cmd_unknown(msg)
        
    def cmd_unknown(self, msg):
        logging.info("Received gibberish message. " +
                    "Replying with a help file.")
        msg.reply(help_message).send()
        
    def restart_script(self, msg):
        answ = "Received restart message. Restarting now.\n"
        msg.reply(answ).send()
        logging.info(answ)
        self.disconnect(wait=True)
        sys.stdout.flush()
        # in Windows, it at least looks cleaner to open a new console
        # also I had some trouble with ctrl+c without it.
        if os.name == 'nt':
            args = ' '.join(sys.argv)
            os.system('cmd /c start cmd /c' + sys.executable + ' ' + args)
        else:
            os.execl(sys.executable, sys.executable, * sys.argv)
        
        
    def stop_bot(self, msg):
        answ = "Received exit message. Quitting now."
        msg.reply(answ).send()
        logging.info(answ)
        self.disconnect(wait=True)
    

    
# (just in case it was launched as main)
if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = EchoBot(login, password)
    xmpp.connect()
    xmpp.process(block=True)
