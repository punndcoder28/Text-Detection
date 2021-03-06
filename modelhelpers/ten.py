import os
from keras import backend as K
from keras.models import load_model
import tensorflow as tf
from modelhelpers.tbpp_model import TBPP512, TBPP512_dense
from modelhelpers.tbpp_utils import PriorUtil
from modelhelpers.ssd_data import InputGenerator
from utils.model import load_weights
from utils.training import Logger

input_shape = (512,512,3)

Model = TBPP512_dense
sl_model = Model(input_shape)
weights_path = 'weights.022.h5'
sl_model.load_weights(weights_path, by_name=True)


model = sl_model


for out in model.outputs:
    print(dir(out))

def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    from tensorflow.python.framework.graph_util import convert_variables_to_constants
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        # Graph -> GraphDef ProtoBuf
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = convert_variables_to_constants(session, input_graph_def,
                                                      output_names, freeze_var_names)
        return frozen_graph


frozen_graph = freeze_session(K.get_session(),
                              output_names=[out.op.name for out in sl_model.outputs])

tf.train.write_graph(frozen_graph, "model_new", "tf_model_final1.pb", as_text=False)
