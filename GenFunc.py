import logging
import logging.handlers
from logging.config import dictConfig
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from email.mime.text import MIMEText

"""
The Generic Functions and Classes for System Linux Team

@Author: Adi Haim, System Linux Administrator
@Email: adi.shimon.haim@gmail.com
"""

class LOG(object):
    """
    Build and Create a Log and Logger for your Application

    """
    def __init__(self, appname, logpath):
        """
        This Class is for configure the log file.
        it will return only the loggers.

        :return: LoggerFile, LoggerStream
        """
        logging.handlers.WatchedFileHandler("%s/%s.log" % (logpath, appname))
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standart': {
                    'format': '%(asctime)s - %(filename)s : %(levelname)-8s ===> %(message)s',
                    'datefmt': '%d-%m-%Y  %H:%M',
                }
            },
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standart',
                    'stream': 'ext://sys.stdout'
                },
                'rotate_file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'formatter': 'standart',
                    'filename': "%s/%s.log" % (logpath, appname),
                    'mode': 'w+',
                    'encoding': 'utf8',
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'standart',
                    'filename': "%s/%s.log" % (logpath, appname),
                    'mode': 'w',
                    'encoding': 'utf8',
                },
            },
            'loggers': {
                'logfile': {
                    'handlers': ['file'],
                    'level': 'INFO',
                    'propagate': False
                },
                'logstream': {
                       'handlers': ['console'],
                        'level': 'INFO',
                        'propagate': False
                },
                'logrotate': {
                    'handlers': ['rotate_file'],
                    'level': 'INFO',
                    'propagate': False
                },
            },
        })

    def INIT_Logger(self):

        self.LoggerFile = logging.getLogger('logfile')
        self.LoggerStream = logging.getLogger('logstream')
        self.LoggerRotateFile = logging.getLogger('logrotate')

        return self.LoggerFile, self.LoggerStream, self.LoggerRotateFile

class VM(object):
    """
    this Class is relevant to VMs in V-centers.
    """
    def __init__(self, vm):
        self.OBJ = vm
        self.Name = vm.name
        self.State = vm.runtime.powerState
        self.IP = vm.guest.ipAddress

    def Get_Attributes(self):
        """
        It will Check and Out put all Vm Attributes in to variable name 'Attr' who is a dictionary.

        :return: Attr
        """

        self.Attributes = {}
        for field in self.OBJ.availableField:
            for field_val in self.OBJ.value:
                if field.key == field_val.key:
                    self.Attributes[field.name] = field_val.value
        return self.Attributes

    def Set_Attribute(self, content, attribute_name,new_value):
        """
        this Function will change attribute for VM in Custom Fields

        :param content: the vim.connect
        :param attribute_name:  String of the Attribute
        :param new_value: String of the New Value
        :return:
        """

        self.ValueChange = False
        self.CustomFM = content.customFieldsManager

        for field in self.OBJ.availableField:
            for custom in self.OBJ.customValue:
                if field.name == attribute_name:
                    if custom.key == field.key:
                        self.CustomFM.SetField(entity=self.OBJ, key=custom.key, value=new_value)
                        self.ValueChange = True

        return self.ValueChange


    def Get_Info(self):
        """
        this function will return a basices information about your VM Object.

        :return:
        """
        self.Info = {}
        self.Summary = self.OBJ.summary

        if self.Summary.guest.ipAddress != None and self.Summary.guest.ipAddress != "":

            self.Info['_IP'] = self.Summary.guest.ipAddress
            self.Info['_Name'] = self.Name
            self.Info['OS'] = self.Summary.guest.guestFullName
            self.Info['CPU_Num'] = self.Summary.config.numCpu
            self.Info['Memory'] = self.Summary.config.memorySizeMB
            self.Info['Status'] = self.Summary.runtime.powerState

            return self.Info

        else:
            pass

    def AreNew(self, create_time):

        """
        This Function will check if the VM is new or not by checking the installation date.

        :param create_time: [Vm Installation Date]
        :return: True or False
        """

        self.Last30DaysAgo = datetime.now() - timedelta(days=30)
        self.Str_Last30DaysAgo = str(self.Last30DaysAgo.day) + "-" + \
                                 str(self.Last30DaysAgo.month) + "-" + str(self.Last30DaysAgo.year)
        self.ConvLast30DaysAgo = datetime.strptime(self.Str_Last30DaysAgo, "%d-%m-%Y")

        self.SplitCreateTime = create_time.split()
        self.ConvCreateTime = datetime.strptime(self.SplitCreateTime[0], "%d-%m-%Y")

        if self.ConvCreateTime >= self.ConvLast30DaysAgo:
            return True
        else:
            return False

class VimObjects(object):


    def Get_VimObjects(self, si, root, vim_type):
        self.container = si.content.viewManager.CreateContainerView(root,
                                                               vim_type,
                                                               True)
        self.view = self.container.view
        self.container.Destroy()
        return self.view

class SEARCH(object):

    """
    this Fuction will content all Search Option for Generic classes.

    """

    def VM_FindByIP(self, content, srvip):
        """
        this Function will find VM Object, it will search with IP address.

        :param content: SI.contect
        :param srvip: VM ip address
        :return: VM Object
        """

        self.SearchIndex = content.searchIndex
        self.SearchVmRes = self.SearchIndex.FindByIp(None, srvip, True)

        return self.SearchVmRes

    def VM_FindByName(self, content, srvname):
        """
        this Function will find VM Object, it will search with Hostname

        :param content: SI.content
        :param srvname: VM hostname
        :return: VM Object
        """

        self.SearchIndex = content.searchIndex
        self.SearchVmRes = self.SearchIndex.FindByDnsName(dnsName=srvname, vmSearch=True)

        return self.SearchVmRes
