#!/usr/bin/python3

import paramiko
import re
import os

def Get_Component_Info():
    # Find the folder path
    folder_list = os.listdir('/tmp/vdnet')
    folder_list.sort(reverse = True)
    for item in folder_list:
        if re.search('^201', item):
            folder_path = '/tmp/vdnet/' + item
            break
    print('=========================================')
    print('The folder is: %s\n' % folder_path)

    # Get the component name and IP address
    with open(folder_path+'/vdnet.log') as f:
        component_dict = {}
        for line in f:
            if re.search('ip address:', line):
                name = re.split('\s+', line.strip())[7]
                value = re.split('\s+', line.strip())[10]
                component_dict[name] = value

    print('=========================================\nComponent Info')
    result = sorted(component_dict.items(), key=lambda x:x[0], reverse=False)
    for i in result:
        print(i[0]+':\t'+i[1])
    print('')


    # Get controller password
    sub_folder_list = os.listdir(folder_path)
    sub_folder_list.sort(key=lambda x:len(x))
    sub_folder_path = folder_path + '/' + sub_folder_list[-1]
    with open(sub_folder_path + '/testcase.log-stderr') as f2:
        for line2 in f2:
            if 'The controller-1 password is' in line2:
                password = re.split(': ',line2.strip())[-1]
                component_dict['controller_password'] = password

    return component_dict



def Get_Controller_Info(component_dict):
    # Get logical switch info from VSM
    print('=========================================\nController Info')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(component_dict['vsm.1'], port='22',username='admin',password='default')
    stdin, stdout, stderr = ssh.exec_command('show controller list all')

    for line in stdout.readlines():
        if re.match('controller', line):
            controller_info = re.split('\s+',line)
            controller_name = controller_info[0]
            controller_ip = controller_info[1]
            print(controller_name + ':\t' + controller_ip + '\t' + component_dict['controller_password'])
    print('')



def Get_TOR_Info(component_dict):
    # The python dict is unordered. This step is to output the TOR information in order.
    result = sorted(component_dict.items(), key=lambda x:x[0], reverse=False)
    for key in result:
        if 'tor' in key[0]:
            print('=========================================\n' + key[0])

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(component_dict[key[0]], port='22',username='root',password='ca$hc0w')
            stdin, stdout, stderr = ssh.exec_command("ifconfig -s | grep -E '^eth|p' | awk '{print $1}'")

            for i in stdout.readlines():
               interface_name = i.strip()
               cmd = 'ifconfig ' + interface_name
               stdin, stdout, stderr = ssh.exec_command(cmd)

               for line in stdout.readlines():
                   if 'HWaddr' in line:
                       mac = re.split('\s+',line)[4]
                   elif 'inet addr:' in line:
                       ip = line.split(':')[1].replace('  Bcast','')
               print(interface_name + ':\t' + ip  + '\t' + mac)
            print('')


def Get_ESX_Info(component_dict):
    # The python dict is unordered. This step is to output the ESX information in order.
    result = sorted(component_dict.items(), key=lambda x:x[0], reverse=False)
    for key in result:
        if 'esx' in key[0]:
            print('=========================================\n' + key[0])

            # Get ESX Info
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(component_dict[key[0]], port='22',username='root',password='ca$hc0w')
            stdin, stdout, stderr = ssh.exec_command('esxcfg-vmknic -l')

            for line in stdout.readlines():
                ESX_INFO = re.split('\s+',line)
                if 'vmk0' in line and 'IPv4' in ESX_INFO:
                    ESX_ID  = ESX_INFO[0]
                    ESX_IP  = ESX_INFO[4]
                    ESX_MAC = ESX_INFO[7]
                    print(ESX_ID + ':\t' + ESX_IP + '\t' + ESX_MAC)

                elif 'vmk1' in line and 'IPv4' in ESX_INFO:
                    ESX_ID  = ESX_INFO[0]
                    ESX_IP  = ESX_INFO[3]
                    ESX_MAC = ESX_INFO[6]
                    print(ESX_ID + ':\t' + ESX_IP + '\t' + ESX_MAC)
            print('')


            # Get VM Info
            stdin, stdout, stderr = ssh.exec_command('esxcli network vm list')
            VM_INFO = {}
            for line in stdout.readlines():
                if re.match('^\s+', line):
                    VM_WORLD_ID = re.split('\s+', line.strip())[0]
                    VM_NAME = 'VM' + re.split('\s+', line.strip())[1].split('-')[0]
                    VM_INFO[VM_NAME] = VM_WORLD_ID

            result = sorted(VM_INFO.items(), key=lambda x:x[0], reverse=False)
            for VM in result:
                    print(VM[0])
                    num = 0
                    stdin, stdout, stderr = ssh.exec_command('esxcli network vm port list -w ' + VM[1])
                    for x in stdout.readlines():
                        if 'MAC Address:' in x:
                            num += 1
                            VM_MAC = x.strip().split(' ')[2]
                        elif 'IP Address:' in x:
                            VM_IP = x.strip().split(' ')[2]
                            print('eth' + str(num) + ':\t' + VM_IP + '\t' + VM_MAC)
                    print('')


def Get_LogicalSwitch_Info(component_dict):
    # The python dict is unordered. This step is to output the logical switch information in order.
    result = sorted(component_dict.items(), key=lambda x:x[0], reverse=False)
    for key in result:
        if 'vsm' in key[0]:
            print('=========================================\nLogical Switch Info: ' + key[0])

            # Get logical switch info from VSM
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(component_dict[key[0]], port='22',username='admin',password='default')
            stdin, stdout, stderr = ssh.exec_command('show logical-switch list all')

            for line in stdout.readlines():
                print(line.strip())
            print('')




my_component = Get_Component_Info()
Get_Controller_Info(my_component)
Get_LogicalSwitch_Info(my_component)
Get_TOR_Info(my_component)
Get_ESX_Info(my_component)


