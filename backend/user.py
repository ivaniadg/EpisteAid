import pickle
import os
import json
from .models.rocchio import Rocchio
from .models.bm25 import BM25
from .utils import binary_search
from datetime import datetime as dt
from config_params import STUDY_RESULTS_PATH
relevance_opposite = {1: -1, -1: 1}
MODELS = {"Rocchio": Rocchio, "BM25": BM25}
import time

class User:
    def __init__(self, id_, experiments, finished_experiments, current_experiment, get_document, get_representation, files_path, row2doc):

        self.id_ = id_
        self.experiments = experiments
        self.finished_experiments = finished_experiments
        self.get_representation = get_representation
        self.get_document = get_document
        self.files_path = files_path
        self.row2doc = row2doc
        self.current_transformation = "pca"
        self.current_experiment = current_experiment
        if self.current_experiment is None:
            self.start_experiment()

    @classmethod
    def load(cls, id_, get_document, get_representation, files_path, row2doc):
        with open(os.path.join(files_path, "{}.user".format(id_)), 'r') as f:
            user = json.load(f)
        if user['current_experiment']:
            user['current_experiment'] = Experiment.load(os.path.join(files_path, "{}-{}.experiment".format(id_, user["current_experiment"])),
                get_document, get_representation, row2doc)
            if user['current_experiment'].survey == 'FinishedSurvey':
                user['current_experiment'] = None
        return cls(id_, user["experiments"], user["finished_experiments"], user["current_experiment"], get_document, get_representation, files_path,
                   row2doc)

    def set_time_experiment(self, minutes, seconds):
        self.current_experiment.minutes_passed = minutes
        self.current_experiment.seconds_passed = seconds

    def save(self):
        if self.current_experiment:
            self.current_experiment.save(os.path.join(self.files_path, "{}-{}.experiment".format(self.id_, self.current_experiment.name)))
        with open(os.path.join(self.files_path, "{}.user".format(self.id_)), 'w+') as f:
            json.dump({"id_": self.id_, "experiments": self.experiments, "finished_experiments": self.finished_experiments,
                       "current_experiment": self.current_experiment.name if self.current_experiment else None}, f)

    def start_experiment(self):
        experiment = self.experiments.pop(0)
        self.current_experiment = Experiment(experiment['document_set_id'], experiment['initial_document'], experiment["title"], self.get_document,
                                             self.get_representation, experiment['interface'], MODELS[experiment['model']],
                                             experiment['model_params'], self.row2doc, 'ExperimentNotFinished', minutes_passed=experiment['minutes_passed'], seconds_passed=experiment['seconds_passed'], known_documents=experiment["known_documents"])
        self.current_experiment.transform = 'pca'

    def finish_experiment(self):
        name = "{}-{}.experiment".format(self.id_, self.current_experiment.name)
        self.current_experiment.survey = 'Starting'
        self.finished_experiments.append(name)
        self.current_experiment.save_results(self.id_)

    def finish_survey_experiment(self):
        name = "{}-{}.experiment".format(self.id_, self.current_experiment.name)
        self.current_experiment.survey = 'FinishedSurvey'
        self.current_experiment.save(os.path.join(self.files_path, name))

    def add_feedback(self, docs, relevance, actions):
        self.current_experiment.actions.extend(actions)
        for d, r in zip(docs, relevance):
            self.current_experiment.add_feedback(d, r)
        self.current_experiment.fit_model()

    def get_rank_documents(self, show_rank, ids):
        return self.current_experiment.rank_documents(show_rank, ids)

    def get_current_state(self, show_rank):
        known_docs, known_classes = self.current_experiment.get_docs_classes()
        # 2. Get current shown docs
        if len(self.current_experiment.current_shown_documents) == 0:
            distance, next_documents = self.current_experiment.rank_documents(show_rank, None)
        else:
            next_documents = self.current_experiment.current_shown_documents[-1]
        return next_documents, known_classes, known_docs, self.current_experiment.actions

    def get_experiments_left(self):
        return len(self.experiments)


class Experiment:
    def __init__(self, document_set_id, initial_document, title, get_document, get_representation, interface, model, model_params, row2doc, survey, minutes_passed=0, seconds_passed=0,known_documents=None):
        # document set
        self.document_set_id = document_set_id
        self.initial_document = initial_document
        self.title = title

        # db
        self.get_document = get_document
        self.get_representation = get_representation
        self.row2doc = row2doc

        # experiment conditions
        self.interface = interface
        self.minutes_passed = minutes_passed
        self.seconds_passed = seconds_passed

        if known_documents is None:
            self.known_documents = {initial_document: 1}
        else:
            self.known_documents = known_documents
            self.known_documents[initial_document] = 1

        if known_documents is None:
            self.model = model(self.get_document(initial_document), **model_params).fit(None,
                                                                                    None)  # Cuando comenzamos el modelo ya está fiteado con params iniciales
        else:
            self.model = model(self.get_document(initial_document), **model_params)
            self.fit_model()
        self.name = "{}-{}-{}".format(document_set_id, model.__name__, self.interface)

        # user generated data
        self.actions = [[{'start': dt.now().timestamp(), "id": initial_document, "relevance": 1}]]  # (num_action, doc, relevance)

        self.current_shown_documents = list()
        self.shown_documents = list()
        self.survey = survey

    def save(self, file_name):
        with open(file_name, 'wb+') as f:
            pickle.dump(self, f)

    def __getstate__(self):
        dict_ = self.__dict__.copy()
        del dict_["get_representation"]
        del dict_["get_document"]
        return dict_

    def __setstate__(self, state):
        state['get_representation'] = None
        state["get_document"] = None
        state["row2doc"] = None
        self.__dict__ = state

    @classmethod
    def load(cls, file_name, get_document, get_representation, row2doc):
        with open(file_name, 'rb') as f:
            obj = pickle.load(f)
            obj.get_representation = get_representation
            obj.get_document = get_document
            obj.row2doc = row2doc
        return obj

    def save_results(self, user):
        name = "{user}-{document_set}-{interface}-{model}.results.json".format(user=user, document_set=self.document_set_id,
                                                                  interface=self.interface, model=self.model.name)
        file_name = os.path.join(os.path.abspath(STUDY_RESULTS_PATH), name)
        data = dict(actions=self.actions, known_documents=self.known_documents,user=user, document_set=self.document_set_id,
                                    interface=self.interface, model=self.model.name)

        with open(file_name, "w+") as f:
            json.dump(data, f)

    def add_feedback(self, doc, relevance_):
        # 0. Agregar acción
        if doc in self.current_shown_documents[-1]:
            self._remove_from_list(self.current_shown_documents[-1], doc)
        if relevance_ == 0 and doc in self.known_documents:
            del self.known_documents[doc]
        else:
            self.known_documents[doc] = relevance_

    def get_x_docs(self, relevance):
        return filter(lambda d: self.known_documents[d] == relevance, self.known_documents)

    @staticmethod
    def _remove_from_list(list_, item):
        try:
            list_.remove(item)
        except ValueError:
            pass

    def fit_model(self):
        # 1. Representación
        docs = self._get_docs()
        X, y = self.get_representation(docs, sorted(self.get_x_docs(1)))

        # 2. Fit
        self.model.fit(X, y)

    def rank_documents(self, show_rank_, ids):
        if show_rank_ is None and ids is None:
            raise ValueError("show_rank and ids cannot be both None")

        # 1. Obtener representación
        X, _ = self.get_representation(ids, None)

        # 2. Cuántos queremos ver?
        if show_rank_ is None:
            show_rank = len(ids)
        else:
            show_rank = show_rank_ + len(self.known_documents)

        # 2. Rerankear
        #print(time.gmtime(), 'ranking')
        _, order = self.model.rank_relevant(X, show_rank)
        #print(time.gmtime(), 'filtering')
        # 3. Filtrar los repetidos y obtener ids del orden
        ids = self._get_filtered_rank(order)
        #print(time.gmtime())
        # 4. Guardar los que se sugieren
        self.current_shown_documents.append(ids[:show_rank_])
        self.shown_documents.append(ids[:show_rank_].copy())
        return None, ids[:show_rank_]

    def _get_filtered_rank(self, order):
        current_ids = self._get_docs()
        current_ids.sort()
        ids = list()
        for position in order:
            try:
                id_ = self.row2doc[position]
            except KeyError:
                continue
            if binary_search(current_ids, id_) == -1:
                ids.append(id_)

        return ids

    def get_docs_classes(self):
        docs, classes = [], []
        for k, v in self.known_documents.items():
            docs.append(k)
            classes.append(v)
        return docs, classes

    def _get_docs(self):
        return list(self.known_documents.keys())
