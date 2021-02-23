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
    def __init__(self, cd_vecs, cm_vecs, cd_ch_vecs, cm_ch_vecs, cls_sz=1,
                 hd_lyr_sz=100, cd_drp=0, cm_drp=0, cd_hd_sz=100, cm_hd_sz=100,
                 cd_ch_hd_sz=25, cm_ch_hd_sz=25, cd_nm_lz=1, cm_nm_lz=1,
                 gpu=False, model_type="both"):
        super(CodeCommClassifier, self).__init__()

        self.use_gpu = gpu
        if model_type == "both":
            self.use_code, self.use_comm = True, True
        elif model_type == "code":
            self.use_code, self.use_comm = True, False
        elif model_type == "comm":
            self.use_code, self.use_comm = False, True
        else:
            raise RuntimeError("Unidentified model type selected")

        self.code_vocab, self.comm_vocab = cd_vecs, cm_vecs
        self.code_char_vocab, self.comm_char_vocab = cd_ch_vecs, cm_ch_vecs

        # Initialize embeddings from pretrained embeddings
        self.code_embedding = nn.Embedding.from_pretrained(cd_vecs.vectors)
        self.comm_embedding = nn.Embedding.from_pretrained(cm_vecs.vectors)
        self.code_char_embedding = nn.Embedding.from_pretrained(cd_ch_vecs.vectors)
        self.comm_char_embedding = nn.Embedding.from_pretrained(cm_ch_vecs.vectors)

        self.NUM_CLASSES, self.HIDDEN_SZ = cls_sz, hd_lyr_sz
        self.CODE_PRCT_DROPOUT, self.COMM_PRCT_DROPOUT = cd_drp, cm_drp
        self.CODE_HD_SZ, self.COMM_HD_SZ = cd_hd_sz, cm_hd_sz
        self.CODE_CHAR_HD_SZ, self.COMM_CHAR_HD_SZ = cd_ch_hd_sz, cm_ch_hd_sz
        self.CODE_NUM_LAYERS, self.COMM_NUM_LAYERS = cd_nm_lz, cm_nm_lz

        self.code_char_lstm = nn.LSTM(cd_ch_vecs.vectors.size()[1],
                                      self.CODE_CHAR_HD_SZ,
                                      num_layers=1,
                                      batch_first=True,
                                      bidirectional=True)

        self.comm_char_lstm = nn.LSTM(cm_ch_vecs.vectors.size()[1],
                                      self.COMM_CHAR_HD_SZ,
                                      num_layers=1,
                                      batch_first=True,
                                      bidirectional=True)

        # Creates a bidirectional LSTM for the code input
        self.CODE_EMB_SZ = cd_vecs.vectors.size()[1] + (2 * cd_ch_vecs.vectors.size()[1])
        self.code_lstm = nn.LSTM(self.CODE_EMB_SZ,      # Size of the code embedding
                                 self.CODE_HD_SZ,       # Size of the hidden layer
                                 num_layers=self.CODE_NUM_LAYERS,
                                 dropout=self.CODE_PRCT_DROPOUT,
                                 batch_first=True,
                                 bidirectional=True)

        # Creates a bidirectional LSTM for the docstring input
        self.COMM_EMB_SZ = cm_vecs.vectors.size()[1] + (2 * cm_ch_vecs.vectors.size()[1])
        self.comm_lstm = nn.LSTM(self.COMM_EMB_SZ,      # Size of the code embedding
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

        # self.sim_layer = nn.Linear(3 * self.CONCAT_SIZE, 1, bias=False)

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

    def get_code_char_embedding(self, code):
        words = list()
        for b_idx, sequence in enumerate(code):
            word_seq = [self.code_vocab.itos[el] for el in sequence]
            for word in word_seq:
                if word.startswith("<") and word.endswith(">"):
                    if word == "<pad>":
                        words.append(["</s>"])
                    else:
                        words.append([word])
                else:
                    words.append(list(word))

        char_lengths = [len(chars) for chars in words]
        max_length = max(char_lengths)
        maxed_words = [ch + (["</s>"] * (max_length - len(ch))) for ch in words]
        maxed_indices = [[self.code_char_vocab.stoi[ch] for ch in char_list]
                         for char_list in maxed_words]

        char_input = torch.tensor(maxed_indices)
        char_lengths = torch.tensor(char_lengths)
        char_lengths, clengths_order = char_lengths.sort(descending=True)
        clengths_inv_order = clengths_order.sort()[1]
        (b_size, _) = char_input.size()

        embedded_chars = self.code_char_embedding(char_input[clengths_order])
        char_enc_pack = pack_padded_sequence(embedded_chars, char_lengths, batch_first=True)
        h0 = torch.randn(2, b_size, self.CODE_CHAR_HD_SZ)     # (Nlayers, Batch size, hidden size)
        c0 = torch.randn(2, b_size, self.CODE_CHAR_HD_SZ)     # (Nlayers, Batch size, hidden size)
        _, (hn, _) = self.code_char_lstm(char_enc_pack, (h0, c0))

        (B, S) = code.size()
        char_embeddings = torch.cat((hn[0, clengths_inv_order],
                                     hn[1, clengths_inv_order]), 1)
        char_embeddings = char_embeddings.view(B, S, -1)
        return char_embeddings

    def get_comm_char_embedding(self, comm):
        words = list()
        for b_idx, sequence in enumerate(comm):
            word_seq = [self.comm_vocab.itos[el] for el in sequence]
            for s_idx, word in enumerate(word_seq):
                if word.startswith("<") and word.endswith(">"):
                    if word == "<pad>":
                        words.append(["</s>"])
                    else:
                        words.append([word])
                else:
                    words.append(list(word))

        char_lengths = [len(chars) for chars in words]
        max_length = max(char_lengths)
        maxed_words = [ch + (["</s>"] * (max_length - len(ch))) for ch in words]
        for i, length in enumerate(char_lengths):
            if length == 0:
                print(words[i])
                print(words[i-1])
                print(words[i+1])
        maxed_indices = [[self.comm_char_vocab.stoi[ch] for ch in char_list]
                         for char_list in maxed_words]

        char_input = torch.tensor(maxed_indices)
        char_lengths = torch.tensor(char_lengths)
        char_lengths, clengths_order = char_lengths.sort(descending=True)
        clengths_inv_order = clengths_order.sort()[1]
        (b_size, _) = char_input.size()

        embedded_chars = self.comm_char_embedding(char_input[clengths_order])
        char_enc_pack = pack_padded_sequence(embedded_chars, char_lengths, batch_first=True)
        h0 = torch.randn(2, b_size, self.COMM_CHAR_HD_SZ)     # (Nlayers, Batch size, hidden size)
        c0 = torch.randn(2, b_size, self.COMM_CHAR_HD_SZ)     # (Nlayers, Batch size, hidden size)
        _, (hn, _) = self.comm_char_lstm(char_enc_pack, (h0, c0))

        (B, S) = comm.size()
        char_embeddings = torch.cat((hn[0, clengths_inv_order],
                                     hn[1, clengths_inv_order]), 1)
        char_embeddings = char_embeddings.view(B, S, -1)
        return char_embeddings

    def forward(self, data):
        """
        Processes the forward pass through the classifier of a batch of data.
        The batch outputs from the last feed-forward layer of the classifier
        are returned as output.

        :param data: [Tuple] -- All input data to be sent through the classifier
        :returns: [Tensor] -- A matrix with a vector of output for each instance
        """
        ((code, code_lengths), (comm, comm_lengths)) = data
        if self.use_gpu:    # Send data to GPU if available
            code = code.cuda()
            comm = comm.cuda()

        # Initialize the models hidden layers and cell states
        self.init_hidden(batch_size=code.size()[1])

        # PROCESS:
        # (0) Prepare data for batch processing
        # (1) Sort instances in descending order and track the sorting for
        #     eventual unsorting (required for packing padded sequences)
        # (2) Encode the batch input using word embeddings
        # (3) Pack input sequences to remove padding
        # (4) Run the LSTMs over the packed input
        # (5) Re-pad input sequences for back-prop

        if self.use_code:
            code = code.transpose(0, 1)
            code_lengths, code_sort_order = code_lengths.sort(descending=True)
            code_inv_order = code_sort_order.sort()[1]
            code_encoding = self.code_embedding(code[code_sort_order])
            code_char_embedding = self.get_code_char_embedding(code[code_sort_order])
            code_comb_encoding = torch.cat((code_encoding, code_char_embedding), dim=2)
            code_enc_pack = pack_padded_sequence(code_comb_encoding, code_lengths, batch_first=True)
            self.code_lstm.flatten_parameters()
            code_packed_outpus, (code_h_n, code_c_n) = self.code_lstm(code_enc_pack, self.code_hd)
            code_outputs, _ = pad_packed_sequence(code_packed_outpus, batch_first=True)

        if self.use_comm:
            comm = comm.transpose(0, 1)
            comm_lengths, comm_sort_order = comm_lengths.sort(descending=True)
            comm_inv_order = comm_sort_order.sort()[1]
            comm_encoding = self.comm_embedding(comm[comm_sort_order])
            comm_char_embedding = self.get_comm_char_embedding(comm[comm_sort_order])
            comm_comb_encoding = torch.cat((comm_encoding, comm_char_embedding), dim=2)
            comm_enc_pack = pack_padded_sequence(comm_comb_encoding, comm_lengths, batch_first=True)
            self.comm_lstm.flatten_parameters()
            comm_packed_outputs, (comm_h_n, comm_c_n) = self.comm_lstm(comm_enc_pack, self.comm_hd)
            comm_outputs, _ = pad_packed_sequence(comm_packed_outputs, batch_first=True)

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
