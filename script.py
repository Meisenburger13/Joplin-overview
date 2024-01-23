import requests

# creates an overview named "<notebook_name> Overview" for all notes in a specified notebook.
# creates a table with defined properties and links to each note.
# the properties must be at the top of each note without any empty lines or lines without the specified separator in between.

# fill these out
token = ""  # authorisation token — you can find it under settings → web clipper
port = "41184"  # port number on which the web clipper is running — can be found in the same location as above, default is 41184
source_notebook = ""  # id of notebook, for which the overview will be created (every note in this notebook will be one row in the overview)
dest_notebook = ""  # id of notebook where overview will be created
Properties = ["Prop1", "Prop2", "Prop3"]  # names of properties in the order in which they will be in the overview
separator = ": "  # separator between property and value


# each page will be one row in the final overview
class Page:
    def __init__(self, id, title, properties):
        self.id = id
        self.title = title
        self.properties = properties

def makePage(note):
    id = note["id"]
    title = note["title"]
    values = {}
    for line in note["body"].splitlines():  # get the property-value pairs
        if line == "" or separator not in line:
            break
        k, v = line.split(separator)
        values[k.lower()] = v
    props = []
    for p in properties:  # put the relevant property-value pairs in the specified order
        if p in values.keys():
            props.append(values[p])
        else:
            props.append("")
    return Page(id, title, props)


properties = [x.lower() for x in Properties]
notes = requests.get(f"http://localhost:{port}/folders/{source_notebook}/notes?token={token}", params={"fields": "id,title,body"}).json()["items"]
pages = []
for note in notes:
    page = makePage(note)
    pages.append(page)
pages.sort(key=lambda x: x.title)  # sort list by title

overview = "| Title | " + " | ".join(Properties) + " |\n"  # create Markdown table headers
overview += "| --- " * (len(Properties) + 1) + "|"
for page in pages:  # add rows to table
    overview += f"\n| [{page.title}](:/{page.id}) | " + " | ".join(page.properties) + " |"

# create note with overview
notebook_name = requests.get(f"http://localhost:{port}/folders/{source_notebook}/?token={token}", params={"fields": "title"}).json()["title"]
requests.post(f"http://localhost:{port}/notes?token={token}", json={"title": notebook_name + " Overview", "body": overview, "parent_id": dest_notebook}).json()