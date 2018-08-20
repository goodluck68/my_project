# -*- coding: UTF-8 -*-

import paramiko

def download_file(sftp_server, local_testcase, local_pylib):
    # Establish connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(launcher_dict[name], port='22',username='root',password='ca$hc0w')

    # Get folder name. e.g. 20180817-131233
    stdin, stdout, stderr = ssh.exec_command("ls -l /tmp/vdnet | awk '{print $9}' | grep ^201* | sort -r | head -1")
    folder_name = stdout.read().strip().decode('ascii')
    print('folder_name: %s' % folder_name)

    # Get sub folder name. e.g. 1_TDS.NSX.TOR.P0Debug.xxx
    cmd = "ls -l /tmp/vdnet/" + folder_name + " | awk '{print $9}' | grep ^1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    sub_folder_name = stdout.read().strip().decode('ascii')
    print('sub_folder_name: %s' % sub_folder_name)

    # Set the full path of testcase.log and pylib.log
    remote_testcase = '/tmp/vdnet/' + folder_name + '/' + sub_folder_name + '/testcase.log'
    remote_pylib = '/tmp/vdnet/' + folder_name + '/' + sub_folder_name + '/pylib.log'

    # Download file
    t = paramiko.Transport((sftp_server, 22))
    t.connect(username='root',password='ca$hc0w')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remote_testcase, local_testcase)
    sftp.get(remote_pylib, local_pylib)
    t.close()
    print('Download file: ' + remote_testcase)
    print('Download file: ' + remote_pylib)
    ssh.close()


launcher_dict = {
    'MC1': '10.144.138.170',
    'MC2': '10.144.138.229',
    'MC3': '10.144.138.168',
    'PRME-MC1': '10.40.79.4',
    'PRME-MC2': '10.40.71.122',
    'PRME-MC3': '10.40.73.11'
}

name = 'MC3'
local_testcase = r'C:\Users\guow\Downloads\脚本文件\\' + name + r'\testcase.log'
local_pylib    = r'C:\Users\guow\Downloads\脚本文件\\' + name + r'\pylib.log'

print('Login: ' + name)
download_file(launcher_dict[name], local_testcase, local_pylib)

