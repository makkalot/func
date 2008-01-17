## func
##
## filetracker
##  maintains a manifest of files of which to keep track
##  provides file meta-data (and optionally full data) to func-inventory
##
## (C) Vito Laurenza <vitolaurenza@gmail.com>
## + Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

# func modules
import func_module

# other modules
from stat import *
import glob
import os
import md5

# defaults
CONFIG_FILE='/etc/func/modules/filetracker.conf'

class FileTracker(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Maintains a manifest of files to keep track of."

    def __load(self):
        """
        Parse file and return data structure.
        """

        filehash = {}
        if os.path.exists(CONFIG_FILE):
            config = open(CONFIG_FILE, "r")
            data   = config.read()
            lines  = data.split("\n")
            for line in lines:
                tokens = line.split(None)
                if len(tokens) < 2:
                    continue
                scan_mode = tokens[0]
                path = " ".join(tokens[1:])
                if str(scan_mode).lower() == "0":
                    scan_mode = 0
                else:
                    scan_mode = 1
                filehash[path] = scan_mode
        return filehash

    #==========================================================

    def __save(self, filehash):
        """
        Write data structure to file.
        """ 

        config = open(CONFIG_FILE, "w+")
        for (path, scan_mode) in filehash.iteritems():
            config.write("%s     %s\n" % (scan_mode, path))
        config.close()

    #==========================================================
               
    def track(self, file_name, full_scan=0):
        """
        Adds files to keep track of.
        full_scan implies tracking the full contents of the file, defaults to off
        """

        filehash = self.__load()
        filehash[file_name] = full_scan
        self.__save(filehash)
        return 1

    #==========================================================

    def untrack(self, file_name):
        """
        Stop keeping track of a file.
        This routine is tolerant of most errors since we're forgetting about the file anyway.
        """

        filehash = self.__load()
        if file_name in filehash.keys():
            del filehash[file_name]
        self.__save(filehash)
        return 1

    #==========================================================

    def inventory(self, flatten=1, checksum_enabled=1):
        """
        Returns information on all tracked files
        By default, 'flatten' is passed in as True, which makes printouts very clean in diffs
        for use by func-inventory.  If you are writting another software application, using flatten=False will
        prevent the need to parse the returns.
        """
 
        # XMLRPC feeds us strings from the CLI when it shouldn't
        flatten = int(flatten)
        checksum_enabled = int(checksum_enabled)

        filehash = self.__load()

        # we'll either return a very flat string (for clean diffs)
        # or a data structure
        if flatten:
            results = ""
        else:
            results = []

        for (file_name, scan_type) in filehash.iteritems():

            if not os.path.exists(file_name):
                if flatten:
                    results = results + "%s: does not exist\n" % file_name
                else:
                    results.append("%s: does not exist\n" % file_name)
                continue

            this_result = []

            # ----- always process metadata
            filestat = os.stat(file_name)
            mode = filestat[ST_MODE]
            mtime = filestat[ST_MTIME]
            uid = filestat[ST_UID]
            gid = filestat[ST_GID]
            if not os.path.isdir(file_name) and checksum_enabled:
                sum_handle = open(file_name)
                hash = self.__sumfile(sum_handle)
                sum_handle.close()
            else:
                hash = "N/A"

            # ------ what we return depends on flatten
            if flatten:
                this_result = "%s:  mode=%s  mtime=%s  uid=%s  gid=%s  md5sum=%s\n" % (file_name,mode,mtime,uid,gid,hash) 
            else:
                this_result = [file_name,mode,mtime,uid,gid,hash]

            # ------ add on file data only if requested
            if scan_type != 0 and os.path.isfile(file_name):
                tracked_file = open(file_name)
                data = tracked_file.read()
                if flatten:
                    this_result = this_result + "*** DATA ***\n" + data + "\n*** END DATA ***\n\n"
                else:
                    this_result.append(data)
                tracked_file.close()
           
            if os.path.isdir(file_name):
                if not file_name.endswith("/"):
                    file_name = file_name + "/"
                files = glob.glob(file_name + "*") 
                if flatten:
                    this_result = this_result + "*** FILES ***\n" + "\n".join(files) + "\n*** END FILES ***\n\n"
                else:
                    this_result.append({"files" : files})

            if flatten:
                results = results + "\n" + this_result
            else:
                results.append(this_result)


        return results

    #==========================================================

    def __sumfile(self, fobj):
        """
        Returns an md5 hash for an object with read() method.
        credit: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/266486
        """

        m = md5.new()
        while True:
            d = fobj.read(8096)
            if not d:
                break
            m.update(d)
        return m.hexdigest()
