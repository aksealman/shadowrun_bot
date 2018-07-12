#!/usr/bin/python3
import os
import consts
#TODO default values for configuration files
def config_parse():
    key_value={}
    with open(consts.config_path, 'r') as config_file:
        for line in config_file:
            #Ignore any lines starting with a #
            if line[0] == '#':
                continue
            else:
                line_split = line.rstrip().split("=")
                key_value[line_split[0]] = line_split[1]
    return key_value
