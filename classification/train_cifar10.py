# -*- coding: utf-8 -*-
import mxnet as mx
import argparse
import os
import sys
import train_model
import importlib


def get_parser():
    parser = argparse.ArgumentParser(description='Train an image classifier on cifar10')
    parser.add_argument('--network', type=str, default='alexnet',
                        help = 'the cnn to use')
    parser.add_argument('--optimizer', type=str, default='sgd',
                        help = 'the optimizer to use')
    parser.add_argument('--gpus', type=str,
                        help='the gpus will be used, e.g "0,1,2,3"')
    parser.add_argument('--num-examples', type=int, default=60000,
                        help='the number of training examples')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='the batch size')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='the initial learning rate')
    parser.add_argument('--lr-factor', type=float, default=1,
                        help='times the lr with a factor for every lr-factor-epoch epoch')
    parser.add_argument('--lr-factor-epoch', type=float, default=1,
                        help='the number of epoch to factor the lr, could be .5')
    parser.add_argument('--momentum', type=float, default=0.9,
                        help='momentum value')
    parser.add_argument('--gamma1', type=float, default=0.95,
                        help='decay factor of moving average for gradient, gradient^2 in RMSprop')
    parser.add_argument('--gamma2', type=float, default=0.9,
                        help='momentum factor in RMSprop')
    parser.add_argument('--num-epochs', type=int, default=20,
                        help='the number of training epochs')
    parser.add_argument('--model-prefix', type=str,
                        help='the prefix of model to load')
    parser.add_argument('--load-epoch', type=int,
                        help='load the model on an epoch using the model-prefix')
    parser.add_argument('--save-model-prefix', type=str,
                        help='the prefix of model to save')
    parser.add_argument('--kv-store', type=str, default='local',
                        help='the kvstore type')
    parser.add_argument('--log-file', type=str,
                        help='the log file')
    parser.add_argument('--log-dir', type=str,
                        help='the log dir')
    return parser


# download data if necessary
def _download(data_dir):
    if not os.path.isdir(data_dir):
        os.system("mkdir " + data_dir)
    os.chdir(data_dir)
    if (not os.path.exists('train.rec')) or \
       (not os.path.exists('test.rec')):
        os.system("wget http://data.dmlc.ml/mxnet/data/cifar10.zip")
        os.system("unzip -u cifar10.zip")
        os.system("mv cifar/* .; rm -rf cifar; rm cifar10.zip")
    os.chdir("..")


def get_iterator(args, kv):
    data_shape = (3, 24, 24)
    _download('cifar10/')

    train = mx.io.ImageRecordIter(
        path_imgrec = "cifar10/train.rec",
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        rand_crop   = True,
        rand_mirror = True,
        num_parts   = kv.num_workers,
        part_index  = kv.rank,
        shuffle     = True)

    val = mx.io.ImageRecordIter(
        path_imgrec = "cifar10/test.rec",
        rand_crop   = False,
        rand_mirror = False,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        num_parts   = kv.num_workers,
        part_index  = kv.rank)

    return (train, val)


if __name__ == '__main__':
    args = get_parser().parse_args()
    net = importlib.import_module('symbol_' + args.network).get_symbol(10)
    train_model.fit(args, net, get_iterator)
