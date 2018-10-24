import markdown
import json
import os

from django.views.decorators.csrf import csrf_exempt
from markdown.extensions.toc import TocExtension
from django.shortcuts import render, render_to_response, redirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, response, StreamingHttpResponse
from app import models
from app.models import UserInfo
from app import check_code
from io import BytesIO
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag

def forget(request):
    error_msg=""
    if request.method == 'GET':
        return render(request, 'forget.html')

def register(request):
    error_msg=""
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        teamDirect = {'0': 'DQA部门', '1': '产品合规', '2': '体系组','3': '可靠性保证', '4': '标准化实验室', '5': '硬件测试', '6': '软件测试'}
        userId = request.POST.get('gonghao')
        password = request.POST.get('pass')
        repassword = request.POST.get('repass')
        username = request.POST.get('username')
        L_team = request.POST.get('team')
        L_team = teamDirect[L_team]
        post_check_code = request.POST.get('vercode')
        print(post_check_code)
        session_check_code = request.session['check_code']
        print(session_check_code)
        if post_check_code.lower() == session_check_code.lower():
            if (password == repassword):
                UserInfo.objects.get_or_create(userId=userId,
                                               defaults={'password': password, 'username': username, 'L_team': L_team})
            else:
                error_msg = "两次输入的密码不一致"
                return render_to_response('register.html', {'error_msg': error_msg})
        else:
            error_msg = "验证码不正确"
            return render_to_response('register.html', {'error_msg': error_msg})
        return HttpResponseRedirect('/login/')



def login(request):
    error_msg = ""
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        post_check_code = request.POST.get('vercode')   #人类验证
        session_check_code = request.session['check_code']
        post_check_code = post_check_code.lower()
        session_check_code = session_check_code.lower()
        if post_check_code == session_check_code:
            userId = request.POST.get('gonghao')
            password = request.POST.get('pass')
            #user = auth.authenticate(userId=userId, password=password)# 去auth_user表中查数据（默认）不知道username是不是必填项  好像只能通过username查找数据
            #print("user", user) #打印出user为NONE
            user = models.UserInfo.objects.get(userId=userId, password=password)
            print("user", user)
            if user:
                #auth.login(request, user)  # 设置session
                #response = HttpResponseRedirect('/index/')  #括号内的值应该为什么？
                #response.set_cookie('userId', userId, 3600)  # 设置cookie
                #return response
                response = render(request, 'blogindex.html')
                response = redirect('/blogindex/')
                response.set_cookie('Id', userId,max_age=3600)
                return response
            else:
                error_msg = '用户名或密码错误'
                return render_to_response('login.html', {'error_msg': error_msg})  # data还未在前端设置
        else:
            error_msg = '验证码错误'
            return render_to_response('login.html', {'error_msg': error_msg})  # data还未在前端设置


def cookie_get(request):
    response = HttpResponse("读取Cookie，数据如下：<br>")
    if 'Id' in request.COOKIES:
        response.write('<h1>' + request.COOKIES['Id'] + '</h1>')
    return response


def dglogout(request):
    if request.method == 'GET':
        auth.logout(request)
        response = HttpResponse('退出成功')
        response.delete_cookie('Id')
        return response
    return HttpResponseRedirect('/login/')


def change_pwd(request):
    error_msg=""
    if request.method == 'POST':
        userId=request.COOKIES["Id"]
        password = request.POST.get('nowpass')
        obj = models.UserInfo.objects.get(userId=userId)
        pas = obj.password
        if (pas == password):
            passw = request.POST.get('pass')
            repassw = request.POST.get('repass')
            if(passw == repassw):
                obj.update(password=passw)
            else:
                error_msg = "两次输入的密码不一致！"
                return render_to_response('set.html', {'error_msg': error_msg})  #应该加一个弹窗
        else:
            error_msg = "密码不正确"
            return render_to_response('set.html', {'error_msg': error_msg})
    else:
        return render(request,'login.html')


def create_code_img(request):
    f = BytesIO()  # 直接在内存开辟一点空间存放临时生成的图片
    img, code = check_code.create_validate_code()  # 调用check_code生成照片和验证码
    request.session['check_code'] = code  # 将验证码存在服务器的session中，用于校验
    img.save(f, 'PNG')  # 生成的图片放置于开辟的内存中
    return HttpResponse(f.getvalue())  # 将内存的数据读取出来，并以HttpResponse返回


def adblog(request):
    if request.method == 'GET':
        category_list = Category.objects.all()
        return render(request, 'addblog.html',{'category_list':category_list})
    else:
        userId = request.COOKIES["Id"]
        if(userId):
            category = request.POST.get("category_id")
            Category.objects.get_or_create(name=category)
            title = request.POST.get('title')
            body = request.POST.get('body')
            excerpt = body[:54]
            obj = Category.objects.filter(name=category)
            category_id = obj.id
            obj1 = models. Post.objects.create(title=title, body=body, excerpt=excerpt, category_id=category_id, author_id=userId)
            #处理标签
            tag = request.POST.get('tag')
            tag_list = tag.split(',')
            for ta in tag_list:
                Tag.objects.get_or_create(name=ta)
            for ta in tag_list:
                obj = models.Tag.objects.get(name=ta)
                tag_id = obj.id
                obj1.tags.add(tag_id)
            message = "添加成功！"
            return render(request,'addblog.html',{"message":message})
        else:
            message = "添加失败！"
            return render(request, 'addblog.html', {"message": message})

def mainpage(request):
    if request.method == 'GET':
        print(request.method)
        return render(request, 'mainpage.html')

def list1(request):
    return render(request, 'list1.html')#这个页面便会呈现到上面的iframe


def addblog(request):
    if request.method == 'GET':
        file_list = models.Post.objects.filter(author_id=956)
        category_list = []
        for file in file_list:
            category_list.append(file.category.name)
        i = 0
        dict = {}
        length = len(category_list)
        while i < length:
            dict[category_list[i]] = category_list[i]
            i = i + 1
        print(dict)
        return render(request, 'addblog.html', {'dict': dict})

    if request.method == 'POST':
        category = request.POST.get("category_id")
        print(category)
        Category.objects.get_or_create(name=category)
        title = request.POST.get('title')
        print(title)
        body = request.POST.get('body')
        print(body)
        excerpt = body[:54]
        print(excerpt)
        obj = Category.objects.get(name=category)
        category_id = obj.id
        print(category_id)
        obj1 = models. Post.objects.create(title=title, body=body, excerpt=excerpt, category_id=category_id, author_id=956)
        #处理标签
        tag = request.POST.get('tag')
        print(tag)
        tag_list = tag.split(',')
        for ta in tag_list:
            Tag.objects.get_or_create(name=ta)
        for ta in tag_list:
            obj = models.Tag.objects.get(name=ta)
            print(obj)
            tag_id = obj.id
            obj1.tags.add(tag_id)
        message = "添加成功！"
        return render(request,'addblog.html',{"message":message})
    else:
        message = "添加失败！"
        return render(request, 'addblog.html', {"message": message})

def blogind(request):
    value = request.COOKIES["Id"]
    if(value.isdigit()):     #判断cookie是否全为数字
        post_list = Post.objects.filter(author_userId=value)
        return render(request, 'blogindex.html', context={'post_list': post_list})
    else:
        return render(request,'login.html')

class IndexView(ListView):
    model = Post
    template_name = 'blogindex.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        """

        # 首先获得父类生成的传递给模板的字典。
        context = super(IndexView, self).get_context_data(**kwargs)

def getCateGoryData(request):
    if request.method == "GET":
        return render(request, 'blogindex.html')

    elif request.method == "POST":
        file_list = models.Post.objects.filter(author_id=956)
        print(file_list)
        files = []
        for file in file_list:
            print(repr(file))
            item = {}
            item['categoryname'] = file.category.name
            files.append(item)
        response_data = json.dumps(files)
        print(response_data)
        return HttpResponse(response_data, "application/json")


def file_download(request,*args,**kwargs):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f: #如果不加‘rb’以二进制方式打开，文件流中遇到特殊字符会终止下载，下载下来的文件不完整
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    path_root = "E:\\download"
    if kwargs['fpath'] is not None and kwargs['fname'] is not None:
        #file_fpath = os.path.join(path_root, kwargs['fpath'])  # kwargs['fapth']是文件的上一级目录名称
        file_dstpath = os.path.join(path_root, kwargs['fname'])  # kwargs['fname']是文件名称
        response = StreamingHttpResponse(file_iterator(file_dstpath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(kwargs['fname'])  # 此处kwargs['fname']是要下载的文件的文件名称
        return response

@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        myFile = request.FILES.get("file", None) # 获取上传的文件，如果没有文件，则默认为None
        filename = myFile.name
        data = request.POST
        parentId = request.POST.get("parentid")
        print(parentId)
        levle = request.POST.get("level")
        print(levle)
        print(data)
        print(filename)
        filesize = myFile.size
        print(filesize)
        if not myFile:
            item = {}
            item['mag'] = 'no files for upload!'
            response_data = json.dumps(item)
            return HttpResponse(response_data, "application/json")
            #return HttpResponse("no files for upload!")
        destination = open(os.path.join("E:\\upload",myFile.name),'wb+')    # 打开特定的文件进行二进制的写操作
        path = os.path.join("E:\\upload",myFile.name)
        file = os.path.splitext(path)
        filepath, filetype = file
        print(filepath)
        print(filetype)
        for chunk in myFile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()
        item = {}
        item['mag'] = 'upload over!'
        response_data = json.dumps(item)
        return HttpResponse(response_data, "application/json")
    if request.method == "GET":
        data = request.GET
        print(data)
        item1 = {}
        item1['mag'] = 'over!'
        response_data1 = json.dumps(item1)
        return HttpResponse(response_data1, "application/json")

def blogindex1(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blogindex1.html', context={'post_list': post_list})