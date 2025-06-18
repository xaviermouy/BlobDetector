# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 15:42:59 2022

@author: xavier.mouy
"""

import os
import faulthandler
import pandas as pd
import ecosound.core.tools
from ecosound.core.metadata import DeploymentInfo
from ecosound.core.audiotools import Sound
from ecosound.core.measurement import Measurement
import ecosound
#import tools
import detection
import time
import dask
from dask.distributed import Client, progress
from dask import config as cfg
from datetime import datetime
import shutil
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
faulthandler.enable()

if __name__ == '__main__':

    # #############################################################################
    # input parameters ############################################################

    #in_dir = r"C:\Users\xavier.mouy\Documents\Projects\2025_Galapagos\test_PAMGuard\Pamguard Files\DOLPHINS DATASET 1"
    in_dir = r'F:\GalapagosDataAll\subset'
    out_dir = r"C:\Users\xavier.mouy\Desktop\Galapagos_blob_detector"
    deployment_info_file = r"C:\Users\xavier.mouy\Documents\GitHub\Blob_generic_detector\deployment_info.csv"  # Deployment metadata
    detection_config_file = r"C:\Users\xavier.mouy\Documents\GitHub\Blob_generic_detector\config_whistles.yaml"  # detection parameters
    Time_of_day_start = 0
    Time_of_day_end = 24
    date_deployment = datetime(1900,11,25,4,8)
    date_retrieval = datetime(2223,11,25,4,18)



    # #############################################################################
    # #############################################################################

    # create tmp folder
    #tmp_dir = os.path.join(out_dir,'tmp')
    #if os.path.isdir(tmp_dir) == False:
    #    os.mkdir(tmp_dir)

    # load deployment metadata
    Deployment = DeploymentInfo()
    Deployment.read(deployment_info_file)

    # load detection parameters
    detection_config = ecosound.core.tools.read_yaml(detection_config_file)

    # find all ausio files to process in the in_dir folder
    files = ecosound.core.tools.list_files(
        in_dir,
        detection_config['AUDIO']['extension'],
        recursive=False,
        case_sensitive=True,
    )

    # Process each audio file
    nfiles = len(files)
    for idx, in_file in enumerate(files):
        print(idx + 1, "/", nfiles, os.path.split(in_file)[1])
        out_file = os.path.join(out_dir, os.path.split(in_file)[1])
        if os.path.exists(out_file + ".nc") is False:
            file_datetime = ecosound.core.tools.filename_to_datetime(out_file)[0]
            file_tod = file_datetime.hour
            #only process files when intrument is in water
            if (file_datetime > date_deployment) and (file_datetime < date_retrieval):
                # only process if camera is ON (during day time)
                if (file_tod > Time_of_day_start) or (file_tod < Time_of_day_end):
                    try:
                        # # create file folder in the tmp dir
                        # tmp_dir_file = os.path.join(tmp_dir, os.path.split(in_file)[1])
                        # if os.path.isdir(tmp_dir_file) == False:
                        #     os.mkdir(tmp_dir_file)

                        # run detector on selected channel
                        print("Detection in progress...")
                        tic = time.perf_counter()
                        detections = detection.run_detector(
                            in_file,
                            detection_config['AUDIO']['channel'],
                            detection_config,
                            deployment_file=deployment_info_file,
                        )

                        # delete first 4 sec to avoid picking up ST calibration tones
                        detections.filter('time_min_offset > 4', inplace=True)

                        detections.data.audio_channel = detections.data.audio_channel.astype(int)
                        detections.insert_values(label_class=detection_config['DETECTOR']['label'])
                        toc = time.perf_counter()
                        print(f"Elapsed time: {toc - tic:0.4f} seconds")
                        print("-> " + str(len(detections)) + " detections found.")

                        # save results as csv and netcdf file:
                        print("Saving results...")
                        detections.to_netcdf(out_file)
                        detections.to_raven(out_dir)
                        print(" ")

                        # delete tmp folder and files
                        #os.rmdir(tmp_dir_file)
                        #shutil.rmtree(tmp_dir_file)
                    except BaseException as e: 
                        print(e)
                        print('Processing failed...')
                else:
                    print("Time of the file outside of the analysis effort. File not processed.")
            else:
                print("File outside of deployment time. File not processed.")
        else:
            print("File already processed")

    print("Processing complete!")
