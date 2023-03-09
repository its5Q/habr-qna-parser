import requests
from multiprocessing.dummy import Pool
from parsel import Selector
from threading import Lock
import orjson as json
import traceback
from tqdm import tqdm

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

def parse_comments(html: Selector):
    comments = []
    for comment_html in html.css('li[role="comments_item"]'):
        comment = {
            "author": "",
            "posted_at": "",
            "body": ""
        }

        comment["author"] = comment_html.css('.user-summary__nickname meta').xpath('@content').get('')
        comment["posted_at"] = comment_html.css('time').xpath('@datetime').get()
        comment["body"] = ''.join(comment_html.css('.comment__text').xpath('node()').getall()).strip()

        comments.append(comment)
    
    return comments


def parse(qid):
    q = {
        "id": qid,
        "author": "",
        "title": "",
        "description": "",
        "tags": [],
        "posted_at": "",
        "view_count": 0,
        "subscribers_count": 0,
        "complexity": "",
        "complexity_votes": 0,
        "comments": [],
        "answers": []
    }
    try:
        resp = requests.get(f'https://qna.habr.com/q/{qid}', headers=headers, timeout=15)
    except Exception:
        traceback.print_exc()
        return
    
    if resp.status_code != 200:
        return
    
    html = Selector(resp.text)
    question_html = html.css('.question_full')[0]
    
    if question_html:
        q["author"] = question_html.css('.question-head .user-summary__nickname meta').xpath('@content').get('')
        q["title"] = question_html.css('.question__title::text').get().strip()
        q["description"] = ''.join(question_html.css('.question__text').xpath('node()').getall()).strip()
        q["tags"] = question_html.css('.tags-list__item').xpath('@data-tagname').getall()
        q["posted_at"] = question_html.css('.question__pub-date time').xpath('@datetime').get()
        q["view_count"] = int(question_html.css('.question__body meta[itemprop="interactionCount"]').xpath('@content').get('0').split()[0])
        q["subscribers_count"] = int(question_html.css('span[role="subscribers_count"]').xpath('meta/@content').get('0').split()[0])
        q["complexity"] = ''.join(question_html.css('.btn_complexity::text').getall()).strip()
        q["completixy_votes"] = int(question_html.css('.btn_complexity').xpath('@title').get('1').split()[-1])
        q["comments"] = parse_comments(question_html.css('.question__comments'))
        

    for answer_html in html.css('div[role="answer_item "]'):
        answer = {
            "id": 0,
            "author": "",
            "posted_at": "",
            "body": "",
            "accepted": False,
            "upvote_count": 0,
            "comments": []
        }
        answer["id"] = int(answer_html.css('.answer_wrapper').xpath('@id').get('0').split('_')[-1])
        answer["author"] = answer_html.css('.answer__header .user-summary__nickname meta').xpath('@content').get('')
        answer["posted_at"] = answer_html.css('time[itemprop="dateCreated"]').xpath('@datetime').get()
        answer["body"] = ''.join(answer_html.css('.answer__text').xpath('node()').getall()).strip()
        answer["accepted"] = "acceptedAnswer" in answer_html.css('.answer_wrapper').xpath("@itemprop").get()
        answer["upvote_count"] = int(answer_html.css('meta[itemprop="upvoteCount"]').xpath("@content").get())
        answer["comments"] = parse_comments(answer_html.css('.answer__comments'))

        q["answers"].append(answer)

    with writelock:
        ofile.write(json.dumps(q, option=json.OPT_APPEND_NEWLINE))

    pbar.update()

pbar = tqdm(total=1259816)
writelock = Lock()
ofile = open('questions.jsonl', 'ab')
pool = Pool(16)
pool.map(parse, range(0, 1259816))
pool.close()
pool.join()