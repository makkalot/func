from config import BaseConfig, BoolOption, Option

class CMConfig(BaseConfig):
    listen_addr = Option('')
    cadir = Option('/etc/pki/func/ca')
    certroot =  Option('/var/lib/certmaster/certmaster/certs')
    csrroot = Option('/var/lib/certmaster/certmaster/csrs')
    autosign = BoolOption(False)


class FuncdConfig(BaseConfig):
    log_level = Option('INFO')
    certmaster = Option('certmaster')
    cert_dir = Option('/etc/pki/func')
    acl_dir = Option('/etc/func/minion-acl.d')
