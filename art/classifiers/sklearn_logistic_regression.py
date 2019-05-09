# MIT License
#
# Copyright (C) IBM Corporation 2018
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

from art.classifiers import Classifier

logger = logging.getLogger(__name__)


class SklearnLogisticRegression(Classifier):

    def __init__(self, clip_values=(0, 1), model=None, channel_index=None, defences=None, preprocessing=(0, 1)):

        super(SklearnLogisticRegression, self).__init__(clip_values=clip_values, channel_index=channel_index,
                                                        defences=defences, preprocessing=preprocessing)

        self.model = model

    def class_gradient(self, x, label=None, logits=False):
        w = self.model.coef_
        num_classes = len(self.model.classes_)
        num_samples, n_features = x.shape
        gradients = np.zeros_like(x)

        class_weight = compute_class_weight(class_weight=self.model.class_weight, classes=self.model.classes_,
                                            y=np.argmax(y, axis=1))

        y_pred = self.model.predict_proba(X=x)
        w_weighted = np.matmul(y_pred, w)

        for i_sample in range(num_samples):
            for i_class in range(num_classes):
                gradients[i_sample, :] += class_weight[i_class] * y[i_sample, i_class] * (
                        w[i_class, :] - w_weighted[i_sample, :])

        return gradients

    def fit(self, x, y, batch_size=128, nb_epochs=20, **kwargs):
        self.model.fit(X=x, y=y, sample_weight=None)

    def get_activations(self, x, layer, batch_size):
        raise NotImplementedError

    def loss_gradient(self, x, y):
        w = self.model.coef_
        num_classes = len(self.model.classes_)
        num_samples, n_features = x.shape
        gradients = np.zeros_like(x)

        class_weight = compute_class_weight(class_weight=self.model.class_weight, classes=self.model.classes_,
                                            y=np.argmax(y, axis=1))

        y_pred = self.model.predict_proba(X=x)
        w_weighted = np.matmul(y_pred, w)

        for i_sample in range(num_samples):
            for i_class in range(num_classes):
                gradients[i_sample, :] += class_weight[i_class] * (1 - y[i_sample, i_class]) * (
                            w[i_class, :] - w_weighted[i_sample, :])

        return gradients

    def predict(self, x, logits=False, batch_size=128):
        return self.model.predict_proba(X=x)

    def save(self, filename, path=None):
        import pickle
        with open(filename + '.pickle', 'wb') as f:
            pickle.dump(self.model, file=f)

    def set_learning_phase(self, train):
        raise NotImplementedError
