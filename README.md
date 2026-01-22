# Multi-TE ASL Processing Scripts

This repository contains a set of Bash and Python scripts for post-processing **multi–echo arterial spin labeling (Multi-TE ASL)** MRI data, with a particular focus on **blood–brain barrier (BBB) integrity measurements**.  
The pipeline implements a **modified Multi-TE ASL signal model** and voxelwise perfusion calibration, following published and validated methods.

---

## Contents

1. [Software Requirements](#1-software-requirements)  
2. [Modified Multi-TE ASL Model](#2-modified-multi-te-asl-model)  
3. [Pipeline Overview & Scripts](#3-pipeline-overview--scripts)  
4. [Suggested Reading](#suggested-reading)  
5. [References](#references)

---

## 1. Software Requirements

This pipeline is based on the **FMRIB Software Library (FSL)** and is intended to run on Linux systems (e.g., Ubuntu or CentOS).

### Required software
- **FSL** (recommended: most recent stable version)  
  Installation instructions:  
  https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation

- **Fabber** (from FSL)  
  Fabber is a tool for fitting timeseries data to a forward model using a Bayesian approach.
  (Chappell et al., 2008).

- **dcm2niix** for DICOM to NIfTI conversion  
  https://github.com/rordenlab/dcm2niix

- **Python** (for M0 fitting)
  - numpy  
  - scipy  
  - nibabel  

> **Important**  
> The modified Multi-TE ASL model used here is **not yet part of the standard FSL distribution**.  
> Model source files must be manually copied and `fabber` recompiled to enable fitting.

---

## 2. Modified Multi-TE ASL Model

This pipeline uses a **modified version of the original Multi-TE ASL model** (Gregori et al., 2013), optimized for **BBB integrity analysis**.

Key features:
- Joint modeling of perfusion and multi-echo decay
- Estimation of:
  - Perfusion (CBF)
  - Arterial transit time (ATT)
  - Exchange time (T<sub>exch</sub>)
  - Intra-voxel transit time (ITT)

Details of the model modification, validation, and performance are described in:

> **Mahroo et al., 2021 — Robust Multi-TE ASL-Based Blood–Brain Barrier Integrity Measurements**

The modified model must be compiled into Fabber before running the fitting step.

---

## 3. Pipeline Overview & Scripts

The scripts are **numbered chronologically** and must be executed **in order**.

### 1. `1_master`
Master configuration script:
- Defines ASL acquisition parameters
- Sets directory structure
- Specifies model parameters used by Fabber  
Model parameters are literature-based and **should not be modified** unless explicitly justified.

---

### 2. `2_dcm2niix`
- Creates directory structure
- Converts DICOM data to NIfTI using `dcm2niix`

---

### 3. `3_Structural_Preprocessing`
- Structural preprocessing using `fsl_anat`
- Brain extraction
- Tissue segmentation
- Partial volume estimation (PVE)

Outputs are used for:
- Registration
- Partial-volume–aware ROI analysis

---

### 4. `4_Mask_ASL_Space`
- Generates ASL brain mask
- Uses first echo of HAD-4 dataset as reference
- Two-step registration between ASL and T1 space

---

### 5. `5_Reg_M0_to_ASL_with_topup`
- Registers M0 images to ASL reference
- Applies distortion correction using **TOPUP** if M0 data with opposing phase-encoding directions are available

---

### 6. `6_HAD_4_MultiTE_MotionCorrection_Decoding`
- Motion correction
- Distortion correction
- Hadamard decoding for HAD-4 multi-TE dataset  
> Decoding matrix is provided and should be verified.  
> Current implementation assumes **Walsh-ordered Hadamard encoding**.

---

### 7. `7_HAD_8_SingleTE_MotionCorrection_Decoding`
- Same preprocessing steps as above
- Applied to HAD-8 single-TE dataset

---

### 8. `8_Concatenating_Datasets`
- Concatenates HAD-4 and HAD-8 datasets
- Produces final input for model fitting

---

### 9. `9_FabberCommand_Merged`
- Calls Fabber with the modified Multi-TE ASL model
- Outputs voxelwise parameter maps:
  - `mean_ftiss` (perfusion)
  - `mean_delttiss` (ATT)
  - `mean_T_exch` (exchange time)
  - `mean_ITT` (intra-voxel trans_
