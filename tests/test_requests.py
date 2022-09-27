"""
import requests

# user has to be user_id
data = {'unique_number': 9999, 'uw': 'JAL', 'named_insured': 'THIS IS A TEST',
        'effective_date': '2020-01-13', 
        'account_number': 9999, 'expiration_date': '2019-10-02'}

#data = {'unique_number': 5555, 'named_insured': 'THIS IS A TEST'}

r = requests.post('http://localhost:8000/api/risk_eval/', data = data)

print("done!", r)



Using cURL:
    curl -X POST -H "Content-Type: application/json" -d '{"unique_number": 2020202, "named_insured": "THIS IS A TEST",  "uw": "JAL", "dba": "rest api 3", "term": "New"}' http://localhost:8000/api/risk_eval/

"""