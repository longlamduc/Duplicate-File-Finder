#!/usr/bin/env python3
import argparse
from os import walk, access, R_OK
from os.path import join, getsize, islink, isdir
from hashlib import md5
from json import loads, dumps


def parse_argu():
    '''
    get the root directory before scanning
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', action='store')
    args = parser.parse_args()
    return args.path

def scan_files(path):
    '''
    get all the file in the root directory
    '''
    list_file = []
    for root, dirs, files in walk(path):
        for file in files:
            path = join(root, file)
            if not islink(path) and access(path, R_OK):
                # only get file that has no link and readable
                list_file.append(path)
    return list_file

def group_files_by_size(list_file_paths):
    '''
    group files into smaller groups with same size
    '''
    group = {}
    result = []
    for path in list_file_paths:
        size = getsize(path)
        if size not in group:
            group[size] = [path]
        elif size > 0:  # ignore file with no content
            group[size].append(path)
    for key in sorted(group.keys()):
        result.append(group[key])
    return result

def get_file_checksum(path):
    '''
    get checksum of the file
    '''
    hash_md5 = md5()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def group_files_by_checksum(list_file_paths):
    '''
    group files into smaller groups that have the same checksum(content)
    '''
    group = {}
    result = []
    for path in list_file_paths:
        checksum = get_file_checksum(path)
        if checksum not in group:
            group[checksum] = [path]
        else:
            group[checksum].append(path)
    for key in group.keys():
        result.append(group[key])
    return result

def find_duplicate_files(list_file_paths):
    '''
    find all the duplicate files in list_file_paths by checking checksum
    '''
    result = []
    group_file_paths = group_files_by_size(list_file_paths)
    for group in group_file_paths:
        group_checksum = group_files_by_checksum(group)
        for duplicate in group_checksum:
            if len(duplicate) >= 2:
                result.append(duplicate)
    return result

def check_content(file1, file2):
    '''
    check if two files have the same content
    '''
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            cmp1 = f1.read(2048)
            cmp2 = f2.read(2048)
            if cmp1 != cmp2:
                return False
            elif not cmp1:
                return True

def group_file_by_content(list_file_paths):
    '''
    divide all path file into groups that have same content
    '''
    result = []
    for file in list_file_paths:
        check = False
        for group in result:
            if check_content(file, group[0]):
                check = True
                group.append(file)
        if not check:
            result.append([file])
    return result

def find_duplicate_files_bonus(list_file_paths):
    '''
    find all duplicate files in list_file_paths by checking content
    '''
    result = []
    group_file_paths = group_files_by_size(list_file_paths)
    for group_size in group_file_paths:
        group_content = group_file_by_content(group_size)
        for group in group_content:
            if len(group) >= 2:
                result.append(group)
    return result


def process(method):
    '''
    return result
    '''
    path = parse_argu()
    if path is None or not isdir(path):
        exit('Path not found')
    if method == 'core':
        return find_duplicate_files(scan_files(path))
    else:
        return find_duplicate_files_bonus(scan_files(path))


if __name__ == "__main__":
    print(dumps(process('bonus'), indent=4))
