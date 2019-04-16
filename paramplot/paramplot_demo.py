# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Simple demo which writes a bunch of toy metrics to events file in various run directories for tensorboard to read"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import random

import tensorflow as tf
import paramplot_summary
from lib.config_writer import ParamPlotConfigWriter

# Directory into which to write tensorboard data.
LOGDIR = '/tmp/paramplotdemo'


def run(logdir, run_name, tag_value_map, parameter_map):
    """Create a dummy set of events data by logging some fake metrics to the runs directory."""

    tf.reset_default_graph()

    placeholders = {tag: tf.placeholder(tf.float32) for tag in tag_value_map}
    summary_ops = {tag: paramplot_summary.op(
        tag, placeholders[tag]) for tag in tag_value_map}

    run_path = os.path.join(logdir, run_name)
    writer = tf.summary.FileWriter(run_path)
    config_writer = ParamPlotConfigWriter(run_path)

    # Add the parameters to the run config
    for parameter in parameter_map:
        config_writer.AddParameter(parameter, parameter_map[parameter])

    # Write the value under the final_loss summary for that particular run
    with tf.Session() as session:
        for tag_name in tag_value_map:
            summary = session.run(summary_ops[tag_name], feed_dict={
                                  placeholders[tag_name]: tag_value_map[tag_name]})
            writer.add_summary(summary)

    config_writer.Save()
    writer.close()


def run_all(logdir, run_names, tag_value_maps, parameter_maps, unused_verbose=False):
    """Run the simulation for every logdir.
    """
    for run_name in run_names:
        run(logdir, run_name,
            tag_value_maps[run_name], parameter_maps[run_name])


def main(unused_argv):
    print('Saving output to %s.' % LOGDIR)

    runs = ["run1", "run2", "run3", "run4", "run5"]
    tag_value_maps = {
        "run1": {
            "final_loss": random.uniform(0, 12),
            "correlation_validation_train": random.random()
        },
        "run2": {
            "final_loss": random.uniform(0, 12),
            "correlation_validation_train": random.random()
        },
        "run3": {
            "final_loss": random.uniform(0, 12),
            "correlation_validation_train": random.random()
        },
        "run4": {
            "final_loss": random.uniform(0, 12),
            "correlation_validation_train": random.random()
        },
        "run5": {
            "final_loss": random.uniform(0, 12),
            "correlation_validation_train": random.random()
        },
    }

    parameter_maps = {
        "run1": {
            "num_layers": 2,
            "mystery_parameter": 1.1
        },
        "run2": {
            "num_layers": 4,
            "mystery_parameter": 2.3
        },
        "run3": {
            "num_layers": 8,
            "mystery_parameter": 5.4
        },
        "run4": {
            "num_layers": 16,
            "mystery_parameter": 10.74
        },
        "run5": {
            "num_layers": 32,
            "mystery_parameter": 8.29
        }
    }

    run_all(LOGDIR, runs, tag_value_maps, parameter_maps, unused_verbose=True)
    print('Done. Output saved to %s.' % LOGDIR)


if __name__ == '__main__':
    tf.app.run()
