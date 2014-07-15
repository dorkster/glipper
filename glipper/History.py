import gobject, gtk, gconf
import glipper
from glipper.Clipboards import *
from glipper.PluginsManager import *
from gettext import gettext as _

class History(gobject.GObject):
	__gsignals__ = {
		"changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
	}
	
	def __init__(self):
		gobject.GObject.__init__(self)
		self.history = []
		get_glipper_clipboards().connect('new-item', self.on_new_item)

		self.max_elements = glipper.GCONF_CLIENT.get_int(glipper.GCONF_MAX_ELEMENTS)
		if self.max_elements == None:
			self.max_elements = 20
		glipper.GCONF_CLIENT.notify_add(glipper.GCONF_MAX_ELEMENTS, lambda x, y, z, a: self.on_max_elements_changed (z.value))
	
	def get_history(self):
		return self.history
	
	def on_new_item(self, clipboards, item, is_from_selection):
		self.add(item, is_from_selection)
		get_glipper_plugins_manager().call('on_new_item', item)
		
	def clear(self):
		self.history = []
		self.emit('changed', self.history)
	
	def get(self, index):
		if index >= len(self.history):
			return

		return self.history[index]
	
	def set(self, index, item):
		assert item is not None
		item = unicode(item)
		if item in self.history:
			self.history.remove(item)

		if index == len(self.history):
			self.history.append(item)
		else:
			self.history[index] = item 
		self.emit('changed', self.history)
	
	def add(self, item, is_from_selection=False):
		if item is not None:
			item = unicode(item)
			if item in self.history:
				self.history.remove(item)
			
			last_item = self.history[0] if self.history else None
			if is_from_selection and last_item is not None and \
					(item.startswith(last_item) or item.endswith(last_item)):
				self.history[0] = item
			else:
				self.history.insert(0, item)
			
			if len(self.history) > self.max_elements:
				self.history = self.history[0:self.max_elements]
			
			ctrl_c_item = get_glipper_clipboards().get_default_clipboard_text()
			if ctrl_c_item is not None and ctrl_c_item not in self.history:
				self.history[-1] = ctrl_c_item
		
		# if item is None, emit changed anyway because 
		# the current (bold) clipboard item has changed.
		self.emit('changed', self.history)

	def remove(self, index):
		del self.history[index]

	def load(self):
		try:
			file = open(glipper.HISTORY_FILE, "r")
		
			length = file.readline()
			while length:
				try:
					bytes_to_read = int(length)
				except ValueError:
					break
				
				self.history.append(unicode(file.read(bytes_to_read), 'UTF-8'))
				file.read(1) # This is for \n
				length = file.readline()
		
			file.close()
		except IOError:
			pass
		
		self.emit('changed', self.history)
		
	def save(self):
		try:
			file = open(glipper.HISTORY_FILE, "w")
		except IOError:
			return # Cannot write to history file
			
		for item in self.history:
			assert isinstance(item, unicode)
			string = item.encode('UTF-8')
			file.write(str(len(string)) + '\n')
			file.write(string + '\n')
		
		file.close()
	
	def on_max_elements_changed (self, value):
		if value is None or value.type != gconf.VALUE_INT:
			return
		self.max_elements = value.get_int()
		if len(self.history) > self.max_elements:
			self.history = self.history[0:self.max_elements]
			self.emit('changed', self.history)
			
history = History()

def get_glipper_history():
	return history
