# Copyright 2007, Red Hat, Inc
# seth vidal
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import sha
import os
import time
import shutil

from modules import func_module




class CopyFile(func_module.FuncModule):

    def __init__(self):
        self.methods = {
                "copyfile" : self.copyfile,
                "checksum" : self.checksum
        }
        func_module.FuncModule.__init__(self)
                             
    def checksum(self, thing):

        CHUNK=2**16
        thissum = sha.new()
        if os.path.exists(thing):
            fo = open(thing, 'r', CHUNK)
            chunk = fo.read
            while chunk:
                chunk = fo.read(CHUNK)
                thissum.update(chunk)
            fo.close()
            del fo
        else:
            # assuming it's a string of some kind
            thissum.update(thing)

        return thissum.hexdigest()


    def copyfile(self, filepath, filebuf):
        # -1 = problem file was not copied
        # 1 =  file was copied
        # 0 = file was not copied b/c file is unchanged
        
        dirpath = os.path.dirname(filepath)
        basepath = os.path.basename(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        
        remote_sum = self.checksum(filebuf)
        local_sum = 0
        if os.path.exists(filepath):
            local_sum = self.checksum(filepath)
        
        if remote_sum != local_sum:
            # back up the localone
            if os.path.exists(filepath):
                if not self._backuplocal(filepath):
                    return -1

            # do the new write
            try:
                fo = open(filepath, 'w')
                fo.write(filebuf)
                fo.close()
                del fo
            except (IOError, OSError), e:
                # XXX logger output here
                return -1
        else:
            return 0
            
        return 1

    def _backuplocal(self, fn):
        """
        make a date-marked backup of the specified file, 
        return True or False on success or failure
        """
        # backups named basename-YYYY-MM-DD@HH:MM~
        ext = time.strftime("%Y-%m-%d@%H:%M~", time.localtime(time.time()))
        backupdest = '%s.%s' % (fn, ext)
        
        try:
            shutil.copy2(fn, backupdest)
        except shutil.Error, e:
            #XXX logger output here
            return False
        return True



methods = CopyFile()
register_rpc = methods.register_rpc
