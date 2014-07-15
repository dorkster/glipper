import gtk, gobject, glipper, gconf

class Clipboards(gobject.GObject):

	__gsignals__ = {
		"new-item" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING, gobject.TYPE_BOOLEAN]),
	}

	def __init__(self):
		gobject.GObject.__init__(self)
		self.default_clipboard = Clipboard(gtk.clipboard_get(),
		                                   self.emit_new_item,
		                                   glipper.GCONF_USE_DEFAULT_CLIPBOARD)
		self.primary_clipboard = Clipboard(gtk.clipboard_get("PRIMARY"),
		                                   self.emit_new_item_selection,
		                                   glipper.GCONF_USE_PRIMARY_CLIPBOARD)
		
	def set_text(self, text):
		self.default_clipboard.set_text(text)
		self.primary_clipboard.set_text(text)

		self.emit('new-item', text, False)

	def clear_text(self):
		self.default_clipboard.clear()
		self.primary_clipboard.clear()
		
	def get_default_clipboard_text(self):
		return self.default_clipboard.get_text()
	
	def emit_new_item(self, item):
		self.emit('new-item', item, False)
	
	def emit_new_item_selection(self, item):
		self.emit('new-item', item, True)
	

class Clipboard(object):
	def __init__(self, clipboard, new_item_callback, use_clipboard_gconf_key):
		self.new_item_callback = new_item_callback
		self.clipboard = clipboard
		self.clipboard_text = self.unicode_or_none(clipboard.wait_for_text())
		self.clipboard.connect('owner-change', self.on_clipboard_owner_change)
		
		self.use_clipboard = glipper.GCONF_CLIENT.get_bool(use_clipboard_gconf_key)
		if self.use_clipboard is None:
			self.use_clipboard = True
		glipper.GCONF_CLIENT.notify_add(use_clipboard_gconf_key, self.on_use_clipboard_changed)
	
	def get_text(self):
		return self.clipboard_text
	
	def set_text(self, text):
		if self.use_clipboard:
			self.clipboard.set_text(text)
			self.clipboard_text = text

	def clear(self):
		if self.use_clipboard:
			self.clipboard.set_text('')
			self.clipboard.clear()
			self.clipboard_text = None
			
	
	def on_clipboard_owner_change(self, clipboard, event):
		if self.use_clipboard:
			self.clipboard_text = self.unicode_or_none(clipboard.wait_for_text())
			self.new_item_callback(self.clipboard_text)
	
	def on_use_clipboard_changed(self, client, connection_id, entry, user_data):
		value = entry.value
		if value is None or value.type != gconf.VALUE_BOOL:
			return
		self.use_clipboard = value.get_bool()
	
	@staticmethod
	def unicode_or_none(bytes_utf8):
		if bytes_utf8 is None:
			return None
		else:
			return unicode(bytes_utf8, 'UTF-8')

clipboards = Clipboards()

def get_glipper_clipboards():
	return clipboards

