import argparse
import sys

import torch
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm

import utils.classfiers as cl
import utils.utils as utils
import torch.nn.functional as F


def main(args):
    torch.manual_seed(17)   # Randomly seed PyTorch

    # Load train, dev, test iterators with auto-batching and pretrained vectors
    (train, dev, test, code_vecs, comm_vecs) = utils.load_all_data("../data/input/", args.batch_size)

    # Pick a model to train
    if args.model == "both":
        model = cl.CodeCommClassifier(code_vecs, comm_vecs, gpu=args.use_gpu)
    elif args.model == "code":
        model = cl.CodeOnlyClassifier(code_vecs, gpu=args.use_gpu)
    elif args.model == "comm":
        model = cl.CommOnlyClassifier(comm_vecs, gpu=args.use_gpu)
    else:
        raise RuntimeError("Unidentified model type selected")

    # Load a saved model
    if args.load != "":
        model.load_state_dict(torch.load(args.load))

    # Discover available CUDA devices and use DataParallelism if possible
    devices = list(range(torch.cuda.device_count()))
    if len(devices) > 1:
        model = nn.DataParallel(model, device_ids=devices)

    # Send model to GPU for processing
    if args.use_gpu:
        model.cuda()

    # Do training
    if args.epochs > 0:
        loss_values = list()
        # Adam optimizer works, SGD fails to train the network for any batch size
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), 0.1)
        for epoch in range(args.epochs):
            model.train()           # Set the model to training mode
            with tqdm(total=len(train), desc="Epoch {}/{}".format(epoch+1, args.epochs)) as pbar:
                # for batch in tqdm(train, desc="Epoch {}/{}".format(epoch+1, args.epochs)):
                for b_idx, batch in enumerate(train):
                    # utils.train_on_batch(model, optimizer, batch, args.use_gpu)
                    model.zero_grad()
                    optimizer.zero_grad()   # Clear current gradient

                    # Get the label into a tensor for loss prop
                    truth = torch.autograd.Variable(batch.label).long()
                    if args.use_gpu:
                        truth = truth.cuda()

                    # Transpose the input data from batch storage to network form
                    # Batch storage will store the code/docstring data as column data, we need
                    # them in row data form to be embedded.
                    code = batch.code[0].transpose(0, 1)
                    comm = batch.comm[0].transpose(0, 1)

                    outputs = model((code, comm))           # Run the model using the batch
                    loss = F.cross_entropy(outputs, truth)  # Get loss from log(softmax())
                    loss.backward()                         # Propagate loss
                    optimizer.step()                        # Update the optimizer
                    curr_loss = loss.item()
                    loss_values.append((epoch, b_idx, curr_loss))
                    pbar.set_postfix(batch_loss=curr_loss)
                    pbar.update()

            # Check DEV accuracy after every epoch
            scores = score_dataset(model, dev)
            acc = utils.accuracy_score(scores)
            sys.stdout.write("Epoch {} -- dev acc: {}%\n".format(epoch+1, acc))

        with open("training_loss.txt", "w+") as loss_file:
            loss_file.write("EPOCH\tBATCH\tLOSS\n")
            for (e, b, l) in loss_values:
                loss_file.write("{}\t{}\t{}\n".format(e, b, l))

    # Save the model weights
    if args.save != "":
        torch.save(model.state_dict(), args.save)

    # Save the DEV set evaluations
    if args.eval_dev:
        scores = score_dataset(model, dev)
        utils.save_scores(scores, "../data/scores_dev.pkl")

    # Save the TEST set evaluations
    if args.eval_test:
        scores = score_dataset(model, test)
        utils.save_scores(scores, "../data/scores_test.pkl")


def score_dataset(model, dataset):
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
    scores = list()
    model.eval()    # Set the model to evaluation mode
    with torch.no_grad():
        for i, batch in enumerate(dataset):
            # Prepare input batch data for classification
            code = batch.code[0].transpose(0, 1)
            comm = batch.comm[0].transpose(0, 1)

            # Run the model on the input batch
            output = model((code, comm))

            # Get predictions for every instance in the batch
            preds = torch.argmax(F.softmax(output, dim=1), dim=1).cpu().numpy()

            # Prepare truth data
            truth = batch.label.cpu().numpy()

            # Add new tuples to output
            scores.extend([(int(p), int(t)) for p, t in zip(preds, truth)])
    return scores


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--load", type=str,
                        help="indicate path to load model config",
                        default="")

    parser.add_argument("-s", "--save", type=str,
                        help="indicate path to save model config",
                        default="")

    parser.add_argument("-m", "--model", type=str,
                        help="model to use (code, comm, both)",
                        default="both")

    parser.add_argument("-e", "--epochs", type=int,
                        help="number of epochs to train",
                        default=10)

    parser.add_argument("-b", "--batch_size", type=int,
                        help="size of batch",
                        default=50)

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
