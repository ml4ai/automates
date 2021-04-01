import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class CodeEncoder(nn.Module):
    def __init__(self, vecs, drop=0, hidden_sz=50, num_layers=1, gpu=False):
        super(CodeEncoder, self).__init__()
        self.use_gpu = gpu
        self.HIDDEN_SIZE = hidden_sz
        self.DROPOUT = drop
        self.NUM_LAYERS = num_layers

        # Initialize embeddings from pretrained embeddings
        self.embedding = nn.Embedding.from_pretrained(vecs)

        # Creates a bidirectional LSTM for the code input
        self.bilstm = nn.LSTM(vecs.size()[1],    # Size of the embedding
                              self.HIDDEN_SIZE,  # Size of the hidden layer
                              num_layers=self.NUM_LAYERS,
                              dropout=self.DROPOUT,
                              bidirectional=True)

    def init_hidden(self):
        """
        Initializes the Cell state and Hidden layer vectors of the LSTMs. Each
        LSTM requires a tuple of the form (Cell state, hidden state) to be sent
        in. The states are updated during the forward process and will be
        available after processing.
        """
        # (# layers * # directions, size of batch, size of hidden layer)
        h_0 = torch.zeros(self.NUM_LAYERS * 2, 1, self.HIDDEN_SIZE)
        c_0 = torch.zeros(self.NUM_LAYERS * 2, 1, self.HIDDEN_SIZE)

        if self.use_gpu:    # Transfer vectors to the GPU if using GPU
            h_0 = h_0.cuda()
            c_0 = c_0.cuda()

        return (h_0, c_0)

    def forward(self, code):
        """
        Todo: add docs

        :param data: [Tuple] -- All input data to be sent through the classifier
        :returns: [Tensor] -- A matrix with a vector of output for each instance
        """
        # Prepare the input
        embedded_code = self.embedding(code).unsqueeze(1)

        # self.bilstm.flatten_parameters()
        return self.bilstm(embedded_code, self.init_hidden())


class AttnCommDecoder(nn.Module):
    def __init__(self, vecs, hidden_sz=50, drop=0, attn_drop=0.05,
                 num_layers=1, max_len=3000, gpu=False):
        super(AttnCommDecoder, self).__init__()
        self.use_gpu = gpu
        self.HIDDEN_SIZE = hidden_sz
        self.NUM_LAYERS = num_layers
        self.MAXIMUM_LENGTH = max_len
        self.DROPOUT, self.ATTN_DROPOUT = drop, attn_drop
        (self.VOCAB_SIZE, self.EMBEDDING_SIZE) = vecs.size()
        self.ATTN_SIZE = (2 * self.HIDDEN_SIZE) + self.EMBEDDING_SIZE

        # Initialize embeddings from pretrained embeddings
        self.embedding = nn.Embedding.from_pretrained(vecs)
        self.dropout = nn.Dropout(self.ATTN_DROPOUT)

        self.attn = nn.Linear(self.ATTN_SIZE, self.MAXIMUM_LENGTH)
        self.COMBINE_SIZE = (2 * self.HIDDEN_SIZE) + self.EMBEDDING_SIZE

        # Creates a bidirectional LSTM for the code input
        self.bilstm = nn.LSTM(self.COMBINE_SIZE,  # Size of the embedding
                              self.HIDDEN_SIZE,     # Size of the hidden layer
                              num_layers=self.NUM_LAYERS,
                              dropout=self.DROPOUT,
                              bidirectional=True)

        self.out = nn.Linear(2 * self.HIDDEN_SIZE, self.VOCAB_SIZE)

    def forward(self, token, state, encoder_outputs):
        embedded = self.embedding(token)
        normed_embedded = self.dropout(embedded)

        (h_n, _) = state
        (_, _, hd_sz) = h_n.size()
        hidden = h_n.view(1, 2 * hd_sz)

        attn_encoding = torch.cat((normed_embedded, hidden), 1)
        attn_weights = F.softmax(self.attn(attn_encoding), dim=1)
        attn_applied = torch.mm(attn_weights, encoder_outputs)

        rec_input = F.relu(torch.cat((normed_embedded, attn_applied), 1))
        output, new_state = self.bilstm(rec_input.unsqueeze(0), state)
        output = F.log_softmax(self.out(output.squeeze(0)), dim=1)
        return output, new_state, attn_weights


class CommDecoder(nn.Module):
    def __init__(self, vecs, drop=0, hidden_sz=50, num_layers=1, gpu=False):
        pass
