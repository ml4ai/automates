import os
import ast
from typing import Dict
import matplotlib.pyplot as plt
import pickle
import tqdm
import pathlib


def load_tokens_input_all(filepath):
    print('START load_tokens_input_all')
    with open(filepath, 'rb') as tia_file:
        tokens_input_all = pickle.load(tia_file)
    print(f'DONE load_tokens_input_all {len(tokens_input_all)}')
    return tokens_input_all


def parse_v2_results_file(filepath):
    name = None
    score = None

    with open(filepath, 'r') as bfile:
        name = None
        score = None
        seq_length = None
        exact_match = None
        target_sequence = None
        target_sequence_p = False
        model_output = None
        model_output_p = False
        for line in bfile.readlines():
            if line.startswith('input file: '):
                name = line[12:].split('__')[0]
            elif line.startswith('bleu score: '):
                score = float(line[12:].strip('\n'))
            elif line.startswith('target sequence:'):
                target_sequence_p = True
            elif target_sequence_p:
                target_sequence_p = False
                target_sequence = ast.literal_eval(line.strip('\n'))
            elif line.startswith('model output:'):
                model_output_p = True
            elif model_output_p:
                model_output_p = False
                model_output = ast.literal_eval(line.strip('\n'))
            elif line.startswith('seq_length:'):
                seq_length = int(line[12:].strip('\n'))
            elif line.startswith('exact_match:'):
                exact_match = bool(line[13:].strip('\n'))

    # print(name, score, seq_length, exact_match)
    # print(target_sequence)
    # print(model_output)
    # import sys
    # sys.exit()

    return name, score, target_sequence[0], model_output, seq_length, exact_match


def load_v2_results_data(path_v2_results):
    print(f'START: load_v2_results_data : {path_v2_results}')
    c = 0
    data = dict()
    for subdir, dirs, files in os.walk(path_v2_results):
        for f in files:
            if f.endswith('.txt'):
                c += 1
                filepath = subdir + os.sep + f
                # print(filepath)
                name, score, target_sequence, model_output, seq_length, exact_match \
                    = parse_v2_results_file(filepath)
                data[name] = (score, target_sequence, model_output)
    print(f'DONE: load_v2_results_data {len(data)}')
    return data


def filter_models_by_bleu_range(data, low, high):
    model_names = list()
    for name, (score, _, mo) in data.items():
        if low <= score <= high:
            model_names.append((name, len(mo)))
    return model_names


def plot_scores_histogram(data: Dict, save_filepath=None):
    scores = [score for score, _, _ in data.values()]
    n, bins, patches = plt.hist(scores, 50, alpha=0.85)
    plt.xlabel('BLUE Scores')
    plt.ylabel('Frequency')
    plt.title(f'BLUE Score Distribution, total={len(scores)}')
    plt.grid(True)
    plt.xlim((0.0, 1.0))
    plt.ylim((0.0, 1000))
    if save_filepath:
        plt.savefig(save_filepath, format='pdf')


def plot_scores_by_length(data_bleu: Dict, data_input_tokens: Dict,
                          save_filepath_target=None,
                          save_filepath_input=None,
                          save_filepath_input_by_target_len=None,
                          save_filepath_target_to_pred_len=None):

    scores = list()
    input_lengths = list()
    target_lengths = list()
    predicted_lengths = list()

    print('START plot_scores_by_length - gathering data')
    for name, (score, ts, mo) in tqdm.tqdm(data_bleu.items()):
        scores.append(score)
        input_lengths.append(len(data_input_tokens[name]))
        target_lengths.append(len(ts))
        predicted_lengths.append(len(mo))
    print('DONE plot_scores_by_length - gathering data')

    # scores = [score for score, _, _ in data_bleu.values()]
    # t_lengths = [len(ts) for _, ts, _ in data_bleu.values()]
    # p_lengths = [len(mo) for _, _, mo in data_bleu.values()]

    my_dpi = 96
    plt.figure(figsize=(1200/my_dpi, 600/my_dpi), dpi=my_dpi)
    plt.scatter(target_lengths, scores, s=3.0, alpha=0.75)
    plt.xlabel('Target CAST token sequence length')
    plt.ylabel('BLEU Score')
    plt.title('Target Sequence Length by BLEU Score')
    if save_filepath_target:
        plt.savefig(save_filepath_target, format='pdf')

    plt.figure(figsize=(1200/my_dpi, 600/my_dpi), dpi=my_dpi)
    plt.scatter(input_lengths, scores, s=3.0, alpha=0.75)
    plt.xlabel('Input Ghidra IR token sequence length')
    plt.ylabel('BLEU Score')
    plt.title('Input Sequence Length by BLEU Score')
    if save_filepath_input:
        plt.savefig(save_filepath_input, format='pdf')

    plt.figure()
    plt.scatter(input_lengths, target_lengths, s=3.0, alpha=0.75)
    plt.xlabel('Input Ghidra IR token sequence length')
    plt.ylabel('Target CAST token sequence length')
    plt.title('Input to Target token lengths')
    if save_filepath_input:
        plt.savefig(save_filepath_input_by_target_len, format='pdf')

    plt.figure()
    plt.scatter(target_lengths, predicted_lengths, s=3.0, alpha=0.75)
    plt.xlabel('Target CAST token sequence length')
    plt.ylabel('Predicted CAST token sequence length')
    plt.title('Target to Predicted token lengths')
    if save_filepath_input:
        plt.savefig(save_filepath_target_to_pred_len, format='pdf')


def main(root_dir, dst_dir, data_input_tokens=None, show_p=False):

    pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)

    data_bleu = load_v2_results_data(root_dir)

    plot_scores_histogram(data_bleu,
                          os.path.join(dst_dir, 'bleu_score_dist.pdf'))

    # Uncomment to plot scores by length
    # if data_input_tokens is None:
    #     data_input_tokens = load_tokens_input_all(
    #         os.path.join(root_dir, 'tokens_input_all.pickle'))
    plot_scores_by_length(
        data_bleu, data_input_tokens,
        save_filepath_target=os.path.join(dst_dir, 'bleu_scores_by_target_len_scatter.pdf'),
        save_filepath_input=os.path.join(dst_dir, 'bleu_scores_by_input_len_scatter.pdf'),
        save_filepath_input_by_target_len=os.path.join(dst_dir, 'input_by_target_len_scatter.pdf'),
        save_filepath_target_to_pred_len=os.path.join(dst_dir, 'target_to_predicted_len_scatter.pdf')
    )

    success = filter_models_by_bleu_range(data_bleu, low=1, high=1)
    print(f'succeeded: {len(success)} {success}')
    failed = filter_models_by_bleu_range(data_bleu, low=0, high=0)
    print(f'failed: {len(failed)} {failed}')
    part_0p9 = filter_models_by_bleu_range(data_bleu, low=0.9, high=0.91)
    print(f'[0.9, 0.91]]: {len(part_0p9)} {part_0p9}')
    part_0p8 = filter_models_by_bleu_range(data_bleu, low=0.8, high=0.81)
    print(f'[0.8, 0.81]]: {len(part_0p8)} {part_0p8}')
    part_0p6 = filter_models_by_bleu_range(data_bleu, low=0.6, high=0.61)
    print(f'[0.6, 0.61]]: {len(part_0p6)} {part_0p6}')

    if show_p:
        plt.show()


if __name__ == '__main__':
    _data_input_tokens = load_tokens_input_all(
        os.path.join('../data/corpus_v2_results', 'tokens_input_all.pickle'))

    # main(root_dir='../data/corpus_v2_results/test_bleu', dst_dir='',
    #      data_input_tokens=_data_input_tokens)

    # main(root_dir='../data/2022-02-10-nmt-results/no_values/seq2seq',
    #      dst_dir='2022-02-10-nmt-results/no_values/seq2seq',
    #      data_input_tokens=_data_input_tokens)
    # main(root_dir='../data/2022-02-10-nmt-results/no_values/attention',
    #      dst_dir='2022-02-10-nmt-results/no_values/attention',
    #      data_input_tokens=_data_input_tokens)
    # main(root_dir='../data/2022-02-10-nmt-results/no_values/transformer',
    #      dst_dir='2022-02-10-nmt-results/no_values/transformer',
    #      data_input_tokens=_data_input_tokens)

    main(root_dir='../data/2022-02-10-nmt-results/with_values/seq2seq',
         dst_dir='2022-02-10-nmt-results/with_values/seq2seq',
         data_input_tokens=_data_input_tokens)
    main(root_dir='../data/2022-02-10-nmt-results/with_values/attention',
         dst_dir='2022-02-10-nmt-results/with_values/attention',
         data_input_tokens=_data_input_tokens)
    main(root_dir='../data/2022-02-10-nmt-results/with_values/transformer',
         dst_dir='2022-02-10-nmt-results/with_values/transformer',
         data_input_tokens=_data_input_tokens)

    plt.show()
