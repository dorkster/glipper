#!/usr/bin/env python

from distutils import dir_util
from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from DistUtilsExtra.command import build_extra, build_i18n, build_help, build_icons
import glob
import os, sys

def write_defs_dot_py(data_dir, version):
	DEFS_PY = \
"""# Variables are filled in by setup.py. Modifications will be overwritten.
DATA_DIR = "%(data_dir)s"
VERSION = "%(version)s"
"""

	substitutions = {
	    'data_dir': data_dir,
	    'version': version,
	}
	
	print "writing defs.py with:", substitutions
	
	file_ = open(os.path.join('glipper', 'defs.py'), 'wb')
	file_.write(DEFS_PY % substitutions)
	file_.flush()
	file_.close()

def read_defs_dot_py():
	file_ = open(os.path.join('glipper', 'defs.py'), 'rb')
	data = file_.read()
	file_.close()
	return data
	
def restore_defs_dot_py(data):
	file_ = open(os.path.join('glipper', 'defs.py'), 'wb')
	file_.write(data)
	file_.flush()
	file_.close()

class custom_install_override(install):
	def finalize_options(self):
		ret = install.finalize_options(self)
		# Fill in variables in glipper/defs.py
		write_defs_dot_py(data_dir=os.path.join(self.install_base, 'share'),
		                  version=self.distribution.get_version())
		return ret

class build_deb(Command):
	user_options = []

	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		sdist = self.reinitialize_command('sdist')
		sdist.formats = ['gztar']
		sdist.keep_temp = True
		self.run_command('sdist')

		source = sdist.get_archive_files()[0]
		assert source.endswith('.tar.gz')

		opts = {
			'name': self.distribution.get_name(),
			'version': self.distribution.get_version(),
		}
		orig_name = '%(name)s_%(version)s.orig.tar.gz' % opts

		base_dir = self.distribution.get_fullname()

		if os.path.exists('debian-build'):
			print ""
			print "== Error: =="
			print "== Please remove debian-build directory first =="
			sys.exit(1)
		os.mkdir('debian-build')
		self.move_file(source, os.path.join("debian-build", orig_name))

		os.rename(base_dir, os.path.join('debian-build', base_dir))
		self.copy_tree('debian', os.path.join('debian-build', base_dir, 'debian'))

		old_cwd = os.getcwd()
		os.chdir(os.path.join(old_cwd, 'debian-build', base_dir))
		os.system('debuild -S -sa')
		os.chdir(old_cwd)
		
		dir_util.remove_tree(os.path.join('debian-build', base_dir))

defs_dot_py_data = read_defs_dot_py()

setup(name='glipper',
      version='2.4',
      description='A clipboard history manager',
      author='Sven Rech',
      author_email='svenrech@gmx.de',
      maintainer='Laszlo Pandy',
      maintainer_email='laszlok2@gmail.com',
      url='http://launchpad.net/glipper',
      license='GNU GPL v2',
      requires=['gtk', 'gio', 'gconf', 'keybinder', 'prctl', 'appindicator', 'xdg'],
      
      packages=['glipper'],
      scripts=['scripts/glipper'],
      data_files=[
                  ('share/glipper',         glob.glob('data/*.ui')),
                  ('share/glipper/plugins', glob.glob('glipper/plugins/*.py')),
                  ('share/glipper/plugins', glob.glob('glipper/plugins/*.ui')),
                  ('share/gconf/schemas',   ['data/glipper.schemas']),
                  ('/etc/xdg/autostart',    ['glipper-autostart.desktop']),
                 ],
      
      cmdclass = { # our custom override (defined above)
                   'install': custom_install_override,
                   # add deb building
                   'build_deb': build_deb,
                   # distutils extra overrides
                   'build' : build_extra.build_extra,
                   'build_i18n' :  build_i18n.build_i18n,
                   'build_help' :  build_help.build_help,
                   'build_icons' :  build_icons.build_icons }
     )

restore_defs_dot_py(defs_dot_py_data)

