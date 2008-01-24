from datetime import datetime
# import the basic Elixir classes and functions for declaring the data model
# (see http://elixir.ematia.de/trac/wiki/TutorialDivingIn)
from elixir import Entity, Field, OneToMany, ManyToOne, ManyToMany
from elixir import options_defaults, using_options, setup_all
# import some datatypes for table columns from Elixir
# (see http://www.sqlalchemy.org/docs/04/types.html for more)
from elixir import String, Unicode, Integer, DateTime
from turbogears import identity

options_defaults['autosetup'] = False


# your data model

# class YourDataClass(Entity):
#     pass


# the identity model


class Visit(Entity):
    """
    A visit to your site
    """
    using_options(tablename='visit')

    visit_key = Field(String(40), primary_key=True)
    created = Field(DateTime, nullable=False, default=datetime.now)
    expiry = Field(DateTime)

    @classmethod
    def lookup_visit(cls, visit_key):
        return Visit.get(visit_key)


class VisitIdentity(Entity):
    """
    A Visit that is link to a User object
    """
    using_options(tablename='visit_identity')

    visit_key = Field(String(40), primary_key=True)
    user = ManyToOne('User', colname='user_id', use_alter=True)


class Group(Entity):
    """
    An ultra-simple group definition.
    """
    using_options(tablename='tg_group')

    group_id = Field(Integer, primary_key=True)
    group_name = Field(Unicode(16), unique=True)
    display_name = Field(Unicode(255))
    created = Field(DateTime, default=datetime.now)
    users = ManyToMany('User', tablename='user_group')
    permissions = ManyToMany('Permission', tablename='group_permission')


class User(Entity):
    """
    Reasonably basic User definition.
    Probably would want additional attributes.
    """
    using_options(tablename='tg_user')

    user_id = Field(Integer, primary_key=True)
    user_name = Field(Unicode(16), unique=True)
    email_address = Field(Unicode(255), unique=True)
    display_name = Field(Unicode(255))
    password = Field(Unicode(40))
    created = Field(DateTime, default=datetime.now)
    groups = ManyToMany('Group', tablename='user_group')

    @property
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms |= set(g.permissions)
        return perms


class Permission(Entity):
    """
    A relationship that determines what each Group can do
    """
    using_options(tablename='permission')

    permission_id = Field(Integer, primary_key=True)
    permission_name = Field(Unicode(16), unique=True)
    description = Field(Unicode(255))
    groups = ManyToMany('Group', tablename='group_permission')


# Set up all Elixir entities declared above

setup_all()
