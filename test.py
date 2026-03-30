import http.client
import ssl

conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com", context=ssl._create_unverified_context())

headers = {
    'x-rapidapi-key': "e53f1ff333msh015bad1e0b37d59p13805ejsn6106d8dcc59b",
    'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("GET", "/mcenter/v1/149618/scard", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))