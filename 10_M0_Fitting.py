# -*- coding: utf-8 -*-
"""
Copyright (c) Fraunhofer MEVIS, Germany. 
Copyright (c) 2026 Amnah Mahroo.
All rights reserved.
"""
# python script for M0 fitting
# results saved in /m0/reg_m0_to_asl_with_topup/m0_fitting/

import numpy as np
import nibabel as nib
from scipy.optimize import curve_fit
import os
import sys

print("START SCRIPT 10")
FOLDER_NIFTI = os.environ["folder_nifti"]
TIs = os.environ["M0_TI_VALUES"].split(",")
tis = np.array([float(i) for i in TIs])

if not os.path.exists(FOLDER_NIFTI + "/m0/reg_m0_to_asl/m0_fitting"):
    os.makedirs(FOLDER_NIFTI + "/m0/reg_m0_to_asl/m0_fitting")

FNAME_IN = FOLDER_NIFTI + "/m0/reg_m0_to_asl/m0_results/m0_RL_merged.nii.gz"
FNAME_MASK = FOLDER_NIFTI + "/mask/asl_mask.nii.gz"
FOLDER_OUTPUT = FOLDER_NIFTI + "/m0/reg_m0_to_asl/m0_fitting"

# NOTE:
# The M0 scan uses saturation of the readout volume after the IR preparation.
# Therefore, the signal follows a saturation-recovery model rather than a true
# inversion-recovery model, and the inversion (factor 2) term is omitted.
# The model assumes S(TI) = M0 * (1 - exp(-TI / T1)).

def t1model(tis, m0, t1):
    return m0 * (1 - np.exp(-tis/t1))

# Load the data
nii_input = nib.load(FNAME_IN)
data_multiti = nii_input.get_fdata()
volshape = list(data_multiti.shape[:-1])

# Load the brain mask and mask off the relevant voxels
nii_roi = nib.load(FNAME_MASK)
roidata = nii_roi.get_fdata()
data_multiti_roi = data_multiti[roidata > 0]
nvoxels_roi = data_multiti_roi.shape[0]
if data_multiti_roi.shape[1] != len(tis):
    print("NUMBER OF MEASUREMENTS %i NOT EQUAL TO NUMBER OF TIS %i !!!" % (data_multiti_roi.shape[1], len(tis)))
    sys.exit(0)
print("%i TIs and %i voxels to be fitted !" % (len(tis), nvoxels_roi))

# Go through each voxel and fit the T1 model for m0 and t1
m0_roi = np.zeros(nvoxels_roi, dtype=np.float32)
t1_roi = np.zeros(nvoxels_roi, dtype=np.float32)
for voxel_idx, data_multiti_voxel in enumerate(data_multiti_roi):
    try:
        m0_init = max(data_multiti_voxel)
        param_init =  [m0_init, 2.0, 1700.0]        
        popt, pcov = curve_fit(t1model, tis, data_multiti_voxel, p0=param_init, bounds=((m0_init,500), (5*m0_init,6000)))
        m0_roi[voxel_idx] = popt[0]
        t1_roi[voxel_idx] = popt[1]
    except Exception as exc:
        print("Fit failed for voxel: %i !!!" % voxel_idx)

# Write out the m0 and T1 map
m0 = np.zeros(volshape, dtype=np.float32)
t1 = np.zeros(volshape, dtype=np.float32)

m0[roidata > 0] = m0_roi
t1[roidata > 0] = t1_roi

nii_m0 = nib.Nifti1Image(m0, None, nii_input.header)
nii_m0.update_header()
nii_m0.to_filename(FOLDER_OUTPUT + "/m0_map.nii.gz")

nii_t1 = nib.Nifti1Image(t1, None, nii_input.header)
nii_t1.update_header()
nii_t1.to_filename(FOLDER_OUTPUT + "/t1_map.nii.gz")

# quick visualization
#import matplotlib.pyplot as plt
#nii_vis = nib.load(FOLDER_OUTPUT + "/t1_map.nii.gz")
#data = nii_vis.get_fdata()
#fig = plt.imshow(data[:,:,12])
print("END SCRIPT 10")

