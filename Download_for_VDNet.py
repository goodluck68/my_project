# -*- coding: UTF-8 -*-

import paramiko


def download_file(sftp_server, local_dir):
    # Establish connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(launcher_dict[name], port='22', username='root', password='ca$hc0w')

    # Get folder name.
    stdin, stdout, stderr = ssh.exec_command("tail -2 /tmp/pytest-of-guow/pytest-guow/session.log | head -1 | awk -F\| '{print $4}'")
    folder_name = stdout.read().strip().decode('ascii')
    print('folder_name: %s' % folder_name)

    # Set the full name of the logs
    remote_test_log = folder_name + '/' + 'test.log'
    remote_testcase_log = folder_name + '/' + 'testcase.log'
    remote_pylib_log = folder_name + '/' + 'pylib.log'
    remote_product_sdk_log = folder_name + '/' + 'product_sdk.log'

    local_test_log = local_dir + r'\test.log'
    local_testcase_log = local_dir + r'\testcase.log'
    local_pylib_log = local_dir + r'\pylib.log'
    local_product_sdk_log = local_dir + r'\product_sdk.log'

    # Download file
    print('Start download files')
    t = paramiko.Transport((sftp_server, 22))
    t.connect(username='root', password='ca$hc0w')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remote_test_log, local_test_log)
    sftp.get(remote_testcase_log, local_testcase_log)
    sftp.get(remote_pylib_log, local_pylib_log)
    sftp.get(remote_product_sdk_log, local_product_sdk_log)
    t.close()
    ssh.close()
    print('Download file: ' + remote_test_log)
    print('Download file: ' + remote_testcase_log)
    print('Download file: ' + remote_pylib_log)
    print('Download file: ' + remote_product_sdk_log)
    print('Finish download files')

launcher_dict = {
    'MC1': '10.144.137.83',
    'MC2': '10.144.139.127',
    'MC3': '10.144.138.168',
    'PRME-MC1': '10.40.69.86',
    'PRME-MC2': '10.40.69.186',
    'PRME-MC3': '10.40.79.115',
    'PRME-MC4': '10.40.77.16',
}

# name = 'MC3'
name = 'PRME-MC3'

print('Login: ' + name)
download_file(launcher_dict[name], r'C:\Users\guow\Downloads\脚本文件\\')
