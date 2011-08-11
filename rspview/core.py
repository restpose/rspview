#!/usr/bin/env python
# -*- coding: utf-8 -
#
# This file is part of the restpose python module, released under the MIT
# license.  See the COPYING file for more information.
"""Simple webapp for browsing contents of a restpose server.

"""

from flask import Flask, render_template, request
import restpose
from . import pagination
from . import search
from .version import __version__

app = Flask(__name__)
server = restpose.Server()

pagination.register(app)

@app.route('/')
def frontpage():
    return render_template('index.html',
                           coll_count=len(server.collections),
                           version=__version__,
                          )

@app.route('/coll/')
def coll_list():
    return render_template('coll_list.html',
                           collections=server.collections,
                          )

@app.route('/coll/<coll_name>/')
def coll_view(coll_name):
    coll = server.collection(coll_name)
    status = coll.status
    collconfig = coll.config
    return render_template('coll_view.html',
                           coll=coll,
                           doc_count=status['doc_count'],
                           collconfig=collconfig,
                           taxonomies=coll.taxonomies(),
                          )

@app.route('/coll/<coll_name>/all', defaults=dict(page=1))
@app.route('/coll/<coll_name>/all/page/<int:page>')
def docs_list(coll_name, page):
    coll = server.collection(coll_name)
    return search.do_search(coll, coll.all(), "All documents", page)

@app.route('/coll/<coll_name>/type/<type_name>')
def type_view(coll_name, type_name):
    coll = server.collection(coll_name)
    collconfig = coll.config
    type = collconfig['types'][type_name]
    type_q = coll.doc_type(type_name)
    type_count = len(type_q.all())

    fields = []
    special_field_names = set(collconfig['special_fields'].values())
    for fieldname, params in type['fields'].items():
        if fieldname not in special_field_names:
            count = len(type_q.field(fieldname).exists())
            fields.append([fieldname, params, count])
    fields.sort(key=lambda x: (-x[2], x[0]))

    special_fields = []
    for fieldname in (collconfig['special_fields'].get('id_field', None),
                      collconfig['special_fields'].get('type_field', None),
                      collconfig['special_fields'].get('meta_field', None)):
        if fieldname is None:
            continue
        params = type['fields'].get(fieldname, None)
        if params is None:
            continue
        special_fields.append([fieldname, params, type_count])

    return render_template('type_view.html',
                           coll=coll,
                           special_fields=special_fields,
                           type=type,
                           type_name=type_name,
                           type_count=type_count,
                           fields=fields,
                          )

@app.route('/coll/<coll_name>/type/<type_name>/all', defaults=dict(page=1))
@app.route('/coll/<coll_name>/type/<type_name>/all/page/<int:page>')
def type_docs_list(coll_name, type_name, page):
    coll = server.collection(coll_name)
    return search.do_search(coll, coll.doc_type(type_name).all(),
                            "Documents of type \'%s\'" % type_name, page)

@app.route('/coll/<coll_name>/search', defaults=dict(type_name='', page=1))
@app.route('/coll/<coll_name>/search/page/<int:page>', defaults=dict(type_name=''))
@app.route('/coll/<coll_name>/type/<type_name>/search', defaults=dict(page=1))
@app.route('/coll/<coll_name>/type/<type_name>/search/page/<int:page>')
def search_view(coll_name, type_name, page):
    coll = server.collection(coll_name)
    if type_name != '':
        target = coll.doc_type(type_name)
        desc = "Documents of type '%s'" % type_name
    else:
        target = coll
        desc = ''
    args = request.args
    q = None

    field_exists = args.getlist('field_exists')
    if field_exists:
        qs = restpose.Or(*[restpose.Field(f).exists() for f in field_exists])
        for num, f in enumerate(field_exists):
            if num == 0:
                desc += " where field '%s' exists" % f
            else:
                desc += " or field '%s' exists" % f
    if q is None:
        docs = target.all()
    else:
        docs = target.find(q)
    return search.do_search(coll, docs, desc, page)

@app.route('/coll/<coll_name>/taxonomy/<taxonomy_name>')
def taxonomy_view(coll_name, taxonomy_name):
    coll = server.collection(coll_name)
    return render_template('taxonomy_view.html',
                           coll=coll,
                           taxonomy=coll.taxonomy(taxonomy_name),
                          )

@app.route('/coll/<coll_name>/taxonomy/<taxonomy_name>/id/<catid>')
def taxonomy_cat_view(coll_name, taxonomy_name, catid):
    coll = server.collection(coll_name)
    taxonomy = coll.taxonomy(taxonomy_name)
    cat = taxonomy.get_category(catid)
    return render_template('taxonomy_cat_view.html',
                           coll=coll,
                           taxonomy=taxonomy,
                           catid=catid,
                           cat=cat,
                          )
