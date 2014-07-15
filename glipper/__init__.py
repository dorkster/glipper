import os, sys
from os.path import join, exists, isdir, isfile, dirname, abspath, expanduser

import xdg.BaseDirectory
import gtk, gtk.gdk, gconf

# Autotools set the actual data_dir in defs.py
from defs import VERSION, DATA_DIR

# Allow to use uninstalled glipper ---------------------------------------------
UNINSTALLED_GLIPPER = False
if '_GLIPPER_UNINSTALLED' in os.environ:
	UNINSTALLED_GLIPPER = True
	print "Running glipper uninstalled"
	
# Sets SHARED_DATA_DIR to local copy, or the system location
# Shared data dir is most the time /usr/share/glipper
if UNINSTALLED_GLIPPER:
	SHARED_DATA_DIR = abspath(join(dirname(__file__), '..', 'data'))
	try:
		file_ = open('.bzr/branch/last-revision')
		string = file_.read()
		file_.close()
	except IOError:
		pass
	else:
		revision = string.split()[0]
		VERSION += "-r%s (bzr)" % revision
else:
	SHARED_DATA_DIR = join(DATA_DIR, "glipper")
print "SHARED_DATA_DIR: %s" % SHARED_DATA_DIR


# check if it exists first, because save_data_path() creates the folder
xdg_dir_existed = exists(join(xdg.BaseDirectory.xdg_data_home, 'glipper'))
try:
	USER_GLIPPER_DIR = xdg.BaseDirectory.save_data_path('glipper')
except OSError, e:
	print 'Error: could not create user glipper dir (%s): %s' % (join(xdg.BaseDirectory.xdg_data_home, 'glipper'), e)
	sys.exit(1)

if exists(expanduser("~/.glipper")) and not xdg_dir_existed:
	# first run for new directory; move old ~/.glipper
	try:
		os.rename(expanduser("~/.glipper"), USER_GLIPPER_DIR)
	except OSError:
		# folder must already have some files in it 
		# (race condition with xdg_dir_existed check)
		pass

# ------------------------------------------------------------------------------

# Path to plugins
if UNINSTALLED_GLIPPER:
	PLUGINS_DIR = join(dirname(__file__), 'plugins')
else:
	PLUGINS_DIR = join(SHARED_DATA_DIR, 'plugins')

# Path to plugins save directory
USER_PLUGINS_DIR = xdg.BaseDirectory.save_data_path('glipper', 'plugins')

# Path to history file
HISTORY_FILE = join(USER_GLIPPER_DIR, "history")

# Maximum length constant for tooltips item in the history
MAX_TOOLTIPS_LENGTH = 11347

#Gconf client
GCONF_CLIENT = gconf.client_get_default()

# GConf directory for deskbar in window mode and shared settings
GCONF_DIR = "/apps/glipper"

# GConf key to the setting for the amount of elements in history
GCONF_MAX_ELEMENTS = GCONF_DIR + "/max_elements"

# GConf key to the setting for the length of one history item
GCONF_MAX_ITEM_LENGTH = GCONF_DIR + "/max_item_length"

# GConf key to the setting for the key combination to popup glipper
GCONF_KEY_COMBINATION = GCONF_DIR + "/key_combination"

# GConf key to the setting for using the default clipboard
GCONF_USE_DEFAULT_CLIPBOARD = GCONF_DIR + "/use_default_clipboard"

# GConf key to the setting for using the primary clipboard
GCONF_USE_PRIMARY_CLIPBOARD = GCONF_DIR + "/use_primary_clipboard"

# GConf key to the setting for whether the default entry should be marked in bold
GCONF_MARK_DEFAULT_ENTRY = GCONF_DIR + "/mark_default_entry"

# GConf key to the setting for whether the history should be saved
GCONF_SAVE_HISTORY = GCONF_DIR + "/save_history"

GCONF_AUTOSTART_PLUGINS = GCONF_DIR + "/autostart_plugins"

# Preload gconf directories
GCONF_CLIENT.add_dir(GCONF_DIR, gconf.CLIENT_PRELOAD_RECURSIVE)

# Functions callable by plugins

from glipper.History import *
from glipper.Clipboards import *
from glipper.PluginsManager import *

import glipper.AppIndicator

def add_menu_item(menu_item):
	get_glipper_plugins_manager().add_menu_item(menu_item)

def add_history_item(item):
	get_glipper_clipboards().set_text(item)

def set_history_item(index, item):
	get_glipper_history().set(index, item)

def get_history_item(index):
	return get_glipper_history().get(index)

def remove_history_item(index):
	return get_glipper_history().remove(index)

def clear_history():
	return get_glipper_history().clear()

def format_item(item):
	return glipper.AppIndicator.format_item(item)
