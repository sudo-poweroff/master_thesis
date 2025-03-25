from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.diagnosticreport import DiagnosticReport
import json
from datetime import datetime, timezone
import uuid
from azure_connection import get_azure_connection
import os
import pandas as pd


def create_patient(participant):
    json_obj = {"resourceType": "Patient",
                "active": True,
                "id": str(participant["participant_id"]),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now().isoformat()
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Patient record for participant ID: {participant['participant_id']}</div>"
                },    
                "gender": "male" if "sex" in participant and (participant["sex"] == "M" or participant["sex"] =="0") else "female" if "sex" in participant and (participant["sex"] == "F" or participant["sex"] == "1") else "unknown",
                "extension": [
                    {
                        "url": "http://example.org/consent#patient-age",
                        "valueString": participant["age"] if "age" in participant and participant["age"]  else "unknown"
                    }
                ]
                }
    if "race" in participant:
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-race",
                        "valueString": "white" if participant["race"] == "w" else "black or african american" if participant["race"]=="b" else "unknown"
                    })
    if "APOE_rs429358" in participant:
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-APOE-rs429358",
                        "valueString": participant["APOE_rs429358"]
                    })
    if "APOE_rs7412" in participant:
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-APOE-rs7412",
                        "valueString": participant["APOE_rs7412"]
                    })
    if "APOE_haplotype" in participant:
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-APOE-haplotype",
                        "valueString": participant["APOE_haplotype"]
                    })
    if "PICALM_rs3851179" in participant:
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-PICALM-rs3851179",
                        "valueString": participant["PICALM_rs3851179"]
                    })
    if "education" in participant:
        education = participant.get("education", "N/A")
    
        education_description = {
            "0": "primary education",
            "1": "secondary education",
			"2": "partial higher education",
			"3": "higher education"
        }.get(education, "Unknown education")
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-education",
                        "valueString": education_description
                    })
    if "learning_deficits" in participant:
        learning_deficits = participant.get("learning_deficits", "N/A")
        learning_deficits_description = {
            "0": "dyslexia",
            "1": "dysgraphia",
			"2": "dysorthography",
			"3": "dyscalculia",
			"4": "none",
			"5": "other"
        }.get(learning_deficits, "Unknown learning deficits")
        json_obj["extension"].append({
                        "url": "http://example.org/consent#patient-learning-deficits",
                        "valueString": learning_deficits_description
                    })
    
    
    patient = Patient.model_validate(json_obj)
    return patient.model_dump()

def create_observation(participant_id, system, code, display, value, unit):
    json_obj = {
        "resourceType": "Observation",
        "id": f"observation-{code.lower()}-{participant_id}",
        "text": {
            "status": "generated",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Observation record for participant ID: {participant_id}</div>"
        },
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": system,
                    "code": code,
                    "display": display  
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{participant_id}"
        }
    }
    try:
        if isinstance(float(value), float) or isinstance(int(value), int):
            json_obj["valueQuantity"] = {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": unit
            }
    except (ValueError, TypeError):
        json_obj["valueString"] = value

    observation = Observation.model_validate(json_obj)
    return observation.model_dump() 

def create_diagnosticreport(participant_id, report_text, report_code, report_type):
    json_obj = {
        "resourceType": "DiagnosticReport",
        "id": f"report-{participant_id}",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": report_code,
                    "display": report_type
                }
            ],
            "text": report_type
        },
        "subject": {
            "reference": f"Patient/{participant_id}"
        },
        "effectiveDateTime": datetime.now(timezone.utc).isoformat(),
        "issued": datetime.now(timezone.utc).isoformat(),
        "conclusion": report_text 
    }
    diagnostic_report = DiagnosticReport.model_validate(json_obj)
    return diagnostic_report.model_dump()

def create_imaging_study(participant_id, images, modality):
    json_obj = {
        "resourceType": "ImagingStudy",
        "id": f"study-{participant_id}",
        "text": {
            "status": "generated",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Imaging study record for participant ID: {participant_id}</div>"
        },
        "status": "available",
        "subject": {
            "reference": f"Patient/{participant_id}"
        },
        "series": [{
                "uid": str(uuid.uuid4()),
                "number": 1,
                "modality": {
                    "coding": [{
                        "system": "http://dicom.nema.org/resources/ontology/DCM",
                        "code": modality,
                        "display": "Magnetic Resonance" if modality == "MR" else "Electrocardiogram" if modality == "ECG" else "Computed Tomography"
                    }]
                    
                },
                "instance": [{
                        "uid": str(uuid.uuid4()),
                        "sopClass": {
                            "system": "urn:ietf:rfc:3986",
                            "code": "urn:oid:1.2.840.10008.5.1.4.1.1.2",
                            "display": f"{modality} Image Storage"
                        },
                        "title": f"Image {i + 1}",
                        "extension": [{
                            "url": "http://example.org/consent#image-url",
                            "valueUrl": image_url
                        }]
                    }
                    for i, image_url in enumerate(images)
                ]
            }]
    }
    imaging_study = ImagingStudy.model_validate(json_obj)
    return imaging_study.model_dump()

def list_images_for_participant(blob_prefix, container_client):
    image_urls = []

    blobs = container_client.list_blobs(name_starts_with=blob_prefix)
    for blob in blobs:
        if blob.name.endswith(".png"):
            image_url = f"https://thesislakehouse.blob.core.windows.net/processeddata/{blob.name}"
            image_urls.append(image_url)
    return image_urls

def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def obtain_data(file_path, container_client):  
    blob_client = container_client.get_blob_client(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

def standardize_stroke_dataset(source_file_path, source_container_client, destination_container_client):
    with open(source_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for record in data:
        fhir_resources = []
        participant = record["input"]

        print(f"Standardizing data of {participant['participant_id']}")
        fhir_resources.append(create_patient(participant))

        if participant["acuteischaemicstroke"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://snomed.info/sct", code="422504002", display="Acute ischaemic stroke", value=participant["acuteischaemicstroke"], unit="boolean"))

        if participant["priorstroke"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://snomed.info/sct", code="141281000119101", display="Evidence of prior stroke", value=participant["priorstroke"], unit="boolean"))
    
        if participant["bmi"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="39156-5", display="Body Mass Index (BMI)", value=participant["bmi"], unit="kg/m2"))
        
        if participant["nihss"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="70182-1", display="NIH Stroke Scale", value=participant["nihss"], unit="score"))

        if participant["gs_rankin_6isdeath"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="75859-9", display="Modified Rankin Scale", value=participant["gs_rankin_6isdeath"], unit="score"))  
        
        if participant["etiology"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91011-7", display="Etiology of stroke",value=participant["etiology"], unit="text"))

        if record["generated_text"] :
            fhir_resources.append(create_diagnosticreport(participant_id=participant['participant_id'], report_text=record["generated_text"], report_code="50398-7", report_type="Stroke report"))
        
        images = list_images_for_participant(f"stroke_dataset/derivatives/lesion_masks/{participant['participant_id']}/", source_container_client)
        images += list_images_for_participant(f"stroke_dataset/{participant['participant_id']}/", source_container_client)
        if images:
            fhir_resources.append(create_imaging_study(participant['participant_id'], images, "MR"))
        else:
            print(f"No images found for participant {participant['participant_id']}")

        output_file_path = f"stroke_dataset/{participant['participant_id']}.json"
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(fhir_resources, f, indent=4, ensure_ascii=False, default=custom_serializer)

        destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
        with open(output_file_path, "rb") as fhir_file:
            destination_blob_client.upload_blob(fhir_file, overwrite=True)
        print(f"Data standardized for participant {participant['participant_id']} uploaded to destination container!")
        os.remove(output_file_path)
        
def standardize_aphasia_dataset(source_file_path, source_container_client, destination_container_client):
    with open(source_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for record in data:
        fhir_resources = []
        participant = record["input"]

        print(f"Standardizing data of {participant['participant_id']}")
        fhir_resources.append(create_patient(participant))

        if participant["wab_days"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="88657-2", display="Western Aphasia Battery Revised days", value=participant["wab_days"], unit="days"))
        
        if participant["wab_aq"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="54805-7", display="Western Aphasia Battery Revised aphasia quotient", value=participant["wab_aq"], unit="score"))

        if participant["wab_type"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="54805-7", display="Aphasia type from the Western Aphasia Battery", value=participant["wab_type"], unit="text"))

        if record["generated_text"]:
            fhir_resources.append(create_diagnosticreport(participant_id=participant['participant_id'], report_text=record["generated_text"], report_code="50398-7", report_type="Aphasia report"))

        images = list_images_for_participant(f"aphasia_dataset/derivatives/lesion_masks/{participant['participant_id']}/", source_container_client)
        images += list_images_for_participant(f"aphasia_dataset/{participant['participant_id']}/", source_container_client)
        if images:
            fhir_resources.append(create_imaging_study(participant['participant_id'], images, "MR"))
        else:
            print(f"No images found for participant {participant['participant_id']}")

        output_file_path = f"aphasia_dataset/{participant['participant_id']}.json"
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(fhir_resources, f, indent=4, ensure_ascii=False, default=custom_serializer)

        destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
        with open(output_file_path, "rb") as fhir_file:
            destination_blob_client.upload_blob(fhir_file, overwrite=True)
        print(f"Data standardized for participant {participant['participant_id']} uploaded to destination container!")
        os.remove(output_file_path)

def standardize_alzheimer_dataset(source_file_path, source_container_client, destination_container_client):
    with open(source_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for record in data:
        fhir_resources = []
        participant = record["input"]

        print(f"Standardizing data of {participant['participant_id']}")
        fhir_resources.append(create_patient(participant))
        if participant["second_phase"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="00000-0", display="Information on whether a given participant took part in the second phase of the experiment", value=participant["second_phase"], unit="boolean"))
        if participant["session_order"]:
            session_order = participant.get("session_order", "N/A")
    
            session_order_description = {
                "0": "first EEG",
                "1": "yes MRI/fMRI"
            }.get(session_order, "Unknown order")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="00000-0", display="Information on whether a given participant underwent an EEG session first or a MRI/fMRI session first", value=session_order_description, unit="integer"))
        if participant["BMI"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="39156-5", display="Body Mass Index (BMI)", value=participant["BMI"], unit="kg/m2"))
        if participant["allergies"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="52473-6", display="Allergies of any type", value=participant["allergies"], unit="boolean"))
        if participant["drugs"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="52471-0", display="Information on taking permanent medication", value=participant["drugs"], unit="boolean"))
        if participant["ibuprofen_intake"]:
            ibuprofen_intake = participant.get("ibuprofen_intake", "N/A")
            ibuprofen_intake_description = {
                "0": "none",
                "1": "very rarely (several times a year)",
                "2": "rarely (1-4 pills per month)",
                "3": "moderately often (5-11 pills per month)",
                "4": "often (>12 pills per month)"
            }.get(ibuprofen_intake, "Unknown ibuprofen intake")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="52471-0", display="Information on intake of medication with ibuprofen or other non-steroidal anti-inflammatory drugs", value=ibuprofen_intake_description, unit="text"))
        if participant["thyroid_diseases"]:
            thyroid_diseases = participant.get("thyroid_diseases", "N/A")
            thyroid_diseases_description = {
                "0": "no",
                "1": "hypothyroidism",
                "2": "hyperthyroidism",
                "3": "other"
            }.get(thyroid_diseases, "Unknown thyroid diseases")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="54799-2", display="Information on thyroid diseases", value=thyroid_diseases_description, unit="text"))
        
        if participant["hypertension"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="LA32904-7", display="Hypertension", value=participant["hypertension"], unit="boolean"))
        if participant["diabetes"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="45636-8", display="Diabetes", value=participant["diabetes"], unit="boolean"))
        if participant["other_diseases"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="46019-6", display="Any other chronic diseases/heatlh problems", value=participant["other_diseases"], unit="boolean"))
        if participant["smoking_status"]:
            smoking_status = participant.get("smoking_status", "N/A")
            smoking_status_description = {
                "0": "no",
                "1": "yes",
                "2": "in the past"
            }.get(smoking_status, "Unknown smoking status")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="LG41856-2", display="Smoking status", value=smoking_status_description, unit="text"))
        if participant["coffee_status"]:
            coffee_status = participant.get("coffee_status", "N/A")
            coffee_status_description = {
                "0": "no",
                "1": "yes, on a daily basis",
                "2": "yes, occasionally",
                "3": "yes, but only decaffeinated coffee"
            }.get(coffee_status, "Unknown coffee status")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="LA11890-0", display="Coffee consumption", value=coffee_status_description, unit="text"))
        if participant["dementia_history_parents"]:
            dementia_history_parents = participant.get("dementia_history_parents", "N/A")
            dementia_history_parents_description = {
                "0": "healthy parents",
                "1": "one demented parent",
                "2": "both demented parents"
            }.get(dementia_history_parents, "Unknown dementia history in parents")
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="10157-6", display="Dementia history in parents", value=dementia_history_parents_description, unit="text"))
        if participant["BDI"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="89211-7", display="Beck's Depression Inventory", value=participant["BDI"], unit="score"))
        if participant["SES"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="62931-1", display="Socioeconomic status", value=participant["SES"], unit="score"))
        if participant["RPM"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Raven's Progressive Matrices", value=participant["RPM"], unit="score"))
        if participant["EHI"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Edinburgh Handedness Inventory", value=participant["EHI"], unit="score"))
        if participant["NEO_NEU"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="NEO-FFI Personality Inventory, total score on neuroticism scale", value=participant["NEO_NEU"], unit="score"))
        if participant["NEO_EXT"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="NEO-FFI Personality Inventory, total score on extraversion scale", value=participant["NEO_EXT"], unit="score"))
        if participant["NEO_OPE"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="NEO-FFI Personality Inventory, total score on openness scale", value=participant["NEO_OPE"], unit="score"))
        if participant["NEO_AGR"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="NEO-FFI Personality Inventory, total score on agreeableness scale", value=participant["NEO_AGR"], unit="score"))
        if participant["NEO_CON"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="NEO-FFI Personality Inventory, total score on conscientiousness scale", value=participant["NEO_CON"], unit="score"))
        if participant["AUDIT"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="72110-0", display="Alcohol Use Disorders Identification Test", value=participant["AUDIT"], unit="score"))
        if participant["MINI-COPE_1"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 1", value=participant["MINI-COPE_1"], unit="points"))
        if participant["MINI-COPE_2"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 2", value=participant["MINI-COPE_2"], unit="points"))
        if participant["MINI-COPE_3"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 3", value=participant["MINI-COPE_3"], unit="points"))
        if participant["MINI-COPE_4"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 4", value=participant["MINI-COPE_4"], unit="points"))
        if participant["MINI-COPE_5"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 5", value=participant["MINI-COPE_5"], unit="points"))
        if participant["MINI-COPE_6"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 6", value=participant["MINI-COPE_6"], unit="points"))
        if participant["MINI-COPE_7"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 7", value=participant["MINI-COPE_7"], unit="points"))
        if participant["MINI-COPE_8"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 8", value=participant["MINI-COPE_8"], unit="points"))
        if participant["MINI-COPE_9"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 9", value=participant["MINI-COPE_9"], unit="points"))
        if participant["MINI-COPE_10"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 10", value=participant["MINI-COPE_10"], unit="points"))
        if participant["MINI-COPE_11"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 11", value=participant["MINI-COPE_11"], unit="points"))
        if participant["MINI-COPE_12"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 12", value=participant["MINI-COPE_12"], unit="points"))
        if participant["MINI-COPE_13"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 13", value=participant["MINI-COPE_13"], unit="points"))
        if participant["MINI-COPE_14"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="Stress coping strategies (Mini-Cope Questionnaire), question no. 14", value=participant["MINI-COPE_14"], unit="points"))
        if participant["CVLT_1"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, list A, task 1-5", value=participant["CVLT_1"], unit="points"))
        if participant["CVLT_2"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, list A, task 1", value=participant["CVLT_2"], unit="points"))
        if participant["CVLT_3"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, list A, task 5", value=participant["CVLT_3"], unit="points"))
        if participant["CVLT_4"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, list B", value=participant["CVLT_4"], unit="points"))
        if participant["CVLT_5"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, short-term delay free recall", value=participant["CVLT_5"], unit="points"))
        if participant["CVLT_6"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, short-term delay cued recall", value=participant["CVLT_6"], unit="points"))
        if participant["CVLT_7"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, long-term delay free recall", value=participant["CVLT_7"], unit="points"))
        if participant["CVLT_8"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, long-term delay cued recall", value=participant["CVLT_8"], unit="points"))
        if participant["CVLT_9"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, perseverations", value=participant["CVLT_9"], unit="points"))
        if participant["CVLT_10"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, intrusion errors - free recall", value=participant["CVLT_10"], unit="points"))
        if participant["CVLT_11"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, intrusion errors - cued recall", value=participant["CVLT_11"], unit="points"))
        if participant["CVLT_12"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, recognition: total hits", value=participant["CVLT_12"], unit="points"))
        if participant["CVLT_13"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="91391-3", display="California Verbal Learning Test, recognition: false alarms", value=participant["CVLT_13"], unit="points"))
        if participant["leukocytes"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26464-8", display="Leukocytes", value=participant["leukocytes"], unit="K/µl"))
        if participant["erythrocytes"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="789-8", display="Erythrocytes", value=participant["erythrocytes"], unit="K/µl"))
        if participant["hemoglobin"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="718-7", display="Hemoglobin", value=participant["hemoglobin"], unit="K/µl"))
        if participant["hematocrit"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="20570-8", display="Hematocrit", value=participant["hematocrit"], unit="%"))
        if participant["MCV"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="787-2", display="Mean cell volume level", value=participant["MCV"], unit="fl"))
        if participant["MCH"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="28539-5", display="Mean cell hemoglobin level", value=participant["MCH"], unit="pg"))
        if participant["MCHC"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="28540-3", display="Mean corpuscular hemoglobin concentration", value=participant["MCHC"], unit="g/dl"))
        if participant["RDW-CV"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="788-0", display="Red blood cell distribution width (RDW-CV)", value=participant["RDW-CV"], unit="%"))
        if participant["platelets"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26515-7", display="Platelets", value=participant["platelets"], unit="K/µl"))
        if participant["PDW"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="51631-0", display="Platelet distribution width (PDW)", value=participant["PDW"], unit="fl"))
        if participant["MPV"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="32623-1", display="Mean platelet volume (MPV)", value=participant["MPV"], unit="fl"))
        if participant["P-LCR"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="48386-7", display="Platelet large cell ratio (P-LCR)", value=participant["P-LCR"], unit="%"))
        if participant["neutrophils"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26499-4", display="Neutrophils level", value=participant["neutrophils"], unit="K/µl"))
        if participant["lymphocytes"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26474-7", display="Lymphocytes level", value=participant["lymphocytes"], unit="K/µl"))
        if participant["monocytes"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="743-5", display="Monocytes level", value=participant["monocytes"], unit="K/µl"))
        if participant["eosinophils"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="711-2", display="Eosinophils level", value=participant["eosinophils"], unit="K/µl"))
        if participant["basophils"]:    
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26444-0", display="Basophils level", value=participant["basophils"], unit="K/µl"))
        if participant["neutrophils_%"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26499-4", display="Neutrophils level percent", value=participant["neutrophils_%"], unit="%"))
        if participant["lymphocytes_%"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26474-7", display="Lymphocytes level percent", value=participant["lymphocytes_%"], unit="%"))
        if participant["monocytes_%"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="743-5", display="Monocytes level percent", value=participant["monocytes_%"], unit="%"))
        if participant["eosinophils_%"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="711-2", display="Eosinophils level percent", value=participant["eosinophils_%"], unit="%"))
        if participant["basophils_%"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="26444-0", display="Basophils level percent", value=participant["basophils_%"], unit="%"))
        if participant["total_cholesterol"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="2093-3", display="Total cholesterol level", value=participant["total_cholesterol"], unit="mg/dl"))
        if participant["cholesterol_HDL"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="2085-9", display="Cholesterol HDL level", value=participant["cholesterol_HDL"], unit="mg/dl"))
        if participant["non-HDL_cholesterol"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="43396-1", display="Non-HDL cholesterol level", value=participant["non-HDL_cholesterol"], unit="mg/dl"))
        if participant["LDL_cholesterol"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="22748-8", display="LDL cholesterol level", value=participant["LDL_cholesterol"], unit="mg/dl"))
        if participant["triglycerides"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="14927-8", display="Triglycerides level", value=participant["triglycerides"], unit="mg/dl"))
        if participant["HSV_r"]:
            fhir_resources.append(create_observation(participant_id=participant['participant_id'], system="http://loinc.org", code="31411-2", display="Herpes simple virus (HSV) IgG", value=participant["HSV_r"], unit="boolean"))
        if record["generated_text"]:
            fhir_resources.append(create_diagnosticreport(participant_id=participant['participant_id'], report_text=record["generated_text"], report_code="50398-7", report_type="Aphasia report"))

        images = list_images_for_participant(f"alzheimer_dataset/{participant['participant_id']}/", source_container_client)
        if images:
            fhir_resources.append(create_imaging_study(participant_id=participant['participant_id'], images=images, modality="MR"))
        else:
            print(f"No images found for participant {participant['participant_id']}")

        output_file_path = f"alzheimer_dataset/{participant['participant_id']}.json"
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(fhir_resources, f, indent=4, ensure_ascii=False, default=custom_serializer)

        destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
        with open(output_file_path, "rb") as fhir_file:
            destination_blob_client.upload_blob(fhir_file, overwrite=True)
        print(f"Data standardized for participant {participant['participant_id']} uploaded to destination container!")
        os.remove(output_file_path)

def standardize_ecg_dataset(source_file_path, source_container_client, destination_container_client):
    data = pd.read_csv(source_file_path)
    grouped_data = data.groupby("participant_id")
    for participant_id, group in grouped_data:
        fhir_resources = []
        print(f"Standardizing data of {participant_id}")
        fhir_resources.append(create_patient(participant = group.iloc[0]))
        for _, row in group.iterrows():
            if row["study_id"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="0000-0", display="Identifier for the study which the diagnostic ECG is associated with", value=row["study_id"], unit="integer"))
            if row["cart_id"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="0000-0", display="Identifier specific to the ECG cart used to collect the diagnostic ECG waveform", value=row["cart_id"], unit="integer"))
            if row["ecg_time"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="74555-4", display="The date that the diagnostic ECG was collected on", value=row["ecg_time"], unit="datetime"))
            if row["bandwidth"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="The bandwidth of the ECG machine", value=row["bandwidth"], unit="text"))
            if row["filtering"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Filter setting", value=row["filtering"], unit="text"))
            if row["rr_interval"]:  
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time between successive R-waves", value=row["rr_interval"], unit="milliseconds"))
            if row["p_onset"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time at the onset of the P-wave", value=row["p_onset"], unit="milliseconds"))
            if row["p_end"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time at the end of the P-wave", value=row["p_end"], unit="milliseconds"))
            if row["qrs_onset"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time at the beginning of the QRS complex", value=row["qrs_onset"], unit="milliseconds"))
            if row["qrs_end"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time at the end of the QRS complex", value=row["qrs_end"], unit="milliseconds"))
            if row["t_end"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="Time at the end of the T-wave", value=row["t_end"], unit="milliseconds"))
            if row["p_axis"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="The electrical axis of the P-wave", value=row["p_axis"], unit="degrees"))
            if row["qrs_axis"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="The electrical axis of the QRS complex", value=row["qrs_axis"], unit="degrees"))
            if row["t_axis"]:
                fhir_resources.append(create_observation(participant_id=participant_id, system="http://loinc.org", code="58253-6", display="The electrical axis of the T-wave", value=row["t_axis"], unit="degrees"))
            if row["report"]:
                fhir_resources.append(create_diagnosticreport(participant_id=participant_id, report_text=row["report"], report_code="50398-7", report_type="ECG report"))
            
            images = list_images_for_participant(f"ecg_dataset/files/p{str(participant_id).zfill(4)[:4]}/p{str(participant_id)}/s{str(row['study_id'])}/", source_container_client)
            if images:
                fhir_resources.append(create_imaging_study(participant_id=participant_id, images=images, modality="ECG"))
            else:
                print(f"No images found for participant {participant_id}")

        output_file_path = f"ecg_dataset/{participant_id}.json"
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(fhir_resources, f, indent=4, ensure_ascii=False, default=custom_serializer)

        destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
        with open(output_file_path, "rb") as fhir_file:
            destination_blob_client.upload_blob(fhir_file, overwrite=True)
        print(f"Data standardized for participant {participant_id} uploaded to destination container!")
        os.remove(output_file_path)

        
        
if __name__ == '__main__':
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)
    dataset = input("Insert the dataset name on witch apply the standardization: ")

    if dataset == "ecg_dataset":
        source_file_path = f"{dataset}/machine_measurements.csv"
    else:
        source_file_path = f"{dataset}/generated_text_data.json"

    obtain_data(source_file_path, source_container_client)

    if dataset =="stroke_dataset":
        standardize_stroke_dataset(source_file_path=source_file_path, source_container_client=source_container_client, destination_container_client=destination_container_client)
    elif dataset == "aphasia_dataset":
        standardize_aphasia_dataset(source_file_path=source_file_path, source_container_client=source_container_client, destination_container_client=destination_container_client)
    elif dataset == "alzheimer_dataset":
        standardize_alzheimer_dataset(source_file_path=source_file_path, source_container_client=source_container_client, destination_container_client=destination_container_client)
    elif dataset == "ecg_dataset":
        standardize_ecg_dataset(source_file_path=source_file_path, source_container_client=source_container_client, destination_container_client=destination_container_client)