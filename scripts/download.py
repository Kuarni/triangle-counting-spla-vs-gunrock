import os
import gzip
import urllib.request

def download():
    FOLDER_NAME = 'graphs'

    GRAPHS = {
        'loc-brightkite_edges.txt': 'http://snap.stanford.edu/data/loc-brightkite_edges.txt.gz',
        'amazon0302.txt': 'https://snap.stanford.edu/data/amazon0302.txt.gz',
        'roadNet-PA.txt': 'https://snap.stanford.edu/data/roadNet-PA.txt.gz',
        'amazon0505.txt': 'https://snap.stanford.edu/data/amazon0505.txt.gz',
        'soc-Epinions1.txt': 'https://snap.stanford.edu/data/soc-Epinions1.txt.gz',
        'email-EuAll.txt': 'https://snap.stanford.edu/data/email-EuAll.txt.gz',
        'loc-gowalla_edges.txt': 'https://snap.stanford.edu/data/loc-gowalla_edges.txt.gz',
        'soc-Slashdot0902.txt': 'https://snap.stanford.edu/data/soc-Slashdot0902.txt.gz',
        'soc-Slashdot0811.txt': 'https://snap.stanford.edu/data/soc-Slashdot0811.txt.gz',
    }

    os.makedirs(FOLDER_NAME, exist_ok=True)

    for filename, url in GRAPHS.items():
        output_path = os.path.join(FOLDER_NAME, filename)

        if not os.path.exists(output_path):
            print(f"Downloading {filename}...")
            gz_path = os.path.join(FOLDER_NAME, f"{filename}.gz")

            urllib.request.urlretrieve(url, gz_path)

            with gzip.open(gz_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())

            os.remove(gz_path)
            print(f"Downloaded and extracted {filename}")
        else:
            print(f"{filename} already exists")

if (__name__ == "__main__"):
    download()
