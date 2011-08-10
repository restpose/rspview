#
# This file is part of the restpose python module, released under the MIT
# license.  See the COPYING file for more information.
"""Search support.

"""

from flask import render_template
from . import pagination

def do_search(coll, docs, search_desc, page):
    hpp = 20
    page = pagination.Page(docs, page, hpp)
    collconfig = coll.config
    special_fields = collconfig['special_fields']
    type_field = special_fields['type_field']
    id_field = special_fields['id_field']
    return render_template('doc_list.html',
                           coll=coll,
                           page=page,
                           search_desc=search_desc,
                           type_field=type_field,
                           id_field=id_field,
                          )
