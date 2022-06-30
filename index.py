# coding:utf-8

import sys
import io
import os
import time
import shutil

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'l2tp'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    cmd = "ps -ef|grep xl2tpd |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def initConf():
    l2tp_cs = getServerDir() + '/chap-secrets'
    if not os.path.exists(l2tp_cs):
        mw.execShell('cp -rf ' + getPluginDir() +
                     '/conf/chap-secrets' + ' ' + getServerDir())

    l2tp_is = getServerDir() + '/ipsec.secrets'
    if not os.path.exists(l2tp_is):
        mw.execShell('cp -rf ' + getPluginDir() +
                     '/conf/ipsec.secrets' + ' ' + getServerDir())


def start():
    initConf()

    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service xl2tpd start')
    if data[0] == '':
        return 'ok'
    return data[1]


def stop():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service xl2tpd stop')
    if data[0] == '':
        return 'ok'
    return data[1]


def restart():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    data = mw.execShell('service xl2tpd restart')
    if data[0] == '':
        return 'ok'
    return data[1]


def reload():
    data = mw.execShell('service xl2tpd reload')
    if data[0] == '':
        return 'ok'
    return data[1]


def getPathFile():
    if mw.isAppleSystem():
        return getServerDir() + '/chap-secrets'
    return '/etc/ppp/chap-secrets'


def getPathFilePsk():
    if mw.isAppleSystem():
        return getServerDir() + '/ipsec.secrets'
    return '/etc/ipsec.secrets'


def getUserList():
    import re
    path = getPathFile()
    if not os.path.exists(path):
        return mw.returnJson(False, '密码配置文件不存在!')
    conf = mw.readFile(path)

    conf = re.sub('#(.*)\n', '', conf)

    if conf.strip() == '':
        return mw.returnJson(True, 'ok', [])

    ulist = conf.strip().split('\n')

    user = []
    for line in ulist:
        line_info = {}
        line = re.match(r'(\w*)\s*(\w*)\s*(\w*)\s*(.*)',
                        line.strip(), re.M | re.I).groups()
        line_info['user'] = line[0]
        line_info['pwd'] = line[2]
        line_info['type'] = line[1]
        line_info['ip'] = line[3]
        user.append(line_info)

    return mw.returnJson(True, 'ok', user)


def addUser():
    if mw.isAppleSystem():
        return mw.returnJson(False, "Apple Computer does not support")

    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]
    ret = mw.execShell('echo ' + args['username'] + '|l2tp -a')
    if ret[1] == '':
        return mw.returnJson(True, '添加成功!:' + ret[0])
    return mw.returnJson(False, '添加失败:' + ret[0])


def delUser():
    if mw.isAppleSystem():
        return mw.returnJson(False, "Apple Computer does not support")

    args = getArgs()
    data = checkArgs(args, ['username'])
    if not data[0]:
        return data[1]

    ret = mw.execShell('echo ' + args['username'] + '|l2tp -d')
    if ret[1] == '':
        return mw.returnJson(True, '删除成功!:' + ret[0])
    return mw.returnJson(False, '删除失败:' + ret[0])


def modUser():

    args = getArgs()
    data = checkArgs(args, ['username', 'password'])
    if not data[0]:
        return data[1]

    path = getPathFile()
    username = args['username']
    password = args['password']

    # sed -i "/^\<${user}\>/d" /etc/ppp/chap-secrets
    # echo "${user}    l2tpd    ${pass}       *" >> /etc/ppp/chap-secrets

    if mw.isAppleSystem():
        mw.execShell("sed -i .bak '/^\(" + username + "\)/d' " + path)
    else:
        mw.execShell("sed -i '/^\(" + username + "\)/d' " + path)
    # print 'echo "' + username + "    l2tpd    " + password + "      *\" >>"
    # + path
    ret = mw.execShell("echo \"" + username +
                       "    l2tpd    " + password + "       *\" >>" + path)
    if ret[1] == '':
        return mw.returnJson(True, '修改成功!')
    return mw.returnJson(False, '修改失败')


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'conf':
        print(getPathFile())
    elif func == 'conf_psk':
        print(getPathFilePsk())
    elif func == 'user_list':
        print(getUserList())
    elif func == 'add_user':
        print(addUser())
    elif func == 'del_user':
        print(delUser())
    elif func == 'mod_user':
        print(modUser())
    else:
        print('error')
