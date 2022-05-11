import multiprocessing
import os
import json
from dataclasses import dataclass

from batch_corpus_generator_v3 import generate_corpus


@dataclass
class Config:
    corpora_root: str = ''
    start: int = 0
    num_samples: int = 0
    batch_size: int = 0


@dataclass
class Parameters:
    corpus_root: str
    start: int
    num_samples: int


# def init_child(lock_):
#     global lock
#     lock = lock_
#
#
# def log(message):
#     with lock:
#         with open('log.txt', 'a') as log_file:
#             log_file.write(message + '\n')
#
#
# def test(params: Parameters):
#     log(f'{params}')


def load_config():
    if not os.path.isfile('config_multi.json'):
        raise Exception("ERROR: config_multi.json not found")

    config = Config()

    with open('config_multi.json') as json_file:
        cdata = json.load(json_file)

        config.corpora_root = cdata['corpora_root']
        config.start = cdata['start']
        config.num_samples = cdata['num_samples']
        config.batch_size = cdata['batch_size']

    return config


def generate_corpus_parameters(config: Config):
    param_set = list()
    new_start = config.start
    remaining_samples = config.num_samples
    continue_split = True

    while continue_split:
        remaining_samples -= config.batch_size

        if remaining_samples < 1:
            continue_split = False
            interval_end = new_start + config.batch_size + remaining_samples - 1
            interval_size = config.batch_size + remaining_samples
            corpus_root_name = f'corpus_{new_start}_{interval_end}'
            corpus_root = os.path.join(config.corpora_root, corpus_root_name)
            params = Parameters(corpus_root, new_start, interval_size)
            param_set.append(params)
        else:
            interval_end = new_start + config.batch_size - 1
            corpus_root_name = f'corpus_{new_start}_{interval_end}'
            corpus_root = os.path.join(config.corpora_root, corpus_root_name)
            params = Parameters(corpus_root, new_start, config.batch_size)
            param_set.append(params)
        new_start += config.batch_size

    return param_set


def generate_corpus_wrapper(params: Parameters):
    generate_corpus(start=params.start,
                    num_samples=params.num_samples,
                    corpus_root=params.corpus_root)


def corpora_generator_multiprocessing():
    print('>>>>>>>>>> START corpora_generator_multiprocessing()')

    # lock = multiprocessing.Lock()
    num_processors = max(multiprocessing.cpu_count() - 5, 1)

    print(f'>>>>>>>>>> num_processors {num_processors}')

    config = load_config()
    param_set = generate_corpus_parameters(config)
    print(f'>>>>>>>>>> num params: {len(param_set)}')

    # with multiprocessing.Pool(num_processors, initializer=init_child, initargs=(lock,)) as p:
    #     p.map(test, param_set)

    with multiprocessing.Pool(num_processors) as p:
        p.map(generate_corpus_wrapper, param_set)

    # tot = 0
    # for ps in param_set:
    #     tot += ps.num_samples
    #     print(ps)
    # print(f'total samples {tot}')

    print('>>>>>>>>>> DONE corpora_generator_multiprocessing()')


if __name__ == '__main__':
    corpora_generator_multiprocessing()
