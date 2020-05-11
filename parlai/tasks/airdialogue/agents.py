#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.teachers import FixedDialogTeacher
from .build import build
import os
import json


def _path(opt):
    # build the data if it does not exist
    build(opt)

    # set up path to data (specific to each dataset)
    jsons_path = os.path.join(
        opt['datapath'], 'airdialogue', 'airdialogue_data', 'airdialogue'
    )
    return jsons_path


class AirDialogueTeacher(FixedDialogTeacher):
    """
    AirDialogue Teacher.

    This also contains other files (dev_kb.json, train_kb.json) with flight data
    about return flights, price, connections, flight airlines, departure times,
    and other flight information.
    """

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        jsons_path = _path(opt)
        self.datatype = opt['datatype'].split(':')[0]
        self.messages = []
        self._setup_data(jsons_path)
        self.id = 'airdialogue'
        self.reset()

    def _setup_data(self, jsons_path):
        train_path = os.path.join(jsons_path, 'train_data.json')
        test_valid_path = os.path.join(jsons_path, 'dev_data.json')
        if self.datatype.startswith('test'):
            with open(test_valid_path) as f:
                for line in f:
                    if len(line) > 1:
                        self.messages.append(json.loads(line))
        elif self.datatype.startswith('valid'):
            with open(test_valid_path) as f:
                for line in f:
                    if len(line) > 1:
                        self.messages.append(json.loads(line))
        else:
            with open(train_path) as f:
                for line in f:
                    if len(line) > 1:
                        self.messages.append(json.loads(line))

    def num_examples(self):
        examples = 0
        for data in self.messages:
            examples += len(data['dialogue']) // 2
        return examples

    def num_episodes(self):
        return len(self.messages)

    def get(self, episode_idx, entry_idx=0):
        log_idx = entry_idx * 2
        entry = self.messages[episode_idx]['dialogue'][log_idx]
        entry = entry.split(': ')[1]
        last_backnforth_idx = len(self.messages[episode_idx]['dialogue']) - 2
        episode_done = log_idx >= last_backnforth_idx
        if log_idx < last_backnforth_idx:
            label_text = self.messages[episode_idx]['dialogue'][log_idx + 1]
            label_text = label_text.split(': ')[1]
            labels = [label_text]
        else:
            labels = ['']
        action = {
            'id': self.id,
            'text': entry,
            'episode_done': episode_done,
            'labels': labels,
        }
        return action


class DefaultTeacher(AirDialogueTeacher):
    pass