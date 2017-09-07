#!/usr/bin/env python


# By Jinfan Duan

# My tmux startup script, reading the configuration from a file and start the
# tmux sessions based on the config file

# Please note this is assume the pane is number start with 1 not zero.
# Otherwise change the global variable

# coding: utf-8
import os
from os import system
import subprocess
import json
import argparse


def border_msg(msg):
    row    = len(msg)
    h      = ''.join(['+'] + ['-' *row] + ['+'])
    result = h + '\n'"|"+msg+"|"'\n' + h
    print(result)

    return

#===========================================================
# Global Variable

# this is the directoy hold all the config json file for sessions. Please note
# that each file is for only one session and only the json format will be
# considered. so if you do not want a session to be loaded. rename to a non-json
# extension will do.
class Config:
    def __init__(self):
        self.config_file        = '.tmux-session.json'
        self.config_dir         = '~/.tmux-session'
        self.tmux_start         = 1
        self.tmux_pane_to_split = 2
        self.base_session       = 'jfdtmx'

#===========================================================
# run tmux command
class Tmux:
    def is_in_tmux(self):
        return 'TMUX' in os.environ

    def cmd(self, command):
        if(command):
            system('tmux %s' % command)

        return

    # run shell command
    def shell(self, command):
        if(command):
            self.cmd('send-keys "%s" "C-m"' % command)

        return

    # change path
    def cd(self, command):
        if(command):
            self.shell("cd %s" % os.path.expanduser(command))

        return

    # see if a session is already there, do not create it if so.
    def has_session(self, name):
        try:
            result=subprocess.check_output(['tmux ls | grep "%s"' % name],
                                           shell=True, stderr=subprocess.STDOUT)
            # print(result)
        except subprocess.CalledProcessError as ex:
            return False

        return not (name not in result)

    def getWinId(self, sessionName, index):
        return  "%s:%s" % (sessionName, str(index+config.tmux_start))

#===========================================================
# main config objects for this script
config = Config()
tmux   = Tmux()
#===========================================================

class Main:
    def __init__(self):
        self.session = config.base_session

    def __call__(self):
        self.parseOpt();
        if (tmux.is_in_tmux()):
            border_msg('You are running in Tmux, please run this in another terminal')
            return

        # 1st check if the file exist in the given path, then load with the
        # config file only.
        if os.path.isfile(os.path.expanduser(config.config_file)):
            self.createSession(os.path.expanduser(config.config_file), False)
        else:
            for file in os.listdir(os.path.expanduser(config.config_dir)):
                if file.endswith(".json"):
                    self.createSession(os.path.join(os.path.expanduser(config.config_dir),
                                                    file), True)

        if(self.session):
            if (tmux.is_in_tmux()):
                border_msg('Session created but not attached')
            else:
                tmux.cmd("select-window -t %s" % tmux.getWinId(self.session, 0))
                tmux.cmd( "-2 attach-session -t %s -d" % self.session)
        else:
            border_msg('No configurations processed')

        return

    def createSession(self, file, isDir):
        with open(file) as json_data:
            c = json.load(json_data)
            # in file based init, use the defined one as the base for the session.
            # if dir based, use the defined only
            if(isDir):
                if(c.get('base_session')):
                    self.session=c.get('name')
            else:
                self.session=c.get('name')

            TmuxSession(c)()

        return

    def parseOpt(self):
        parser = argparse.ArgumentParser(description
                                         ='Initializing the Tmux of your configuration')
        parser.add_argument( '-d', '--dir-session', type=str,
                            help='Directory of the session configurations [default %(default)s]',
                            required=False, default=config.config_dir)
        parser.add_argument( '-f', '--file-session', type=str,
                            help='File of the session configuration [default %(default)s]',
                            required=False, default=config.config_file)
        parser.add_argument( '-b', '--base-session', type=str,
                            help='Default session to be attached [default %(default)s]',
                            required=False, default=config.base_session)
        parser.add_argument('-s', '--tmux-start-number',
                            default=config.tmux_start, type=int,
                            help='The Tmux window/pane start number [default %(default)s]',
                            required=False)
        parser.add_argument('-p', '--tmux-pane-number-to-split',
                            default=config.tmux_pane_to_split, type=int,
                            help='The Tmux pane to have the majority of splitting [default %(default)s]',
                            required=False)

        # get all these args if any.
        args                      = parser.parse_args()
        config.config_dir         = args.dir_session
        config.config_file        = args.file_session
        config.base_session       = args.base_session
        config.tmux_start         = args.tmux_start_number
        config.tmux_pane_to_split = args.tmux_pane_number_to_split

        # print the configurations
        print "The running configuration"
        print config.__dict__

        return

class TmuxSession:
    def __init__(self, s):
        self.name   = s.get('name')
        self.path   = s.get('path')
        self.window = s.get('window')

    def __call__(self):
        if (tmux.has_session(self.name)):
            print("Session [%s] already exists." % self.name)
        else:
            # need to check if it is in tmux, otherwise we need to detach first
            self.createSession()
        return

    def createSession(self):
        # create the session
        print("Create session [%s]" % self.name)
        cmd="-2 new-session -d -s '%s'" % self.name
        if self.path:
            cmd += " -c '%s' " %  os.path.expanduser(self.path)

        tmux.cmd(cmd)

        if(tmux.is_in_tmux()):
            tmux.cmd("switchc -t '%s'" % self.name)

        for i, w in enumerate(self.window):
            # tmux_cd(w.get('path'))
            w_id = tmux.getWinId(self.name, i)
            cmd  = "new-window -t %s" % w_id

            if w.get('path'):
                cmd += " -c '%s' " %  w.get('path')

            if w.get('name'):
                cmd += " -n '%s' " % w.get('name')

            if(i> 0):
                tmux.cmd(cmd)

            if w.get('name'):
                tmux.cmd("rename-window '%s'" % w.get('name'))

            TmuxWindow(w)()

            if w.get('syncpanes', False):
                # :setw synchronize-panes
                tmux.cmd("set-option -w -t %s synchronize-panes on" % w_id)

        return

class TmuxWindow:
    def __init__(self, w) :
        self.config = w

    def __call__(self):
        self.splitWindow()
        self.postAction()
        return

    def splitWindow(self):
        # create panes
        numPanes = len(self.config.get('pane'))
        if numPanes == 3 :
            tmux.cmd ("split-window -h")
            tmux.cmd ("split-window -v")
        elif numPanes == 4 :
            tmux.cmd ("split-window -h")
            tmux.cmd ("split-window -v")
            tmux.cmd ("select-pane -t %s" % str(config.tmux_pane_to_split))
            tmux.cmd ("split-window -h")
        elif numPanes == 5 :
            tmux.cmd ("split-window -h")
            tmux.cmd ("split-window -v")
            tmux.cmd ("select-pane -t %s" % str(config.tmux_pane_to_split))
            tmux.cmd ("split-window -h")
            tmux.cmd ("split-window -h")
        elif numPanes > 5 :
            tmux.cmd ("split-window -h")
            for i in range (2, numPanes) :
                tmux.cmd ("split-window -v")
                tmux.cmd("select-layout main-vertical")
        else :
            tmux.cmd ("split-window -h")

        return

    def postAction(self):
        for i, p in enumerate(self.config.get('pane')):
            tmux.cmd ("select-pane -t %s" % str(i+config.tmux_start))
            tmux.cd(p.get('path'))
            tmux.shell(p.get('action'))

        return

#===========================================================
# main run for this script
if __name__=='__main__':
    Main()()

#===========================================================
