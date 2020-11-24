import re
import copy


class planning:
    def __init__(self, filename):
        file = open(filename)
        filestr = file.readlines()
        self.action = {}
        self.objects = {}
        self.fact = []
        self.goal = []
        self.notgoal = []
        self.path = []
        """获取domain"""
        domain = []
        parterndomain = re.compile(r"\(\s*define\s+\(\s*domain\s+(.*?)\s*\)")
        for each in filestr:
            temp = re.findall(parterndomain, each)
            if len(temp) != 0:
                domain.extend(temp)
        self.domain = domain[0]
        """获取动作序列"""
        action = []
        parternaction = re.compile(r"\(\s*:\s*action\s+(.*?)\s*\Z")
        for each in filestr:
            temp = re.findall(parternaction, each)
            if len(temp) != 0:
                action.extend(temp)
        """获取参数列表"""
        parameters = []
        parternparameters = re.compile(r"\s*:\s*parameters\s+\(\s*(.*?)\s*\)\s*\Z")
        for each in filestr:
            temp = re.findall(parternparameters, each)
            if len(temp) != 0:
                parameters.extend(temp)
        for i in range(len(parameters)):
            var = []
            parternvar = re.compile(r"[\s-]+")
            var = re.split(parternvar, parameters[i])
            self.action[action[i]] = {}
            self.action[action[i]]["para"] = {}
            for j in range(0, len(var), 2):
                self.action[action[i]]["para"][var[j]] = var[j + 1]  # 举例就是action:{变量：类型}
        """获取前提条件"""
        precondition = []
        parternpre = re.compile(r"\s*:\s*precondition\s+\(\s*(.*?)\s*\)\s*\Z")
        for each in filestr:
            temp = re.findall(parternpre, each)
            if len(temp) != 0:
                precondition.extend(temp)
        parternclause = re.compile(r"\((.*?)\)")
        parternnot = re.compile(r"not\s*\(\s*(.*?)\Z")
        for i in range(len(precondition)):
            clause = re.findall(parternclause, precondition[i])
            self.action[action[i]]["prepositive"] = []
            self.action[action[i]]["prenagative"] = []
            for each in clause:
                if "not" in each:
                    tempk = re.findall(parternnot, each)
                    tempk = re.split(r"\s+", tempk[0])
                    self.action[action[i]]["prenagative"].append(tempk)
                else:
                    tempk = re.split(r"\s+", each)
                    self.action[action[i]]["prepositive"].append(tempk)
        """获取effect"""
        effect = []
        parterneffect = re.compile(r"\s*:\s*effect\s+\(\s*(.*?)\s*\)\s*\Z")
        for each in filestr:
            temp = re.findall(parterneffect, each)
            if len(temp) != 0:
                effect.extend(temp)
        for i in range(len(effect)):
            clause = re.findall(parternclause, effect[i])
            self.action[action[i]]["efpositive"] = []
            self.action[action[i]]["efnagative"] = []
            for each in clause:
                if "not" in each:
                    tempk = re.findall(parternnot, each)
                    tempk = re.split(r"\s+", tempk[0])
                    self.action[action[i]]["efnagative"].append(tempk)
                else:
                    tempk = re.split(r"\s+", each)
                    self.action[action[i]]["efpositive"].append(tempk)

    def setproblem(self, filename):
        file = open(filename)
        filestr = file.readlines()
        self.objects = {}  # 一开始先清空objects
        self.fact = []
        self.goal = []
        """获得objects"""
        objects = []
        for each in filestr:
            temp = re.findall(r"\s*\(\s*:\s*objects\s*(.*?)\s*\)", each)
            if len(temp) != 0:
                objects.extend(temp)
        var = []
        var = re.split(r"[\s-]+", objects[0])
        for i in range(0, len(var), 2):
            self.objects[var[i]] = var[i + 1]
        """获得初始化的事实"""
        init = []
        for each in filestr:
            temp = re.findall(r"\s*\(\s*:\s*init\s*(.*?)\s*\)\s*\Z", each)
            if len(temp) != 0:
                init.extend(temp)
        condition = []
        condition = re.findall(r"\s*\((.*?)\s*\)", init[0])
        for each in condition:
            tempk = re.split(r"\s+", each)
            self.fact.append(tempk)
        """获得goal"""
        goal = []
        for each in filestr:
            temp = re.findall(r"\s*\(\s*:\s*goal\s*\(\s*(.*?)\s*\)\s*\)\s*\Z", each)
            if len(temp) != 0:
                goal.extend(temp)
        goal = re.findall(r"and\s*(.*?)\s*\Z", goal[0])
        goal = re.findall(r"\(\s*(.*?)\s*\)", goal[0])

        for each in goal:
            tempj = re.findall(r"not\s+\(\s*(.*?)\Z", each)
            if len(tempj) != 0:
                tempj = re.split(r"\s+", tempj[0])
                self.notgoal.append(tempj)
                continue
            tempk = re.split(r"\s+", each)
            self.goal.append(tempk)

    """得到所有参数的排列组合"""

    def getlist(self, para, depth, data):
        if depth == len(para):
            toreturn = []
            for each in para[depth - 1]:
                temp = copy.deepcopy(data)
                temp.append(each)
                toreturn.append(temp)
            return toreturn
        toreturn = []
        for each in para[depth - 1]:
            temp = copy.deepcopy(data)
            temp.append(each)
            toreturn.extend(self.getlist(para, depth + 1, temp))
        return toreturn

    """检查某个参数序列是不是满足能够执行动作"""

    def checkaction(self, mylist, action):
        prepositive = copy.deepcopy(action["prepositive"])
        prenagative = copy.deepcopy(action["prenagative"])
        for i in range(len(prepositive)):  # 做一个参数替换
            for j in range(1, len(prepositive[i])):
                prepositive[i][j] = mylist[prepositive[i][j]]
        for i in range(len(prenagative)):
            for j in range(1, len(prenagative[i])):
                prenagative[i][j] = mylist[prenagative[i][j]]
        for each in prepositive:  # 如果正条件在里面不满足，就返回不可执行
            if each not in self.fact:
                return False
        for each in prenagative:  # 如果负条件存在于fact中，返回不可执行
            if each in self.fact:
                return False
        return True

    """得到能够执行的动作"""

    def getaction(self, action):
        dopara = []
        wait = {}
        for para in self.action[action]["para"]:
            wait[para] = []
            for object1 in self.objects:
                if self.objects[object1] == self.action[action]["para"][para]:
                    wait[para].append(object1)
            if len(wait[para]) == 0:
                return dopara
        tempwait = []
        for key in wait:
            tempwait.append(wait[key])
        mylist = self.getlist(tempwait, 1, [])
        for each in mylist:
            temp = {}
            i = 0
            for key in wait:
                temp[key] = each[i]
                i += 1
            if self.checkaction(temp, self.action[action]):  # 一个个检查是否能够被执行。
                dopara.append(copy.deepcopy(temp))
        return dopara

    """进行某种行动以后更新fact"""

    def takeaction(self, action, dopara):
        efpositive = copy.deepcopy(self.action[action]["efpositive"])  # 为了保护数据先做一次深拷贝
        efnagative = copy.deepcopy(self.action[action]["efnagative"])
        for i in range(len(efpositive)):  # 然后进行变量替换，先替换新的
            for j in range(len(efpositive[i])):
                if efpositive[i][j] in dopara:
                    efpositive[i][j] = dopara[efpositive[i][j]]
        for each in efpositive:  # 把新的到的加入到事实中去
            if each not in self.fact:
                self.fact.append(each)
        for i in range(len(efnagative)):  # 然后那些非的结果如果事实中有的话就要删去
            for j in range(len(efnagative[i])):
                if efnagative[i][j] in dopara:
                    efnagative[i][j] = dopara[efnagative[i][j]]
        for each in efnagative:
            if each in self.fact:
                self.fact.remove(each)
        temppath = list([action])
        temppath.append(dopara)
        self.path.append(temppath)
        return 0

    """检查是否到达目标"""

    def checkgoal(self):
        for each in self.goal:
            if each not in self.fact:
                return False
        for each in self.notgoal:
            if each in self.fact:
                return False
        return True

    """展示路径"""

    def showpath(self):
        print("solution:")
        for each in self.path:
            print(each)

    """判断事实集合是否相等"""

    @staticmethod
    def usefulfact(fact1, fact2):
        if len(fact1) != len(fact2):
            return True
        for each in fact1:
            if each not in fact2:
                return True
        return False

    """松弛问题的pre就不考虑not的情况，有pre就可以了"""
    def getactionwithoutnot(self, action):
        dopara = []
        wait = {}
        for para in self.action[action]["para"]:
            wait[para] = []
            for object1 in self.objects:
                if self.objects[object1] == self.action[action]["para"][para]:
                    wait[para].append(object1)
            if len(wait[para]) == 0:
                return dopara
        tempwait = []
        for key in wait:
            tempwait.append(wait[key])
        mylist = self.getlist(tempwait, 1, [])
        for each in mylist:
            temp = {}
            i = 0
            for key in wait:
                temp[key] = each[i]
                i += 1
            if self.checkaction(temp, self.action[action]):  # 一个个检查是否能够被执行。
                dopara.append(copy.deepcopy(temp))
        return dopara


"""BFS版本"""


def BFS(node):
    myqueue = list()  # 创建一个队列
    myqueue.append(node)  # 把元素加入到队列中去
    allfact = list([node.fact])
    count = 0
    while len(myqueue) != 0:  # 当队列长度不为0的时候
        count += 1
        tempnode = myqueue[0]
        myqueue = myqueue[1:]
        for action in tempnode.action:  # 把所有能做的动作做一遍得到子节点
            dopara = tempnode.getaction(action)
            for each in dopara:
                nextnode = copy.deepcopy(tempnode)
                nextnode.takeaction(action, each)
                gonext = True
                for fact1 in allfact:
                    if not nextnode.usefulfact(fact1, nextnode.fact):
                        gonext = False
                if not gonext:
                    continue
                allfact.append(nextnode.fact)
                if nextnode.checkgoal():
                    return nextnode
                myqueue.append(nextnode)
    return False


temp100 = planning("test3_domain.txt")
temp100.setproblem("test3_problem.txt")
"""
paradd = [[1,2],[3,4],[5,6]]
temp = temp100.getlist(paradd,1,[])
temp = temp100.getaction("move")
temp100.takeaction("move",temp[0])
"""
myfinalnode = BFS(temp100)
if isinstance(myfinalnode, bool):
    print("error")
else:
    myfinalnode.showpath()
