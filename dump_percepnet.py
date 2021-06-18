
#!/usr/bin/python3
'''Copyright (c) 2017-2018 Mozilla
                 2020-2021 Seonghun Noh
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:
   - Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
   - Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
   A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import torch
import sys
import rnn_train
from torch.nn import Sequential, GRU, Conv1d
import numpy as np

def printVector(f, vector, name, dtype='float'):
    v = np.reshape(vector.detach().numpy(), (-1))
    #print('static const float ', name, '[', len(v), '] = \n', file=f)
    f.write('static const {} {}[{}] = {{\n   '.format(dtype, name, len(v)))
    for i in range(0, len(v)):
        f.write('{}'.format(v[i]))
        if (i!=len(v)-1):
            f.write(',')
        else:
            break
        if (i%8==7):
            f.write("\n   ")
        else:
            f.write(" ")
    #print(v, file=f)
    f.write('\n};\n\n')
    return

def dump_fc_module(self, f, name):
    print("printing layer " + name)
    weight = self[0].weight
    bias = self[0].bias
    print("weight:", weight)
    activation = self[1].__class__.__name__.upper()
    printVector(f, weight, name + '_weights')
    printVector(f, bias, name + '_bias')
    f.write('const DenseLayer {} = {{\n   {}_bias,\n   {}_weights,\n   {}, {}, ACTIVATION_{}\n}};\n\n'
            .format(name, name, name, weight.shape[1], weight.shape[0], activation))
Sequential.dump_data = dump_fc_module

def dump_gru_module(self, f, name):
    pass
GRU.dump_data = dump_gru_module

def dump_conv1d_module(self, f, name):
    pass
Conv1d.dump_data = dump_conv1d_module

if __name__ == '__main__':
    model = rnn_train.PercepNet()
    #model = (
    model.load_state_dict(torch.load(sys.argv[1]))

    if len(sys.argv) > 2:
        cfile = sys.argv[2]
        #hfile = sys.argv[3];
    else:
        cfile = 'src/nnet_data.c'
        #hfile = 'nnet_data.h'


    f = open(cfile, 'w')
    #hf = open(hfile, 'w')

    f.write('/*This file is automatically generated from a Pytorch model*/\n\n')
    f.write('#ifdef HAVE_CONFIG_H\n#include "config.h"\n#endif\n\n#include "nnet.h"\n#include "nnet_data.h"\n\n')

    for name, module in model.named_children():
        module.dump_data(f, name)