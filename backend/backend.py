import json
from .models.dimensionality_reduction import TRANSFORMATIONS, reduce_dimensions
from db_connection import DB

from .data_transform_bow import get_bow_representation, get_bow, \
    remove_zero_columns, get_document
import os
from .utils import binary_search
from collections import defaultdict
from .user import User

import time


class Server:
    def __init__(self, inputpath, dbname, dbuser, dbpass, dbhost, data_config, show_rank=100):
        self.users = {}
        self.conn = DB(user=dbuser, host=dbhost,
                                    passwd=dbpass, db=dbname).connect()
        self.all_docs, self.doc2row, self.row2doc = get_bow(inputpath,
                                                            self.conn, data_config)
        self.show_rank = show_rank
        self.get_bow_representation = get_bow_representation(self.doc2row,
                                                             self.all_docs)
        self.get_document = get_document(self.doc2row, self.all_docs)
        self.files_path = inputpath

    @staticmethod
    def get_transformations():
        return TRANSFORMATIONS

    # -------- SURVEY --------- #

    def set_survey_applied(self, user_id):
        try:
            with open(os.path.join(self.files_path, "{}.user".format(user_id)), 'r') as f:
                user = json.load(f)
            user["initial_survey"] = True

            with open(os.path.join(self.files_path, "{}.user".format(user_id)), 'w') as f:
                json.dump(user, f)

        except FileNotFoundError:
            return None

    def get_init_survey_data(self, user_id):
        try:
            with open(os.path.join(self.files_path, "{}.user".format(user_id)), 'r') as f:
                user = json.load(f)
                if "initial_survey" in user:
                    return user["initial_survey"]
                else:
                    return True
        except FileNotFoundError:
            return None

    def do_survey_now(self, user_id):
        experiment = self.users[user_id].current_experiment
        return experiment.survey

    def get_final_survey_data(self, user_id):
        experiment = self.users[user_id].current_experiment
        return experiment.document_set_id, experiment.interface, experiment.model.name

    # --------- USER --------- #

    def get_user(self, user_id):
        if user_id not in self.users:
            try:
                self.users[user_id] = User.load(user_id, self.get_document,
                                                self.get_bow_representation,
                                                self.files_path, self.row2doc)
            except FileNotFoundError:
                return None
        return self.users[user_id]

    def save_user(self, user_id, minutes, seconds):
        if not (minutes == seconds == 0):
            self.users[user_id].set_time_experiment(minutes, seconds)
        self.users[user_id].save()

    def remove_user(self, user_id):
        # Esto es por seguridad. Es para que un usuario se pueda modificar solo si la sesión está abierta
        del self.users[user_id]

    # -------- USER Actions --------- #

    def add_feedback(self, user_id, documents, relevance, actions):
        user = self.users[user_id]
        #print(time.gmtime(), "fit")
        user.add_feedback(documents, relevance, actions)
        #print(time.gmtime(), "rank")
        _, new_ids = user.get_rank_documents(self.show_rank, None)
        #print(time.gmtime())
        ## Agregamos nuevos documentos. De estos debemos obtener su información
        metadata, metadata_dict = self._get_documents_metadata(new_ids)
        known_docs, known_classes = user.current_experiment.get_docs_classes()
        if user.current_experiment.interface == "viz":
            coordinates = list(self._get_documents_transformed(known_docs + new_ids, user.current_transformation, classes=known_classes + [0 for _ in range(len(new_ids))]))
            coordinates = coordinates[-len(new_ids):]
        else:
            coordinates = map(lambda x: {'x': 0, 'y': 0}, new_ids)
        revisions = self._get_documents_revisions(new_ids, metadata_dict)
        documents = []
        for meta, coord, r in zip(metadata, coordinates, revisions):
            meta.update(coord)
            meta['revisions'] = r
            meta['relevance'] = 0
            documents.append(meta)
        return documents

    def _get_documents_revisions(self, ids, meta):
        filtered_ids = list(filter(lambda x: meta[x]['type'] not in ['broad-synthesis', 'structured-summary-of-systematic-review','systematic-review', 'overview'], ids ))
        #print(time.gmtime(), "rev")
        # Obtener la info desde la db
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT from_document, title, to_document from doc_ref_doc_simple"
                           " where to_document in ('{}') and classification in "
                           "('broad-synthesis', 'structured-summary-of-systematic-review','systematic-review', 'overview')".format("','".join(filtered_ids)))
            docs = cursor.fetchall()
        #print(time.gmtime())
        docs_revisions = defaultdict(list)
        for d in docs:
            revision = dict(zip(['id', 'title'], d[:2]))
            docs_revisions[d[-1]].append(revision)

        docs_revisions = [docs_revisions[i] if i in docs_revisions.keys() else list() for i in ids]
        return docs_revisions

    def _get_documents_metadata(self, ids):
        # Obtener la info desde la db
        #print(time.gmtime(), "data")
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, abstract, authors, year, classification, rct from document where id in ('{}')".format(
                    "','".join(ids)))
            docs = cursor.fetchall()
        #print(time.gmtime())
        docs = {k["id"]: k for k in map(lambda c: dict(zip(
            ['id', 'title', 'abstract', "authors", "year", "type",
             "rct", 'relevance'], c)), docs)}
        for v in docs.values():
            try:
                a = json.loads(v['authors'])
                if a:
                    v['authors'] = ", ".join(a)
                else:
                    v['authors'] = "Unknown"
            except json.JSONDecodeError:
                continue

        docs_to_return = [docs[i] for i in ids]
        return docs_to_return, docs

    def _get_documents_transformed(self, ids, transformation, classes=None):
        rows = [self.doc2row[id_] for id_ in ids]
        bow = self.all_docs[rows]
        bow = remove_zero_columns(bow[bow.getnnz(1) > 0]).toarray()
        data_new_dimensions = reduce_dimensions(transformation, bow, classes=classes)
        return map(lambda coord: {'x': float(coord[0]), 'y': float(coord[1])},
                data_new_dimensions)

    def get_documents_info(self, ids, transformation, classes, get_cordinates=True):
        metadata, metadata_dict = self._get_documents_metadata(ids)
        revisions = self._get_documents_revisions(ids, metadata_dict)
        if get_cordinates:
            coordinates = self._get_documents_transformed(ids, transformation, classes=classes)
        else:
            coordinates = map(lambda x: {'x': 0, 'y': 0}, ids)

        documents = []
        for meta, coord, r, c in zip(metadata, coordinates, revisions, classes):
            meta.update(coord)
            meta['revisions'] = r
            meta['relevance'] = c
            documents.append(meta)
        return documents

    def load_experiment(self, user_id):
        user = self.get_user(user_id)

        # 1. Get ids
        next_documents, known_classes, known_docs, actions = user.get_current_state(
            self.show_rank)

        # 2. Get meta and positions
        current_experiment = user.current_experiment
        documents = self.get_documents_info(known_docs + next_documents,
                                            user.current_transformation,
                                            known_classes + [0] * len(
                                                next_documents), get_cordinates=current_experiment.interface == 'viz')

        return documents, (current_experiment.title, actions, (current_experiment.document_set_id, current_experiment.model.name, current_experiment.interface, current_experiment.minutes_passed, current_experiment.seconds_passed))

    def change_transformation(self, user_id, transformation, ids, classes):
        self.users[user_id].current_transformation = transformation
        coordinates = self._get_documents_transformed(ids, transformation, classes=classes)
        documents = []
        for i, coord in zip(ids, coordinates):
            aux = {'id': i}
            aux.update(coord)
            documents.append(aux)
        return documents

    def finish_experiment(self, user_id):
        user = self.users[user_id]
        user.finish_experiment()

    def start_experiment(self, user_id):
        user = self.users[user_id]
        user.start_experiment()
        return self.load_experiment(user_id)

    def get_experiments_left(self, user_id):
        return self.get_user(user_id).get_experiments_left()


