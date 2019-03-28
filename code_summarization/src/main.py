import argparse
import sys

import torch
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm

import utils.classfiers as cl
import utils.utils as utils
import torch.nn.functional as F
import numpy as np


def main(args):
    torch.manual_seed(17)   # Randomly seed PyTorch

    # Load train, dev, test iterators with auto-batching and pretrained vectors
    (train, dev, test,
     code_vecs, comm_vecs,
     code_char_vecs, comm_char_vecs) = utils.load_all_data(args.batch_size, args.corpus)

    # Create model
    model = cl.CodeCommClassifier(code_vecs,
                                  comm_vecs,
                                  code_char_vecs,
                                  comm_char_vecs,
                                  gpu=args.use_gpu,
                                  model_type=args.model)

    # Load a saved model
    if args.load != "":
        model.load_state_dict(torch.load(args.load))

    # Discover available CUDA devices and use DataParallelism if possible
    devices = list(range(torch.cuda.device_count()))
    if len(devices) > 1:
        print("Using {} GPUs!!".format(len(devices)))
        model = nn.DataParallel(model)

    # Send model to GPU for processing
    if args.use_gpu:
        model.cuda()

    # Do training
    if args.epochs > 0:
        print("Training {} model w/ batch_sz={} on {} dataset".format(args.model, args.batch_size, args.corpus))
        # Adam optimizer works, SGD fails to train the network for any batch size
        optimizer = optim.Adam(model.parameters(), args.learning_rate)
        class_weights = torch.tensor([10.])
        if args.use_gpu:
            class_weights = class_weights.cuda()
        for epoch in range(args.epochs):
            model.train()           # Set the model to training mode
            with tqdm(total=len(train), desc="Epoch {}/{}".format(epoch+1, args.epochs)) as pbar:
                total_loss = 0
                for b_idx, batch in enumerate(train):
                    # model.zero_grad()
                    optimizer.zero_grad()   # Clear current gradient

                    # Get the label into a tensor for loss prop
                    truth = torch.autograd.Variable(batch.label).float()
                    if args.use_gpu:
                        truth = truth.cuda()

                    # Run the model using the batch
                    outputs = model((batch.code, batch.comm))
                    # Get loss from log(softmax())
                    loss = F.binary_cross_entropy_with_logits(outputs.view(-1),
                                                              truth.view(-1),
                                                              pos_weight=class_weights)

                    loss.backward()                         # Propagate loss
                    optimizer.step()                        # Update the optimizer

                    new_loss = loss.item()
                    total_loss += new_loss
                    curr_loss = total_loss / (b_idx + 1)
                    pbar.set_postfix(batch_loss=curr_loss)
                    pbar.update()

            # Check DEV accuracy after every epoch
            scores = score_dataset(model, dev)
            acc = utils.accuracy_score(scores)
            sys.stdout.write("Epoch {} -- dev acc: {}%\n".format(epoch+1, acc))

    # Save the model weights
    if args.save != "":
        torch.save(model.state_dict(), args.save)

    # Save the DEV set evaluations
    if args.eval_dev:
        print("Evaluating Dev for {} model w/ batch_sz={} on {} dataset".format(args.model, args.batch_size, args.corpus))
        scores = score_dataset(model, dev)
        dev_score_path = utils.CODE_CORPUS / "results" / "{}_{}_{}_{}_gpus_scores_dev.pkl".format(args.model, args.batch_size, args.corpus, len(devices))
        utils.save_scores(scores, dev_score_path)

    # Save the TEST set evaluations
    if args.eval_test:
        print("Evaluating Dev for {} model w/ batch_sz={} on {} dataset".format(args.model, args.batch_size, args.corpus))
        scores = score_dataset(model, test)
        test_score_path = utils.CODE_CORPUS / "results" / "{}_{}_{}_{}_gpus_scores_test.pkl".format(args.model, args.batch_size, args.corpus, len(devices))
        utils.save_scores(scores, test_score_path)


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
    classes = [0, 1]
    with torch.no_grad():
        for i, batch in enumerate(dataset):
            # Run the model on the input batch
            output = model((batch.code, batch.comm))

            # Get predictions for every instance in the batch
            signum_outs = torch.sign(output).cpu().numpy()
            preds = [0 if arr_el[0] < 0 else 1 if arr_el[0] > 0 else np.choice(classes) for arr_el in signum_outs]

            # Prepare truth data
            truth = batch.label.cpu().numpy()

            # Add new tuples to output
            scores.extend([(p, int(t)) for p, t in zip(preds, truth)])
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
                        default=30)

    parser.add_argument("-r", "--learning-rate", type=float,
                        help="learning rate",
                        default=1e-3)

    parser.add_argument("-c", "--corpus", type=str,
                        help="Dataset to use for classification",
                        default="random_draw")

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
