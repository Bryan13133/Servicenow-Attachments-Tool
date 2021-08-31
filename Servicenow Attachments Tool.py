import requests
import os,shutil
import requests
import requests
import re
import json
import urllib.parse
import magic
import time
from os.path import basename
from zipfile import ZipFile
folders = os.scandir('C:/Users/Villa/Downloads/Attachments-20210729T002026Z-001/Attachments/media')
path = "C:/Users/Villa/Downloads/Attachments-20210729T002026Z-001/Attachments/"
moveto = "C:/Users/Villa/Downloads/Attachments-20210729T002026Z-001/Attachments/attachmentsZip"
moveto2 = os.scandir('C:/Users/Villa/Downloads/Attachments-20210729T002026Z-001/Attachments/attachmentsZip')
user = ''
pwd = ''
instance = ''
class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
def zipAttachment(folder,file,sys_id):
    zipObj = ZipFile(folder.name +'.zip', 'w')
    zipObj.write(file.path,basename(file.path))
    zipObj.close()
    files = os.listdir(path)
    files.sort()
    for f in files:
        if f.endswith('.zip'):
            src = path+f
            dst = moveto+f
            shutil.move(src,dst)         
            
def getSysId(number,table):
    url = f'https://{instance}.service-now.com/api/now/table/{table}?sysparm_query=u_contract_number%3D{number}'
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    response = requests.get(url, auth=(user, pwd), headers=headers )
    if response.status_code != 200: 
        print(bcolors.OKGREEN+'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json()+bcolors.ENDC)
    data = response.json()
    if data['result']:
        return data['result']
    
def uploadAttachment(file,sys_id,table):
    name = file.name[:40]
    url = f'https://{instance}.service-now.com/api/now/attachment/upload'
    payload = {'table_name': table, 'table_sys_id':sys_id}
    mime = magic.Magic(mime=True)
    files = {'file': (name[:40], open(file.path, 'rb'), mime.from_file(file.path), {'Expires': '0'})}
    headers = {"Accept":"*/*"}
    response = requests.post(url, auth=(user, pwd), headers=headers, files=files, data=payload) 
    return response
 
def createDocRecord(file,sys_id,folder):
    name=file.name[:40]
    fType = name.split(".",1)
    name = name.replace("."+fType[1],'')
    name = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in name.split("\n")]
    print(name[0])
    name[0] = name[0] + "."+fType[1]
    url = f'https://{instance}.service-now.com/api/now/table/x_stave_cm_document'
    data=f'<request><entry><reference>{sys_id}</reference><document_name>{name[0]}</document_name><provider>Attachment</provider><table>x_stave_cm_contract</table></entry></request>'
    ##data = f{"reference":sys_id,"document_name":name[0],"provider": "Attachment","table": "x_stave_cm_contract"}
    headers = {"Content-Type":"application/XML","Accept":"application/json"}
    response = requests.post(url, auth=(user, pwd), headers=headers, data=data)
    if response.status_code != 201:
        f = open('errorCR.txt','a') 
        f.write('Folder: '+ folder.name +'\n')
        f.write('File: '+ file.name +'\n')
        f.write('------------------------'+'\n')
        f.close()
        print(bcolors.FAIL+'Folder #'+str(folder.name)+'& file'+ file.name+bcolors.ENDC) 
    data = response.json()
    dictionary = json.loads(response.text)
    key =  "result" in dictionary
    if key:
        return data
        
    
 
def insertAttachments():
    counter = 0
    tic = time.perf_counter()
    f = open('errorCR.txt','a') 
    f.write("1")
    f.close()
    for folder in folders:
        folderPath = os.scandir(folder.path)
        sys_ids = getSysId(folder.name,'x_stave_cm_contract')
        print(folder.name)
        if sys_ids:
            for sys_id in sys_ids:
                for file in folderPath:
                    data = createDocRecord(file,sys_id['sys_id'],folder)
                    if data:
                        response = uploadAttachment(file,data['result']['sys_id'],'x_stave_cm_document')
                        if response:
                            if response.status_code != 201:
                                f = open('errorCR.txt','a') 
                                f.write('Folder: '+ folder.name +'\n')
                                f.write('File: '+ file.name +'\n')
                                f.write('------------------------'+'\n')
                                f.close()
                                print(bcolors.FAIL+'Folder #'+str(folder.name)+'& file'+ file.name+bcolors.ENDC) 
                                zipAttachment(folder,file,sys_id)
                            print ('Record '+ folder.name + ' Completed')
                            print('Status code: '+ str(response.status_code))
                            print(' ')
                counter = counter + 1
                0
        
    for filesAttach in moveto2:
        response = uploadAttachment(filesAttach,sys_id)
        if response.status_code != 201:
          print(bcolors.FAIL+'Folder #'+str(folder.name)+'& file'+ file.name+bcolors.ENDC) 
        print ('Record '+ folder.name + ' Completed')
        print('Status code: '+ str(response.status_code))
        print(' ')
    toc = time.perf_counter()
    print(bcolors.OKGREEN+ f'Success!! You have finished in {toc - tic:0.4f} seconds'  + bcolors.ENDC)
    print('Number of folders' + str(counter))
        
insertAttachments()
