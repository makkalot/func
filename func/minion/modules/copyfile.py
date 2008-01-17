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

import func_module


class CopyFile(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.2"
    description = "Allows for smart copying of a file."

    def _checksum_blob(self, blob):
        thissum = sha.new()
        thissum.update(blob)
        return thissum.hexdigest()
                       
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


    def copyfile(self, filepath, filebuf, mode=0644, uid=0, gid=0, force=None):
        # -1 = problem file was not copied
        # 1 =  file was copied
        # 0 = file was not copied b/c file is unchanged


        # we should probably verify mode,uid,gid are valid as well

        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        remote_sum = self._checksum_blob(filebuf.data)
        local_sum = 0
        if os.path.exists(filepath):
            local_sum = self.checksum(filepath)

        if remote_sum != local_sum or force is not None:
            # back up the localone
            if os.path.exists(filepath):
                if not self._backuplocal(filepath):
                    return -1

            # do the new write
            try:
                fo = open(filepath, 'w')
                fo.write(filebuf.data)
                fo.close()
                del fo
            except (IOError, OSError), e:
                # XXX logger output here
                return -1
        else:
            return 0

        # hmm, need to figure out proper exceptions -akl
        try:
            # we could intify the mode here if it's a string
            os.chmod(filepath, mode)
            os.chown(filepath, uid, gid)
        except (IOError, OSError), e:
            return -1

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
