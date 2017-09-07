Tmux-Init
=============

By [@jinfan](https://github.com/jinfan) 


To start Tmux sessions with your configuration inn json format.

Installation
------------

You just need to clone this project and put this dir into your bin path or just copy the tmux_init.py into somewhere under your bin path.

Since this is a python script and the python are required. Most likely, it should be on your osx and linux/unix systems, but not yor windows. so please find a way to install python. Since you are using tmux, i doubt this could be an issue at all.

Usage
-----

* You need to create json files identifying what kind of sessions/windows/panes to be created.

    - each session is one json file
    - in each session file, you can have multiple windows/panes.
    - for each window/pane, you can define the start directory and initial action when the pane created.
    - window can be synchronized. Basically you can have all panes in the window to have the same typing. (see examples/sysadmin.json)
    - session can also be defined as the default session to be loaded, using base_session key.

* then you can run tmux_init.py with options. please use --h to see them in the runtime.

    - Generally, it will search the current path to see if has a specific file (default to .tmux-session.json) or the file you given ( with -f option). If it exists, this session is checked or created and be the current session for your current terminal window.
    - if not exists, it will search the default dir for the json files (in this case, ~/.tmux-session).
    - Since I number my pane/window index from 1, if you are not, please use -s to specify, otherwise the name and index will be messed.
    - If you open more than 3 panes in a window, I always allocate them in the 2nd pane, if you prefer, you can chose a different number.

* How I use it in daily life:

    - I put my default session(s) into each machine under ~/.tmux-session. These sessions will always be created once I login to these machines.
    - Since I am using iTerm2 and I configured a profile for each machine, in each profile, once I login, the first thing (sendkey in Iterm2) is run this script, which will load all my session defined in the ~/.tmux-session.
    - then in some project directory, I have different json files for each project, once I need to do developement for a project, I will goto that dir or a central place to run this script with the -f option and the session will be create/attached.

Issue
-----

Do not run this script inside tmux session, it will create session but put all those panes into current session. I tried but was not able to solve for a while so I gave up:).

Feedback
--------

I have been using this for a while, now I am starting to publish some of the utilities I use to configure my development environment. I have not tested it in all environments, So feeedbacks are appreciated and I will do my best. Thanks!

