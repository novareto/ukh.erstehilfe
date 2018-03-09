# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2011 NovaReto GmbH

import grok
from fanstatic import Library, Resource

library = Library('ukh.erstehilfe', 'static')
remote = Resource(library, 'remote.js')
main = Resource(library, 'main.css')
