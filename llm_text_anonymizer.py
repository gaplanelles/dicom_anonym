from flask import Flask, request, jsonify, send_from_directory
from flask_api import status
from flask_cors import CORS
import os
import shutil
import oci
from oci.config import validate_config
import json
import cohere



app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

with open('config.json', 'r') as file:
    config = json.load(file)




def llm_deidentifier(text, co):
    
    cleansed_text = co.chat(
    message="Anonimizuj dane wrażliwe z tego tekstu. Musisz zastąpić imiona, wiek, daty, numery identyfikacyjne, ulice, telefony, e-maile, nazwy miast, kraje... literą X za każdy znak słowa do zanonimizowania: "+ str(text),

    model="command-r-plus"
)
    
    
    
    return str(cleansed_text.text)


def download_txt(object_storage_path,namespace,bucket_name):
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    namespace = namespace
    bucket_name = bucket_name
    prefix = object_storage_path
    retrieve_files_loc ="/home/ubuntu/LLM_text_anonymizer/txt_downloaded"
    
    validate_config(config)

    object_storage_client = oci.object_storage.ObjectStorageClient(config)
    object_list = object_storage_client.list_objects(namespace, bucket_name, prefix = prefix , fields="name,timeCreated,size")
    #for o in object_list.data.objects:
    #    print(o.name)
    for filenames in object_list.data.objects:
        if not filenames.name.endswith("/"):
            target_filename = filenames.name.split("/")[-1]
            
            get_obj = object_storage_client.get_object(namespace, bucket_name,filenames.name)
            with open(retrieve_files_loc+'/'+target_filename,'wb') as f:
                for chunk in get_obj.data.raw.stream(1024 * 1024, decode_content=False):
                    f.write(chunk)
            print(f'downloaded "{target_filename}" in "{retrieve_files_loc}" from bucket "{bucket_name}"')

    return True



def read_all_txt_files(folder_path, compartmentId, co):


    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist.")
    
    print(folder_path)
    print(compartmentId)
    for filename in os.listdir(folder_path):
        print(filename)
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                
                content = file.read()
                
                print(content)
                compartment_id = compartmentId
                
                deidentified_text = llm_deidentifier(content, co) #-------------------------------------------
                print(deidentified_text)

                new_filename = filename.replace(".txt", "_deidentified.txt")
                new_file_path = os.path.join(folder_path, new_filename)
                
                with open(new_file_path, 'w', encoding='utf-8') as new_file:
                    new_file.write(deidentified_text)
                print(f"Archivo deidentificado guardado como: {new_filename}")

def upload_to_bucket(namespace, bucket_name):

    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    object_storage = oci.object_storage.ObjectStorageClient(config)
    folder_path="txt_downloaded"
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist")
    
    for filename in os.listdir(folder_path):
        if filename.endswith("_deidentified.txt"):
            file_path = os.path.join("txt_downloaded", filename)
            # Sube el archivo al bucket
            with open(file_path, 'rb') as f:
                obj = object_storage.put_object(namespace, bucket_name, "TRG_TEXT/"+filename, f)
            print(f"Archivo subido al bucket: {filename}")


def delete_folder_contents(folder):
    """
    Deletes all contents of the specified folder.

    Args:
        folder (str): Path to the folder whose contents will be deleted.
    """
    # Verify that the folder exists
    if not os.path.exists(folder):
        print(f"The folder {folder} does not exist.")
        return

    # Iterate through all files and directories in the folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        
        try:
            # Delete files and directories
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


@app.route('/llm_txt_anonymizer', methods=['GET'])
def llm_txt_anonymizer():
    
    with open('config.json', 'r') as file:
        config = json.load(file)

    co = cohere.Client(
        api_key=config["cohere_api_key"],
    )

    download_txt("SRC_TEXT",config["namespace"],config["bucketName"])
    folder_path = 'txt_downloaded'
    print(folder_path)
    print(config["compartmentId"])
    read_all_txt_files(folder_path, config["compartmentId"], co)
    upload_to_bucket(config["namespace"],config["bucketName"])
    delete_folder_contents("txt_downloaded")
    return jsonify({'message':'todo ok'})




def app_init():
    app.run(host='0.0.0.0', port=2056, debug=True) #ssl_context=('cert/cert.pem', 'cert/ck.pem'))

def writeLog(path, obj):
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(path, "a") as logfile:
        logfile.write(date_time + ":" + str(obj) + "\n")

if __name__ == "__main__":
    app_init()