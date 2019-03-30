import argparse
import random
import sys

import torch
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm

import utils.generators as gen
import utils.utils as utils


def main(args):
    torch.manual_seed(17)   # Randomly seed PyTorch
    MAX_SIZE = 3000

    # Load train, dev, test iterators with auto-batching and pretrained vectors
    (train, dev, test,
     code_vocab, comm_vocab) = utils.load_generation_data()

    code_vecs = code_vocab.vectors
    comm_vecs = comm_vocab.vectors

    # Create model
    encoder = gen.CodeEncoder(code_vecs, gpu=args.use_gpu)
    if args.model == "attn":
        decoder = gen.AttnCommDecoder(comm_vecs, max_len=MAX_SIZE, gpu=args.use_gpu)
    else:
        decoder = gen.CommDecoder(comm_vecs, gpu=args.use_gpu)

    # Send model to GPU for processing
    if args.use_gpu:
        encoder.cuda()
        decoder.cuda()

    print(f"Training w/ {args.model} model")
    # Adam optimizer works, SGD fails to train the network for any batch size
    enc_optimizer = optim.Adam(encoder.parameters(), args.learning_rate)
    dec_optimizer = optim.Adam(decoder.parameters(), args.learning_rate)
    criterion = nn.NLLLoss()
    train_set = train.examples

    for epoch in range(args.epochs):
        # Set the model to training mode
        encoder.train()
        decoder.train()

        random.shuffle(train_set)

        with tqdm(total=len(train_set), desc=f"Epoch {epoch+1}/{args.epochs}") as pbar:
            total_loss = 0
            for idx, example in enumerate(train_set):
                # Clear the model gradients
                encoder.zero_grad()
                decoder.zero_grad()

                # Clear current gradient
                enc_optimizer.zero_grad()
                dec_optimizer.zero_grad()

                encoder_outputs = torch.zeros(MAX_SIZE, 100)
                code = torch.tensor([code_vocab.stoi[w] for w in example.code])
                comm = torch.tensor([comm_vocab.stoi[w] for w in example.comm])

                # Send data to GPU if available
                if args.use_gpu:
                    code = code.cuda()
                    comm = comm.cuda()
                    encoder_outputs = encoder_outputs.cuda()

                enc_outputs, enc_state = encoder(code)
                enc_outputs = enc_outputs.squeeze(1)
                (seq_len, _) = enc_outputs.size()
                encoder_outputs[:seq_len, :] = enc_outputs  # Add the outputs to the zero padding

                loss = 0
                state = enc_state
                dec_input = comm[0].unsqueeze(0)
                for di in range(1, len(comm)):
                    dec_output, state, _ = decoder(dec_input, state, encoder_outputs)
                    loss += criterion(dec_output, comm[di].unsqueeze(0))

                    _, dec_input = dec_output.max(dim=1)
                    dec_input = dec_input.detach()
                    if dec_input.item() == comm_vocab.stoi["<EoL>"]:
                        break

                # Propagate loss
                loss.backward()

                # Update the optimizer
                enc_optimizer.step()
                dec_optimizer.step()

                new_loss = loss.item()
                total_loss += new_loss
                curr_loss = total_loss / (idx + 1)
                pbar.set_postfix(loss=curr_loss)
                pbar.update()

    # Save the DEV set evaluations
    if args.eval_dev:
        print(f"Translating dev for {args.model} model")
        pairs = translate(encoder, decoder, dev, code_vocab, comm_vocab)
        dev_path = utils.CODE_CORPUS / "results" / f"dev_{args.model}_model"
        utils.save_translations(pairs, str(dev_path))

    # Save the TEST set evaluations
    if args.eval_test:
        print(f"Translating test for {args.model} model")
        pairs = translate(encoder, decoder, test, code_vocab, comm_vocab)
        test_path = utils.CODE_CORPUS / "results" / f"test_{args.model}_model"
        utils.save_translations(pairs, str(test_path))


def translate(encoder, decoder, dataset, code_vocab, comm_vocab, max_length=3000):
    """
    Given a neural net classification model and a dataset of batches, evaluate
    the model on all the batches and return the predictions along with the truth
    values for every batch.

    :param model:   [nn.Module] -- A classification network (single arg)
    :param dataset: [Batch Iterator] -- The training set of batches
    :returns:       [List[Tuple]] -- A flat list of tuples, one tuple for each
                                     training instance, where the tuple is of
                                     the form (prediction, truth)
    """
    # Set the model to evaluation mode
    encoder.eval()
    decoder.eval()

    pairs = list()
    with torch.no_grad():
        for example in tqdm(dataset.examples, desc="Translating"):
            encoder_outputs = torch.zeros(max_length, 100)

            code = torch.tensor([code_vocab.stoi[w] for w in example.code])
            comm = torch.tensor([comm_vocab.stoi[w] for w in example.comm])

            # Send data to GPU if available
            if args.use_gpu:
                code = code.cuda()
                comm = comm.cuda()
                encoder_outputs = encoder_outputs.cuda()

            enc_outputs, enc_state = encoder(code)
            enc_outputs = enc_outputs.squeeze(1)
            (seq_len, _) = enc_outputs.size()
            encoder_outputs[:seq_len, :] = enc_outputs  # Add the outputs to the zero padding

            decoded_words = ["<BoL>"]
            state = enc_state
            dec_input = comm[0].unsqueeze(0)
            for di in range(1, len(comm)):
                dec_output, state, _ = decoder(dec_input, state, encoder_outputs)
                _, dec_input = dec_output.max(dim=1)
                word_idx = dec_input.item()
                if word_idx == comm_vocab.stoi["<EoL>"]:
                    decoded_words.append("<EoL>")
                    break
                else:
                    decoded_words.append(comm_vocab.itos[word_idx])

            pairs.append((example.code, example.comm, decoded_words))

    return pairs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--load", type=str,
                        help="indicate path to load model config",
                        default="")

    parser.add_argument("-s", "--save", type=str,
                        help="indicate path to save model config",
                        default="")

    parser.add_argument("-m", "--model", type=str,
                        help="model to use (reg or attn)",
                        default="attn")

    parser.add_argument("-e", "--epochs", type=int,
                        help="number of epochs to train",
                        default=10)

    parser.add_argument("-r", "--learning-rate", type=float,
                        help="learning rate",
                        default=1e-3)

    parser.add_argument("-g", "--use_gpu", dest="use_gpu", action="store_true",
                        help="indicate whether to use CPU or GPU")
    parser.set_defaults(use_gpu=False)

    parser.add_argument("-d", "--eval-dev", dest="eval_dev", action="store_true",
                        help="indicate evaluation on development set")
    parser.set_defaults(eval_dev=False)

    parser.add_argument("-t", "--eval-test", dest="eval_test", action="store_true",
                        help="indicate evaluation on test set")
    parser.set_defaults(eval_test=False)
    args = parser.parse_args()
    main(args)
