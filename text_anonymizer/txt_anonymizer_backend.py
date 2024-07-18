from flask import Flask, request, jsonify, send_from_directory
from flask_api import status
from flask_cors import CORS
import os
import shutil
import oci
from oci.config import validate_config
import json





app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

with open('config.json', 'r') as file:
    config = json.load(file)


def deidentify_text(texttoanalyse, compartment_id):
    
    config = oci.config.from_file()
    ai_language_client = oci.ai_language.AIServiceLanguageClient(config)
    
    
    batch_detect_language_pii_entities_response = ai_language_client.batch_detect_language_pii_entities(
        batch_detect_language_pii_entities_details=oci.ai_language.models.BatchDetectLanguagePiiEntitiesDetails(
            documents=[
                oci.ai_language.models.TextDocument(
                    key="String1",
                    text=texttoanalyse, 
                    language_code="en")],
            compartment_id=compartment_id))
    
    
    cleansedtext = texttoanalyse
    for document in batch_detect_language_pii_entities_response.data.documents:
        for entities in document.entities:
            replacement = 'X' * len(entities.text)
            cleansedtext = cleansedtext.replace(entities.text, replacement)
            #print(entities.text)
    return cleansedtext

def translate_and_deidentify(text, source_language, target_language, compartment_id):
    
    config = oci.config.from_file()
    ai_client = oci.ai_language.AIServiceLanguageClient(config)
    
    
    doc_key = "doc1"
    doc = oci.ai_language.models.TextDocument(key=doc_key, text=text, language_code=source_language)
    documents = [doc]
    
    
    batch_language_translation_details = oci.ai_language.models.BatchLanguageTranslationDetails(
        documents=documents,
        compartment_id=compartment_id,
        target_language_code=target_language
    )
    
    
    translation_response = ai_client.batch_language_translation(batch_language_translation_details)
    
    
    translated_text = translation_response.data.documents[0].translated_text
    print("Text translated:", translated_text)
    
    
    ai_language_client = oci.ai_language.AIServiceLanguageClient(config)
    
    
    batch_detect_language_pii_entities_response = ai_language_client.batch_detect_language_pii_entities(
        batch_detect_language_pii_entities_details=oci.ai_language.models.BatchDetectLanguagePiiEntitiesDetails(
            documents=[
                oci.ai_language.models.TextDocument(
                    key="String1",
                    text=translated_text,
                    language_code=target_language
                )],
            compartment_id=compartment_id
        )
    )
    
    
    cleansed_text = translated_text
    for document in batch_detect_language_pii_entities_response.data.documents:
        for entities in document.entities:
            replacement = 'X' * len(entities.text)
            cleansed_text = cleansed_text.replace(entities.text, replacement)
    
    return cleansed_text


def download_txt(object_storage_path,namespace,bucket_name):
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    namespace = namespace
    bucket_name = bucket_name
    prefix = object_storage_path
    retrieve_files_loc ="/home/ubuntu/text_anonymizer/txt_downloaded"
    
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

def read_all_txt_files(folder_path, compartmentId):


    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist.")
    
    
    for filename in os.listdir(folder_path):
        print(filename)
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                
                content = file.read()
                
                print(content)
                compartment_id =compartmentId
                
                deidentified_text = translate_and_deidentify(content, "auto", "en", compartment_id)
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
 
@app.route('/txt_anonymizer', methods=['GET'])
def txt_anonymizer():
    
    with open('config.json', 'r') as file:
        config = json.load(file)

    download_txt("SRC_TEXT",config["namespace"],config["bucketName"])
    folder_path = 'txt_downloaded'
    read_all_txt_files(folder_path, config["compartmentId"])
    upload_to_bucket(config["namespace"],config["bucketName"])
    delete_folder_contents("txt_downloaded")
    return jsonify({'message':'todo ok'})




def app_init():
    app.run(host='0.0.0.0', port=2055, debug=True) #ssl_context=('cert/cert.pem', 'cert/ck.pem'))

def writeLog(path, obj):
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(path, "a") as logfile:
        logfile.write(date_time + ":" + str(obj) + "\n")

if __name__ == "__main__":
    app_init()