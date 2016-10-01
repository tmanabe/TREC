#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import csv
import re


class Query(dict):
    linebreak = '\n'
    separator = ':'

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                query_id, query = line.split(Query.separator, 1)
                self[query_id] = query.rstrip()
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for k in sorted(list(self.keys())):
                file.write(Query.separator.join([str(k), self[k]]))
                file.write(Query.linebreak)
        return self


class ProbabilisticRelevance(dict):
    linebreak = '\n'
    separator = ' '

    class relevance(int):
        def __new__(self,
                    relevance='0',
                    method_id='-1',
                    probability='nan'):
            self = int.__new__(self, relevance)
            self.method_id = method_id
            self.probability = float(probability)
            return self

    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(self.relevance))
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 4)
                query_id, document_id = l[0:2]
                relevance = self.relevance(*l[2:])
                self[query_id]['0'][document_id] = relevance
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                from_d = self[query_id]['0']
                for document_id in sorted(list(from_d.keys())):
                    relevance = from_d[document_id]
                    if not isinstance(relevance, self.relevance):
                        relevance = self.relevance(relevance)
                    l = [
                        query_id,
                        document_id,
                        str(relevance),
                        relevance.method_id,
                        str(relevance.probability),
                    ]
                    file.write(ProbabilisticRelevance.separator.join(l))
                    file.write(ProbabilisticRelevance.linebreak)
        return self


class Relevance(dict):
    linebreak = '\n'
    separator = ' '

    def __missing__(self, query_id):
        self[query_id] = defaultdict(lambda: defaultdict(int))
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 3)
                query_id, intent_id, document_id, relevance = l
                relevance = int(relevance)
                self[query_id][intent_id][document_id] = relevance
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                from_i = self[query_id]
                for intent_id in sorted(list(from_i.keys())):
                    from_d = from_i[intent_id]
                    for document_id in sorted(list(from_d.keys())):
                        relevance = from_d[document_id]
                        l = [
                            query_id,
                            intent_id,
                            document_id,
                            str(relevance),
                        ]
                        file.write(Relevance.separator.join(l))
                        file.write(Relevance.linebreak)
        return self


class Result(dict):
    linebreak = '\n'

    class query_id(str):
        def __new__(self, query_id, run_id='_'):
            self = str.__new__(self, query_id)
            self.run_id = run_id
            return self

    def __missing__(self, query_id):
        self[query_id] = {}
        return self[query_id]

    def read(self, path):
        with open(path, 'r') as file:
            for d in csv.DictReader(file):
                query_id = self.query_id(query_id=d.pop('topic'),
                                         run_id=d.pop('runid').rstrip())
                l = self[query_id]
                for measure in d:
                    value = float(d[measure])
                    if(value != value):  # NaN
                        l[measure] = None
                    else:
                        l[measure] = value
        return self

    def write(self, path):
        fieldnames = ['runid', 'topic']
        fieldnames += list(self[list(self.keys())[0]].keys())
        with open(path, 'w', newline=Result.linebreak) as file:
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            for query_id in sorted(list(self.keys())):
                d_s = self[query_id]
                if not isinstance(query_id, self.query_id):
                    query_id = self.query_id(query_id)
                d_d = {'runid': query_id.run_id, 'topic': query_id}
                for measure in d_s:
                    value = d_s[measure]
                    if value is None:
                        d_d[measure] = '-nan'
                    else:
                        d_d[measure] = '{0:.6f}'.format(value)
                writer.writerow(d_d)
        return self


class Run(dict):
    linebreak = '\n'
    separator = ' '

    class document_id(str):
        def __new__(self, document_id, score, key='Q0', run_id='_'):
            self = str.__new__(self, document_id)
            self.score = score
            self.key = key
            self.run_id = run_id
            return self

    def __missing__(self, query_id):
        self[query_id] = []
        return self[query_id]

    def read(self, path):
        query_id_to_pairs = defaultdict(list)
        with open(path, 'r') as file:
            for line in file:
                l = re.split('\\s+', line.strip(), 5)
                query_id, key, document_id, rank, score, run_id = l
                query_id_to_pairs[query_id].append([
                    -float(score),
                    self.document_id(document_id,
                                     score=score,
                                     key=key,
                                     run_id=run_id),
                ])
        for query_id in query_id_to_pairs:
            pairs = query_id_to_pairs[query_id]
            l = self[query_id]
            for pair in sorted(pairs):
                l.append(pair[-1])
        return self

    def write(self, path):
        with open(path, 'w') as file:
            for query_id in sorted(list(self.keys())):
                document_ids = self[query_id]
                rank = 1.0
                for document_id in document_ids:
                    if not isinstance(document_id, self.document_id):
                        document_id = self.document_id(document_id,
                                                       score=-rank)
                    l = [
                        query_id,
                        document_id.key,
                        document_id,
                        str(rank),
                        str(document_id.score),
                        document_id.run_id,
                    ]
                    file.write(Run.separator.join(l))
                    file.write(Run.linebreak)
                    rank += 1.0
        return self
