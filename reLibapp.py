from darter.file import parse_elf_snapshot, parse_appjit_snapshot
from darter.asm.base import populate_native_references
import re
from collections import defaultdict
import os
import shutil


def get_funciont(fun_index, s, span=False):
    spanStr = ''
    if span:
        spanStr = '    '
    fun_str = '\n'+spanStr+'// 函数索引:' + '{0}'.format(fun_index)+'\n'
    returnTypeStr = ''
    if '_class' in s.refs[fun_index].x['result_type'].x.keys():
        returnTypeStr = s.refs[fun_index].x['result_type'].x['_class'].x['name'].x['value']
    elif 'name' in s.refs[fun_index].x['result_type'].x.keys():
        returnTypeStr = str(s.refs[fun_index].x['result_type'])
    else:
        returnTypeStr = s.refs[fun_index].x['result_type'].x['value']
    fun_str = fun_str+spanStr + returnTypeStr
    fun_str = fun_str + ' ' + s.refs[fun_index].x['name'].x['value']+'('
    parameterCount = 0
    if type(s.refs[fun_index].x['parameter_types'].x['value']) != type(''):
        for parameterName in s.refs[fun_index].x['parameter_names'].x['value']:
            parType = ''
            if '_class' in s.refs[fun_index].x['parameter_types'].x['value'][parameterCount].x.keys():
                parType = s.refs[fun_index].x['parameter_types'].x['value'][parameterCount].x['_class'].x['name'].x['value']
            else:
                parType = s.refs[fun_index].x['parameter_types'].x['value'][parameterCount].x['value']
            fun_str = fun_str + parType + ' '
            fun_str = fun_str + parameterName.x['value'] + ', '
            parameterCount = parameterCount + 1
    fun_str = fun_str + ') \n'+spanStr+'{ \n'
    for nrefsItem in s.refs[fun_index].x['code'].x['nrefs']:
        detail = ''
        if 'call' in nrefsItem[2]:
            detail = ' -> {0}'.format(nrefsItem[0].x['owner'])
        fun_str = fun_str + spanStr + \
            '    {0}{1}'.format(nrefsItem, detail) + '\n'

    fun_str = fun_str + spanStr+'}'
    return fun_str


def get_classDis(clas_index, s):
    class_str = '\n// 类索引:' + '{0}'.format(clas_index)+' 使用s.refs[xxxx].x跟查\n'
    superName = ''
    if '_class' in s.refs[clas_index].x['super_type'].x.keys():
        superName = s.refs[clas_index].x['super_type'].x['_class'].x['name'].x['value']
    else:
        superName = s.refs[clas_index].x['super_type'].x['value']
    class_str = class_str + \
        'class {0} : {1} {2}\n'.format(
            s.refs[clas_index].x['name'].x['value'], superName, '{')
    if type(s.refs[clas_index].x['functions'].x['value']) != type(''):
        for fun in s.refs[clas_index].x['functions'].x['value']:
            class_str = class_str+'\n'+get_funciont(fun.ref, s, True)
    return class_str+'\n\n}'


def get_lob_class(lib, s):
    all_class = ''
    for item in lib.src:
        if 'name' in item[0].x.keys():
            all_class = all_class + get_classDis(item[0].ref, s) + '\n'
    if '类索引' in all_class:
        return all_class
    else:
        return '没有获得任何信息'


def show_lob_class(lib, s):
    print(get_lob_class(lib, s))


def writeStringInPackageFile(packageFile, content):
    packageFile = packageFile.replace('dart:', 'package:dart/')
    filename = packageFile.replace('package:', 'out/')
    filePath = filename[0:filename.rfind('/')]
    content = '// {0} \n'.format(packageFile)+content
    if os.path.exists(filePath) == False:
        os.makedirs(filePath)
    file = open(filename, 'w')
    file.write(content)
    file.close()


def getFiles(elfFile, filter):
    s = parse_elf_snapshot(elfFile)
    populate_native_references(s)
    allLibrary = sorted(s.getrefs('Library'),
                        key=lambda x: x.x['url'].x['value'])
    for tempLibrary in allLibrary:
        name = tempLibrary.x['url'].x['value']
        if filter in name:
            print(name + '开始生成....')
            writeStringInPackageFile(
                name, get_lob_class(s.strings[name].src[1][0], s))
            print(name + '生成成功✅')


# 开始执行
getFiles('samples/arm-app.so', '')
