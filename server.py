import os
import pickle
import random
import numpy as np
import tensorflow as tf
import PIL.Image
import dnnlib
import dnnlib.tflib as tflib
from flask import Flask
from flask_restful import Resource, Api, reqparse
import config

fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)

parser = reqparse.RequestParser()
parser.add_argument('key')

app = Flask(__name__)
api = Api(app)

url_ffhq = 'https://drive.google.com/uc?id=1eYHcNrI_kLRfWnC9Kb8xbak6548vTuyt'

_Gs_cache = dict()
""" 

def load_Gs(url):
    if url not in _Gs_cache:
        with dnnlib.util.open_url(url, cache_dir=config.cache_dir) as f:
            _G, _D, Gs = pickle.load(f)
        _Gs_cache[url] = Gs
    return _Gs_cache[url] """


global Gs
tflib.init_tf()
with dnnlib.util.open_url(url_ffhq, cache_dir=config.cache_dir) as f:
    _G, _D, Gs = pickle.load(f)

"""
@runway.setup(options={'checkpoint': runway.file(extension='.pkl')})
def setup(opts):
    global Gs
    tflib.init_tf()
    with open(opts['checkpoint'], 'rb') as file:
        G, D, Gs = pickle.load(file)
    return Gs


generate_inputs = {
    'z': runway.vector(length=512, sampling_std=0.5),
    'truncation': runway.number(min=0, max=1, default=0.8, step=0.01)
}

@runway.command('generate', inputs=generate_inputs,
    outputs={'image': runway.image})
def convert(model, inputs):
    z = inputs['z']
    truncation = inputs['truncation']
    latents = z.reshape((1, 512))
    images = model.run(latents, None, truncation_psi=truncation,
        randomize_noise=False, output_transform=fmt)
    output = np.clip(images[0], 0, 255).astype(np.uint8)
    return {'image': output} """


class MyResource(Resource):
    def get(self):
        args = parser.parse_args()
        truncation = 0.8
        rnd = np.random.RandomState(int(1000*random.random()))
        latents = rnd.randn(1, *Gs.input_shapes[0][1:])
        images = Gs.run(latents, None, truncation_psi=truncation,
                        randomize_noise=False, output_transform=fmt)
        output = np.clip(images[0], 0, 255).astype(np.uint8)
        return {'image': output}


api.add_resource(MyResource, '/generate')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
