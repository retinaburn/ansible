# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import collections

from jinja2 import Undefined as j2undefined

from ansible.template import Templar

__all__ = ['HostVars']

# Note -- this is a Mapping, not a MutableMapping
class HostVars(collections.Mapping):
    ''' A special view of vars_cache that adds values from the inventory when needed. '''

    def __init__(self, vars_manager, play, inventory, loader):
        self._vars_manager = vars_manager
        self._play         = play
        self._inventory    = inventory
        self._loader       = loader
        self._lookup       = {}

    def __getitem__(self, host_name):

        if host_name not in self._lookup:
            host = self._inventory.get_host(host_name)
            if not host:
                return j2undefined
            result = self._vars_manager.get_vars(loader=self._loader, play=self._play, host=host)
            templar = Templar(variables=result, loader=self._loader)
            self._lookup[host_name] = templar.template(result, fail_on_undefined=False)
        return self._lookup[host_name]

    def __contains__(self, host_name):
        item = self.get(host_name)
        if item and item is not j2undefined:
            return True
        return False

    def __iter__(self):
        raise NotImplementedError('HostVars does not support iteration as hosts are discovered on an as needed basis.')

    def __len__(self):
        raise NotImplementedError('HostVars does not support len.  hosts entries are discovered dynamically as needed')

    def __getstate__(self):
        return self._lookup

    def __setstate__(self, data):
        self._lookup = data
