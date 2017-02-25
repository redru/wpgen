import argparse
import sys
import zipfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlretrieve
from mysql.connector.errors import ProgrammingError

import mysql.connector

if 'raw_input' in locals():
    input = raw_input

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

_downloaddir = "./wprepo/wordpress-"
_wpurl = "https://wordpress.org/wordpress-"

def download_wp_version(version):
    def dlProgress(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            sys.stdout.write("\rDownload wp-{version}: {percent}%".format(version=version, percent=str(int(percent))))
            if readsofar >= totalsize: # near the end
                sys.stdout.write(bcolors.OKGREEN + " SUCCESS\n" + "\x1b[0m")
        else: # total size is unknown
            sys.stderr.write("read %d\n" % (readsofar,))

        sys.stdout.flush()

    try:
        urlretrieve(_wpurl + version + ".zip", _downloaddir + version + ".zip", reporthook=dlProgress)
    except HTTPError:
        print("Version '" + version + "' does not exists.")
        sys.exit(0)


def unzip_wp_version(version, path):
    wp_zippedfolder = Path(_downloaddir + version + ".zip")
    if not wp_zippedfolder.is_file():
        if input("Wordpress " + version + " has not been downloaded yet. Do you want to download? ").lower() in ["y", "s"]:
            download_wp_version(version)
        else:
            print("Wordpress installation aborted")
            sys.exit(0)
        
    zip_ref = zipfile.ZipFile(_downloaddir + version + ".zip", 'r')
    uncompress_size = sum((file.file_size for file in zip_ref.infolist()))
    extracted_size = 0
    for file in zip_ref.infolist():
        extracted_size += file.file_size
        zip_ref.extract(file, path=path)
        sys.stdout.write("\rExtract wp-{version}: {percent}%".format(version=version, percent=str(int(extracted_size * 100 / uncompress_size))))
        sys.stdout.flush()

    sys.stdout.write(bcolors.OKGREEN + " SUCCESS\n" + "\x1b[0m")


def wpconfig_process(path):
    connected = False

    while not connected:
        dbname = input("Inserire il nome del database (wordpress): ") or "wordpress"
        dbuser = input("Inserire l'utente del database (wp): ") or "wp"
        dbpassword = input("Inserire la password del database (password): ") or "password"
        dbhost = input("Inserire host del database (localhost): ") or "localhost"

        sampleconfig = open(path + "/wordpress/wp-config-sample.php", "r")
        config = sampleconfig.read()
        config = config.replace('database_name_here', dbname, 1).replace('username_here', dbuser, 1).replace('password_here', dbpassword, 1).replace('localhost', dbhost, 1)
        
        wpconfig = open(path + "/wordpress/wp-config.php", "w")
        wpconfig.write(config)

        sampleconfig.close()
        wpconfig.close()

        try:
            cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=dbhost, database=dbname)
            connected = True
        except ProgrammingError:
            print(bcolors.FAIL + "Failed connecting to database. Try again..." + "\x1b[0m")

    print(bcolors.OKGREEN + "Configuration completed. Your wordpress folder is ready at " + bcolors.WARNING + "'" + path + "/wordpress" + "\x1b[0m" + "'")


def init_arguments():
    parser = argparse.ArgumentParser(description='Wordpress generator manual.')

    parser.add_argument('params', metavar='P', type=str, nargs='+',
                        help='list of wordpress generator parameters')

    parser.add_argument('-d', '--download', dest='_download', action='store_const',
                        const=download_wp_version, help='set if you want to download the target wordpress version')

    parser.add_argument('-e', '--extract', dest='_extract', action='store_const',
                        const=unzip_wp_version, help='set if you want to extract the target wordpress version')

    return parser.parse_args()


args = init_arguments()

if args._download and len(args.params) >= 1:
    args._download(args.params[0])

if args._extract and len(args.params) >= 2:
    args._extract(args.params[0], args.params[1])

wpconfig_process(args.params[1])
