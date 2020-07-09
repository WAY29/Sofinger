'''
@Description:Myplugin Main
@Author: Longlone
@LastEditors  : Longlone
@Date: 2020-01-07 16:37:40
@LastEditTime : 2020-01-11 13:00:37
'''
from os import listdir, path


class Platform():
    '''从目录中导入插件

        @param:

        plugin_path=plugins 相对目录路径

        required=None 导入的插件必须的函数名,否则导入失败

        load_now=[TRUE/flase] 当初始化该类时立即从相对目录下导入所有路径

        message=[FALSE/true] 是否保存插件导入的消息,如保存,则可以通过调用get_messages与print_messages来得到/输出消息列表
    '''

    def __init__(self, plugin_path='plugins', required=None, load_now=True, message=False):  # 初始化,导入文件夹下所有模块
        self.plugin_path = plugin_path.replace('\\', '.').replace('/', '.')
        self.__require = required
        self.__message = message
        self.__plugin_dict = {}
        self.__message_dict = {}
        self.loaded_plugins = 0
        self.total_plugins = 0
        if (load_now is True):
            self.load_all(plugin_path)

    def load(self, pluginName):  # 加载某个插件
        loaded = False
        required = True
        try:
            plugin = __import__(self.plugin_path + '.' +
                                pluginName, fromlist=[pluginName])
            if (self.__require is not None):
                if (hasattr(plugin, self.__require)):
                    loaded = True
                else:
                    required = False  # 没有需要的插件
            else:
                loaded = True
            self.total_plugins += 1
            if (loaded is True):  # 加载成功
                self.__plugin_dict[pluginName] = plugin
                self.loaded_plugins += 1
            if (self.__message is True):  # 需要输出信息
                if (required is True):
                    self.__message_dict[pluginName] = self.plugin_path + \
                        '.' + pluginName + ' Success Loaded.'
                else:
                    self.__message_dict[pluginName] = self.plugin_path + \
                        '.' + pluginName + ' Failed Loaded by missing required.'
        except ImportError as e:  # 导入错误
            if (self.__message is True):
                self.__message_dict[pluginName] = self.plugin_path + \
                    '.' + pluginName + ' Failed Loaded.' + str(e)

    def load_all(self, plugin_path):  # 读取目录下所有插件
        for filename in listdir(plugin_path):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue
            pluginName = path.splitext(filename)[0]
            self.load(pluginName)

    def all_loaded(self):  # 成功载入所有插件
        return True if self.loaded_plugins == self.total_plugins else False

    def call(self, plugin_name, func_name, args):  # 运行一个插件中的函数
        if (type(args) != tuple):
            return None
        func = getattr(self.get(plugin_name), func_name)
        return func(*args)

    def call_all(self, func_name, args):  # 运行所有插件中的某个函数
        if (type(args) != tuple):
            return None
        response_dict = {}
        for x in self.names():
            try:
                func = getattr(self.get(x), func_name)
                response_dict[x] = func(*args)
            except Exception:
                continue
        return response_dict

    def get_messages(self):  # 获取所有信息
        return self.__message_dict.values()

    def print_messages(self):  # 输出所有信息
        for v in self.__message_dict.values():
            print(v)

    def names(self):  # 获取所有已导入插件的名字
        return self.__plugin_dict.keys()

    def plugins(self):  # 获取所有已导入插件
        return self.__plugin_dict.values()

    def items(self):  # 获取所有已导入插件及其名字
        return self.__plugin_dict.items()

    def has_method(self, plugin_name, method_name):
        return hasattr(self.__plugin_dict[plugin_name], method_name)

    def get(self, plugin_name):  # 获得某个导入的插件
        return self.__plugin_dict[plugin_name] if (plugin_name in self.__plugin_dict) else None

    def __getitem__(self, plugin_name):  # 获得某个导入的插件
        return self.__plugin_dict[plugin_name] if (plugin_name in self.__plugin_dict) else None

    def __delitem__(self, plugin_name):  # 删除某个导入的插件
        del(self.__plugin_dict[plugin_name])

    def __call__(self, func_name, args):  # 调用call_all函数
        return self.call_all(func_name, args)

    def __contains__(self, plugin_name):  # 某个插件是否存在于该平台上
        if (plugin_name in self.__plugin_dict):
            return True
        else:
            return False

    def __len__(self):  # 获取已导入插件的个数
        return self.total_plugins

    def __iter__(self):  # 迭代初始化
        self.__iter = iter(self.__plugin_dict.values())
        return self

    def __next__(self):  # 迭代
        return next(self.__iter)
