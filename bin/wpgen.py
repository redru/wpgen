import argparse
import urllib.request
import sys

_downloaddir = "./wprepo/wordpress-"
_wpurl = "https://wordpress.org/wordpress-"

# print(urllib.request.urlopen(_wpurl).read())
# response = urllib.request.urlretrieve(_wpurl, _downloaddir + "/wordpress-4.7.2.zip")

def download_wp_version(version):
    def dlProgress(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\rDownload wp-{version}: {percent}".format(version=version, percent=str(percent)[0:4])
            sys.stderr.write(s)
            if readsofar >= totalsize: # near the end
                sys.stderr.write("\n")
        else: # total size is unknown
            sys.stderr.write("read %d\n" % (readsofar,))

    try:
        urllib.request.urlretrieve(_wpurl + version + ".zip", _downloaddir + version + ".zip", reporthook=dlProgress)
    except urllib.error.HTTPError:
        print("Version '" + version + "' does not exists.")


def init_arguments():
    parser = argparse.ArgumentParser(description='Wordpress generator manual.')

    parser.add_argument('params', metavar='P', type=str, nargs='+',
                        help='an integer for the accumulator')

    parser.add_argument('-d', '--download', dest='_download', action='store_const',
                        const=download_wp_version, help='sum the integers (default: find the max)')

    return parser.parse_args()


args = init_arguments()

if args._download:
    args._download(args.params[0])