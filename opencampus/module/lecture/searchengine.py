# -*- coding: utf-8 -*-
# Copyright (C) 2015 opencampus.kr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from elasticsearch import Elasticsearch
from opencampus.server import app


def _get_index_name(campus_id):
    return '%s_lectures' % str(campus_id)


def init_index(campus_id):
    es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))
    try:
        es.indices.close(index=_get_index_name(campus_id))
    except:
        pass
    try:
        es.indices.put_settings(index=_get_index_name(campus_id), body={
            "index": {
                "analysis": {
                    "analyzer": {
                        "korean": {
                            "type": "custom",
                            "tokenizer": "mecab_ko_standard_tokenizer"
                        }
                    }
                }
            }
        })
    except:
        es.indices.create(index=_get_index_name(campus_id), body={
            "settings": {
                "index": {
                    "analysis": {
                        "analyzer": {
                            "korean": {
                                "type": "custom",
                                "tokenizer": "mecab_ko_standard_tokenizer"
                            }
                        }
                    }
                }
            }
        })

    es.indices.open(index=_get_index_name(campus_id))
    try:
        es.indices.delete_mapping(index=_get_index_name(campus_id), doc_type='lecture')
    except:
        pass
    es.indices.put_mapping(index=_get_index_name(campus_id), doc_type='lecture', body={
        "_all": {
            "analyzer": "korean"
        }
    })


def index(lecture):
    es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))
    es.index(index=_get_index_name(lecture.campus_id), doc_type='lecture', id=str(lecture.id), body={
        'year': lecture.year,
        'term_code': lecture.term,
        'term': lecture.get_term_text(),
        'code': lecture.code,
        'type': lecture.type,
        'subject_code': lecture.subject_code,
        'subject_name': lecture.subject_name,
        'credit': lecture.credit,
        'grade': lecture.grade,
        'departments': lecture.departments,
        'professors': lecture.professors,
        'tags': lecture.tags
    })


def search(campus_id, query, page, size=24, year=None, term=None):
    from opencampus.module.lecture.models import Lecture
    results = []

    page -= 1

    if query == '':
        if not year or not term:
            query = Lecture.objects(campus_id=campus_id)
        else:
            query = Lecture.objects(campus_id=campus_id, year=year, term=term)

        for lecture in query.skip(page*size).limit(size):
            results.append({
                'year': lecture.year,
                'term_code': lecture.term,
                'term': lecture.get_term_text(),
                'code': lecture.code,
                'type': lecture.type,
                'subject_code': lecture.subject_code,
                'subject_name': lecture.subject_name,
                'credit': lecture.credit,
                'grade': lecture.grade,
                'departments': lecture.departments,
                'professors': lecture.professors,
                'tags': lecture.tags if lecture.tags else [],
                'term_str': Lecture.term_int_to_str(lecture.term)
            })
    else:
        es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))

        search_body = {
            'from': page*size,
            'size': size,
            'sort': ['_score', {'year': 'desc'}, {'term_code': 'desc'}],
            'query': {
                'bool': {
                    'must': [
                        {
                            'query_string': {
                                'default_field': '_all',
                                'query': query
                            }
                        }
                    ]
                }
            }
        }

        if year and term:
            search_body['query']['bool']['must'] += [
                {
                    'term': {
                        'lecture.year': year
                    }
                },
                {
                    'term': {
                        'lecture.term_code': term
                    }
                }
            ]

        res = es.search(index=_get_index_name(campus_id), body=search_body)

        for lecture in res.get('hits').get('hits'):
            lecture = lecture.get('_source')
            lecture['term_str'] = Lecture.term_int_to_str(lecture['term_code'])
            results.append(lecture)

    return results
