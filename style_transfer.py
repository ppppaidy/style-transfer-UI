from __future__ import print_function

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim

import os
import PIL
import numpy as np

import torchvision.transforms as transforms
import torchvision.models as models

import copy
import argparse

from loss import ContentLoss, GramMatrix, StyleLoss
from utils import image_loader, image_loader_gray, save_image

parser = argparse.ArgumentParser()
parser.add_argument('--content', '-c', type=str, required=True, help='The path to the Content image')
parser.add_argument('--style', '-s', type=str, required=True, help='The path to the style image')
parser.add_argument('--output', '-o', type=str, help='The path storing transferred image')
parser.add_argument('--epoch', '-e', type=int, default=300, help='The number of epoch')
parser.add_argument('--content_weight', '-c_w', type=int, default=1, help='The weight of content loss')
parser.add_argument('--style_weight', '-s_w', type=int, default=500, help='The weight of style loss')
parser.add_argument('--size', '-s_z', type=int, default=512, help='The size of image')
parser.add_argument('--initialize_noise', '-i_n', action='store_true', help='Initialize with white noise? elif initialize with content image')
parser.add_argument('--cuda', action='store_true', help='use cuda?')
parser.add_argument('--content_layers', '-c_l', type=str, action='append', nargs='+', help='The layers which you think have content information, name like conv_i or relu_i')
parser.add_argument('--style_layers', '-s_l', type=str, action='append', nargs='+', help='The layers which you think have style information, name like conv_i or relu_i')
parser.add_argument('--model', '-m', type=str, default='vgg19', help='The net structure')
args = parser.parse_args()

use_cuda = torch.cuda.is_available() and args.cuda
dtype = torch.cuda.FloatTensor if use_cuda else torch.FloatTensor

# desired size of the output image
#imsize = 512 if use_cuda else 128  # use small size if no gpu
imsize = args.size

style_img = image_loader(args.style, imsize).type(dtype)
content_img = image_loader_gray(args.content, imsize).type(dtype)

if args.initialize_noise:
    input_img = Variable(torch.randn(content_img.data.size())).type(dtype)
else:
    input_img = image_loader_gray(args.content, imsize).type(dtype)

input_size = PIL.Image.open(args.content).size

assert style_img.size() == content_img.size(), \
    "we need to import style and content images of the same size"
if args.model == 'vgg19':
    cnn = models.vgg19(pretrained=True).features
elif args.model == 'vgg16':
    cnn = models.vgg16(pretrained=True).features
elif args.model == 'vgg13':
    cnn = models.vgg13(pretrained=True).features
elif args.model == 'vgg11':
    cnn = models.vgg11(pretrained=True).features
# move it to the GPU if possible:
if use_cuda:
    cnn = cnn.cuda()

# desired depth layers to compute style/content losses :
content_layers_default = ['conv_4']
style_layers_default = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']


def get_style_model_and_losses(cnn, style_img, content_img, style_weight=1000, content_weight=1, content_layers=content_layers_default, style_layers=style_layers_default):
    cnn = copy.deepcopy(cnn)

    # just in order to have an iterable access to or list of content/syle
    # losses
    content_losses = []
    style_losses = []

    model = nn.Sequential()  # the new Sequential module network
    gram = GramMatrix()  # we need a gram module in order to compute style targets

    # move these modules to the GPU if possible:
    if use_cuda:
        model = model.cuda()
        gram = gram.cuda()

    i = 1
    for layer in list(cnn):
        if isinstance(layer, nn.Conv2d):
            name = "conv_" + str(i)
            model.add_module(name, layer)

            if name in content_layers:
                # add content loss:
                target = model(content_img).clone()
                content_loss = ContentLoss(target, content_weight)
                model.add_module("content_loss_" + str(i), content_loss)
                content_losses.append(content_loss)

            if name in style_layers:
                # add style loss:
                target_feature = model(style_img).clone()
                target_feature_gram = gram(target_feature)
                style_loss = StyleLoss(target_feature_gram, style_weight)
                model.add_module("style_loss_" + str(i), style_loss)
                style_losses.append(style_loss)

        if isinstance(layer, nn.ReLU):
            name = "relu_" + str(i)
            model.add_module(name, layer)

            if name in content_layers:
                # add content loss:
                target = model(content_img).clone()
                content_loss = ContentLoss(target, content_weight)
                model.add_module("content_loss_" + str(i), content_loss)
                content_losses.append(content_loss)

            if name in style_layers:
                # add style loss:
                target_feature = model(style_img).clone()
                target_feature_gram = gram(target_feature)
                style_loss = StyleLoss(target_feature_gram, style_weight)
                model.add_module("style_loss_" + str(i), style_loss)
                style_losses.append(style_loss)

            i += 1

        if isinstance(layer, nn.MaxPool2d):
            name = "pool_" + str(i)
            model.add_module(name, layer)  # ***

    return model, style_losses, content_losses

def get_input_param_optimizer(input_img):
    # this line to show that input is a parameter that requires a gradient
    input_param = nn.Parameter(input_img.data)
    optimizer = optim.LBFGS([input_param])
    return input_param, optimizer

#processing
from tkinter import *
pb_x = 0
pb_y = 0
pb_width = 100
pb_height = 20
pb_bg = "white"
pb_fg = "green"
pb_frame_size = 0
canvas = Canvas
class progress:
    def __init__(self):
        pass

    def init(self, master, x=pb_x, y=pb_y,
             width=pb_width, height=pb_height,
             bg=pb_bg, fg=pb_fg,
             frame_size=pb_frame_size):
        global pb_x
        pb_x = x
        global pb_y
        pb_y = y
        global pb_width
        pb_width = width
        global pb_height
        pb_height = height
        global pb_bg
        pb_bg = bg
        global pb_fg
        pb_fg = fg
        global pb_frame_size
        pb_frame_size = frame_size
        global canvas
        canvas = Canvas(master, width=width, height=height, bg=pb_bg)
        canvas.place(x=x, y=y)

    def run(self, master, percentage, text=None):
        global canvas
        fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill=pb_fg)
        canvas.coords(fill_line, (0, 0, percentage, 60))
        if text:
            label = Label(master, text=text)
            label.place(x=pb_x + pb_width, y=pb_y)
        master.update()

def run_style_transfer(cnn, content_img, style_img, input_img, num_steps=300, style_weight=1000, content_weight=1, content_layers=content_layers_default, style_layers=style_layers_default):
    """Run the style transfer."""
    #print('Building the style transfer model..')
    model, style_losses, content_losses = get_style_model_and_losses(cnn, style_img, content_img, style_weight, content_weight, content_layers, style_layers)
    input_param, optimizer = get_input_param_optimizer(input_img)

    #print('Optimizing..')
    root = Tk()
    root.title("进度条")
    root.geometry("300x100")
    progress.init(self=progress, master=root, x=10, y=20)
    run = [0]
    while run[0] < num_steps:
        def closure():
            # correct the values of updated input image
            input_param.data.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_param)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.backward()
            for cl in content_losses:
                content_score += cl.backward()

            run[0] += 1
            progress.run(self=progress, master=root, percentage=int(run[0]*100/num_steps), text="生成中……"+str(int(run[0]*100/num_steps))+"%")
            #print(run[0])
            #if run[0] % 50 == 0:
                #print("run {}:".format(run))
                #print('Style Loss : {:4f} Content Loss: {:4f}'.format(style_score.item(), content_score.item()))

            return style_score + content_score

        optimizer.step(closure)

    # a last correction...
    input_param.data.clamp_(0, 1)

    return input_param.data

content_layers = content_layers_default if args.content_layers is None else args.content_layers[0]
style_layers = style_layers_default if args.style_layers is None else args.content_layers[0]
#print(content_layers)
output = run_style_transfer(cnn, content_img, style_img, input_img, args.epoch, args.style_weight, args.content_weight, content_layers, style_layers)

name_content, ext = os.path.splitext(os.path.basename(args.content))
name_style, _ = os.path.splitext(os.path.basename(args.style))
fname = name_content+'-'+name_style+ext if args.output is None else args.output

save_image(output, size=input_img.data.size()[1:], input_size=input_size, fname=fname)
