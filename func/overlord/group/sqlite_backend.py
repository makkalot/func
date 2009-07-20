from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey,Column,Integer,String
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import not_

Base = declarative_base()
class Group(Base):
    """
    Group Table
    """
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100),nullable=False,unique=True)
    
    def __init__(self,name):
        self.name = name
        
    def __repr__(self):
        return "<Group('%s')>" % (self.name)

class Host(Base):
    """
    Hosts Table
    """

    __tablename__ = 'hosts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False,unique=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    
    group = relation(Group, backref=backref('hosts', order_by=id))
    
    def __init__(self, name,group_id):
        self.name = name
        self.group_id = group_id
    
    def __repr__(self):
        return "<Host('%s')>" % self.name


from func.commonconfig import OVERLORD_CONFIG_FILE,OverlordConfig
CONF_FILE = OVERLORD_CONFIG_FILE
DB_PATH = "/var/lib/certmaster/groups.db"
from certmaster.config import read_config
from func.overlord.group.base import BaseBackend
import os

class SqliteBackend(BaseBackend):
    """
    Sqlite backend for groups api
    """

    def __init__(self,conf_file = None,db_file=None,*args,**kwargs):
        """
        Initializing the database if it doesnt exists it is created and
        connection opened for serving nothing special

        @param conf_file : Configuration file
        @param db_file   : Place of the database file override if needed
        """
        self.config = conf_file or CONF_FILE
        self.config = read_config(self.config,OverlordConfig)
        self.db_path = db_file or self.config.group_db or DB_PATH

        self._recreate_session()

    def _recreate_session(self):
        if os.path.exists(self.db_path):
            #we have it so dont have to create the databases
            engine = create_engine('sqlite:///%s'%self.db_path)
        else:
            engine = create_engine('sqlite:///%s'%self.db_path)
            Base.metadata.create_all(engine)

        #create a session for querying
        Session = scoped_session(sessionmaker(bind=engine))
        self.session = Session()

    
    def add_group(self,group,save=True):
        """
        Adds a group
        """
        #check for group first
        gr = self._group_exists(group)
        if gr[0]:
            return (False,"Group already exists %s "%(gr[1]))
        
        #add the group
        self.session.add(Group(group))
        self._check_commit(save)
        return (True,'')
    
    def add_host_to_group(self,group,host,save=True):
        """
        Adds a host to a group
        """
        try:
            self.session.add(Host(host,self.session.query(Group).filter_by(name=group).one().id))
            self._check_commit(save)
        except Exception,e:
            self._recreate_session()
            return (False,"The host is already in database %s : %s "%(host,e))
        
        return (True,'')
    
    def remove_group(self,group,save=True):
        """
        Removes a group
        """
       #check for group first
        group = self._group_exists(group)
        if not group[0]:
            return group
        else:
            group = group[1]
        
        self.session.delete(group)
        self._check_commit(save)
        return (True,'')


    def remove_host(self,group,host,save=True):
        """
        Remove a host from groups
        """
        #check for group first
        group = self._group_exists(group)
        if not group[0]:
            return group
        else:
            group = group[1]
        #check for dupliate
        host_db = None
        try:
            host_db=self.session.query(Host).filter_by(name=host,group_id=group.id).one()
        except Exception,e:
            #we dont have it so we can add it
            return (False,str(e))
        
        self.session.delete(host_db)
        self._check_commit(save)
        return (True,"")
    
    def save_changes(self):
        """
        Save the stuff that is in memory
        """
        self._check_commit()

    
    def get_groups(self,pattern=None,exact=True,exclude=None):
        """
        Get a set of groups
        
        @param pattern : You may request to get an exact host or
                         a one in proper pattern .
        @param exact   : Related to pattern if you should do exact 
                         matching or related one.
        @param exclude : A list to be excluded from final set
        """
        if not pattern:
            #that means we want all of them
            if not exclude:
                return [g.name for g in self.session.query(Group).all()]
            else:
                return [g.name for g in self.session.query(Group).filter(not_(Group.name.in_(exclude))).all()]

        else:
            if not exact:
                if not exclude:
                    return [g.name for g in self.session.query(Group).filter(Group.name.like("".join(["%",pattern,"%"]))).all()]
                else:
                    return [g.name for g in self.session.query(Group).filter(Group.name.like("".join(["%",pattern,"%"]))).filter(not_(Group.name.in_(exclude))).all()]

            else:
                return [g.name for g in self.session.query(Group).filter_by(name=pattern).all()]
    
        return []

    def get_hosts(self,pattern=None,group=None,exact=True,exclude=None):
        """
        Get a set of hosts

        @param pattern : You may request to get an exact host or
                         a one in proper pattern .
        @param exact   : Related to pattern if you should do exact 
                         matching or related one.
        @param exclude : A list to be excluded from final set
        """
        group = self._group_exists(group)
        if not group[0]:
            return []
        else:
            group = group[1]

        if not pattern:
            #if there is no pattern there are 2 possible options
            if not exclude:
                return [h.name for h in self.session.query(Host).filter_by(group_id=group.id).all()]
            else:
                return [h.name for h in self.session.query(Host).filter_by(group_id=group.id).filter(not_(Host.name.in_(exclude))).all()]

        else:
            #there is some pattern so we should go for it
            if exact:
                if type(pattern)==list or type(pattern)==set:
                    #it seems we got a list to pull from database
                    return [h.name for h in self.session.query(Host).filter_by(group_id=group.id).filter(Host.name.in_(pattern)).all()]
                else:
                    return [h.name for h in self.session.query(Host).filter_by(name=pattern,group_id=group.id).all()]

            else:
                if not exclude:
                    return [h.name for h in self.session.query(Host).filter(Host.name.like("".join(["%",pattern,"%"]))).filter_by(group_id=group.id).all()]
                else:
                    return [h.name for h in self.session.query(Host).filter(Host.name.like("".join(["%",pattern,"%"]))).filter_by(group_id=group.id).filter(not_(Host.name.in_(exclude))).all()]
        
        return []
    def _check_commit(self,commit=True):
        """
        A simple util that checks if we should commit
        """
        if commit:
            self.session.commit()

    def _group_exists(self,group):
        """
        Checks if a group already exists
        """
        try:
            group=self.session.query(Group).filter_by(name=group).all()
            if group and len(group)==1:
                return (True,group[0])
            else:
                return (False,"Not existing group name")
        except Exception,e:
            return (False,str(e))

