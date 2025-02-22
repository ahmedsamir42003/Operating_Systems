import json
import math
import os
from random import random
from datetime import datetime
# to remove files from the actual OS
import shutil
# to deep copy an object
import copy
from turtle import update
from leaf import leaf

class tree:
    """
    Modify a little in the __init__ function to accept initialization
    using a dictionary representation
    """
    def __init__(self, **dict):
        if dict:
            self.root = leaf(**dict)
        else:
            self.root = leaf('root', 'directory', True)

    def addChild(self, Dir, leaf):
        # check if the name exists before creating new file/folder
        if leaf.name in self.ls(Dir):
            print('Duplicated name')
            return

        # check if the user has permissions to write before creating file/folder
        if Dir.access[1]!='w':
            print('Access denied')
            return

        # changing the path of the new file to be present in the directory and creating it
        leaf.path = Dir.path + f'/{leaf.name}'
        Dir.children.append(leaf)

    # check if the permissions are entered as read, write, execute. Also a user cannot write if they can't read the file
    def validAccess(self, a):
        if len(a)>3 or a[0] not in ['r', '-'] or a[1] not in ['w', '-'] or a[2] not in ['x', '-'] or (a[1] == 'w' and a[0] == '-'):
            return False
        return True

    # return the names of files/folders in a directory or the content in a file
    def ls(self, leaf):
        if leaf.type !='directory':
            return leaf.content

        names = []
        for x in leaf.children:
            names.append(x.name)
        return names

    # iterates from root node to our last file
    def parsePath(self, path):
        # change path to a list of steps,  if a step (directory) not found then the path is wrong
        path = path.split('/')
        path.remove('root')
        # var root will be our iterator
        root = self.root
        # when we open a file/folder we must change its access time
        root.accessTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for x in path:
            # catch an error if the file/folder not found and returning the last available folder in the path
            try:
                # check if we have the read permission before accessing the file/folder then change accessTime if you have the permission,  O.W return last available folder
                if root.children[self.ls(root).index(x)].access[0] == 'r':
                    root = root.children[self.ls(root).index(x)]
                    root.accessTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    print('access denied')
                    return root
            except:
                print('Invalid path')
                return root
        return root

    def isWritable(self, f):
        if f.access[1] == 'w':
            return True
        return False

    # print the tree in the console
    def showTree(self, node):
        # we add spaces before file name = the depth of the file (number of folders before it) to create a hierarchy view
        print(' '*(len(node.path.split('/'))-1)*2, node.name)
        # if it's a directory we recursively do the same for its children
        if node.type == 'directory':
            for x in node.children:
                self.showTree(x)

    # same idead as showTree but it writes the files in the real OS
    def writeTree(self, node):
        if node.type == 'directory':
            os.makedirs(node.path)
            for x in node.children:
                self.writeTree(x)
        else:
            with open(node.path, 'w') as f:
                f.write(node.content)


    def delete(self, Dir, name):
        # we chekc if write permission is granted and if the file exist in the directory. if so,  we remove the file and modifyTime in the directory
        if Dir.access[1] == 'w':
            if name in self.ls(Dir):
                Dir.children.pop(self.ls(Dir).index(name))
                Dir.modifyTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                print('File does not exist')
                return
        else:
            print('Access denied')
            return

    def changeAccess(self, file, access):
        # check again if the entered access is the way we parse it
        if self.validAccess(access):
            file.access = access
        else:
            print('Wrong access')
            return

    # pastes a copied object
    def copy(self, Dir, file):
        # if where we are trying to paste is not a directory we say don't paste it
        if Dir.type != 'directory':
            print('operation not possible')
        else:
            # if name already exist,  change to a new name and paste it
            #TODO windows only does this to files but it merges directories if the name is the same
            if file.name in self.ls(Dir):
                file.name = 'copy_'+file.name
            self.addChild(Dir, file)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # change file dates because it's a new file
            Dir.modifyTime = now
            file.createTime = now
            file.modifyTime = now
            file.accessTime = now
            # file.path = Dir.path+'/'+file.name
            self.updatePath(Dir,file,'copy')

    def updatePath(self,Dir,f,o):
        f.path = Dir.path+'/'+f.name
        if o == 'copy':
            f.getID()
        if f.type == 'directory':
            for x in f.children:
                self.updatePath(f,x)
    # same as copy function but it asks the user if the want to overwrite the file instead of changing the name
    def cut(self, Dir, file):
        if Dir.type != 'directory':
            print('operation not possible')
        else:
            if file.name in self.ls(Dir):
                r = input('File already exist,  overwrite? (Y|N): ')
                if r == 'Y':
                    Dir.children.remove(Dir.children[self.ls(Dir).index(file.name)])
                else:
                    return
            old = self.parsePath(file.path[:file.path.rfind('/')])
            old.children.remove(old.children[self.ls(old).index(file.name)])
            self.addChild(Dir, file)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Dir.modifyTime = now
            file.createTime = now
            file.modifyTime = now
            file.accessTime = now
            # file.path = Dir.path+'/'+file.name
            self.updatePath(Dir,file,'cut')

    #TODO incomplete, we need to properly adjust size
    def updateContent(self, file):
        file.content = input('')
        file.size = len(file.content)

    #TODO we need to figure out the best way to calculate sizes of files,  directories,  partitions. Note that in partitions we have to calculate the remaining disk space
    def getSize(self, Dir):
        pass

    """
    a method that recursively generate the dictionary representation of the program 
    """
    def dict(self, node=None):
        dictt = {}
        if node == None:
            dictt[self.root.name] = self.root.children.copy()
            dictt[self.root.name].insert(0, self.root.dict())
            for i in range(1, len(dictt[self.root.name])):
                if dictt[self.root.name][i].type == 'directory':
                    dictt[self.root.name][i] = self.dict(dictt[self.root.name][i])
                else:
                    dictt[self.root.name][i] = json.dumps(dictt[self.root.name][i].dict())
        else:
            dictt[node.name] = node.children.copy()
            dictt[node.name].insert(0, node.dict())
            for i in range(1, len(dictt[node.name])):
                if dictt[node.name][i].type == 'directory':
                    dictt[node.name][i] = self.dict(dictt[node.name][i])
                else:
                    dictt[node.name][i] = json.dumps(dictt[node.name][i].dict())
        return dictt

    """
    This is used to save the program dictionary representation to 'file.json'
    in a json format
    """
    def submit(self):
        with open('file.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.dict()))

    """
    A method to return the dictionary representation of this instance
    in a string form
    """
    def __str__(self):
        return str(self.dict())

    """
    A method that is called if there is a json file found in the working directory
    and it calls the self.load() method with the 'root' as a path and the list that
    has root's information
    """
    def load_system(self):
        with open('file.json', 'r', encoding='utf-8') as f:
            dict = json.load(f)
        self.load('root', dict['root'])        
    
    """
    A method that is called by self.load_system() it is used to recursively iterate through
    the root's list of information and if it finds a file it attaches it to the current directory
    and if it finds a directory it creates it then use its information to build it.
    """
    def load(self, path, lst):
        for i in range(1, len(lst)):
            if type(lst[i]).__name__ == 'str':
                self.addChild(self.parsePath(path), leaf(**json.loads(lst[i])))
            else:
                nleaf = leaf(**lst[i][list(lst[i].keys())[0]][0])
                self.addChild(self.parsePath(path), nleaf)
                self.load(nleaf.path, lst[i][list(lst[i].keys())[0]])
