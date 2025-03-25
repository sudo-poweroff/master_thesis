import csv
import json
from openai import OpenAI
from azure_connection import get_azure_connection
import os


def obtain_data(container_client):  
    csv_file_path = input("Insert the csv file path: ")
    blob_client = container_client.get_blob_client(csv_file_path)
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    with open(csv_file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

    return csv_file_path

def generate_stroke_dataset_prompt(row):
    etiology_code = row.get("etiology", "N/A")
    
    etiology_description = {
        "1": "Large-artery atherosclerosis (e.g., carotid or basilar artery stenosis)",
        "2": "Cardioembolism (e.g., atrial fibrillation/flutter, prosthetic heart valve, recent MI)",
        "3": "Small-vessel disease (e.g., Subcortical or brain stem lacunar infarction <1.5 cm)",
        "4": "Stroke of other determined etiology",
        "5": "Cryptogenic Stroke"
    }.get(etiology_code, "Unknown etiology")

    clinical_context = "\n".join([f"{key}: {value}" for key, value in row.items()])
    
    if all(value == "n/a" for key, value in row.items() if key != "participant_id"):
        return "n/a"

    return (
        f"Given the following clinical context of a patient:\n{clinical_context}\n"
        f"Generate detailed text of max 200 words with emphasis on etiology: {etiology_description}."
        f" Do not consider paticipant id and race."
    )

def generate_aphasia_dataset_prompt(row):
    wab_type = row.get("wab_type", "N/A")
    wab_type_description = {
        "Anomic": "Anomic as defined by WAB",
        "Broca": "Broca's Aphasia",
        "Conduction": "Conduction",
        "Global": "Global",
        "TranscorticalMotor": "Transcortical Motor",
        "Wernicke": "Wernicke's"
    }.get(wab_type, "Not Aphasic based on WAB cut offs")

    clinical_context = "\n".join([f"{key}: {value}" for key, value in row.items()])
    
    if all(value == "n/a" for key, value in row.items() if key != "participant_id"):
        return "n/a"

    return (
        f"Given the following clinical context of a patient:\n{clinical_context}\n"
        f"Generate detailed text of max 200 words with emphasis on wab type: {wab_type_description}."
        f" Do not consider paticipant id and race."
    )

def generate_alzheimer_dataset_prompt(row):
    def get_description(key, value):
        if key == "session_order":
            return {"0": "first EEG", "1": "yes MRI/fMRI"}.get(value, "Unknown session order")
        elif key == "sex":
            return {"0": "male", "1": "female"}.get(value, "Unknown sex")
        elif key == "education":
            return {
                "0": "primary education",
                "1": "secondary education",
                "2": "partial higher education",
                "3": "higher education"
            }.get(value, "Unknown education")
        elif key == "learning_deficits":
            return {
                "0": "dyslexia",
                "1": "dysgraphia",
                "2": "dysorthography",
                "3": "dyscalculia",
                "4": "none",
                "5": "other"
            }.get(value, "Unknown learning deficits")
        elif key == "ibuprofen_intake":
            return {
                "0": "none",
                "1": "very rarely (several times a year)",
                "2": "rarely (1-4 pills per month)",
                "3": "moderately often (5-11 pills per month)",
                "4": "often (>12 pills per month)"
            }.get(value, "Unknown ibuprofen intake")
        elif key == "thyroid_diseases":
            return {
                "0": "no",
                "1": "hypothyroidism",
                "2": "hyperthyroidism",
                "3": "other"
            }.get(value, "Unknown thyroid diseases")
        elif key == "smoking_status":
            return {
                "0": "no",
                "1": "yes",
                "2": "in the past"
            }.get(value, "Unknown smoking status")
        elif key == "coffee_status":
            return {
                "0": "no",
                "1": "yes, on a daily basis",
                "2": "yes, occasionally",
                "3": "yes, but only decaffeinated coffee"
            }.get(value, "Unknown coffee status")
        elif key == "dementia_history_parents":
            return {
                "0": "healthy parents",
                "1": "one demented parent",
                "2": "both demented parents"
            }.get(value, "Unknown dementia history parents")
        return value

    clinical_context = "\n".join([
        f"{key}: {get_description(key, value)}" 
        for key, value in row.items() if value != "n/a"
    ])

    return (
        f"Given the following clinical context of a patient:\n{clinical_context}\n"
        "Generate detailed text of max 200 words describing the patient's clinical history and risk factors."
        "Do not consider paticipant id."
    )

def process_csv_and_generate_text(client, dataset, csv_path, output_path):
    results = []

    if dataset == "stroke_dataset":
        generate_prompt = generate_stroke_dataset_prompt
    elif dataset == "aphasia_dataset":
        generate_prompt = generate_aphasia_dataset_prompt
    elif dataset == "alzheimer_dataset":
        generate_prompt = generate_alzheimer_dataset_prompt

    with open(csv_path, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prompt = generate_prompt(row)
            print(f"Generating text for participant: {row['participant_id']}")
            if prompt == "n/a":
                results.append({"input": row, "generated_text": "n/a"})
            else:
                try:
                    completion = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )

                    generated_text = completion.choices[0].message.content.strip()
                    results.append({"input": row, "generated_text": generated_text})

                except Exception as e:
                    print(f"Errore durante la generazione per la riga: {row}\nErrore: {e}")

    # Save the results to a JSON file
    with open(output_path, mode="w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Configure OpenAI API key
    api_key = input("Enter OpenAI API key: ")
    client = OpenAI(api_key=api_key)

    container_name = input("Insert the container name: ")
    connection_string = input("Insert the connection string: ")
    container_client = get_azure_connection(container_name, connection_string)
    csv_file_path = obtain_data(container_client = container_client)
    dataset_name = csv_file_path.split("/")[0]
    output_file_path = dataset_name + "/generated_text_data.json"

    # Execure text generation
    process_csv_and_generate_text(client = client, dataset = dataset_name, csv_path = csv_file_path, output_path = output_file_path)
    print(f"Processing complete, the results are saved in {output_file_path}.")

    # Upload the generated text data to Azure Blob Storage
    blob_client = container_client.get_blob_client(output_file_path)
    with open(output_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print("Results uploaded to Azure Blob Storage.")

    os.remove(csv_file_path)
    os.remove(output_file_path)