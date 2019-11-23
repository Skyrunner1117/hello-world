
# coding:utf-8
import io
import os
import time          #2019/11/9 郑晓宁
# import glob
from wand.image import Image
from wand.color import Color
from PyPDF2 import PdfFileReader, PdfFileWriter
import zipfile

memo = {}
name = ""

def getPdfReader(filename):
    reader = memo.get(filename, None)
    if reader is None:
        reader = PdfFileReader(filename, strict=False)
        memo[filename] = reader
    return reader


def _run_convert(pdfile, savedfilename, page_index, index, res=120):		#将PDF第index页转化为图片
    temp_time = time.time() * 1000                  #2019/11/9郑晓宁        开始的系统时间
    idx = page_index + 1                            #

    pageObj = pdfile.getPage(page_index)  # 获取pdf的第page_index页
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(pageObj)
    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)
    img = Image(file=pdf_bytes, resolution=res)

    img.format = 'png'

    img.compression_quality = 90
    img.background_color = Color("white")

    img_path = '%s%04d.jpg' % (savedfilename, index)
    img.save(filename=img_path)
    print(img_path)
    img.destroy()

    print('converted page %d cost time %d' % (idx, (time.time() * 1000 - temp_time)))   #输出用时


def dealPerPdf(path, file, index):
    savedfilename = path.split('/')[-1].split('-')[0] + '_'
    savedfilename = path + name + savedfilename  # 要保存的图片文件名

    new_path = os.path.join(path, file)		#PDF的路径
    pdfile = getPdfReader(new_path)  # 打开pdf文件句柄
    page_nums = pdfile.getNumPages()  # 获取pdf总页数

    for page_index in range(page_nums):
        # print(index)
        _run_convert(pdfile, savedfilename, page_index, index)
        index = index + 1
    return index


def getAllfiles(path):
    files = os.listdir(path)		#返回路径包含的文件或文件夹的名字的列表
    files.sort()
    index = 0
    for file in files:
        new_path = path + '/' + file;
        if os.path.isdir(new_path):
            getAllfiles(new_path)
        elif os.path.isfile(new_path):
            is_pdf = file.split('.')[-1]
            if is_pdf != 'pdf':
                continue
            index = dealPerPdf(path, file, index)
            index = index + 1


def DealBatchPdf(path):
    getAllfiles(path)


def doPdftoPicture(path, name1):
    #path = os.getcwd()
    #path = path+'/static/photo/test/'
    global name
    name = name1
    is_batch_deal = True
    if is_batch_deal:
        DealBatchPdf(path)
    else:
        filename = '001.pdf'  # 要处理的pdf文件名
        dealPerPdf(path, filename, 0)


def compress(path,zipstring):
    get_files_path = path+str(zipstring) # 需要压缩的文件夹
    set_files_path = path+str(zipstring)+".zip" # 存放的压缩文件地址(注意:不能与上述压缩文件夹一样)
    f = zipfile.ZipFile(set_files_path , 'w', zipfile.ZIP_DEFLATED )
    for dirpath, dirnames, filenames in os.walk( get_files_path ):
        fpath = dirpath.replace(get_files_path,'') #注意2
        fpath = fpath and fpath + os.sep or ''     #注意2
        for filename in filenames:
            f.write(os.path.join(dirpath,filename), fpath+filename)
    f.close()

