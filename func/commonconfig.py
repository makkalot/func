from config import BaseConfig, BoolOption, IntOption, Option

class CMConfig(BaseConfig):
    listen_addr = Option('')
    cadir = Option('/etc/pki/func/ca')
    certroot =  Option('/var/lib/func/certmaster/certs')
    csrroot = Option('/var/lib/func/certmaster/csrs')
    autosign = BoolOption(False)


class FuncdConfig(BaseConfig):
    log_level = Option('INFO')
    certmaster = Option('certmaster')
    cert_dir = Option('/etc/pki/func')
    acl_dir = Option('/etc/func/minion-acl.d')
