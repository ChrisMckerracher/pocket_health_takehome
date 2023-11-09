# DICOM Server
# Running and Testing
## Testing and Running locally
**Note** Currently this app doesn't support Windows, due to a difference in filesystem layout compared to POSIX environments

We need to first install the requirements as listed in setup.py. To do this, you can run the following:
```
python setup.py egg_info
pip install -r *.egg-info/requires.txt
rm -rf *.egg-info/

```

I didn't include any dcm files for testing. Mainly I wasn't sure if the person providing the dcm files for the sake of the takehome would be comfortable with their files being online. In order to remedy this, download a dcm, and put it in assets. The test file local_dicom_file_repository_test needs to be updated with the name of the dcm file, as well as its *expected* byte length. You can obtain its byte length by running:
```
wc -c assets/*.dcm
```

once this is done, you can run all tests via:  
```
pytest test
```

and similarly you can run the server via:  
```
uvicorn main:app
```

## Running the server via docker
From the docker container, I provided a docker-compose file which will allow you to start the server with a port mapping such that the localhost's 8000 port will map to the containers server port

## Hitting endpoints via postman
Import the provided postman collection, which gives some high level instructions on how to hit endpoints on the server. It also provides high level step-by-step instructions on how to obtain an auth token for local testing

# Api Overview
## POST File


`POST /patient/{patient_id}/dicom -> The uuid id of the uploaded file`

> Body parameter

```
body: FormData file upload, with specified content-type equlling application/dicom

```

### Parameters

|Name|In|Type|Description|
|---|---|---|---|
|patient_id|path|string|patient id|
|access-token|header|string|Access token associated with the user|
|body|body|Form Data|Form Data file upload|

### Responses

|Status|Description|
|---|---|
|200|Successful Response|
|401|Unauthorized|


## GET a Dicom Tag


`GET /patient/{patient_id}/dicom/{dicom_id}/tag/{header_tag} -> A simplified Dicom Tag`

### Parameters

|Name|In|Type|Description|
|---|---|---|---|
|patient_id|path|string|patient id|
|dicom_id|path|string|uuid of the dicom file|
|header_tag|path|string|The groupId+element_id of the tag. Ex: 00081140 would map to 0008,1140|
|access-token|header|string|Access token associated with the user|

### Responses

|Status|Description|
|---|---|
|200|Successful Response|
|401|Unauthorized|
|404|Not Found|
|422|Validation Error|


## GET File


`GET /patient/{patient_id}/dicom/{dicom_id} - A file relevant to the provided content type`

### Parameters

|Name|In|Type|Description|
|---|---|---|---|
|patient_id|path|string|patient id|
|dicom_id|path|string|uuid of the dicom file|
|content-type|header|string|Either application/dicom, or image/png are curently supported|
|access-token|header|string|Access token associated with the user|

### Responses

|Status|Description|
|---|---|
|200|Successful Response|
|401|Unauthorized|
|404|Not Found|
|422|Validation Error|

# System Design

## SQL vs Local Storage
At a high level, the simplest design for this could have been to simply save files which are submitted. When getting tags, a file could be read using pydicom, and the relevant tag could be returned this way. I choose not to go this route for a few reasons:
1. Without a SQL component at all, the design would be limitted to saving files, and retrieving info either by name, or by a pre-known id.
2. Dicoms can have the same file name, we want to avoid collisions, and thus want a way to map a unique_id to the original file name.
3. Dicoms are likely going to be submitted by patients. In other words, there's a relationship between the entity 'user' and the entity 'file'. (There's a few more examples of this)
4. Designing a relational entity-oriented design will allow the server to scale more simply with new product requirements. Ex: Patients probably want to have some way to list all their files uploaded. With the simplest possible design, you'd have to refactor and add lots of code to account for this. With SQL, if your Dicom table already has a patient_id relationship, you can essentially already support this
5. Storing certain data in a table allows for faster lookups for key queries. For example, we probably don't want to have to scan through a file to find a relevant Tag, when we can store those tags directly. Furthermore, if the app scales past having files on local storage, you want to avoid pulling from s3(or similar object store) if there's a cache-miss on the file locally, just to get a tag.
6. Lastly, by normalizing some data(specific name out of a spefied (group_id, element_id) tag, you can reduce data load requirements over something like a no-sql db or json object store

In saying that, I maintained an aspect of storing files locally alongside the sql tables. The primary reason for this was
1. Uncertain future business requirements. Despite my research, I would be foolish to assume I have a total understanding of Dicom in 2 days. As such, I can't be sure if there's future patient needs that wouldn't be satisfied by me storing the data in SQL. Ultimately any design has to make assumptions, including my own. Whereas, the original file is the Source-of-Truth
2. Similarly, being able to maintain the original file means that even if we run into a situation where say, my tag-extraction-to-sql-table code is bugged, we can fix the bug and simply run a job to re-load older dcm files into sql

## Entity / SQL design
To ignore the term 'tag' for a bit. We essentially have 'DataItems', which more or less(among other things I will omit here) have some design as followed:  
**DataSet = List[DataTag]  
accepted_types = Union[str, int, float, bytes,...,etc,etc]**
|Field|Type|Description|
|---|---|---|
|group_id|int|group id|
|element_id|int|element id|
|VM|int|1-or-more|
|VR|string or enum|Essentially tells you the 'kind' of data of the value|
|value|Union(accepted_types, List[accepted_types], List[DataSet])|The value of the data Item|  

In other words, data items are members of datasets, which themselves can hold sequences(ie an array or list) of other datasets. In the context of a 'Tag', a Tag can be thought of as a dataitem without an actual parent dataset. In otherwords, a Tag is the root DataItem among a recursive structure of dataItems.  

Of course, this recursive structure only happens if you have VR=SQ, and its child datasets having data items where VR=SQ, and so on and so forth.  

Wrapping my head around this relationship and understanding how to ultimately map this recursive relationship ended up being a lot of fun. At a high level here is what a somewhat normalized SQL Table design can look like to account for this:


![image](https://github.com/ChrisMckerracher/pocket_health_takehome/assets/5733725/9df40a74-7079-4368-8e27-a2212682d97d) 

I denormalized the dataset table and put that into datasetitem, as it seemed reundant. This in otherwords giving a FK-PK recursive relationship with datasetitem and itself.

Constructing a recursive tag then was essentially selecting from datasetitem the relevant tags with an associated tag_id. This would give a flat list of all the datasetitems representing a Tag. Navigating this list grouped by dataset_ids, and traversing through it in a tree-like manner through parent_datasetitem_ids allowed you to take that flat list and construct a DataSetItem entity.  


To skim over it quickly as well, the Dicom table also has a file_name column to represent location of the file. I also added a ImageFile table which allowed you to find the location of a png(or any future image files we'd want to support). The reason for this being, that you could essentially construct the png once, only if the ImageFile table indicated there was no png file cached, and could simply repull this file on future requests. This seemed somewhat preferable to pulling the original dicom and creating an image file on every request. This was chosen over storing raw image bytes as a binary/blob/etc in a table, as there seems to be a lot of caveats of reading binary data like this and converting it in to an Image, according to pydicom's source code as well as documentation.

## Zero-trust lite aka Auth
I originally asked Nilay if I can assume that that this service isn't directly customer facing. My original intention was that, if I assume it is not, I can assume that authorization was 'terminated'(by this i mean in the same way services terminate ssl early on in the pipeline), and that the caller was 'trusted'. I thought more about this howver, and thought that it shouldn't matter. I don't think it's a stretch to say that Dicom files hold very sennsitive and personal data. People need to trust us(as in whatever orgnization storing it) to ensure no one else is accessing that. That means that it shouldn't matter who the caller is. Someone's Dicom's files shouldn't be able to be leaked just because an attacker or rogue-employee 'broke into' the relevant network and was able to do raw http requests on anyone they chose.  

To address, I implemented basic authorization via jwt tokens. For the sake of a takehome I simplified this a little such that we're using a symmetric key hardcoded in one of the python files, which I only did for readability and for the sake of the takehome. You can only make read and write requests pertaining to a patient provided that your jwt claim(That sounds fancier than one it really is. At the moment, the jwt contains a patient_id) matches the patient_id.  

I currently use a dev-only point to generate a basic jwt for server testing.  

In future designs, you'd want more robust jwt support, including probbaly a jwks service somewhere, with rotating keys and auth tokens that actually can expire!

## Things I'd like to change in the future
1. Some of my ORM design is limitted by sqlite support. I'd like to be able to support more native structures like making the value column in dataset_item support actual Array types. Currently I have to convert things to a string, and then convert that string to a relevant data type depending on VR+VM
2. I'd like to add error logging, as right now a sql error just bubbles up to a 5xx to the user, and some info in stdout. I wasn't too concerned about this for the context of a take home, but having richer logs would make future debugging simpler
3. Possibly using a job queue. Right now posting a file, which involves essentially some basic ETL into SQL, as well as writing to a local file completes, in my rough opinion, in a reasonable time. As more requests come in, we may want our SLA for web requests to be super small. Similarly, if files aren't writing locally, we probably want to do that async
4. Right now DicomTag entities return their group and element ids as their int representation, but the api accepts their hex representation, which could be confusing
