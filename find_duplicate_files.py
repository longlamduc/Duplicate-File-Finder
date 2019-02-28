#!/usr/bin/env python3

import argparse
from os import walk, access, R_OK
from os.path import join, getsize, islink, isdir
from hashlib import md5
from json import loads, dumps


class duplicate_files_finder:
    '''
    to find all the duplicate files
    '''
    def parse_argu(self):
        '''
        to get the root directory before scanning
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', action='store')
        args = parser.parse_args()
        return args.path

    def scan_files(self, path):
        '''
        to get all the file in the root directory
        '''
        list_file = []
        for root, dirs, files in walk(path):
            for file in files:
                path = join(root, file)
                if not islink(path) and access(path, R_OK):
                    list_file.append(path)
        return list_file

    def group_files_by_size(self, list_file_paths):
        '''
        to group files into smaller groups with same size
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

    def get_file_checksum(self, path):
        '''
        to get checksum of the file
        '''
        hash_md5 = md5()
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def group_files_by_checksum(self, list_file_paths):
        '''
        to group files into smaller groups that have the same checksum(content)
        '''
        group = {}
        result = []
        for path in list_file_paths:
            checksum = self.get_file_checksum(path)
            if checksum not in group:
                group[checksum] = [path]
            else:
                group[checksum].append(path)
        for key in group.keys():
            result.append(group[key])
        return result

    def find_duplicate_files(self, list_file_paths):
        '''
        to find all the duplicate files from the list files
        '''
        result = []
        group_file_paths = self.group_files_by_size(list_file_paths)
        for group in group_file_paths:
            group_checksum = self.group_files_by_checksum(group)
            for duplicate in group_checksum:
                if len(duplicate) >= 2:
                    result.append(duplicate)
        return result

    def process(self):
        '''
        to return result
        '''
        path = self.parse_argu()
        if path is None or not isdir(path):
            exit('Path not found')
        return self.find_duplicate_files(self.scan_files())


if __name__ == "__main__":
    finder = duplicate_files_finder()
    print(dumps(finder.process(), indent=4))
