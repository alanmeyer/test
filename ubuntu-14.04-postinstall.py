#!/usr/bin/env python
# Alan Meyer
# https://github.com/alanmeyer/test
#
# Based on work from http://www.nicolargo.com
# Distributed under the GPL version 3 license
#

"""
Post linux installation script
"""

import os
import sys
import platform
import getopt
import shutil
import logging
import getpass
import ConfigParser

# Global variables
#-----------------------------------------------------------------------------

# Change these values based on your project location
_GIT_USER       = "alanmeyer"
_GIT_PROJECT    = "test"
_GIT_FILE       = "ubuntu-14.04-postinstall"
_GIT_BRANCH     = "master"

# Change these based on your server
_OS_VERSION     = "trusty"
_IP             = '192.3.22.147'



# Generated based on user config
_GIT_PREFIX     = "https://raw.github.com/"
_SLASH          = "/"
_GIT_SUFFIX     = _GIT_USER + _SLASH + _GIT_PROJECT + _SLASH + _GIT_BRANCH + _SLASH + _GIT_FILE + ".cfg"
_LOG_FILE       = _GIT_FILE + ".log"
_CONF_FILE      = _GIT_PREFIX + _GIT_SUFFIX

_VERSION        = "0.01.AM"
_DEBUG          = 1

# System commands
#-----------------------------------------------------------------------------

_NO_FRONTEND    = "DEBIAN_FRONTEND=noninteractive "
_APT_GET        = "apt-get "
_FORCE_YES      = "-y --force-yes --allow-unauthenticated "
_PKG_OPTIONS    = "-o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\" "
_APT_GET_OPTS   = _NO_FRONTEND + _APT_GET + _FORCE_YES + _PKG_OPTIONS
_APT_REMOVE     = _APT_GET_OPTS + "-f remove"
_APT_INSTALL    = _APT_GET_OPTS + "-f install"
_APT_UPDATE     = _APT_GET_OPTS + "   update"
_APT_UPGRADE    = _APT_GET_OPTS + "   upgrade"
_APT_ADD        = "add-apt-repository -y"
_APT_KEY        = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys"
_USER_ADD       = "adduser --disabled-password --gecos \"\""
_USER_ADD_SUDO  = "adduser --disabled-password --gecos \"\" --group sudo"
_WGET           = "wget"

# Classes
#-----------------------------------------------------------------------------


class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ORANGE = '\033[93m'
    NO = '\033[0m'

    def disable(self):
        self.RED = ''
        self.GREEN = ''
        self.BLUE = ''
        self.ORANGE = ''
        self.NO = ''

# Functions
#-----------------------------------------------------------------------------


def init():
    """
    Init the script
    """
    # Globals variables
    global _VERSION
    global _DEBUG

    # Set the log configuration
    logging.basicConfig( \
        filename=_LOG_FILE, \
        level=logging.DEBUG, \
        format='%(asctime)s %(levelname)s - %(message)s', \
         datefmt='%d/%m/%Y %H:%M:%S', \
     )


def syntax():
    """
    Print the script syntax
    """
    print "Post installation script version %s" % _VERSION
    print ""
    print "Syntax: python " + (__file__) + " [-c cfgfile] [-h] [-v]"
    print "  -c cfgfile: Use the cfgfile instead of the default one"
    print "  -h        : Print the syntax and exit"
    print "  -v        : Print the version and exit"
    print ""
    print "Examples:"
    print ""
    print " # " + (__file__)
    print " > Run the script with the default configuration file"
    print "   %s" % _CONF_FILE
    print ""
    print " # " + (__file__) + " -c ./myconf.cfg"
    print " > Run the script with the ./myconf.cfg file"
    print ""
    print " # " + (__file__) + " -c http://mysite.com/myconf.cfg"
    print " > Run the script with the http://mysite.com/myconf.cfg configuration file"
    print ""


def version():
    """
    Print the script version
    """
    sys.stdout.write("Script version %s" % _VERSION)
    sys.stdout.write(" (running on %s %s)\n" % (platform.system(), platform.machine()))


def isroot():
    """
    Check if the user is root
    Return TRUE if user is root
    """
    return (os.geteuid() == 0)


def showexec(description, command, exitonerror = 0, presskey = 0, waitmessage = ""):
    """
    Exec a system command with a pretty status display (Running / Ok / Warning / Error)
    By default (exitcode=0), the function did not exit if the command failed
    """

    if _DEBUG:
        logging.debug("%s" % description)
        logging.debug("%s" % command)

    # Wait message
    if (waitmessage == ""):
        waitmessage = description

    # Manage very long description
    if (len(waitmessage) > 65):
        waitmessage = waitmessage[0:65] + "..."
    if (len(description) > 65):
        description = description[0:65] + "..."

    # Display the command
    if (presskey == 1):
        status = "[ ENTER ]"
    else:    
        status = "[Running]"
    statuscolor = colors.BLUE
    sys.stdout.write (colors.NO + "%s" % waitmessage + statuscolor + "%s" % status.rjust(79-len(waitmessage)) + colors.NO)
    sys.stdout.flush()

    # Wait keypressed (optionnal)
    if (presskey == 1):
        try:
            input = raw_input
        except: 
            pass
        raw_input()

    # Run the command
    returncode = os.system ("/bin/sh -c \"%s\" >> /dev/null 2>&1" % command)
    
    # Display the result
    if ((returncode == 0) or (returncode == 25600)):
        status = "[  OK   ]"
        statuscolor = colors.GREEN
    else:
        if exitonerror == 0:
            status = "[Warning]"
            statuscolor = colors.ORANGE
        else:
            status = "[ Error ]"
            statuscolor = colors.RED

    sys.stdout.write (colors.NO + "\r%s" % description + statuscolor + "%s\n" % status.rjust(79-len(description)) + colors.NO)

    if _DEBUG: 
        logging.debug ("Returncode = %d" % returncode)

    # Stop the program if returncode and exitonerror != 0
    if ((returncode != 0) & (exitonerror != 0)):
        if _DEBUG: 
            logging.debug ("Forced to quit")
        exit(exitonerror)


def getpassword(description = ""):
    """
    Read password (with confirmation)
    """
    if (description != ""): 
        sys.stdout.write ("%s\n" % description)
        
    password1 = getpass.getpass("Password: ");
    password2 = getpass.getpass("Password (confirm): ");

    if (password1 == password2):
        return password1
    else:
        sys.stdout.write (colors.ORANGE + "[Warning] Password did not match, please try again" + colors.NO + "\n")
        return getpassword()


def getstring(message = "Enter a value: "):
    """
    Ask user to enter a value
    """
    try:
        input = raw_input
    except: 
        pass
    return raw_input(message)


def waitenterpressed(message = "Press ENTER to continue..."):
    """
    Wait until ENTER is pressed
    """
    try:
        input = raw_input
    except: 
        pass
    raw_input(message)
    return 0

        
def main(argv):
    """
    Main function
    """
    try:
        opts, args = getopt.getopt(argv, "c:hv", ["config", "help", "version"])
    except getopt.GetoptError:
        syntax()
        exit(2)

    config_file = ""
    config_url = _CONF_FILE
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            if arg.startswith("http://") or \
                arg.startswith("https://") or \
                arg.startswith("ftp://"):
                config_url = arg
            else:
                config_file = arg
        elif opt in ("-h", "--help"):
            syntax()
            exit()
        elif opt in ('-v', "--version"):
            version()
            exit()

    # Are your root ?
    if (not isroot()):
        showexec ("Script should be run as root", "whoami", exitonerror = 1)
        
    # Is it Trusty?
    _UBUNTU_VERSION = platform.linux_distribution()[2]
    if (_UBUNTU_VERSION != _OS_VERSION):
        showexec (_UBUNTU_VERSION)
        showexec ("Script only for " + _OS_VERSION, "lsb_release -a", exitonerror = 1)
    
    # Read the configuration file
    if (config_file == ""):
        config_file = _GIT_FILE + ".cfg"
        showexec ("Download the configuration file", "rm -f "+config_file+" ; "+_WGET+" -O "+config_file+" "+config_url)
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    # Parse and exec pre-actions
    for action_name, action_cmd in config.items("preactions"):
        showexec ("Execute preaction "+action_name.lstrip("action_"), action_cmd)
        
    # Update repos
    #showexec ("Update repositories", _APT_UPDATE)
    
    # Upgrade system
    #showexec ("System upgrade (~20 mins, please be patient...)", _APT_UPGRADE)

    # Parse and install packages
    for pkg_type, pkg_list in config.items("packages"):
        if (pkg_type.startswith("remove_")):
            showexec ("Remove packages "+pkg_type.lstrip("remove_"), _APT_REMOVE+" "+pkg_list)
        else:
            showexec ("Install packages "+pkg_type, _APT_INSTALL+" "+pkg_list)
    
    # Download and install dotfiles: vimrc, prompt...
    if (config.has_section("dotfiles")):
        # Create the bashrc.d subfolder
        showexec ("Create the ~/.bashrc.d subfolder", "mkdir -p $HOME/.bashrc.d")
        if (config.has_option("dotfiles", "bashrc")):
            showexec ("Download bash main configuration file", _WGET+" -O $HOME/.bashrc "+config.get("dotfiles", "bashrc"))
        if (config.has_option("dotfiles", "bashrc_common")):
            showexec ("Download bash prompt configuration file", _WGET+" -O $HOME/.bashrc.d/bashrc_common "+config.get("dotfiles", "bashrc_common"))
        showexec ("Install the bash configuration file", "chown -R $USERNAME:$USERNAME $HOME/.bashrc*")
        # Vim
        if (config.has_option("dotfiles", "vimrc")):
            showexec ("Donwload the Vim configuration file", _WGET+" -O $HOME/.vimrc "+config.get("dotfiles", "vimrc"))
            showexec ("Install the Vim configuration file", "chown -R $USERNAME:$USERNAME $HOME/.vimrc")

        # Htop
        if (config.has_option("dotfiles", "htoprc")):
            showexec ("Download the Htop configuration file", _WGET+" -O $HOME/.htoprc "+config.get("dotfiles", "htoprc"))
            showexec ("Install the Htop configuration file", "chown -R $USERNAME:$USERNAME $HOME/.htoprc")
        
        # Pythonrc
        if (config.has_option("dotfiles", "pythonrc")):
            showexec ("Download the Pythonrc configuration file", _WGET+" -O $HOME/.pythonrc "+config.get("dotfiles", "pythonrc"))
            showexec ("Install the Pythonrc configuration file", "chown -R $USERNAME:$USERNAME $HOME/.pythonrc")

    # Add new users
    if (config.has_section("users")):
        for user_op, user_name in config.items("users"):
            showexec ("Users "+user_op, _USER_ADD+" "+user_name)

    # Config changes
    if (config.has_section("config")):
        for action_name, action_cmd in config.items("config"):
            showexec ("Execute config action "+action_name.lstrip("action_"), action_cmd)

    # Parse and exec post-actions
    for action_name, action_cmd in config.items("postactions"):
        showexec ("Execute postaction "+action_name.lstrip("action_"), action_cmd)

    # End of the script
    print("---")
    print("End of the script.")
    print(" - Cfg file: "+config_file)
    print(" - Log file: "+_LOG_FILE)
    print("")
    print("Please restart your session to complete.")
    print("---")

# Main program
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    init()
    print("File name of script: " + __file__)
    print("Path to script: " + os.path.realpath(__file__))
    main(sys.argv[1:])
    exit()
