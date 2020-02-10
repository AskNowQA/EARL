import tensorflow as tf
import sys

START_ID=0
PAD_ID = 1
END_ID=2

class PointerWrapper(tf.contrib.seq2seq.AttentionWrapper):
  """Customized AttentionWrapper for PointerNet."""

  def __init__(self,cell,attention_size,memory,initial_cell_state=None,name=None):
    # In the paper, Bahdanau Attention Mechanism is used
    # We want the scores rather than the probabilities of alignments
    # Hence, we customize the probability_fn to return scores directly
    attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(attention_size, memory, probability_fn=lambda x: x )
    # According to the paper, no need to concatenate the input and attention
    # Therefore, we make cell_input_fn to return input only
    cell_input_fn=lambda input, attention: input
    # Call super __init__
    super(PointerWrapper, self).__init__(cell,
                                         attention_mechanism=attention_mechanism,
                                         attention_layer_size=None,
                                         alignment_history=False,
                                         cell_input_fn=cell_input_fn,
                                         output_attention=True,
                                         initial_cell_state=initial_cell_state,
                                         name=name)
  @property
  def output_size(self):
    return self.state_size.alignments

  def call(self, inputs, state):
    _, next_state = super(PointerWrapper, self).call(inputs, state)
    return next_state.alignments, next_state
 

class PointerNet(object):
  """ Pointer Net Model
  
  This class implements a multi-layer Pointer Network 
  aimed to solve the Convex Hull problem. It is almost 
  the same as the model described in this paper: 
  https://arxiv.org/abs/1506.03134.
  """

  def __init__(self, batch_size=128, max_input_sequence_len=5, max_output_sequence_len=7, 
              rnn_size=128, attention_size=128, num_layers=2, beam_width=2,
              learning_rate=0.001, max_gradient_norm=5, forward_only=False):
    """Create the model.

    Args:
      batch_size: the size of batch during training
      max_input_sequence_len: the maximum input length 
      max_output_sequence_len: the maximum output length
      rnn_size: the size of each RNN hidden units
      attention_size: the size of dimensions in attention mechanism
      num_layers: the number of stacked RNN layers
      beam_width: the width of beam search 
      learning_rate: the initial learning rate during training
      max_gradient_norm: gradients will be clipped to maximally this norm.
      forward_only: whether the model is forwarding only
    """

    self.batch_size = batch_size
    self.max_input_sequence_len = max_input_sequence_len
    self.max_output_sequence_len = max_output_sequence_len
    self.forward_only = forward_only
    self.init_learning_rate = learning_rate
    # Note we have three special tokens namely 'START', 'END'
    # Here the size of vocab need be added by 3
    self.vocab_size = max_input_sequence_len+3
    # Global step
    self.global_step = tf.Variable(0, trainable=False)
    # Choose LSTM Cell
    cell = tf.contrib.rnn.LSTMCell
    # Create placeholders
    self.inputs = tf.placeholder(tf.float32, shape=[self.batch_size,self.max_input_sequence_len,803], name="inputs")
    self.outputs = tf.placeholder(tf.int32, shape=[self.batch_size,self.max_output_sequence_len+1], name="outputs")
    self.enc_input_weights = tf.placeholder(tf.int32,shape=[self.batch_size,self.max_input_sequence_len], name="enc_input_weights")
    self.dec_input_weights = tf.placeholder(tf.int32,shape=[self.batch_size,self.max_output_sequence_len], name="dec_input_weights")
    # Calculate the lengths
    enc_input_lens=tf.reduce_sum(self.enc_input_weights,axis=1)
    dec_input_lens=tf.reduce_sum(self.dec_input_weights,axis=1)
    # Special token embedding
    special_token_embedding = tf.get_variable("special_token_embedding", [3,803], tf.float32, tf.contrib.layers.xavier_initializer())
    # Embedding_table
    # Shape: [batch_size,vocab_size,features_size]
    embedding_table = tf.concat([tf.tile(tf.expand_dims(special_token_embedding,0),[self.batch_size,1,1]), self.inputs],axis=1)   
    # Unstack embedding_table
    # Shape: batch_size*[vocab_size,features_size]
    embedding_table_list = tf.unstack(embedding_table, axis=0)
    # Unstack outputs
    # Shape: (max_output_sequence_len+1)*[batch_size]
    outputs_list = tf.unstack(self.outputs, axis=1)
    # targets
    # Shape: [batch_size,max_output_sequence_len]
    self.targets = tf.stack(outputs_list[1:],axis=1)
    # decoder input ids 
    # Shape: batch_size*[max_output_sequence_len,1]
    dec_input_ids = tf.unstack(tf.expand_dims(tf.stack(outputs_list[:-1],axis=1),2),axis=0)
    # encoder input ids 
    # Shape: batch_size*[max_input_sequence_len+1,1]
    enc_input_ids = [tf.expand_dims(tf.range(2,self.vocab_size),1)]*self.batch_size
    # Look up encoder and decoder inputs
    encoder_inputs = []
    decoder_inputs = []
    for i in range(self.batch_size):
      encoder_inputs.append(tf.gather_nd(embedding_table_list[i], enc_input_ids[i]))
      decoder_inputs.append(tf.gather_nd(embedding_table_list[i], dec_input_ids[i]))
    # Shape: [batch_size,max_input_sequence_len+1,2]
    encoder_inputs = tf.stack(encoder_inputs,axis=0)
    # Shape: [batch_size,max_output_sequence_len,2]
    decoder_inputs = tf.stack(decoder_inputs,axis=0)
    # Stack encoder cells if needed
    if num_layers > 1:
      fw_enc_cell = tf.contrib.rnn.MultiRNNCell([cell(rnn_size) for _ in range(num_layers)]) 
      bw_enc_cell = tf.contrib.rnn.MultiRNNCell([cell(rnn_size) for _ in range(num_layers)]) 
    else:
      fw_enc_cell = cell(rnn_size)
      bw_enc_cell = cell(rnn_size)    
    # Tile inputs if forward only
    if self.forward_only:
      # Tile encoder_inputs and enc_input_lens
      encoder_inputs = tf.contrib.seq2seq.tile_batch(encoder_inputs,beam_width)
      enc_input_lens = tf.contrib.seq2seq.tile_batch(enc_input_lens,beam_width)
    # Encode input to obtain memory for later queries
    memory,_ = tf.nn.bidirectional_dynamic_rnn(fw_enc_cell, bw_enc_cell, encoder_inputs, enc_input_lens, dtype=tf.float32)
    # Shape: [batch_size(*beam_width), max_input_sequence_len+1, 2*rnn_size]
    memory = tf.concat(memory, 2) 
    # PointerWrapper
    pointer_cell = PointerWrapper(cell(rnn_size), attention_size, memory)
    # Stack decoder cells if needed
    if num_layers > 1:
      dec_cell = tf.contrib.rnn.MultiRNNCell([cell(rnn_size) for _ in range(num_layers-1)]+[pointer_cell])
    else:
      dec_cell = pointer_cell
    # Different decoding scenario
    if self.forward_only:
      # Tile embedding_table
      tile_embedding_table = tf.tile(tf.expand_dims(embedding_table,1),[1,beam_width,1,1])
      # Customize embedding_lookup_fn
      def embedding_lookup(ids):
        # Note the output value of the decoder only ranges 0 to max_input_sequence_len
        # while embedding_table contains two more tokens' values 
        # To get around this, shift ids
        # Shape: [batch_size,beam_width] 
        ids = ids+2
        # Shape: [batch_size,beam_width,vocab_size]
        one_hot_ids = tf.cast(tf.one_hot(ids,self.vocab_size), dtype=tf.float32)
        # Shape: [batch_size,beam_width,vocab_size,1]
        one_hot_ids = tf.expand_dims(one_hot_ids,-1)
        # Shape: [batch_size,beam_width,features_size]
        next_inputs = tf.reduce_sum(one_hot_ids*tile_embedding_table, axis=2)
        return next_inputs
      # Do a little trick so that we can use 'BeamSearchDecoder'
      shifted_START_ID = START_ID - 2
      shifted_END_ID = END_ID - 2
      # Beam Search Decoder
      decoder = tf.contrib.seq2seq.BeamSearchDecoder(dec_cell, embedding_lookup, 
                                          tf.tile([shifted_START_ID],[self.batch_size]), shifted_END_ID, 
                                          dec_cell.zero_state(self.batch_size*beam_width,tf.float32), beam_width)
      # Decode
      outputs, a, b = tf.contrib.seq2seq.dynamic_decode(decoder)
      self.op = outputs
      # predicted_ids
      # Shape: [batch_size, max_output_sequence_len,  beam_width]
      predicted_ids = outputs.predicted_ids
      # Transpose predicted_ids
      # Shape: [batch_size, beam_width, max_output_sequence_len]
      self.predicted_ids = tf.transpose(predicted_ids,[0,2,1])
    else:
      # Get the maximum sequence length in current batch
      cur_batch_max_len = tf.reduce_max(dec_input_lens)
      # Training Helper
      helper = tf.contrib.seq2seq.TrainingHelper(decoder_inputs, dec_input_lens)    
      # Basic Decoder
      decoder = tf.contrib.seq2seq.BasicDecoder(dec_cell, helper, dec_cell.zero_state(self.batch_size,tf.float32)) 
      # Decode
      outputs, _, _ = tf.contrib.seq2seq.dynamic_decode(decoder,impute_finished=True)
      # logits
      logits = outputs.rnn_output
      self.rnn_output = outputs.rnn_output
      # predicted_ids_with_logits
      self.predicted_ids_with_logits=tf.nn.top_k(logits)
      # Pad logits to the same shape as targets
      logits = tf.concat([logits,tf.ones([self.batch_size,self.max_output_sequence_len-cur_batch_max_len,self.max_input_sequence_len+1])],axis=1)
      # Subtract target values by 2
      # because prediction output ranges from 0 to max_input_sequence_len+1
      # while target values are from 0 to max_input_sequence_len + 3 
      self.shifted_targets = (self.targets - 2)*self.dec_input_weights
      # Losses
      losses = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.shifted_targets, logits=logits)
      # Total loss
      self.loss = tf.reduce_sum(losses*tf.cast(self.dec_input_weights,tf.float32))/self.batch_size
      # Get all trainable variables
      parameters = tf.trainable_variables()
      # Calculate gradients
      gradients = tf.gradients(self.loss, parameters)
      # Clip gradients
      clipped_gradients, _ = tf.clip_by_global_norm(gradients, max_gradient_norm)
      # Optimization
      #optimizer = tf.train.GradientDescentOptimizer(self.init_learning_rate)
      optimizer = tf.train.AdamOptimizer(self.init_learning_rate)
      # Update operator
      self.update = optimizer.apply_gradients(zip(clipped_gradients, parameters),global_step=self.global_step)
      # Summarize
      tf.summary.scalar('loss',self.loss)
      for p in parameters:
        tf.summary.histogram(p.op.name,p)
      for p in gradients:
        tf.summary.histogram(p.op.name,p)
      # Summarize operator
      self.summary_op = tf.summary.merge_all()
      #DEBUG PART
      self.debug_var = logits
      #/DEBUG PART

    # Saver
    self.saver = tf.train.Saver(tf.global_variables(),max_to_keep=0)


  def step(self, session, inputs, enc_input_weights, outputs=None, dec_input_weights=None, update=True):
    """Run a step of the model feeding the given inputs.

    Args:
      session: tensorflow session to use.
      inputs: the point positions in 2D coordinate. shape: [batch_size,max_input_sequence_len,2]
      enc_input_weights: the weights of encoder input points. shape: [batch_size,max_input_sequence_len]              
      outputs: the point indexes in inputs. shape: [batch_size,max_output_sequence_len+1] 
      dec_input_weights: the weights of decoder input points. shape: [batch_size,max_output_sequence_len] 

    Returns:
      (training)
      The summary      
      The total loss
      The predicted ids with logits
      The targets
      The variable for debugging

      (evaluation)
      The predicted ids
    """
    #Fill up inputs 
    input_feed = {}
    input_feed[self.inputs] = inputs
    input_feed[self.enc_input_weights] = enc_input_weights
    if self.forward_only==False:
      input_feed[self.outputs] = outputs
      input_feed[self.dec_input_weights] = dec_input_weights

    #Fill up outputs
    output_feed = []
    if self.forward_only and not update:
      output_feed = [self.predicted_ids,self.op]
    if not self.forward_only and update:
      output_feed = [self.update, self.summary_op, self.loss, self.predicted_ids_with_logits, self.shifted_targets, self.debug_var, self.rnn_output]
    if not update and not self.forward_only:
      output_feed = [self.summary_op, self.loss, self.predicted_ids_with_logits, self.shifted_targets, self.debug_var]

    #Run step
    outputs = session.run(output_feed, input_feed)

    if  update and not self.forward_only:
      return outputs[1],outputs[2],outputs[3],outputs[4],outputs[5],outputs[6]
    if self.forward_only and not update:
      return outputs[0],outputs[1]
    if not update and not self.forward_only:
      return outputs[0],outputs[1],outputs[2],outputs[3],outputs[4]
