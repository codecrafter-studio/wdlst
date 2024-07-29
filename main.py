import tkinter as tk
#import tkinter.ttk as ttk
import tkinter.simpledialog as dlg
import tkinter.filedialog as filedlg
import json
import sys
if sys.platform=="win32":
    import win32com.client
import threading
import random

def readfile(path):#读取列表（返回字典）
    f=open(path,'r',encoding='utf-8')
    cont=f.read()
    cont=cont.replace("'",'"')#在读取的时候，必须把所以单引号换成双引号
    contjson=json.loads(cont)
    return contjson

def writefile(path,contjson):#写入列表（传入路径、字典）
    f=open(path,'w',encoding='utf-8')
    cont=str(contjson)
    f.write(cont)

def refresh(contjson,item=None,word=None):#针对直接给定单词内容的调用，这里设一个word可选参数
    global wordtxt,cntxt,lstbox
    lstbox.delete(0,tk.END)
    for i in contjson.keys():
        lstbox.insert(tk.END,str(i))
    if item!= None:#软件启动时没有选择任何内容
        #详情部分的标题变动
        wordtxt['text']=list(contjson.keys())[item]
        cntxt['text']=''
        #详情部分的中文变动
        for i in contjson[wordtxt['text']]:
            cntxt['text']+=i
            cntxt['text']+='   '
        #解决蓝背景缺失的问题
        lstbox.selection_set(item)
        lstbox.see(item)
    elif word!= None:#基本上还是老套路
        #详情部分的标题变动
        wordtxt['text']=word
        cntxt['text']=''
        #详情部分的中文变动
        for i in contjson[word]:
            cntxt['text']+=i
            cntxt['text']+='   '
        #解决蓝背景缺失的问题
        lstbox.selection_set(list(contjson.keys()).index(word))
        lstbox.see(list(contjson.keys()).index(word))

def delete(item):#删除词汇
    global lstpath
    cont=readfile(lstpath)
    cont.pop(list(readfile(lstpath).keys())[item])
    writefile(lstpath,cont)
    refresh(readfile(lstpath))

def edit(word,cn):#完成编辑并保存
    global lstpath,editwin
    editwin.destroy()
    lst=readfile(lstpath)
    if word!='':
        lst[word]=cn
        writefile(lstpath,lst)
    refresh(lst,word=word)

def editui(cont,word=''):#编辑与创建（界面）
    global win,editwin
    editwin=tk.Toplevel()
    editwin.transient(win)
    editwin.configure(background='#FFFFFF')
    editwin.title('创建与编辑 - WordLST')
    tk.Label(editwin,text='目标词条',anchor='w',bg='#FFFFFF',font=('等线',15)).pack(fill=tk.X,padx=20)
    wordentry=tk.Entry(editwin,bd=0,bg='#EEEEEE',font=('等线',15))
    wordentry.pack(fill=tk.X)
    tk.Label(editwin,text='词性与义项',anchor='w',bg='#FFFFFF',font=('等线',15)).pack(fill=tk.X,padx=20)
    cnlst=tk.Listbox(editwin,width=20,bd=0,font=('等线',15),highlightbackground='#FFFFFF',highlightthickness=0,selectbackground='#0078D7',bg='#EEEEEE',activestyle='none')
    cnlst.pack(fill=tk.BOTH)
    btnpt=tk.Frame(editwin,bg='#FFFFFF')
    btnpt.pack(fill=tk.X)
    tk.Button(btnpt,text='添加',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:cnlst.insert(tk.END,dlg.askstring('输入词性与义项','请输入欲添加的词性与义项'))).pack(side=tk.LEFT,fill=tk.X,expand=True)
    tk.Button(btnpt,text='移除',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:cnlst.delete(gs(cnlst))).pack(side=tk.RIGHT,fill=tk.X,expand=True)
    tk.Button(editwin,text='完成',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:edit(word=wordentry.get(),cn=list(cnlst.get(0,tk.END)))).pack(fill=tk.X,expand=True)
    editwin.resizable(0,0)
    #在输入框内填入传入的词汇
    wordentry.insert(tk.END,word)
    #如果传入的词汇数据包含在当前的字典中，则将义项插入输入框
    if word in cont:
        for i in cont[word]:
            cnlst.insert(tk.END,i)
    editwin.focus()
    #editwin.lift()
    wordentry.bind("<Return>",lambda event:cnlst.insert(tk.END,dlg.askstring('输入词性与义项','请输入欲添加的词性与义项')))
    editwin.mainloop()


def resize(event=None):#自适应
    global root,window_width,window_height
    if event != None:
        # listen events of window resizing.
        # 窗口宽高任一值产生变化，则记录并使自适应窗体调整。
        if window_width != root.winfo_width() or window_height != root.winfo_height():
            if window_width != root.winfo_width():
                window_width = root.winfo_width()
                cntxt['width']=root.winfo_width()-370
            if window_height != root.winfo_height():
                window_height = root.winfo_height()

def pickword(lst,txt):
    global truewd
    truewd=random.choice(list(lst.keys()))
    txt['text']=random.choice(lst[truewd])#.split('.')[1]
    #print(truewd)
    #print(txt['text'])
    return truewd

def nextwd(wd,txt,enter,win):
    global chklst,truelst,truewd
    enter.delete(0,tk.END)
    if wd==truewd:
        truelst.append(wd)
    chklst.pop(truewd)#int(list(chklst.keys()).index(truewd)))
    if chklst!={}:
        pickword(chklst,txt)
    else:
        win.destroy()
        doneui()

def doneui():
    global truelst,win
    #root.deiconify()
    dwin=tk.Toplevel()
    dwin.title('词汇选择 - WordLST')
    #dwin.transient(1)
    dwin.configure(background='#FFFFFF')
    dwin.protocol("WM_DELETE_WINDOW",lambda:done([],dwin))
    tk.Label(dwin,text='选择一切您认为自己已经掌握的词汇',bg='#FFFFFF',font=('等线',15),anchor='w').pack(fill=tk.X,padx=20)
    dlst=tk.Listbox(dwin,width=20,bd=0,font=('等线',15),highlightbackground='#FFFFFF',highlightthickness=0,selectbackground='#0078D7',bg='#EEEEEE',activestyle='none',selectmode='multiple',height=20)
    dlst.pack(fill=tk.BOTH)
    tk.Button(dwin,text='完成',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:done(dlst.curselection(),dwin)).pack(fill=tk.X,expand=True)
    for i in truelst:
        dlst.insert(tk.END,i)

def done(si,w):
    global truelst,root
    root.deiconify()
    lst=readfile(lstpath)
    slst=[]
    #获取选中项
    for i in list(si):
        slst.append(truelst[int(i)])
    #删除已经背下来的
    for wd in slst:
        lst.pop(wd)
    print(lst)
    writefile(lstpath,lst)
    w.destroy()
    refresh(lst)

def check(cont):
    #初始化
    global win,cwin,chklst,truelst
    root.withdraw()
    chklst=cont
    truelst=[]
    #窗口
    cwin=tk.Toplevel()
    #cwin.transient(win)
    cwin.configure(background='#FFFFFF')
    cwin.title('自我测验 - WordLST')
    ctxt=tk.Message(cwin,text='自我测验',bg='#FFFFFF',font=('等线',25),anchor='w',width=350)
    ctxt.pack(fill=tk.X,pady=10)
    center=tk.Entry(cwin,bd=0,bg='#EEEEEE',font=('等线',25))
    center.pack(fill=tk.X)
    center.bind('<KeyPress-Return>',lambda event:nextwd(center.get(),ctxt,center,cwin))
    tk.Button(cwin,text='下一个  >',bd=0,bg='#0078D7',fg='#FFFFFF',font=('等线',20),command=lambda:nextwd(center.get(),ctxt,center,cwin)).pack(fill=tk.X)
    #主要
    pickword(chklst,ctxt)
    cwin.resizable(0,0)

def gs(lb):
    if len(lb.curselection())==0:
        return 0
    else:
        return lb.curselection()[0]

def _handle_ask_list_file_selection(choosewin,create=False):
    global lstpath
    if create:
        lstpath=filedlg.asksaveasfilename(title='新建单词表文件',filetypes=[('单词表文件','.wdl')])+".wdl"
        f=open(lstpath,"w",encoding="utf-8")
        f.write("{}")
        f.close()
    else:
        lstpath=filedlg.askopenfilename(title='请选择单词表文件',filetypes=[('单词表文件','.wdl')])
    choosewin.destroy()
    refresh(readfile(lstpath))
    return lstpath

def ask_list_file():
    global root
    choosewin=tk.Toplevel()
    choosewin.transient(root)
    choosewin.configure(background="#ffffff")
    tk.Label(choosewin,text="",bg="#ffffff",anchor=tk.W).pack(fill=tk.X,padx=35)
    tk.Label(choosewin,text="开始背诵吧！",bg="#ffffff",anchor=tk.W).pack(fill=tk.X,padx=35)
    tk.Button(choosewin,text="→ 打开一个已存在的单词表",bg="#ffffff",fg="#0078dc",bd=0,anchor=tk.W,
              command=lambda:_handle_ask_list_file_selection(choosewin,False)).pack(fill=tk.X,padx=35)
    tk.Button(choosewin,text="→ 新建一个单词表",bg="#ffffff",fg="#0078dc",bd=0,anchor=tk.W,
              command=lambda:_handle_ask_list_file_selection(choosewin,True)).pack(fill=tk.X,padx=35)
    tk.Label(choosewin,text="",bg="#ffffff",anchor=tk.W).pack(fill=tk.X,padx=35)
    choosewin.update()
    choosewin.geometry("{w}x{h}+{x}+{y}".format(w=choosewin.winfo_width(),h=choosewin.winfo_height(),
                                                x=root.winfo_x()+(root.winfo_width()-choosewin.winfo_width())//2,
                                                y=root.winfo_y()+(root.winfo_height()-choosewin.winfo_height())//2))
    choosewin.mainloop()


try:#每日诗词
    import requests
    req=requests.get("https://v1.jinrishici.com/all.json")
    contjson=req.json()
    sent=contjson['content']+'     ——'+contjson['author']+'《'+contjson['origin']+'》'
except:#获取失败的话，也不能让那里空着
    sent='今天也要加油背诵呢！'

window_width=720
window_height=480

root=tk.Tk()
root.title('WordLST')
if sys.platform=="win32":
    root.iconbitmap("./icon.ico")
root.configure(background='#FFFFFF')
root.minsize(750,480)

tk.Label(root,text='单词本',anchor='w',font=('等线',30),bg='#FFFFFF').pack(fill=tk.X,padx=40,pady=20)
tk.Label(root,text=sent,anchor='w',font=('等线',12),bg='#FFFFFF').pack(fill=tk.X,padx=40)

#主要部分
win=tk.Frame(root,bg='#FFFFFF')

lstbox=tk.Listbox(win,width=20,bd=0,font=('等线',15),highlightbackground='#FFFFFF',highlightthickness=0,selectbackground='#0078D7',bg='#FFFFFF',activestyle='none')
lstbox.pack(side=tk.LEFT,fill=tk.Y,padx=10,pady=20)

win.pack(fill=tk.BOTH,expand=True)

#词汇详情部分
infopt=tk.Frame(win,bg='#FFFFFF')

wordtxt=tk.Button(infopt,text='Word',bg='#FFFFFF',font=('等线',30),anchor='w',bd=0)
wordtxt.pack(fill=tk.X,padx=60,pady=20)
if sys.platform=="win32":
    wordtxt['command']=lambda:spk.speak(wordtxt['text'])

cntxt=tk.Message(infopt,text='n.单词',bg='#FFFFFF',font=('等线',15),anchor='w',width=350)
cntxt.pack(fill=tk.X,padx=60,pady=20)

#功能按钮部分
btnpt=tk.Frame(infopt,bg='#FFFFFF')
btnpt.pack(fill=tk.X)

infopt.pack(fill=tk.BOTH,side=tk.RIGHT,expand=True)

#列表框初始内容
lstbox.insert(tk.END,'请稍候...')

tk.Button(btnpt,text='添加',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:editui(readfile(lstpath))).pack(side=tk.LEFT,fill=tk.X,expand=True,pady=5,padx=10)
tk.Button(btnpt,text='编辑',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:editui(readfile(lstpath),lstbox.get(lstbox.curselection()))).pack(side=tk.LEFT,fill=tk.X,expand=True,pady=5,padx=10)
tk.Button(btnpt,text='删除',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:delete(gs(lstbox))).pack(side=tk.LEFT,fill=tk.X,expand=True,pady=5,padx=10)
tk.Button(btnpt,text='考察',bd=0,bg='#0078D7',fg='#FFFFFF',command=lambda:check(readfile(lstpath))).pack(side=tk.LEFT,fill=tk.X,expand=True,pady=5,padx=10)
root.update()

#事件绑定
lstbox.bind('<<ListboxSelect>>',lambda event:refresh(readfile(lstpath),gs(lstbox)))#自动切换
root.bind('<Configure>', resize)#自适应

#启动执行
#TTS初始化
if sys.platform=="win32":
    spk=win32com.client.Dispatch("SAPI.SpVoice")
    spk.Voice=spk.GetVoices().Item(1)
#加载列表
ask_list_file()
#root.withdraw()
#lstpath=filedlg.askopenfilename(title='请选择单词表文件',filetypes=[('单词表文件','.wdl')])
root.deiconify()

#窗口刷新
root.mainloop()
