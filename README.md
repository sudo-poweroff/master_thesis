# Development of a Data Lakehouse Architecture for Digitalized Clinical Data: Acquisition, Processing, Standardization, and AI Optimization

Welcome to the repository of my thesis project, which collects all the scripts used for processing clinical data. The growing need for scalable systems for managing healthcare data motivated the development of this thesis, which aimed to build a data lakehouse infrastructure in Azure environment for acquiring, process, standardize and transform clinical data into an AI-ready format.

## 📂 Datasets

The datasets selected for the project are:
- [A Polish Electroencephalography, Alzheimer’s Risk-genes, Lifestyle and Neuroimaging (PEARL-Neuro) Database](https://openneuro.org/datasets/ds004796/versions/1.0.9) (Alzheimer dataset)
- [Stroke Outcome Optimization Project (SOOP)](https://openneuro.org/datasets/ds004889/versions/1.1.2) (Stroke dataset)
- [Aphasia Recovery Cohort (ARC) Dataset](https://openneuro.org/datasets/ds004884/versions/1.0.2) (Aphasia dataset)
- [MIMIC-IV-ECG: Diagnostic Electrocardiogram Matched Subset](https://physionet.org/content/mimic-iv-ecg/1.0/)

## ⚙️ ​Project structure
The project is organized as follows:
- __alzheimer_dataset__ contains the metrics computed on alzheimer_dataset;
- __alzheimer_dataset_second_phase_0__ contains the metrics computed on the subset of alzheimer_dataset with 'second_phase=0';
- __alzheimer_dataset_second_phase_1__ contains the metrics computed on the subset of alzheimer_dataset with 'second_phase=1';
- __aphasia_dataset__ contains the metrics computed on aphasia_dataset;
- __container_metrics__ contains the metrics computed on Azure containers;
- __ecg_dataset__ contains the metrics computed on ecg_dataset;
- __plots__ contains the plots used in my thesis;
- __scripts__ contains the scripts developed for the project;
- __stroke_dataset__ contains the metrics computed on stroke_dataset

## 💻 Project environment setup & usage
To replicate this project use the following steps:
1. Clone the repository by running:
```bash
git clone https://github.com/sudo-poweroff/master_thesis.git
```
2. Install the required dependencies by running:
```bash
pip install -r requirements.txt
```
----------------------------------------------------------------------------
If you have new data and want to process it, execute the following steps:
1. If you have NIfTI files (namely magnetic resonance imaging) check for 4th dimension (time axis) and eventually remove it running `scripts\reduce_nifti_file_size.py`
2. Load the data in Azure using AzCopy (previously downloaded in your machine) using a command like:
```bash
azcopy copy "path/to/dataset" "container-shared-access-token"
    --recursive=true --overwrite=false
```
3. If you want to check the uppload integrity run `scripts\dataset_integrity.py`
4. Extract images from new files:
    1. If you have NIfTI files run `scripts\extract_images_from_nii_files.py` for image extraction
    2. If you have ECG files run `scripts\extract_images_from_ecg_files.py`
    3. If you have a new type of imaging data develop code for image extraction
5. If you need to generate text data use `scripts\text_data_generation.py`. If you are considering a new dataset please create a newer prompt for this dataset!
6. Check the integrity of tabular data
7. Standardize data runing `scripts\standardize_data.py`. If you are considering a new dataset please create a new mapping function.
8. Convert image to tensors using `scripts\image_to_tensor.py`
9. Tokenize and embed text data using `scripts\text_tokenization_and_embedding.py`
10. Process tabular data to handle missing values, embed categorical features and normalize continuous features using `scripts\tabular_data_processing.py`
11. Convert tabular data to tensors using `scripts\tabular_data_to_tensor.py`
12. If you want compute containers metrics use `scripts\compute_container_metrics.py`

## 🛠️ Feature works
- [ ] Delta Lake integration
- [ ] Reduce execution times
- [ ] Pipeline automatization 
- [ ] Improve data quality
- [ ] Datasets expansion

## 📧 Contact
Simone Della Porta - sdellaporta34@gmail.com

