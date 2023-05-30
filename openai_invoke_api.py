import json
import openai
import os
import requests
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import dbinfo
import threading
import random

conn = pymysql.connect(
    host = dbinfo.db_host,
    user = dbinfo.db_username,
    passwd = dbinfo.db_password,
    db = dbinfo.db_name,
    port = dbinfo.db_port,
    charset='utf8'
    )

case_type = ['cyberbullying', 'extortion', 'outcast', 'physical_violence', 'pressure', 'school_violence', 'sexual_violence', 'verbal_abuse']

model = "gpt-3.5-turbo"
openai.api_key = os.environ['openai_api_key']

empty_list = []

def connect():
    cur = conn.cursor()

    q_list = []
    a_list = []
    for i in case_type:
        q_sql = f'SELECT * FROM {i}_question ORDER BY rand() LIMIT 1;'
        a_sql = f'SELECT * FROM {i}_answer ORDER BY rand() LIMIT 1;'
        cur.execute(q_sql)
        q = cur.fetchall()
        q_list.append(q[0][0])
        cur.execute(a_sql)
        a = cur.fetchall()
        a_list.append(a[0][0])

    cur.close()

    return q_list, a_list
    
def sim(s, q_list):
    tfidf_vectorizer = TfidfVectorizer()

    result = []

    for q in q_list:
        sentences = (q, s)
        tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
        cos_similar = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        sim_score = float(cos_similar)
        result.append(sim_score)

    for idx, i in enumerate(result):
        if i >= 0.2:
            return idx, i
        else:
            return result.index(max(result)), i
            
def gpt(U_message):
    messages = [
        {"role": "system", "content": "You are a helpful assistant for school violence"},
        {"role": "user", "content": U_message[0]}
    ]
        
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature=0.3
    )
    
    empty_list.append(response['choices'][0]['message']['content'])

def lambda_handler(event, context):
    request_body = json.loads(event['body'])
    # request_body = event
    U_message = request_body['userRequest']['utterance'].strip()
    
    response = threading.Thread(target=gpt, args=([U_message]))
    response.daemon = True
    response.start()
    
    q_list, a_list = connect()
    
    idx, score = sim(U_message, q_list)
    
    num = random.randint(0, len(a_list)-1)
    

    if score >= 0.2:
        answer = a_list[idx]
    else :
        try :
            answer = empty_list[0]
        except :
            answer = a_list[idx]

    response_body = {
            'version': '2.0',
            'template': {
                'outputs': [
                {
                    'simpleText': {
                        'text': answer
                    }
                }
            ]
        }
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
