from func.overlord import overlord_module
import os
import stat
import xmlrpclib

class copyfile(overlord_module.BaseModule):
    def send(self, localpath, remotepath, bufsize=60000):
        try:
            f = open(localpath, "r")
        except IOError, e:
            sys.stderr.write("Unable to open file: %s: %s\n" % (self.options.filename, e))
            return

        st = os.stat(localpath)
        mode = stat.S_IMODE(st.st_mode)
        uid = st.st_uid
        gid = st.st_gid

        self.parent.run("copyfile", "open", [remotepath, mode, uid, gid])

        while True: 
            data=f.read(bufsize)
            if data:
                self.parent.run("copyfile", "append", [remotepath, xmlrpclib.Binary(data)])
            else:
                break
    
        return True
