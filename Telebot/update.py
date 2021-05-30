import requests
import zipfile
def up():
    url = 'https://data.gov.ua/dataset/cc13621d-d6fa-46ea-ad86-f845bb1f4bbc/resource/3cfa4627-9505-435b-8fb5-1ccef979099a/download'
    r = requests.get(url, allow_redirects=True)
    open('reestrsubsidii.zip', 'wb').write(r.content)

            
    fantasy_zip = zipfile.ZipFile('F:\\KP\\reestrsubsidii.zip')
    fantasy_zip.extractall('F:\\KP')
    
    fantasy_zip.close()