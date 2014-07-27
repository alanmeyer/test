#!/usr/bin/env python
# Alan Meyer
# https://github.com/alanmeyer/test
#
# Post linux installation script
#
# Based on work from http://www.nicolargo.com
# Distributed under the GPL version 3 license


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
_VERSION            = "0.10.AM"
_DEBUG              = 1

# Change these values based on your project location
_GIT_USER           = "alanmeyer"
_GIT_PROJECT        = "test"
_GIT_BRANCH         = "master"
_GIT_FILE           = "test"

# Change these only if you want a different set of common configuration files
_GIT_COMMON_USER    = "alanmeyer"
_GIT_COMMON_PROJECT = "postinstall-common"
_GIT_COMMON_BRANCH  = "master"

# Generated based on user config
_GIT_PREFIX         = "https://raw.github.com/"
_SLASH              = "/"
_GIT_SUFFIX         = _GIT_USER + _SLASH + _GIT_PROJECT + _SLASH + _GIT_BRANCH + _SLASH + _GIT_FILE + ".cfg"
_LOG_FILE           = _GIT_FILE + ".log"
_DPKG_LOG_BEFORE    = _GIT_FILE + "-packages-before.log"
_DPKG_LOG_AFTER     = _GIT_FILE + "-packages-after.log"
_CONF_FILE          = _GIT_PREFIX + _GIT_SUFFIX
_REPO_COMMON        = _GIT_PREFIX + _GIT_COMMON_USER + _SLASH + _GIT_COMMON_PROJECT + _SLASH + _GIT_COMMON_BRANCH + _SLASH

# The following should be set in the configuration file
# These are just placeholder values or for missing info in the config file
_DEFAULT_OS_VERSION = "trusty"
_DEFAULT_IP         = "10.10.10.10"
_DEFAULT_HOSTNAME   = "server"
_DEFAULT_DOMAIN     = "example.com"


# System commands
#-----------------------------------------------------------------------------

_NO_FRONTEND        = "DEBIAN_FRONTEND=noninteractive "
_APT_GET            = "apt-get "
_FORCE_YES          = "-y --force-yes --allow-unauthenticated "
_PKG_OPTIONS        = "-o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\" "
_APT_GET_OPTS       = _NO_FRONTEND + _APT_GET + _FORCE_YES + _PKG_OPTIONS
_APT_REMOVE         = _APT_GET_OPTS + "-f remove"
_APT_INSTALL        = _APT_GET_OPTS + "-f install"
_APT_UPDATE         = _APT_GET_OPTS + "   update"
_APT_UPGRADE        = _APT_GET_OPTS + "   upgrade"
_APT_ADD            = "add-apt-repository -y"
_APT_KEY            = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys"
_USER_ADD           = "adduser --disabled-password --gecos ,,,"
_GROUP_ADD          = "addgroup"
_USER_MOD_GROUP     = "usermod -a -G"
_USER_DEL           = "deluser"
_GROUP_DEL          = "delgroup"
_WGET               = "wget"


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
    print " # python " + (__file__)
    print " > Run the script with the default configuration file"
    print "   %s" % _CONF_FILE
    print ""
    print " # python " + (__file__) + " -c ./myconf.cfg"
    print " > Run the script with the ./myconf.cfg file"
    print ""
    print " # python " + (__file__) + " -c http://mysite.com/myconf.cfg"
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

    # Read the configuration file
    if (config_file == ""):
        config_file = _GIT_FILE + ".cfg"
        showexec ("Download the configuration file", "rm -f "+config_file+" ; "+_WGET+" -O "+config_file+" "+config_url)
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    # Get our server variables
    # First set the default values
    my_os_version   = _DEFAULT_OS_VERSION
    my_ip           = _DEFAULT_IP
    my_hostname     = _DEFAULT_HOSTNAME
    my_domain       = _DEFAULT_DOMAIN

    # Update with the config file if present
    if (config.has_section("server")):
        if (config.has_option("server", "os_version")):
            my_os_version = config.get("server", "os_version")
        if (config.has_option("server", "ip")):
            my_ip = config.get("server", "ip")
        if (config.has_option("server", "hostname")):
            my_hostname = config.get("server", "hostname")
        if (config.has_option("server", "domain")):
            my_domain = config.get("server", "domain")
    my_fqdn = my_hostname+"."+my_domain

    showexec("server: os_version = " + my_os_version, "true")
    showexec("server: ip         = " + my_ip        , "true")
    showexec("server: hostname   = " + my_hostname  , "true")
    showexec("server: domain     = " + my_domain    , "true")
    showexec("server: fqdn       = " + my_fqdn      , "true")


    # Are your root ?
    if (not isroot()):
        showexec ("Script should be run as root", "whoami", exitonerror = 1)
        
    # Is it the right OS version ?
    _UBUNTU_VERSION = platform.linux_distribution()[2]
    if (_UBUNTU_VERSION != my_os_version):
        showexec (_UBUNTU_VERSION)
        showexec ("Script only for " + my_os_version, "lsb_release -a", exitonerror = 1)
    

    # Set the hostname & IP
    showexec ("hosts: save original hosts file","cp -n /etc/hosts /etc/hosts.orig")
    showexec ("hosts: ip update", "sed -i 's/^"+my_ip+" .*/"+my_ip+" "+my_fqdn+" "+my_hostname+" localhost.localdomain localhost/g' /etc/hosts")
    showexec ("hosts: update hostname","echo \""+my_fqdn+"\" | tee /etc/hostname")
    showexec ("hosts: hostname service restart","service hostname restart")

    # Parse and exec pre-actions
    for action_name, action_cmd in config.items("preactions"):
        name=action_name[len("action_"):]
        showexec ("preaction: "+name, action_cmd)
        
    # Update repos
    showexec ("update repositories", _APT_UPDATE)
    
    # Upgrade system
    showexec ("system upgrade (~20 mins, please be patient...)", _APT_UPGRADE)

    # Parse and install packages
    showexec ("pacakages: log before ", "dpkg -l > " + _DPKG_LOG_BEFORE)
    for pkg_type, pkg_list in config.items("packages"):
        if (pkg_type.startswith("remove_")):
            packages=pkg_type[len("remove_"):]
            showexec ("packages: Remove "+packages, _APT_REMOVE+" "+pkg_list)
        else:
            showexec ("packages: Install "+pkg_type, _APT_INSTALL+" "+pkg_list)
    showexec ("packages: log after ", "dpkg -l > " + _DPKG_LOG_AFTER)
    
    # Download and install dotfiles: vimrc, prompt...
    if (config.has_section("dotfiles")):
        if (config.has_option("dotfiles", "bashrc")):
            showexec ("dotfiles: get bash main configuration file", _WGET+" -O $HOME/.bashrc "+_REPO_COMMON+config.get("dotfiles", "bashrc"))
            showexec ("dotfiles: update ownership", "chown $USERNAME:$USERNAME $HOME/.bashrc")
            showexec ("dotfiles: copy to skel", "cp -f $HOME/.bashrc /etc/skel")
        if (config.has_option("dotfiles", "bashrc_common")):
            showexec ("dotfiles: create the ~/.bashrc.d subfolder", "mkdir -p $HOME/.bashrc.d")
            showexec ("dotfiles: get bash prompt configuration file", _WGET+" -O $HOME/.bashrc.d/bashrc_common "+_REPO_COMMON+config.get("dotfiles", "bashrc_common"))
            showexec ("dotfiles: update ownership", "chown $USERNAME:$USERNAME $HOME/.bashrc.d/bashrc_common")
            showexec ("dotfiles: copy to skel", "cp -f -r $HOME/.bashrc.d /etc/skel")
        # Create scripts and bin folders
        showexec ("dotfiles: create the $HOME/bin subfolder", "mkdir -p $HOME/bin")
        showexec ("dotfiles: create the $HOME/scripts subfolder", "mkdir -p $HOME/scripts")
        showexec ("dotfiles: create the /etc/skel/bin subfolder", "mkdir -p /etc/skel/bin")
        showexec ("dotfiles: create the /etc/skel/scripts subfolder", "mkdir -p /etc/skel/scripts")

        # Vim
        if (config.has_option("dotfiles", "vimrc")):
            showexec ("dotfiles: get the vim configuration file", _WGET+" -O $HOME/.vimrc "+_REPO_COMMON+config.get("dotfiles", "vimrc"))
            showexec ("dotfiles: update ownership", "chown -R $USERNAME:$USERNAME $HOME/.vimrc")
            showexec ("dotfiles: copy to skel", "cp -f $HOME/.vimrc /etc/skel")

        # Htop
        if (config.has_option("dotfiles", "htoprc")):
            showexec ("dotfiles: get the htop configuration file", _WGET+" -O $HOME/.htoprc "+_REPO_COMMON+config.get("dotfiles", "htoprc"))
            showexec ("dotfiles: update ownership", "chown -R $USERNAME:$USERNAME $HOME/.htoprc")
            showexec ("dotfiles: copy to skel", "cp -f $HOME/.htoprc /etc/skel")

        # Pythonrc
        if (config.has_option("dotfiles", "pythonrc")):
            showexec ("dotfiles: get the pythonrc configuration file", _WGET+" -O $HOME/.pythonrc "+_REPO_COMMON+config.get("dotfiles", "pythonrc"))
            showexec ("dotfiles: update ownership", "chown -R $USERNAME:$USERNAME $HOME/.pythonrc")
            showexec ("dotfiles: copy to skel", "cp -f $HOME/.pythonrc /etc/skel")

    # Media files
    if (config.has_section("media")):
        showexec ("media: create images directory", "mkdir -p /media/images")
        for media_index, media_name in config.items("media"):
            name=media_name[len("media_"):]
            showexec ("media: get "+media_index, _WGET+" -O /media/images/"+name+" "+_REPO_COMMON+media_name)
        showexec ("media: update image directory privlidges", "chmod -R +644 /media/images")

    # Scripts
    if (config.has_section("scripts")):
        showexec ("scripts: create the $HOME/scripts subfolder", "mkdir -p $HOME/scripts")
        for script_index, script_name in config.items("scripts"):
            if (script_index.startswith("script_")):
                script_local="$HOME/scripts/"+script_name[len("scripts_"):]
                showexec ("scripts: get "+script_index, _WGET+" -O "+script_local+" "+_REPO_COMMON+script_name+" && chmod +x "+script_local)
            else:
                if (script_index.startswith("script-initd_")):
                    script_local="/etc/init.d/"+script_name[len("scripts_"):]
                    script=script_name[len("scripts_"):]
                    showexec ("scripts: initd get "+script_index, _WGET+" -O "+script_local+" "+_REPO_COMMON+script_name+" && chmod +x "+script_local+" && update-rc.d "+script+" defaults")
                else:
                    if (script_index.startswith("script-cron_")):
                        script=script_name[len("scripts_"):]
                        showexec ("scripts: cron get "+script_index, _WGET+" -O "+script+" "+_REPO_COMMON+script_name+" && crontab "+script+" && rm "+script)

    # Config changes
    if (config.has_section("config")):
        for action_name, action_cmd in config.items("config"):
            name=action_name[len("config_"):]
            showexec ("config: "+name, action_cmd)

    # Add new users
    if (config.has_section("users")):
        for user_op, user_name in config.items("users"):
            showexec ("users: "+user_name, _USER_ADD+" "+user_name)

    # Add new groups
    if (config.has_section("groups")):
        for group_op, group_name in config.items("groups"):
            showexec ("groups: "+group_name, _GROUP_ADD+" "+group_name)

    # Add an existing user to an existing group
    if (config.has_section("users groups")):
        for user_name, group_names in config.items("users groups"):
            showexec ("users groups: "+user_name, _USER_MOD_GROUP+" "+group_names+" "+user_name)

    # Delete an existing group
    if (config.has_section("delete groups")):
        for group_op, group_name in config.items("delete groups"):
            showexec ("delete groups: "+user_op, _GROUP_DEL+" "+group_name)

    # Delete an existing user
    if (config.has_section("delete users")):
        for user_op, user_name in config.items("delete users"):
            showexec ("delete users: "+user_op, _USER_DEL+" "+user_name)

    # Parse and exec post-actions
    for action_name, action_cmd in config.items("postactions"):
        name=action_name[len("action_"):]
        showexec ("postaction: "+name, action_cmd)

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
