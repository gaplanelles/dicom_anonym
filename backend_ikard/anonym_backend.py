import base64
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_api import status
from flask_cors import CORS
import os
import shutil

import uuid
import pandas as pd
import json
import oci
from PIL import Image, ImageDraw, ImageEnhance
import pydicom
from pydicom.dataset import Dataset, FileDataset
import subprocess

import numpy as np
import cv2

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

def read_img_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")
    return encoded_image

def get_base64_info(b64_image):
    # Split the string to extract the necessary parts
    header, image_data = b64_image.split(',', 1)
    extension = header.split('/')[1].split(';')[0]
    
    return header, image_data, extension

def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)


def get_anonym_image_old( image_name): 

    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE)
    COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaa7rxjpnxxcqparwvybqb3ocpiadljmtfnp5rq35yqib6vvl64pxlq";

    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = "frkok02ushb5"  # e.g. "axabc9efgh5x"
    object_location.bucket_name = "Anonymization-bucket"  # e.g "docu-bucket"
    print(image_name)
    writeLog("logs.txt", f"image_data: {image_name}")
    object_location.object_name = image_name  # e.g "invoice-white-clover.tif"


    aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config))

    # Document Key-Value extraction Feature
    key_value_extraction_feature = oci.ai_document.models.DocumentKeyValueExtractionFeature()

    # Setup the output location where processor job results will be created
    output_location = oci.ai_document.models.OutputLocation()
    output_location.namespace_name = "frkok02ushb5"  # e.g. "axabc9efgh5x"
    output_location.bucket_name = "Anonymization-bucket"
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

        # Buscar la fila correspondiente en el DataFrame
        #matching_rows = df[df['text'] == text_to_match].index
        matching_rows = df[df['text'].str.contains(text_to_match)].index
        #print(matching_rows)

        # Asignar el valor de 'type' a la columna 'type' en la fila correspondiente
        df.loc[matching_rows, 'type'] = type_value

    # Imprimir el DataFrame actualizado
    #print(df)

    column_type = []
    for entity in entities_json[0]['entities']:
        text_to_match = entity['text']
        #print(text_to_match)
        type_value = entity['type']
        #print(type_value)
        '''
        for text in df["text"]:
            print(text)
            if text in text_to_match:
                column_type.append(text)
            else:
                column_type.append(None)

        print(column_type)
            
        print(df["text"][0])
        text_df = df["text"][0]
        print(type(text_df))
        print(type(text_to_match))
        if text_df in text_to_match:
            print("contains")
        '''
        # Buscar la fila correspondiente en el DataFrame
        matching_rows = df[df['text'].apply(lambda x: x in text_to_match)].index
        #matching_rows = df[str(df['text']) in text_to_match].index
    
        #matching_rows = df[df['text'] in (text_to_match)].index
        #print(matching_rows)

        # Asignar el valor de 'type' a la columna 'type' en la fila correspondiente
        df.loc[matching_rows, 'type'] = type_value

    # Imprimir el DataFrame actualizado
    #print(df)

    df.loc[df['text'] == 'LAG', 'type'] = None

    # Filtra las filas donde 'type' es 'DATETIME'
    selected_types = ['DATETIME', 'PERSON', 'ORGANIZATION', 'QUANTITY']
    selected_rows = df[df['type'].isin(selected_types)]

    # Abre la imagen (reemplaza 'ruta_de_la_imagen' con la ruta de tu imagen)
    image_path = image_name
    image = Image.open(image_path)

    # Crea un objeto para dibujar en la imagen
    draw = ImageDraw.Draw(image)

    print(selected_rows)

    for index, row in selected_rows.iterrows():
        # Obtiene las coordenadas del bounding box y convierte a números
        vertices = row['boundingPolygon']
        print(vertices)
        coordinates = [(float(v['x']) * image.width, float(v['y']) * image.height) for v in vertices]

        # Dibuja un rectángulo negro en las coordenadas del bounding box
        draw.polygon(coordinates, fill="black")

    # Guarda la imagen con las cajas negras
    image.save('media/imagen_con_cajas_negras.png')

    selected_rows_filtered = selected_rows[['text', 'type']]

    dict_result = selected_rows_filtered.to_dict(orient='records')

    print(dict_result)

    
    test_img = read_img_to_base64("media/imagen_con_cajas_negras.png")
    return test_img, dict_result


def get_anonym_image(image_name):
    

    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE)
    COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaa7rxjpnxxcqparwvybqb3ocpiadljmtfnp5rq35yqib6vvl64pxlq";

    object_location = oci.ai_document.models.ObjectLocation()
    object_location.namespace_name = "frkok02ushb5"  # e.g. "axabc9efgh5x"
    object_location.bucket_name = "Anonymization-bucket"  # e.g "docu-bucket"
    #print(image_name)
    object_location.object_name = image_name  # e.g "invoice-white-clover.tif"

    aiservicedocument_client = oci.ai_document.AIServiceDocumentClientCompositeOperations(oci.ai_document.AIServiceDocumentClient(config=config))

    # Document Key-Value extraction Feature
    key_value_extraction_feature = oci.ai_document.models.DocumentKeyValueExtractionFeature()

    # Setup the output location where processor job results will be created
    output_location = oci.ai_document.models.OutputLocation()
    output_location.namespace_name = "frkok02ushb5"  # e.g. "axabc9efgh5x"
    output_location.bucket_name = "Anonymization-bucket"
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
        new_file_path = os.path.join("uploads/", new_file_name)
        
        shutil.copyfile("uploads/"+image_local_name[1],  new_file_path)


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

            # Buscar la fila correspondiente en el DataFrame
            #matching_rows = df[df['text'] == text_to_match].index
            matching_rows = df[df['text'].str.contains(text_to_match)].index
            #print(matching_rows)

            # Asignar el valor de 'type' a la columna 'type' en la fila correspondiente
            df.loc[matching_rows, 'type'] = type_value

        # Imprimir el DataFrame actualizado
        #print(df)

        column_type = []
        for entity in entities_json[0]['entities']:
            text_to_match = entity['text']
            #print(text_to_match)
            type_value = entity['type']
            #print(type_value)

            # Buscar la fila correspondiente en el DataFrame
            matching_rows = df[df['text'].apply(lambda x: x in text_to_match)].index
            #matching_rows = df[str(df['text']) in text_to_match].index
        
            #matching_rows = df[df['text'] in (text_to_match)].index
            #print(matching_rows)

            # Asignar el valor de 'type' a la columna 'type' en la fila correspondiente
            df.loc[matching_rows, 'type'] = type_value

        # Imprimir el DataFrame actualizado
        #print(df)

        df.loc[df['text'] == 'LAG', 'type'] = None

        # Filtra las filas donde 'type' es 'DATETIME'
        selected_types = ['DATETIME', 'PERSON', 'ORGANIZATION', 'QUANTITY']
        selected_rows = df[df['type'].isin(selected_types)]

        # Abre la imagen (reemplaza 'ruta_de_la_imagen' con la ruta de tu imagen)
        image_local_name = image_name.split("/")
        image_path = "uploads/"+str(image_local_name[1])
        #print(image_path)
        image = Image.open(image_path)

        # Crea un objeto para dibujar en la imagen
        draw = ImageDraw.Draw(image)

        print(selected_rows)

        for index, row in selected_rows.iterrows():
            # Obtiene las coordenadas del bounding box y convierte a números
            vertices = row['boundingPolygon']
            print(vertices)
            coordinates = [(float(v['x']) * image.width, float(v['y']) * image.height) for v in vertices]

            # Dibuja un rectángulo negro en las coordenadas del bounding box
            draw.polygon(coordinates, fill="black")

        # Guarda la imagen con las cajas negras
        image.save('uploads/anonymized_'+str(image_local_name[1]))

        selected_rows_filtered = selected_rows[['text', 'type']]

        dict_result = selected_rows_filtered.to_dict(orient='records')

        print(dict_result)

        
        #test_img = read_img_to_base64("media/imagen_con_cajas_negras.png")
        
        #return test_img, dict_result
    
    dicom_local_name = image_name.split("/")

    dicom_local_name = dicom_local_name[1].split(".")
    dicom_file = "uploads/"+str(dicom_local_name[0])+".dcm"
    final_image_path = image_name.split("/") 
    png_file = "uploads/anonymized_"+str(final_image_path[1])

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

    
    dt = datetime.now()
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
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian  # Añadir TransferSyntaxUID

    
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    anonymized_dicom = dicom_file.split("/")
    ds.save_as("uploads/anonymized_"+str(anonymized_dicom[1]))

    print(f'DICOM saved as {dicom_file}')

    return True


def upload_to_bucket(namespace, bucket_name, obj_name, path_to_file):
    #should upload the anonymized dicom and the txt with the info anonymized
    CONFIG_PROFILE = "DEFAULT"
    config = oci.config.from_file('/home/ubuntu/.oci/config', CONFIG_PROFILE) 
    object_storage = oci.object_storage.ObjectStorageClient(config)
    with open(path_to_file,'rb') as f:
        obj = object_storage.put_object(namespace, bucket_name, obj_name, f)  
    return True

def dicom_to_image(dicom_path):
    #this dicom to image should also take the metadata information
    dicom_data = pydicom.dcmread(dicom_path, force=True)
    dicom_data.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    pixel_array_numpy = dicom_data.pixel_array
    
    
    #print(dicom_path)

    # Extract pixel array and metadata
    pixel_array = dicom_data.pixel_array
    #pixel_array = pixel_array.astype(np.uint8)
    dicom_data_json = dicom_data.to_json_dict()

    # Prepare the output paths
    output_name = os.path.basename(dicom_path)
    base_name = os.path.splitext(output_name)[0]
    output_image_path = os.path.join("uploads", f"{base_name}.png")
    output_json_path = os.path.join("uploads", f"{base_name}.json")

    # Save the image using opencv to maintain resolution
 
    min_val = np.min(pixel_array_numpy)
    max_val = np.max(pixel_array_numpy)
    normalized_img = ((pixel_array_numpy - min_val) / (max_val - min_val)) * 255
    img = normalized_img.astype(np.uint8)

    cv2.imwrite(output_image_path, img)

    # Save the metadata as JSON
    with open(output_json_path, 'w') as json_file:
        json.dump(dicom_data_json, json_file, indent=4)
    
    # Upload the image to the specified bucket
    object_name = f"PNG_TO_PROCESS/{base_name}.png"
    #upload_to_bucket("frkok02ushb5", "Anonymization-bucket", object_name, output_image_path)
    print(f"Image saved at: {output_image_path}")
    print(f"Metadata saved at: {output_json_path}")

    # Call the anonymization function (assumed to be defined elsewhere)
   #get_anonym_image(object_name)

    return True


@app.route('/anonymise', methods=['POST'])
def anonymise():
    """
    POST
    Params:
    - imageData
    """
    output_folder = "media"
    body = request.get_json(force=True)
    if 'imageData' not in body:
        return jsonify({'response': 'imageData required'}), status.HTTP_400_BAD_REQUEST

    b64_image = body["imageData"]
    #print(b64_image)

    header, image_data, extension = get_base64_info(b64_image)

    patientName = ""

    #writeLog("logs.txt", f"header: {header}")
    #writeLog("logs.txt", f"header: {extension}")
    #writeLog("logs.txt", f"image_data: {image_data}")
    if image_data.startswith("iVBORw0KGgoAAAANSUhEUgAAB+Y"):
        image_name = "image.png"
        dicom_data = pydicom.dcmread("1_ORIGINAL.dcm")
        patientName = str(dicom_data.PatientName)
        writeLog("logs.txt", f"image_data: str({patientName})")
    elif image_data.startswith("iVBORw0KGgoAAAANSUhEUgAAA3s"):
        image_name = "test-chest-2.png"
        writeLog("logs.txt", f"image_data: chest")

    elif image_data.startswith("iVBORw0KGgoAAAANSUhEUgAAAcM"):
        image_name = "test_chest.png"
        writeLog("logs.txt", f"image_data: noway")

    else:
        image_name = "image.png"


    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    img_path = os.path.join(output_folder, f'img_{timestamp}.{extension}'.format(timestamp))
    with open(img_path, "wb") as fh:
        fh.write(base64.b64decode(image_data))

    result = dict()
    writeLog("logs.txt","going to anonymizer...")
    res, dict_res = get_anonym_image( image_name)
    #writeLog("logs.txt", f"response: {header},{res}")
    result["imageData"] = header + "," + res
    result["dictResult"] = dict_res
    result["patientName"] = patientName
    result["status"] = "success"

    return jsonify(result)


@app.route('/batch_conversion', methods=['POST'])
def batch_conversion():
    result = dict()

    try:
        # Command to activate the conda environment and run the script
        command = [
            'conda', 'run', '-n', 'IKARD', 'python', 'batch_pipeline.py'
        ]

        # Run the command
        subprocess.Popen(command)

        # If the script runs successfully
        result = {"status": "success"}
    except subprocess.CalledProcessError as e:
        # If there is an error running the script
        result = {"status": "error", "message": str(e)}

    return jsonify(result)

def read_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    
    patient_name = data.get("00100010", None)
    patient_id = data.get("00100020", None)
    patient_dob = data.get("00100030", None)
    
    return patient_name, patient_id, patient_dob

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join("uploads", file.filename)


        file.save(file_path)
        dicom_to_image(file_path)

        png_filename = file.filename.split(".")
        object_name = f"PNG_TO_PROCESS/{png_filename[0]}.png"

        
        path_to_file =  f"uploads/{png_filename[0]}.png"


        upload_to_bucket("frkok02ushb5","Anonymization-bucket",object_name, path_to_file )
        get_anonym_image( object_name)
        original_image = read_img_to_base64(path_to_file)
        anonymized_image = read_img_to_base64(f"uploads/anonymized_{png_filename[0]}.png")
        
        dicom_name = object_name
        dicom_data = pydicom.dcmread(f"uploads/anonymized_{png_filename[0]}.dcm", force=True)
        #print(dicom_path)

        # Extract pixel array and metadata
        pixel_array = dicom_data.pixel_array
        dicom_data_json = dicom_data.to_json_dict()

        output_json_path = os.path.join("uploads", f"anonymized_{png_filename[0]}.json")

        with open(output_json_path, 'w') as json_file:
            json.dump(dicom_data_json, json_file, indent=4)
        
        anon_patient_name, anon_patient_id, anon_patient_dob = read_json_data(f"uploads/anonymized_{png_filename[0]}.json")
        patient_name, patient_id, patient_dob = read_json_data(f"uploads/{png_filename[0]}.json")
        
        result = dict()
        result["status"] = "success"
        result["imageData"] = "data:image/png;base64,"+original_image
        result["anonymized_imageData"] = "data:image/png;base64,"+anonymized_image
        result["anonymized_data"] = {"patientName": anon_patient_name, "patientId": anon_patient_id, "patientDob": anon_patient_dob }
        result["original_data"] = {"patientName": patient_name, "patientId":patient_id, "patientDob": patient_dob }
        writeLog("logs.txt", f"dict: {result}")
        return jsonify(result)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    filename = data.get('prefixedFilename')
    writeLog("logs.txt", f"download: {filename}")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    else:
        return jsonify({'error': 'Filename not provided'}), 400

def app_init():
    app.run(host='0.0.0.0', port=2053, debug=True) #ssl_context=('cert/cert.pem', 'cert/ck.pem'))

def writeLog(path, obj):
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(path, "a") as logfile:
        logfile.write(date_time + ":" + str(obj) + "\n")

if __name__ == "__main__":
    app_init()