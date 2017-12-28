# -*- coding:utf-8 -*-

"cdx --- cd a directory with bookmark."

import os
import sys
import getopt
import shelve
import webbrowser 
import locale
import time

homedir = ''
shell = ''
if 'HOME' in os.environ:
    homedir = os.environ['HOME']
    shell = os.environ['SHELL']
elif 'USERPROFILE' in os.environ:
    homedir = os.environ['USERPROFILE']
    shell = os.environ['COMSPEC']
else:
    print("Home directory was not found.")
    exit(-1)

platform = sys.platform

locale_encoding = locale.getpreferredencoding()

colours = {
            'end'        :'\033[0m',
            'notes'    :'\033[32m',
            'gold'   :'\033[33m',
            'blue' :'\033[34m',
        }

cdxDir = '{}/.cdx'.format(homedir)

if sys.version[0]== '2':
    dbFile = '{}/database'.format(cdxDir).decode(locale_encoding)
if sys.version[0] == '3':
    dbFile = '{}/database'.format(cdxDir)

def init_db():
    if not os.path.exists(cdxDir):
        try:
            os.mkdir(cdxDir)
        except Exception:
            print("cdx: can not create data file.")
            sys.exit(-1)
    else:
        pass

class Cdx(object):
    "cdx"

    def usage(self):
        print("""usage: cdx [option] [arg] ..
Options and arguments:
cdx -s bookmark [dirpath|url|note1 note2 ..] # save the CURRENT dirpath or some notes as bookmark (also --save)
cdx bookmark                                 # cdx to a location or retuan notes by bookmark
cdx -l                                       # dispaly the saved bookmarks(also --list)
cdx -m old_bookmark new_bookmark             # modify a bookmark name (also --modify)
cdx -d bookmark1 bookmark2 ...               # delete a bookmark (also --delete)""")


    def version(self):
        return 'cdx version 1.2.3 ,  Dec 28 2017'

    def save(self, bookmark, apath=None):
        "save the bookmark"
        date = datetime.datetime.today()
        self._data = shelve.open(dbFile)
        if not apath:  # 如果没有提供apath值，默认保持当前目录路径。 参数apath 是个列表
            self._data[bookmark] = [os.path.abspath(os.getcwd()),'path',0, time.ctime()]
            self._data.close()
            print('cdx {0} >>> {1}'.format(bookmark,os.getcwd()))
        elif len(apath)==1:  # 如果提供了apath值长度为1，只提供一个元素作为参数
            if apath[0].startswith('~'):  # 如果第一字符为 ~ 进行置换
                tpath = os.path.expanduser(apath[0])  # 转换 ～ 为用户名home/user，再下一步判断
                if os.path.exists(tpath):  # 如果路径正确，则保存路径
                    self._data[bookmark] = [os.path.abspath(tpath), 'path', 0, time.ctime()]
                    self._data.close()
                    print('cdx {0} >>> {1}'.format(bookmark,tpath))
            if os.path.exists(apath[0]):  # 如果不是 ~ 开头的参数，并且路径存在，
                self._data[bookmark] = [os.path.abspath(apath[0]), 'path', 0, time.ctime()]
                self._data.close()
                print('cdx {0} >>> {1}'.format(bookmark,apath[0]))
            
            elif apath[0].startswith('http'): # 如果是http开头 http \ https, 直接保持为url标签
                self._data[bookmark] = [apath[0], 'url', 0, time.ctime()]
                self._data.close()

            else:  # 如果不是路径也不是url，则保存为笔记
                self._data[bookmark] =  [apath[0], 'note', 0, time.ctime()]
                self._data.close()
                columns =  os.get_terminal_size()[0]  # 获取终端列宽
                if len(apath[0]) < columns:
                    print("cdx {0} >>> {1}".format(bookmark, apath[0]))
                else:  # 优化排版
                    print("cdx {0} >>> {1}...".format(bookmark, apath[0][:columns-len(apath[0])-3]))
        elif len(apath)>1:  # 如果 apath 参数的元素 大于1个， 则连接保存元素
            notes = ' '.join(apath)
            self._data[bookmark] = [notes, 'notes', 0, time.ctime()]
            self._data.close()
            columns =  os.get_terminal_size()[0]
            if len(notes) < columns:
                print("cdx {0} >>> {1}".format(bookmark, notes))
            else:
                print("cdx {0} >>> {1}...".format(bookmark, notes[:columns-len(apath[0])-3]))


    def list_bookmarks(self):  # 展示所有保存到书签
        "display the paths marked"
        self._data = shelve.open(dbFile)
        
        print("-"*70)
        print("{:16}    {:16}".format("Bookmarks", "Locations"))
        print("-"*70)
        if not self._data:
            print("-"*columns)
            print("Empty bookmark! 'cdx -s bookmark [dirpath]' to save a bookmark.")
        # columns =  os.get_terminal_size()[0]
        Cdx.listEven(self,'path')
        Cdx.listEven(self,'url')
        Cdx.listEven(self,'note')
        self._data.close()
    

    def listEven(self,even):
        columns =  os.get_terminal_size()[0]
        for k, v in self._data.items():
            if v[1] == even:
                if platform == 'linux':
                    if len(v[0]) <= columns-20:
                        print('{0}{1:10}{2}    {3}{4}{5}'.format(colours['gold'], k, colours['end'], colours['blue'], v[0], colours['end']))
                    else:
                        print('{0}{1:10}{2}    {3}{4}...{5}'.format(colours['gold'], k, colours['end'], colours['blue'], v[0][:(columns-20)], colours['end']))
                else:
                    if len(v[0]) <= columns-20:
                        print('{0:10}    {1}'.format(k, v))
                    else:
                        print('{0:10}    {1}...'.format(k, v[:(columns-20)]))
                print("-"*columns)


    def cdx(self, bookmark):
        "cd to the location path marked"
        self._data = shelve.open(dbFile)

        if bookmark in self._data.keys():
            if not self._data[bookmark][0].startswith('http'):
                if os.path.exists(self._data[bookmark][0]):
                    os.chdir(self._data[bookmark][0])
                    self._data[bookmark][2] += 1
                    self._data.close()
                    os.system(shell)
                else:
                    print(self._data[bookmark][0])
                    self._data[bookmark][2] += 1
            else:
                webbrowser.open(self._data[bookmark][0])
                self._data[bookmark][2] += 1
                self._data.close()
                if platform == 'linux':
                    os.system(shell) 
        else:
            if os.path.exists(bookmark):
                os.chdir(bookmark)
                self._data[bookmark][2] += 1
                self._data.close()
                os.system(shell)
            elif bookmark.startswith('http'):
                webbrowser.open(bookmark)
                self._data[bookmark][2] += 1
                self._data.close()
                if platform == 'linux':
                    os.system(shell)
            else:
                self._data.close()
                print("cdx: '{}' is not in the bookmarks or the location does not exist.\
                \nusing 'cdx -s bookmark [dirpath]' to save a bookmark.".format(bookmark))
                Cdx.list_bookmarks(self)
                    


    def modify(self, old_bookmark, new_bookmark):
        "modify bookmarks"
        self._data = shelve.open(dbFile)
        try:
            self._data[new_bookmark] = self._data[old_bookmark]
            del self._data[old_bookmark]
            print("cdx {0} >>> {1}".format(new_bookmark, self._data[new_bookmark]))
            self._data.close()
        except Exception:
            Cdx.list_bookmarks(self)
    def dalete(self, bookmarks):
        "delete bookmark"
        self._data = shelve.open(dbFile)
        for bk in bookmarks:
            if bk in self._data:
                del self._data[bk]
                print("cdx: '{}' was removed.".format(bk))
            else:
                print("cdx: fail to delete '{}'.".format(bk))
        Cdx.list_bookmarks(self)

    def truncate(self):
        "clear the data."
        print("Do you really want to truncate the datafile?")
        if sys.version[0] == '3':
            warning = input("y / n ? >  ")
        else:
            warning = raw_input("y / n ? >  ")
        if warning == 'y':
            
            if platform == "win32":
                os.system("RD /S /Q {}".format(cdxDir))
            else:
                #os.chdir(cdxDir)
                os.remove(dbFile)
            self._data = shelve.open(dbFile)
            self._data.clear()
            self._data.close()
            print("Data is empty.\nUsing 'cdx -s bookmark [dirpath]' to save a bookmark.")
        else:
            sys.exit(0)


def main():
    "get options and arguments from command."
    init_db()
    cdx_go = Cdx()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvls:dm:t", ["help", 'version', 'list',\
        'save=', 'delete=', 'modify=', 'truncate'])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    for name, value in opts:
        if name in ("-h", "--help"):
            cdx_go.usage()
            sys.exit(0)
        elif name in ('-s', '--save'):
            if name == '-s':
                if not args:
                    cdx_go.save(value)
                else:
                    cdx_go.save(value, args)
            if name == '--save':
                if value and not args:
                    cdx_go.save(value)
                elif value and args:
                    cdx_go.save(value, args)
            sys.exit(0)
        elif name in ('-l', '--list'):
            cdx_go.list_bookmarks()
            sys.exit(0)
        elif name in ('-d'):
            if args:
                    cdx_go.dalete(args)
                    sys.exit(0)
            else:
                print('Enter bookmarks to delete.')
                print('cdx -d bookmark_1 bookmark_2 bookmark_3 ...')
                sys.exit(1)

        elif name in ('-v', '--version'):
            print(cdx_go.version())
            sys.exit(0)
        elif name in ('-m', '--modify'):
            cdx_go.modify(value, args[0])
            sys.exit(0)
        elif name in ('-t','--truncate'):
            cdx_go.truncate()
            sys.exit(0)
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        for x in args:
            cdx_go.cdx(x)
    else:
        # os.chdir(homedir)
        cdx_go.usage()
        cdx_go.list_bookmarks()
        # os.system(shell)



if __name__ == "__main__":
    sys.exit(main())
