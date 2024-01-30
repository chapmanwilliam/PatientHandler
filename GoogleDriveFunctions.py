from GoogleDrive import *
from SQL import *
patients_folderID="17dYiXTP4BN60Rcx2TGiSVUJ76MaBsya6"
new_letterID='1ZbbDezlUO8Due_bWFw3uUBUnOjSj6pYRLQaT2AWtd84'
import webbrowser

from pathlib import Path

def getFolderNamePatient(patientID):
    print('Getting folder name patient...')
    folder_name=None
    result = executeScript(
        f"SELECT Second_Name || ', ' || First_name AS 'f_name' FROM PATIENTS WHERE ROWID={patientID}")
    if result:
        rows = result.fetchone()
        if rows:
            folder_name = rows['f_name'] + " {" + str(patientID).zfill(6) + "}"
    return folder_name
def createPatientFolder(folder_name):
    print('Creating patient folder name...')
    if not folder_name: return
    service = get_gdrive_service()
    # folder details we want to make
    folder_metadata = {
        "name": folder_name,
        "parents": [patients_folderID],
        "mimeType": "application/vnd.google-apps.folder"
    }
    # create the folder
    file = service.files().create(body=folder_metadata, fields="id").execute()
    # get the folder id
    folder_id = file.get("id")
    print ("Folder created: ", folder_id, folder_name)
    return folder_id
    pass
def doesFolderExistOnDrive(folderID):
    print('Checking if folder exists on drive already...')
    service = get_gdrive_service()
    try:
        res = service.files().get(fileId=folderID, fields="id, name, parents").execute()
        print("Folder exists on drive")
        return True
    except:
        print('Folder does not exist on drive')
        return False
def doesPatientHaveFolderIDAlreadyinDB(patientID):
    print('Checking if folder id provided on DB...')
    result=executeScript(f"SELECT folderID FROM PATIENTS WHERE ROWID={patientID}")
    if result:
        row=result.fetchone()
        if row:
            if row['folderID']==None:
                print("It does not have folder on DB")
                return False
            else:
                print("It does have folder on DB: ", row['folderID'])
                return True
def doesPatientHaveFolder(patientID):
    print('Checking if folderID on DB and, if so, if it exists on drive...')
    #Checks if there is folderID on database. Then it checks if this exists on Google Drive
    if doesPatientHaveFolderIDAlreadyinDB(patientID):
        folder_id=getFolderIDPatient(patientID)
        if doesFolderExistOnDrive(folder_id):
            print('It does have folder on DB and on Drive')
            return True
    print('It does not have folder on DB or on Drive')
    return False
def createPatientFolderFromID(patientID):
    print('Creating patient folder if it does not exist already...')
    #the name of the folder should be:
    # Second_Name, First_Name {patientID}
    #creates patient folder if folder does not exist already
    if not doesPatientHaveFolder(patientID):
        folder_name=getFolderNamePatient(patientID)
        if not folder_name: return
        folder_id=createPatientFolder(folder_name)
        result=executeScript(f"UPDATE PATIENTS SET folderID=\'{folder_id}\' WHERE ROWID={patientID}")
        if result: print('Folder created: ', folder_name, folder_id)
        return folder_id
    print('No folder created')
    return None

def getFolderIDPatient(patientID):
    print('Getting folder id of patient from DB')
    result=executeScript(f"SELECT folderID FROM PATIENTS WHERE ROWID={patientID}")
    if result:
        row=result.fetchone()
        if row:
            if row['folderID']==None:
                print('No folder ID')
                return False
            else:
                print('Folder ID is: ', row['folderID'])
                return row['folderID']

def saveFileToPatientFolder(patientID,file):
    print('Saving file to patient folder...')
    #TODO need a progress bar for upload timings - can it not do it in background using a thread?
    if patientID==-1: return
    createPatientFolderFromID(patientID) #creates folder if doesn't exist
    folder_id=getFolderIDPatient(patientID)
    if folder_id is None: return
    service = get_gdrive_service()
    file_metadata = {
        "name": file,
        "parents": [folder_id]
    }
    #name new file
    stem=Path(file).stem
    ext=Path(file).suffix
    dt=getTimeStamp()
    id="{"+str(patientID).zfill(6) + "}"
    new_name=dt + " " + stem + " " + id + ext
    # upload
    media = MediaFileUpload(file, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("File created, id:", file, file.get("id"))
    body = {'name': new_name}
    return service.files().update(fileId=file.get('id'), body=body).execute()

def createAGoogleDocFile(patientID):
    docs_service=get_gocs_service()
    drive_service=get_gdrive_service()
    # Retrieve the documents contents from the Docs service.
    folder_id=getFolderIDPatient(patientID)
    if not folder_id: return
    folder_metadata = {
        "name": "test this two",
        "parents": [folder_id],
        "mimeType": "application/vnd.google-apps.document"
    }
    file = drive_service.files().create(body=folder_metadata, fields="id, title").execute()
    file_id=file.get('id')
    print(file.get('id'))
    # Text insertion
    text = "Some sample text. VERY HUGE CHARACTERS. CamelCaseSentence."
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': text
            }
        }
    ]
    result = docs_service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()


def replace_named_range(service, document_id, range_name, new_text):
    """Replaces the text in existing named ranges."""

    # Determine the length of the replacement text, as UTF-16 code units.
    # https://developers.google.com/docs/api/concepts/structure#start_and_end_index
    new_text_len = len(new_text.encode('utf-16-le')) / 2

    # Fetch the document to determine the current indexes of the named ranges.
    document = service.documents().get(documentId=document_id).execute()

    # Find the matching named ranges.
    named_range_list = document.get('namedRanges', {}).get(range_name)
    if not named_range_list:
        raise Exception('The named range is no longer present in the document.')

    # Determine all the ranges of text to be removed, and at which indices the
    # replacement text should be inserted.
    all_ranges = []
    insert_at = {}
    for named_range in named_range_list.get('namedRanges'):
        ranges = named_range.get('ranges')
        all_ranges.extend(ranges)
        # Most named ranges only contain one range of text, but it's possible
        # for it to be split into multiple ranges by user edits in the document.
        # The replacement text should only be inserted at the start of the first
        # range.
        insert_at[ranges[0].get('startIndex')] = True

    # Sort the list of ranges by startIndex, in descending order.
    all_ranges.sort(key=lambda r: r.get('startIndex'), reverse=True)

    # Create a sequence of requests for each range.
    requests = []
    for r in all_ranges:
        # Delete all the content in the existing range.
        requests.append({
            'deleteContentRange': {
                'range': r
            }
        })

        segment_id = r.get('segmentId')
        start = r.get('startIndex')
        if insert_at[start]:
            # Insert the replacement text.
            requests.append({
                'insertText': {
                    'location': {
                        'segmentId': segment_id,
                        'index': start
                    },
                    'text': new_text
                }
            })
            # Re-create the named range on the new text.
            requests.append({
                'createNamedRange': {
                    'name': range_name,
                    'range': {
                        'segmentId': segment_id,
                        'startIndex': start,
                        'endIndex': start + new_text_len
                    }
                }
            })

    # Make a batchUpdate request to apply the changes, ensuring the document
    # hasn't changed since we fetched it.
    body = {
        'requests': requests,
        'writeControl': {
            'requiredRevisionId': document.get('revisionId')
        }
    }
    service.documents().batchUpdate(documentId=document_id, body=body).execute()



def copy(document_id,patientID):
    drive_service=get_gdrive_service()
    createPatientFolderFromID(patientID) #creates folder if doesn't exist
    folder_id=getFolderIDPatient(patientID)
    dt=getTimeStamp()
    id='{'+str(patientID).zfill(6)+'}'
    copy_title = dt + ' ' + 'patient letter ' + id
    body = {
        'name': copy_title,
        'parents':[folder_id]
    }
    drive_response = drive_service.files().copy(
        fileId=document_id, body=body).execute()
    document_copy_id = drive_response.get('id')
    return document_copy_id, copy_title

def search_and_replace(document_id, contents):
    #where contents is dictionary of tags and replacement text
    if not document_id: return None
    requests=[]
    for key,value in contents.items():
        a={'replaceAllText': {'containsText': {'text': '{{'+key+'}}', 'matchCase': 'true'},
                            'replaceText': value}}
        requests.append(a)

    docs_service=get_gocs_service()

    result = docs_service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()
    return document_id
def getDocumentLink(document_id):
    if document_id:
        lnk="https://docs.google.com/document/d/"
        lnk+=document_id
        lnk+='/edit?usp=drive_link'
        return lnk
    return None

def getFolderLink(folder_id):
    if folder_id:
        lnk="https://docs.google.com/drive/folders/"
        lnk+=folder_id
        lnk+='?ddrp=1#'
        return lnk
    return None

def showFolder(patient_id):
    #show folder of the patient
    createPatientFolderFromID(patient_id)
    folder_id=getFolderIDPatient(patient_id)
    if folder_id: webbrowser.open_new_tab(getFolderLink(folder_id)) #display link
def add_correspondence_to_DB(patientID,document_id, document_title):
    sql=f"INSERT INTO CORRESPONDENCE (Date, Title, PATIENT_ID, Document_ID) VALUES ({addQuotes(getTimeStamp())},{addQuotes(document_title)},{patientID},{addQuotes(document_id)})"
    executeScript(sql)


def new_letter_patient(patientID, contents):
    #where contents is disctionary of tags and replacing content
    document_id, document_title=copy(new_letterID, patientID) #copy template
    search_and_replace(document_id,contents) #fill template
    add_correspondence_to_DB(patientID,document_id,document_title) #add to database
    webbrowser.open_new_tab(getDocumentLink(document_id)) #display link

#new_letter_patient(2,None)