import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class CodeCommClassifier(nn.Module):
    """
    PyTorch Neural Network model consisting of two Bi-directional LSTMs whose
    outputs are concatenated and then fed through a classification layer.
    One LSTM runs over the code input and the other runs over the docstring.
    """
    def __init__(self, cd_vecs, cm_vecs, cls_sz=1, cd_drp=0, cm_drp=0, hd_lyr_sz=100,
                 cd_hd_sz=50, cm_hd_sz=50, cd_nm_lz=1, cm_nm_lz=1, gpu=False, use_code=True, use_comm=True):
        super(CodeCommClassifier, self).__init__()
        self.use_gpu, self.use_code, self.use_comm = gpu, use_code, use_comm

        # Initialize embeddings from pretrained embeddings
        self.code_embedding = nn.Embedding.from_pretrained(cd_vecs)
        self.comm_embedding = nn.Embedding.from_pretrained(cm_vecs)

        self.NUM_CLASSES, self.HIDDEN_SZ = cls_sz, hd_lyr_sz
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
        if self.use_code and self.use_comm:
            self.CONCAT_SIZE = ((self.CODE_HD_SZ + self.COMM_HD_SZ) * 2)
        elif self.use_code:
            self.CONCAT_SIZE = ((self.CODE_HD_SZ) * 2)
        elif self.use_comm:
            self.CONCAT_SIZE = ((self.COMM_HD_SZ) * 2)
        else:
            raise RuntimeError("Not using any data in classifier.")

        # FFNN layer to transform LSTM output into class predictions
        self.lstm2hidden = nn.Linear(self.CONCAT_SIZE, self.HIDDEN_SZ)
        self.hidden2label = nn.Linear(self.HIDDEN_SZ, self.NUM_CLASSES)

    def init_hidden(self, batch_size=50):
        """
        Initializes the Cell state and Hidden layer vectors of the LSTMs. Each
        LSTM requires a tuple of the form (Cell state, hidden state) to be sent
        in. The states are updated during the forward process and will be
        available after processing.

        :param batch_size: [Integer] -- size of the batch to be processed
        """

        # Tensor size should be (# layers, size of batch, size of hidden layer)
        self.code_hd = (Variable(torch.zeros(2, batch_size, self.CODE_HD_SZ)),
                        Variable(torch.zeros(2, batch_size, self.CODE_HD_SZ)))
        self.comm_hd = (Variable(torch.zeros(2, batch_size, self.COMM_HD_SZ)),
                        Variable(torch.zeros(2, batch_size, self.COMM_HD_SZ)))

        if self.use_gpu:    # Transfer vectors to the GPU if using GPU
            self.code_hd = (self.code_hd[0].cuda(), self.code_hd[1].cuda())
            self.comm_hd = (self.comm_hd[0].cuda(), self.comm_hd[1].cuda())

    def forward(self, data):
        """
        Processes the forward pass through the classifier of a batch of data.
        The batch outputs from the last feed-forward layer of the classifier
        are returned as output.

        :param data: [Tuple] -- All input data to be sent through the classifier
        :returns: [Tensor] -- A matrix with a vector of output for each instance
        """
        ((code, code_lengths), (comm, comm_lengths)) = data
        # if self.use_gpu:    # Send data to GPU if available
        #     code = code.cuda()
        #     comm = comm.cuda()

        # Prepare data for batch processing
        code = code.transpose(0, 1)
        comm = comm.transpose(0, 1)

        # Initialize the models hidden layers and cell states
        bs = code.size()[0]
        self.init_hidden(batch_size=bs)

        # PROCESS:
        # (1) Sort instances in descending order and track the sorting for
        #     eventual unsorting (required for packing padded sequences)
        # (2) Encode the batch input using word embeddings
        # (3) Pack input sequences to remove padding
        # (4) Run the LSTMs over the packed input
        # (5) Re-pad input sequences for back-prop

        if self.use_code:
            code_lengths, code_sort_order = code_lengths.sort(descending=True)
            code_inv_order = code_sort_order.sort()[1]
            code_encoding = self.code_embedding(code[code_sort_order])
            code_enc_pack = pack_padded_sequence(code_encoding, code_lengths, batch_first=True)
            self.code_lstm.flatten_parameters()
            code_enc_pad, (code_h_n, code_c_n) = self.code_lstm(code_enc_pack)
            code_vecs, _ = pad_packed_sequence(code_enc_pad, batch_first=True)

        if self.use_comm:
            comm_lengths, comm_sort_order = comm_lengths.sort(descending=True)
            comm_inv_order = comm_sort_order.sort()[1]
            comm_encoding = self.comm_embedding(comm[comm_sort_order])
            comm_enc_pack = pack_padded_sequence(comm_encoding, comm_lengths, batch_first=True)
            self.comm_lstm.flatten_parameters()
            comm_enc_pad, (comm_h_n, comm_c_n) = self.comm_lstm(comm_enc_pack)
            comm_vecs, _ = pad_packed_sequence(comm_enc_pad, batch_first=True)

        # Concatenate the final output from both LSTMs
        if self.use_code and self.use_comm:
            recurrent_vecs = torch.cat((code_h_n[0, code_inv_order],
                                        code_h_n[1, code_inv_order],
                                        comm_h_n[0, comm_inv_order],
                                        comm_h_n[1, comm_inv_order]), 1)
        elif self.use_code:
            recurrent_vecs = torch.cat((code_h_n[0, code_inv_order],
                                        code_h_n[1, code_inv_order]), 1)
        elif self.use_comm:
            recurrent_vecs = torch.cat((comm_h_n[0, comm_inv_order],
                                        comm_h_n[1, comm_inv_order]), 1)
        else:
            raise RuntimeError("Not using any data in classifier.")

        # Transform recurrent output vector into a class prediction vector
        y = F.relu(self.lstm2hidden(recurrent_vecs))
        y = self.hidden2label(y)
        return y
