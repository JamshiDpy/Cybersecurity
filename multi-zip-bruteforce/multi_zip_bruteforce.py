import os
import subprocess
import argparse
import threading

class ZipScanner:
    def __init__(self, zip_dir):
        self.zip_dir = zip_dir if zip_dir else os.getcwd()
        self.archive_files = []

    def scan_archives(self):
        archive_exts = ['.zip', '.gz']
        for root, dirs, files in os.walk(self.zip_dir):
            for file in files:
                for ext in archive_exts:
                    if file.endswith(ext):
                        full_path = os.path.join(root, file)
                        self.archive_files.append(full_path)
                        break
        return self.archive_files

class ZipCracker:
    def __init__(self, zip_path, wordlists_path):
        self.zip_path = zip_path
        self.wordlists_path = wordlists_path


    def zip(self):
        with open(self.wordlists_path, 'r') as wordlists:
            for password in wordlists:
                password = password.strip()
                result = subprocess.run(
                    ['unzip', '-P', password, '-t', self.zip_path],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL
                        )
                if result.returncode == 0:
                    zip_file_name = os.path.basename(self.zip_path)
                    print(f"[+] Password found: {password} for {zip_file_name}")
                    return
            print(f"[-] Password not found for {self.zip_path}")

    def gzipped(self):
        with open(self.wordlists_path, 'r') as wordlists:
            for password in wordlists:
                password = password.strip()
                result = subprocess.run(
                    ['gunzip', '-c', self.zip_path],
                    input=password.encode('utf-8'),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                    )
                if result.returncode == 0:
                    zip_file_name = os.path.basename(self.zip_path)
                    print(f"[+] Password found: {password} for {zip_file_name}")
                    return
            print(f"[-] Password not found for {self.zip_path}")

    def try_crack(self):
        if self.zip_path.endswith('.zip'):
            self.zip()
        elif self.zip_path.endswith('.gz'):
            self.gzipped()
        else:
            print(f"[-] Unsupported archive format: {self.zip_path}")


class ThreadingZipCracker:
    def __init__(self, file_paths, wordlists_path):
        self.file_paths = file_paths
        self.wordlists_path = wordlists_path

    def thread_zip_cracker(self):
        threads = []
        for file in self.file_paths:
            file_name = os.path.basename(file)
            print(f"\n[+] Starting thread for {file_name}\n")
            zip_cracker = ZipCracker(zip_path=file, wordlists_path=self.wordlists_path)
            thread = threading.Thread(target=zip_cracker.try_crack)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

def run(zip_path, wordlist_path):
    scanner = ZipScanner(zip_path)
    archive_files = scanner.scan_archives()
    count = 1
    for file in archive_files:
        print(f"[+] {count} Found archive: {file}")
        count += 1
    zip_cracker = ThreadingZipCracker(archive_files, wordlist_path)
    zip_cracker.thread_zip_cracker()


def main():
    parser = argparse.ArgumentParser(description="Cracking passwords for zip files.")
    parser.add_argument(
        "-z", "--zip_path",
        type=str,
        required=False,
        help="Directory containing zip files (optional, default: current directory"
    )

    parser.add_argument(
        "-w", "--wordlist_path",
        type=str,
        required=True,
        help="Path to wordlist file"
    )

    run(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
