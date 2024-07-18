
import os
import oci
from oci.config import validate_config
import pydicom 
from pydicom.dataset import Dataset, FileDataset
import datetime
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
import matplotlib.pyplot as plt
import json
import uuid
import pandas as pd


def download_dicom(object_storage_path):
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE)
    with open('config.json', 'r') as file:
        configfile = json.load(file)

    namespace = configfile["namespace"]
    bucket_name = configfile["bucketName"]
    prefix = object_storage_path
    retrieve_files_loc ="/home/ubuntu/backend/dicoms_downloaded"
    
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

def dicom_to_image(dicom_path):
    #this dicom to image should also take the metadata information
    dicom_data = pydicom.dcmread(dicom_path)
    #print(dicom_path)

    # Extract pixel array and metadata
    pixel_array = dicom_data.pixel_array
    dicom_data_json = dicom_data.to_json_dict()

    # Prepare the output paths
    output_name = os.path.basename(dicom_path)
    base_name = os.path.splitext(output_name)[0]
    output_image_path = os.path.join("dicom_processed", f"{base_name}.png")
    output_json_path = os.path.join("dicom_processed", f"{base_name}.json")

    # Save the image using PIL to maintain resolution
    img = Image.fromarray(pixel_array)
    enhancer = ImageEnhance.Brightness(img)
    img.save(output_image_path)

    # Save the metadata as JSON
    with open(output_json_path, 'w') as json_file:
        json.dump(dicom_data_json, json_file, indent=4)
    
    # Upload the image to the specified bucket
    object_name = f"PNG_TO_PROCESS/{base_name}.png"
    upload_to_bucket("frkok02ushb5", "Anonymization-bucket", object_name, output_image_path)
    print(f"Image saved at: {output_image_path}")
    print(f"Metadata saved at: {output_json_path}")

    # Call the anonymization function (assumed to be defined elsewhere)
    get_anonym_image(object_name)

    return True

def dicom_to_image_old(dicom_path):
    #this dicom to image should also take the metadata information
    dicom_data = pydicom.dcmread(dicom_path)
    #print(dicom_path)

    #save image

    pixel_array = dicom_data.pixel_array
    fig, ax = plt.subplots()
    ax.imshow(pixel_array, cmap=plt.cm.gray)
    ax.set_title("")
    ax.axis("off")
    output_name = dicom_path.split("/")[-1]
    png_name = output_name.split(".")
    output_path = f"dicom_processed/{png_name[0]}.png"
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    dicom_data_json = dicom_data.to_json_dict()
    json_name = output_name.split('.')

    output_path = os.path.join( f"dicom_processed/{json_name[0]}.json")
    with open(output_path, 'w') as json_file:
        json.dump(dicom_data_json, json_file, indent=4)
    
    object_name = f"PNG_TO_PROCESS/{png_name[0]}.png"
    path_to_file =  f"dicom_processed/{png_name[0]}.png"
    upload_to_bucket("frkok02ushb5","Anonymization-bucket",object_name, path_to_file )
    print(f"file saved in: {output_path}")

    get_anonym_image(object_name)

    return True


def image_to_dicom(nombre):
    #this image to dicom should also anonymize the metadata information, transform to dicom

    return True


def upload_to_bucket(namespace, bucket_name, obj_name, path_to_file):
    #should upload the anonymized dicom and the txt with the info anonymized
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    object_storage = oci.object_storage.ObjectStorageClient(config)
    with open(path_to_file,'rb') as f:
        obj = object_storage.put_object(namespace, bucket_name, obj_name, f)  
    return True



def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)


def get_anonym_image(image_name):
    
    with open('config.json', 'r') as file:
        configfile = json.load(file)

    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE)
    COMPARTMENT_ID = configfile["compartmentId"]

    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = configfile["namespace"]  # e.g. "axabc9efgh5x"
    object_location.bucket_name = configfile["bucketName"]  # e.g "docu-bucket"
    #print(image_name)
    object_location.object_name = image_name  # e.g "invoice-white-clover.tif"

    aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config))

    # Document Key-Value extraction Feature
    key_value_extraction_feature = oci.ai_document.models.DocumentKeyValueExtractionFeature()

    # Setup the output location where processor job results will be created
    output_location = oci.ai_document.models.OutputLocation()
    
    output_location.namespace_name = configfile["namespace"]  # e.g. "axabc9efgh5x"
    output_location.bucket_name = configfile["bucketName"]
    output_location.prefix = "PNG_ANONYMIZED"

    # Create a processor_job for invoice key_value_extraction feature. 
    # Note: If you want to use another key value extraction feature, set document_type to "RECIEPT" "PASSPORT" or "DRIVER_ID". If you have a mix of document types, you can remove document_type
    create_processor_job_details_key_value_extraction = oci.ai_document.models.CreateProcessorJobDetails(
                                                        display_name=str(uuid.uuid4()),
                                                        compartment_id=COMPARTMENT_ID,
                                                        input_location=oci.ai_document.models.ObjectStorageLocations(object_locations=[object_location]),
                                                        output_location=output_location,
                                                        processor_config=oci.ai_document.models.GeneralProcessorConfig(features=[key_value_extraction_feature],
                                                                                                                    document_type="INVOICE"))


    #print("Calling create_processor with create_processor_job_details_key_value_extraction:", create_processor_job_details_key_value_extraction)
    create_processor_response = aiservicedocument_client.create_processor_job_and_wait_for_state(
        create_processor_job_details=create_processor_job_details_key_value_extraction,
        wait_for_states=[oci.ai_document.models.ProcessorJob.LIFECYCLE_STATE_SUCCEEDED],
        waiter_kwargs={"wait_callback": create_processor_job_callback})

    #print("processor call succeeded with status: {} and request_id: {}.".format(create_processor_response.status, create_processor_response.request_id))
    processor_job: oci.ai_document.models.ProcessorJob = create_processor_response.data
    #print("create_processor_job_details_key_value_extraction response: ", create_processor_response.data)

    #print("Getting defaultObject.json from the output_location")
    object_storage_client = oci.object_storage.ObjectStorageClient(config=config)
    get_object_response = object_storage_client.get_object(namespace_name=output_location.namespace_name,
                                                        bucket_name=output_location.bucket_name,
                                                        object_name="{}/{}/{}_{}/results/{}.json".format(
                                                            output_location.prefix, processor_job.id,
                                                            object_location.namespace_name,
                                                            object_location.bucket_name,
                                                            object_location.object_name))
    #print(str(get_object_response.data.content.decode()))

    # Suponiendo que get_object_response.data es una cadena JSON
    json_data_str = get_object_response.data.content.decode()

    # Convertir la cadena JSON a un diccionario
    json_data = json.loads(json_data_str)
    
    #print(json_data["pages"])
    if json_data["pages"][0]["dimensions"] is None:
        image_local_name = image_name.split("/")
        #print("dicom_processed/"+str(image_local_name[1]))
        new_file_name = "anonymized_" + image_local_name[1]
        # Construct the full path to the new file
        new_file_path = os.path.join("dicom_processed/", new_file_name)
        
        os.rename("dicom_processed/"+image_local_name[1], new_file_path)

    if json_data["pages"][0]["dimensions"] != None:
       
    
        #print(json_data["pages"])
        # Crear listas para cada columna
        text_list = []
        confidence_list = []
        boundingPolygon_list = []

        # Iterar sobre las palabras en la lista y extraer la información
        for word in json_data["pages"][0]["words"]:
            text_list.append(word["text"])
            confidence_list.append(word["confidence"])
            boundingPolygon_list.append(word["boundingPolygon"]["normalizedVertices"])

        # Crear DataFrame
        df = pd.DataFrame({
            "text": text_list,
            "confidence": confidence_list,
            "boundingPolygon": boundingPolygon_list
        })

        # Mostrar el DataFrame
        #print(df)

        text_concatenated = ' '.join(df['text'])

        #print(text_concatenated)

        ai_client = oci.ai_language.AIServiceLanguageClient(oci.config.from_file())

        key1 = "doc1"
        key2 = "doc2"
        text1 = "Hello Support Team, I am reaching out to seek help with my credit card number 1234 5678 9873 2345 expiring on 11/23. There was a suspicious transaction on 12-Aug-2022 which I reported by calling from my mobile number +1 (423) 111-9999 also I emailed from my email id sarah.jones1234@hotmail.com. Would you please let me know the refund status? Regards, Sarah"
        text2 = "Using high-performance GPU systems in the Oracle Cloud, OCI will be the cloud engine for the artificial intelligence models that drive the MIT Driverless cars competing in the Indy Autonomous Challenge."

        compartment_id = "<COMPARTMENT_ID>" #TODO Specify your compartmentId here

        #language Detection of Input Documents
        doc1 = oci.ai_language.models.DominantLanguageDocument(key=key1, text=text_concatenated)
        #doc1 = oci.ai_language.models.DominantLanguageDocument(key=key1, text=text1)
        #doc2 = oci.ai_language.models.DominantLanguageDocument(key=key2, text=text2)
        #documents = [doc1, doc2]
        documents = [doc1]
        batch_detect_dominant_language_details = oci.ai_language.models.BatchDetectDominantLanguageDetails(documents=documents, compartment_id=COMPARTMENT_ID)
        output = ai_client.batch_detect_dominant_language(batch_detect_dominant_language_details)
        #print(output.data)

        doc1 = oci.ai_language.models.TextDocument(key=key1, text=text_concatenated, language_code="en")
        #doc1 = oci.ai_language.models.TextDocument(key=key1, text=text1, language_code="en")
        #doc2 = oci.ai_language.models.TextDocument(key=key2, text=text2, language_code="en")
        #documents = [doc1, doc2]

        documents = [doc1]

        #Text Classification of Input Documents
        batch_detect_language_text_classification_details = oci.ai_language.models.BatchDetectLanguageTextClassificationDetails(documents=documents, compartment_id=COMPARTMENT_ID)
        output = ai_client.batch_detect_language_text_classification(batch_detect_language_text_classification_details)
        #print(output.data)

        #Named Entity Recognition of Input Documents
        batch_detect_language_entities_details = oci.ai_language.models.BatchDetectLanguageEntitiesDetails(documents=documents, compartment_id=COMPARTMENT_ID)
        output = ai_client.batch_detect_language_entities(batch_detect_language_entities_details)
        #print(output.data)

        json_data_str = str(output.data)

        new_json_data = json.loads(json_data_str)

        entities_json = new_json_data["documents"]

        entities_json

        for entity in entities_json[0]['entities']:
            text_to_match = entity['text']
            #print(text_to_match)
            type_value = entity['type']
            #print(type_value)

            #print(df["text"][0])

            
            #matching_rows = df[df['text'] == text_to_match].index
            matching_rows = df[df['text'].str.contains(text_to_match)].index
            #print(matching_rows)

            
            df.loc[matching_rows, 'type'] = type_value

        
        #print(df)

        column_type = []
        for entity in entities_json[0]['entities']:
            text_to_match = entity['text']
            #print(text_to_match)
            type_value = entity['type']
            #print(type_value)

            
            matching_rows = df[df['text'].apply(lambda x: x in text_to_match)].index
            #matching_rows = df[str(df['text']) in text_to_match].index
        
            #matching_rows = df[df['text'] in (text_to_match)].index
            #print(matching_rows)

            
            df.loc[matching_rows, 'type'] = type_value

        # Imprimir el DataFrame actualizado
        #print(df)

        df.loc[df['text'] == 'LAG', 'type'] = None

        
        selected_types = ['DATETIME', 'PERSON', 'ORGANIZATION', 'QUANTITY']
        selected_rows = df[df['type'].isin(selected_types)]

        
        image_local_name = image_name.split("/")
        image_path = "dicom_processed/"+str(image_local_name[1])
        #print(image_path)
        image = Image.open(image_path)

        
        draw = ImageDraw.Draw(image)

        print(selected_rows)

        for index, row in selected_rows.iterrows():
            
            vertices = row['boundingPolygon']
            print(vertices)
            coordinates = [(float(v['x']) * image.width, float(v['y']) * image.height) for v in vertices]

            
            draw.polygon(coordinates, fill="black")

        
        image.save('dicom_processed/anonymized_'+str(image_local_name[1]))

        selected_rows_filtered = selected_rows[['text', 'type']]

        dict_result = selected_rows_filtered.to_dict(orient='records')

        print(dict_result)

        
        
        
        #return test_img, dict_result
    
    dicom_local_name = image_name.split("/")

    dicom_local_name = dicom_local_name[1].split(".")
    dicom_file = "dicoms_dowloaded/"+str(dicom_local_name[0])+".dcm"
    final_image_path = image_name.split("/") 
    png_file = "dicom_processed/anonymized_"+str(final_image_path[1])

    print(png_file, dicom_file)
    
    image = Image.open(png_file)
    image = image.convert('L')  
    np_image = np.array(image)

    
    ds = Dataset()

    
    ds.PatientName = "Anonymized"
    ds.PatientID = "Anonymized"
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.SOPClassUID = pydicom.uid.SecondaryCaptureImageStorage

    
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S')

    
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows = np_image.shape[0]
    ds.Columns = np_image.shape[1]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = np_image.tobytes()


    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
    file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian  # Add TransferSyntaxUID

    
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    anonymized_dicom = dicom_file.split("/")
    ds.save_as("dicom_processed/anonymized_"+str(anonymized_dicom[1]))

    create_anonymized_json("dicom_processed/anonymized_"+str(anonymized_dicom[1]))

    print(f'DICOM saved as {dicom_file}')

    return True






def delete_files_in_directory(directory_path):

    if not os.path.exists(directory_path):
        print(f"Path {directory_path} does not exist.")
        return
    

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        
        if os.path.isfile(file_path):

            os.remove(file_path)
            print(f"File {file_path} dropped.")
        else:
            print(f"{file_path} is not a file. Nothing to do.")
            
def create_anonymized_json(dcm_path):
        
    
    dicom_data = pydicom.dcmread(dcm_path, force=True)
    #print(dicom_path)

    # Extract pixel array and metadata
    pixel_array = dicom_data.pixel_array
    dicom_data_json = dicom_data.to_json_dict()
    json_filename = dcm_path.split("/")
    json_filename = json_filename[1]
    json_filename = json_filename.split(".")

    output_json_path = os.path.join("dicom_processed", f"{json_filename[0]}.json")

    with open(output_json_path, 'w') as json_file:
        json.dump(dicom_data_json, json_file, indent=4)
    
    return True


def delete_temp_objects_bucket(object_storage_path):
    
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    with open('config.json', 'r') as file:
        configfile = json.load(file)
    namespace = configfile["namespace"]
    bucket_name = configfile["bucketName"]
    prefix = object_storage_path
    retrieve_files_loc ="/home/ubuntu/backend/dicoms_downloaded"
    
    validate_config(config)

    object_storage_client = oci.object_storage.ObjectStorageClient(config)
    object_list = object_storage_client.list_objects(namespace, bucket_name, prefix = prefix , fields="name,timeCreated,size")
    for o in object_list.data.objects:
        print(o.name)
    for filenames in object_list.data.objects:
        if filenames.name !="PNG_ANONYMIZED/" and filenames.name !="PNG_TO_PROCESS/":
            object_storage_client.delete_object(namespace, bucket_name,filenames.name)
            print(f'deleted "{filenames.name}" from bucket "{bucket_name}"')
            

def main():
    object_storage_path =  "SRC_DICOM/" 

    with open('config.json', 'r') as file:
        config = json.load(file)

    #download_txt("SRC_TEXT",config["namespace"],config["bucketName"]) 

    download_dicom(object_storage_path)
    

    dcm_files = []
    for root, _, files in os.walk("/home/ubuntu/backend/dicoms_downloaded/"):
        for file in files:
            if file.endswith('.dcm'):
                dicom_to_image(os.path.join(root, file))

    dcm_anonymized_files = []
    for root, _, files in os.walk("/home/ubuntu/backend/dicom_processed/"):
        for file in files:

            upload_to_bucket(config["namespace"], config["bucketName"],"TRG_DICOM/"+str(file),os.path.join(root, file))
            print(file+ " uploaded to object storage")

    delete_files_in_directory("/home/ubuntu/backend/dicom_processed")
    delete_files_in_directory("/home/ubuntu/backend/dicoms_downloaded")
    object_storage_path =  "PNG_ANONYMIZED/"  
    delete_temp_objects_bucket(object_storage_path)
    object_storage_path =  "PNG_TO_PROCESS/"  
    delete_temp_objects_bucket(object_storage_path)


    
    





if __name__ == "__main__":
    main()