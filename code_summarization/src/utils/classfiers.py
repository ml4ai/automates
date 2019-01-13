import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn import functional as F


class CodeCommClassifier(nn.Module):
    """
    PyTorch Neural Network model consisting of two Bi-directional LSTMs whose
    outputs are concatenated and then fed through a classification layer.
    One LSTM runs over the code input and the other runs over the docstring.
    """
    def __init__(self, cd_vecs, cm_vecs, cls_sz=1, cd_drp=0, cm_drp=0,
                 cd_hd_sz=50, cm_hd_sz=50, cd_nm_lz=1, cm_nm_lz=1, gpu=False):
        super(CodeCommClassifier, self).__init__()
        self.use_gpu = gpu

        # Initialize embeddings from pretrained embeddings
        self.code_embedding = nn.Embedding.from_pretrained(cd_vecs)
        self.comm_embedding = nn.Embedding.from_pretrained(cm_vecs)

        self.NUM_CLASSES = cls_sz
        self.CODE_PRCT_DROPOUT, self.COMM_PRCT_DROPOUT = cd_drp, cm_drp
        self.CODE_HD_SZ, self.COMM_HD_SZ = cd_hd_sz, cm_hd_sz
        self.CODE_NUM_LAYERS, self.COMM_NUM_LAYERS = cd_nm_lz, cm_nm_lz

        # Creates a bidirectional LSTM for the code input
        self.code_lstm = nn.LSTM(cd_vecs.size()[1],     # Size of the code embedding
                                 self.CODE_HD_SZ,       # Size of the hidden layer
                                 num_layers=self.CODE_NUM_LAYERS,
                                 dropout=self.CODE_PRCT_DROPOUT,
                                 batch_first=True,
                                 bidirectional=True)

        # Creates a bidirectional LSTM for the docstring input
        self.comm_lstm = nn.LSTM(cm_vecs.size()[1],     # Size of the code embedding
                                 self.COMM_HD_SZ,       # Size of the hidden layer
                                 num_layers=self.COMM_NUM_LAYERS,
                                 dropout=self.COMM_PRCT_DROPOUT,
                                 batch_first=True,
                                 bidirectional=True)

        # Size of the concatenated output from the 2 LSTMs
        self.CONCAT_SIZE = (self.CODE_HD_SZ + self.COMM_HD_SZ) * 2

        # FFNN layer to transform LSTM output into class predictions
        self.lstm2hidden = nn.Linear(self.CONCAT_SIZE, 50)
        self.hidden2label = nn.Linear(50, self.NUM_CLASSES)

    def forward(self, data):
        """
        Processes the forward pass through the classifier of a batch of data.
        The batch outputs from the last feed-forward layer of the classifier
        are returned as output.

        :param data: [Tuple] -- All input data to be sent through the classifier
        :returns: [Tensor] -- A matrix with a vector of output for each instance
        """
        (code, code_lengths, comm, comm_lengths) = data
        if self.use_gpu:    # Send data to GPU if available
            code = code.cuda()
            comm = comm.cuda()

        # Transform the input to LSTM form: (batch, sequence, embedding)
        code = code.transpose(0, 1)
        comm = comm.transpose(0, 1)

        # keep track of how code and comm were sorted so that we can unsort them later
        # because packing requires them to be in descending order
        code_lengths, code_sort_order = code_lengths.sort(descending=True)
        comm_lengths, comm_sort_order = comm_lengths.sort(descending=True)
        code_inv_order = code_sort_order.sort()[1]
        comm_inv_order = comm_sort_order.sort()[1]

        # Encode the batch input using word embeddings
        code_encoding = self.code_embedding(code[code_sort_order])
        comm_encoding = self.comm_embedding(comm[comm_sort_order])

        # pack padded input
        code_enc_pack = torch.nn.utils.rnn.pack_padded_sequence(code_encoding, code_lengths, batch_first=True)
        comm_enc_pack = torch.nn.utils.rnn.pack_padded_sequence(comm_encoding, comm_lengths, batch_first=True)

        # Run the LSTMs over the packed input
        code_enc_pad, (code_h_n, code_c_n) = self.code_lstm(code_enc_pack)
        comm_enc_pad, (comm_h_n, comm_c_n) = self.comm_lstm(comm_enc_pack)

        # back to padding
        code_vecs, _ = torch.nn.utils.rnn.pad_packed_sequence(code_enc_pad, batch_first=True)
        comm_vecs, _ = torch.nn.utils.rnn.pad_packed_sequence(comm_enc_pad, batch_first=True)

        # Concatenate the final output from both LSTMs
        recurrent_vecs = torch.cat((code_h_n[0,code_inv_order], code_h_n[1,code_inv_order], comm_h_n[0,comm_inv_order], comm_h_n[1,comm_inv_order]), 1)

        # Transform recurrent output vector into a class prediction vector
        y = F.relu(self.lstm2hidden(recurrent_vecs))
        y = self.hidden2label(y)
        return y


class CodeOnlyClassifier(nn.Module):
    """
    PyTorch Neural Network model consisting of a Bi-directional LSTM whose
    output is fed through a classification layer. This classifier only processes
    an LSTM over code input.

    NOTE: This classifier is built to fail, as classification should not be
          possible without seeing both the code and docstring.

    NOTE: For documentation on the functions of this class, refer to the docs
          for the CodeCommClassifier class
    """
    def __init__(self, cd_vecs, cls_sz=2, cd_drp=0, cd_hd_sz=50, cd_nm_lz=1, gpu=False):
        super(CodeOnlyClassifier, self).__init__()
        self.use_gpu = gpu

        self.NUM_CLASSES = cls_sz
        self.CODE_PRCT_DROPOUT = cd_drp
        self.CODE_HD_SZ = cd_hd_sz
        self.CODE_NUM_LAYERS = cd_nm_lz

        self.code_embedding = nn.Embedding.from_pretrained(cd_vecs)
        self.code_lstm = nn.LSTM(cd_vecs.size()[1],
                                 self.CODE_HD_SZ,
                                 num_layers=self.CODE_NUM_LAYERS,
                                 dropout=self.CODE_PRCT_DROPOUT,
                                 bidirectional=True)

        self.hidden2label = nn.Linear(self.CODE_HD_SZ * 2, self.NUM_CLASSES)
        self.init_hidden()

    def init_hidden(self, batch_size=50):
        self.code_hd = (Variable(torch.zeros(2, batch_size, self.CODE_HD_SZ)),
                        Variable(torch.zeros(2, batch_size, self.CODE_HD_SZ)))

        if self.use_gpu:
            self.code_hd = (self.code_hd[0].cuda(), self.code_hd[1].cuda())

    def forward(self, data):
        (code, _) = data
        if self.use_gpu:
            code = code.cuda()

        self.init_hidden(batch_size=code.size()[0])
        code_encoding = self.code_embedding(code)
        code_encoding = code_encoding.transpose(0, 1)
        code_vecs, self.code_hd = self.code_lstm(code_encoding, self.code_hd)
        y = self.hidden2label(code_vecs[-1])
        return y


class CommOnlyClassifier(nn.Module):
    """
    PyTorch Neural Network model consisting of a Bi-directional LSTM whose
    output is fed through a classification layer. This classifier only processes
    an LSTM over docstring input.

    NOTE: This classifier is built to fail, as classification should not be
          possible without seeing both the code and docstring.

    NOTE: For documentation on the functions of this class, refer to the docs
          for the CodeCommClassifier class
    """
    def __init__(self, cm_vecs, cls_sz=2, cm_drp=0, cm_hd_sz=50, cm_nm_lz=1, gpu=False):
        super(CommOnlyClassifier, self).__init__()
        self.use_gpu = gpu

        self.NUM_CLASSES = cls_sz
        self.COMM_PRCT_DROPOUT = cm_drp
        self.COMM_HD_SZ = cm_hd_sz
        self.COMM_NUM_LAYERS = cm_nm_lz

        self.comm_embedding = nn.Embedding.from_pretrained(cm_vecs)
        self.comm_lstm = nn.LSTM(cm_vecs.size()[1],
                                 self.COMM_HD_SZ,
                                 num_layers=self.COMM_NUM_LAYERS,
                                 dropout=self.COMM_PRCT_DROPOUT,
                                 bidirectional=True)

        self.hidden2label = nn.Linear(self.COMM_HD_SZ * 2, self.NUM_CLASSES)
        self.init_hidden()

    def init_hidden(self, batch_size=50):
        self.comm_hd = (Variable(torch.zeros(2, batch_size, self.COMM_HD_SZ)),
                        Variable(torch.zeros(2, batch_size, self.COMM_HD_SZ)))

        if self.use_gpu:
            self.comm_hd = (self.comm_hd[0].cuda(), self.comm_hd[1].cuda())

    def forward(self, data):
        (_, comm) = data
        if self.use_gpu:
            comm = comm.cuda()

        self.init_hidden(batch_size=comm.size()[0])
        comm_encoding = self.comm_embedding(comm)
        comm_encoding = comm_encoding.transpose(0, 1)
        comm_vecs, self.comm_hd = self.comm_lstm(comm_encoding, self.comm_hd)
        y = self.hidden2label(comm_vecs[-1])
        return y
