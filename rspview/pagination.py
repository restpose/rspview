#
# This file is part of the restpose python module, released under the MIT
# license.  See the COPYING file for more information.
"""Pagination support.

"""

from flask import abort, request, url_for

class Page(object):
    def __init__(self, docs, pagenum, hpp=20):
        if pagenum < 1:
            abort(404)
        self.docs = docs[hpp * (pagenum - 1): hpp * pagenum].check_at_least(-1)
        self.pagenum = pagenum
        self.pages = (self.docs.matches_lower_bound + hpp - 1) / hpp
        if pagenum > 1 and len(self.docs) == 0:
            abort(404)

    @property
    def pagenums(self):
        return range(1, self.pages + 1)

def url_for_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

def register(app):
    app.jinja_env.globals['url_for_page'] = url_for_page
