from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import os

root = Tk()
root.title('图像风格迁移')
root.geometry('512x512')
content_filename=''
style_filename=''
output_filename=''
init_noise_s=''
gpu_cpu_s=''
model_s=' -m vgg19'

#title
title_lb = Label(root, text='图像风格迁移小程序')
title_lb.place(relx=0.3, rely=0, relwidth=0.4, relheight=0.08)

#content_file
def content_sel():
    filename = tkinter.filedialog.askopenfilename()
    content.delete(0.0, END)
    content_filename = filename
    if filename != '':
        content.insert(END, filename)
    else:
        content.insert(END, '请选择文件')

content_lb = Label(root, text='内容图片地址：', anchor=W)
content_lb.place(relx=0, rely=0.08, relwidth=0.2, relheight=0.06)
content = Text(root)
content.place(relx=0.2, rely=0.09, relwidth=0.6, relheight=0.04)
content.insert(END, '请选择文件')
content_bt = Button(root, text='选择文件', command=content_sel)
content_bt.place(relx=0.82, rely=0.09, relwidth=0.15, relheight=0.04)
print(content_filename)

#style_file
def style_sel():
    filename = tkinter.filedialog.askopenfilename()
    style.delete(0.0, END)
    style_filename = filename
    if filename != '':
        style.insert(END, filename)
    else:
        style.insert(END, '请选择文件')

style_lb = Label(root, text='风格图片地址：', anchor=W)
style_lb.place(relx=0, rely=0.14, relwidth=0.2, relheight=0.06)
style = Text(root)
style.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.04)
style.insert(END, '请选择文件')
style_bt = Button(root, text='选择文件', command=style_sel)
style_bt.place(relx=0.82, rely=0.15, relwidth=0.15, relheight=0.04)

#output_file
outp_lb = Label(root, text='输出文件名：', anchor=W)
outp_lb.place(relx=0, rely=0.20, relwidth=0.2, relheight=0.06)
outp = Entry(root)
outp.place(relx=0.2, rely=0.21, relwidth=0.6, relheight=0.04)
output_filename = 'result.jpg'
outp.insert(END, 'result')
outp_lb2 = Label(root, text='.jpg', anchor=W)
outp_lb2.place(relx=0.82, rely=0.21, relwidth=0.15, relheight=0.04)

#epoch
epoch_lb = Label(root, text='迭代次数：', anchor=W)
epoch_lb.place(relx=0, rely=0.27, relwidth=0.2, relheight=0.08)
epoch_var = IntVar()
epoch = Scale(root, from_=100, to=500, orient=HORIZONTAL,\
              tickinterval=100, resolution=20, variable=epoch_var)
epoch.set(300)
epoch.place(relx=0.2, rely=0.25, relwidth=0.8, relheight=0.15)

#content_weight
content_weight_lb = Label(root, text='内容权重：', anchor=W)
content_weight_lb.place(relx=0, rely=0.39, relwidth=0.2, relheight=0.08)
content_weight_var = IntVar()
content_weight = Scale(root, from_=1, to=10, orient=HORIZONTAL,\
               tickinterval=3, resolution=1, variable=content_weight_var)
content_weight.set(0)
content_weight.place(relx=0.2, rely=0.37, relwidth=0.8, relheight=0.15)

#style_weight
style_weight_lb = Label(root, text='风格权重(lg)：', anchor=W)
style_weight_lb.place(relx=0, rely=0.51, relwidth=0.2, relheight=0.08)
style_weight_var = DoubleVar()
style_weight = Scale(root, from_=3, to=5, orient=HORIZONTAL,\
               tickinterval=0.5, resolution=0.1, variable=style_weight_var)
style_weight.set(4)
style_weight.place(relx=0.2, rely=0.49, relwidth=0.8, relheight=0.15)

#initialize_noise
def init_noise_sel():
    if init_noise_var.get() == 0:
        init_noise_s = ''
    else:
        init_noise_s = ' -i_n'

init_noise_lb = Label(root, text='初始图像：', anchor=W)
init_noise_lb.place(relx=0, rely=0.60, relwidth=0.14, relheight=0.06)
init_noise_var = IntVar()
init_noise1 = Radiobutton(root, text='内容图片', variable=init_noise_var,\
                          value=0, command=init_noise_sel)
init_noise1.place(relx=0.14, rely=0.60, relwidth=0.18, relheight=0.06)
init_noise2 = Radiobutton(root, text='白噪声', variable=init_noise_var,\
                          value=1, command=init_noise_sel)
init_noise2.place(relx=0.32, rely=0.60, relwidth=0.18, relheight=0.06)
init_noise_var.set(0)

#gpu_cpu
def gpu_cpu_sel():
    if gpu_cpu_var.get() == 0:
        gpu_cpu_s = ''
    else:
        gpu_cpu_s = ' --cuda'

gpu_cpu_lb = Label(root, text='运行环境：', anchor=W)
gpu_cpu_lb.place(relx=0.5, rely=0.60, relwidth=0.14, relheight=0.06)
gpu_cpu_var = IntVar()
gpu_cpu1 = Radiobutton(root, text='GPU', variable=gpu_cpu_var,\
                       value=1, command=gpu_cpu_sel)
gpu_cpu1.place(relx=0.64, rely=0.60, relwidth=0.18, relheight=0.06)
gpu_cpu2 = Radiobutton(root, text='CPU', variable=gpu_cpu_var,\
                       value=0, command=gpu_cpu_sel)
gpu_cpu2.place(relx=0.82, rely=0.60, relwidth=0.18, relheight=0.06)
gpu_cpu_var.set(0)

#content_layer
content_layer_lb = Label(root, text='内容层:', anchor=W)
content_layer_lb.place(relx=0, rely=0.66, relwidth=0.15, relheight=0.06)
content_layer_var1 = IntVar()
content_layer1 = Checkbutton(root, text='conv_1', variable=content_layer_var1,\
                             onvalue=1, offvalue=0)
content_layer1.place(relx=0.15, rely=0.66, relwidth=0.17, relheight=0.06)
content_layer_var1.set(1)
content_layer_var2 = IntVar()
content_layer2 = Checkbutton(root, text='conv_2', variable=content_layer_var2,\
                             onvalue=1, offvalue=0)
content_layer2.place(relx=0.32, rely=0.66, relwidth=0.17, relheight=0.06)
content_layer_var3 = IntVar()
content_layer3 = Checkbutton(root, text='conv_3', variable=content_layer_var3,\
                             onvalue=1, offvalue=0)
content_layer3.place(relx=0.49, rely=0.66, relwidth=0.17, relheight=0.06)
content_layer_var4 = IntVar()
content_layer4 = Checkbutton(root, text='conv_4', variable=content_layer_var4,\
                             onvalue=1, offvalue=0)
content_layer4.place(relx=0.66, rely=0.66, relwidth=0.17, relheight=0.06)
content_layer_var5 = IntVar()
content_layer5 = Checkbutton(root, text='conv_5', variable=content_layer_var5,\
                             onvalue=1, offvalue=0)
content_layer5.place(relx=0.83, rely=0.66, relwidth=0.17, relheight=0.06)
content_layer_var2.set(0)
content_layer_var3.set(0)
content_layer_var4.set(0)
content_layer_var5.set(0)

#style_layer
style_layer_lb = Label(root, text='风格层:', anchor=W)
style_layer_lb.place(relx=0, rely=0.72, relwidth=0.15, relheight=0.06)
style_layer_var1 = IntVar()
style_layer1 = Checkbutton(root, text='conv_1', variable=style_layer_var1,\
                             onvalue=1, offvalue=0)
style_layer1.place(relx=0.15, rely=0.72, relwidth=0.17, relheight=0.06)
style_layer_var1.set(1)
style_layer_var2 = IntVar()
style_layer2 = Checkbutton(root, text='conv_2', variable=style_layer_var2,\
                             onvalue=1, offvalue=0)
style_layer2.place(relx=0.32, rely=0.72, relwidth=0.17, relheight=0.06)
style_layer_var2.set(1)
style_layer_var3 = IntVar()
style_layer3 = Checkbutton(root, text='conv_3', variable=style_layer_var3,\
                             onvalue=1, offvalue=0)
style_layer3.place(relx=0.49, rely=0.72, relwidth=0.17, relheight=0.06)
style_layer_var3.set(1)
style_layer_var4 = IntVar()
style_layer4 = Checkbutton(root, text='conv_4', variable=style_layer_var4,\
                             onvalue=1, offvalue=0)
style_layer4.place(relx=0.66, rely=0.72, relwidth=0.17, relheight=0.06)
style_layer_var4.set(1)
style_layer_var5 = IntVar()
style_layer5 = Checkbutton(root, text='conv_5', variable=style_layer_var5,\
                             onvalue=1, offvalue=0)
style_layer5.place(relx=0.83, rely=0.72, relwidth=0.17, relheight=0.06)
style_layer_var5.set(1)

#model
def model_sel():
    if model_var.get() == 0:
        model_s = ' -m vgg11'
    elif model_var.get() == 1:
        model_s = ' -m vgg13'
    elif model_var.get() == 2:
        model_s = ' -m vgg16'
    else:
        model_s = ' -m vgg19'

model_lb = Label(root, text='模型：', anchor=W)
model_lb.place(relx=0,rely=0.78, relwidth=0.2, relheight=0.06)
model_var = IntVar()
model1 = Radiobutton(root, text='vgg11', variable=model_var,\
                     value=0, command=model_sel)
model1.place(relx=0.2, rely=0.78, relwidth=0.2, relheight=0.06)
model2 = Radiobutton(root, text='vgg13', variable=model_var,\
                     value=1, command=model_sel)
model2.place(relx=0.4, rely=0.78, relwidth=0.2, relheight=0.06)
model3 = Radiobutton(root, text='vgg16', variable=model_var,\
                     value=2, command=model_sel)
model3.place(relx=0.6, rely=0.78, relwidth=0.2, relheight=0.06)
model4 = Radiobutton(root, text='vgg19', variable=model_var,\
                     value=3, command=model_sel)
model4.place(relx=0.8, rely=0.78, relwidth=0.2, relheight=0.06)
model_var.set(3)

#size
size_lb = Label(root, text='清晰度：', anchor=W)
size_lb.place(relx=0,rely=0.84, relwidth=0.2, relheight=0.06)
size_var = IntVar()
size1 = Radiobutton(root, text='低', variable=size_var, value=128)
size1.place(relx=0.2, rely=0.84, relwidth=0.2, relheight=0.06)
size2 = Radiobutton(root, text='中', variable=size_var, value=256)
size2.place(relx=0.4, rely=0.84, relwidth=0.2, relheight=0.06)
size3 = Radiobutton(root, text='高（耗时长）', variable=size_var, value=512)
size3.place(relx=0.6, rely=0.84, relwidth=0.2, relheight=0.06)
size4 = Radiobutton(root, text='超高（耗时长）', variable=size_var, value=1024)
size4.place(relx=0.8, rely=0.84, relwidth=0.2, relheight=0.06)
size_var.set(128)

#run
def run():
    args = 'python style_transfer.py'
    content_filename=content.get(0.0, END)
    args = args+' -c '+content_filename
    args=args.strip('\n')
    style_filename=style.get(0.0, END)
    args = args+' -s '+style_filename
    args=args.strip('\n')
    if content_filename.find('请选择文件')==0 or\
       style_filename.find('请选择文件')==0:
        answer=tkinter.messagebox.showerror('Error','请选择文件')
        return
    if outp.get()=='':
        answer=tkinter.messagebox.showerror('Error','请输入文件名')
        return
    output_filename=outp.get()+'.jpg'
    args = args+' -o '+output_filename
    epoch_num=str(epoch_var.get())
    args = args+' -e '+epoch_num
    content_weight_num=str(content_weight_var.get())
    args = args+' -c_w ' + content_weight_num
    style_weight_num=str(int(pow(10,style_weight_var.get())))
    args = args+' -s_w '+style_weight_num
    if init_noise_var.get() == 1:
        args = args+' -i_n'
    if gpu_cpu_var.get() == 1:
        args = args+' --cuda'
    if content_layer_var1.get()+content_layer_var2.get()+\
       content_layer_var3.get()+content_layer_var4.get()+\
       content_layer_var5.get()>0:
        args = args+' -c_l'
        if content_layer_var1.get()>0:
            args = args+' conv_1'
        if content_layer_var2.get()>0:
            args = args+' conv_2'
        if content_layer_var3.get()>0:
            args = args+' conv_3'
        if content_layer_var4.get()>0:
            args = args+' conv_4'
        if content_layer_var5.get()>0:
            args = args+' conv_5'
    else:
        answer=tkinter.messagebox.showerror('Error','请选择内容层')
        return
    if style_layer_var1.get()+style_layer_var2.get()+\
       style_layer_var3.get()+style_layer_var4.get()+\
       style_layer_var5.get()>0:
        args = args+' -s_l'
        if style_layer_var1.get()>0:
            args = args+' conv_1'
        if style_layer_var2.get()>0:
            args = args+' conv_2'
        if style_layer_var3.get()>0:
            args = args+' conv_3'
        if style_layer_var4.get()>0:
            args = args+' conv_4'
        if style_layer_var5.get()>0:
            args = args+' conv_5'
    else:
        answer=tkinter.messagebox.showerror('Error','请选择风格层')
        return
    args = args+' -m'
    if model_var.get()==0:
        args = args+' vgg11'
    if model_var.get()==1:
        args = args+' vgg13'
    if model_var.get()==2:
        args = args+' vgg16'
    if model_var.get()==3:
        args = args+' vgg19'
    args = args+' -s_z '+str(size_var.get())
    os.system(args)

run_bt = Button(root, text='生成图片', command=run)
run_bt.place(relx=0.18, rely=0.92, relwidth=0.14, relheight=0.06)

#reset
def reset():
    content.delete(0.0, END)
    content_filename=''
    content.insert(END, '请选择文件')
    style.delete(0.0, END)
    style_filename=''
    style.insert(END, '请选择文件')
    outp.delete(0, END)
    output_filename = 'result.jpg'
    outp.insert(END, 'result')
    epoch.set(300)
    content_weight.set(0)
    style_weight.set(4)
    init_noise_var.set(0)
    gpu_cpu_var.set(0)
    content_layer_var1.set(1)
    content_layer_var2.set(0)
    content_layer_var3.set(0)
    content_layer_var4.set(0)
    content_layer_var5.set(0)
    style_layer_var1.set(1)
    style_layer_var2.set(1)
    style_layer_var3.set(1)
    style_layer_var4.set(1)
    style_layer_var5.set(1)
    model_var.set(3)
    size_var.set(128)
    
reset_bt = Button(root, text='重置', command=reset)
reset_bt.place(relx=0.68, rely=0.92, relwidth=0.14, relheight=0.06)

root.mainloop()
