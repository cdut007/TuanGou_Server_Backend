#!/usr/bin/env python
import pika, json, time, urllib2, os
from datetime import datetime

class Config:
    def __init__(self):
        self.mode = os.environ.get('MODE', '')
        self.cwd = os.getcwd()
        self._init_()

    def _init_(self):
        folder_name = self.cwd.split('/')[-1]
        if self.mode == 'TESTING'and folder_name == 'TuanGou_Server_Backend':
            self.live_env()
        elif self.mode == 'TESTING'and folder_name == 'TuanGou_Server_Backend_Testing':
            self.staging_env()
        elif self.mode == 'HOME' :
            self.home_env()
        else:
            self.dev_env()

    def live_env(self):
        self.server_run_addr = '47.90.86.229:3000'

    def staging_env(self):
        self.server_run_addr = '47.90.86.229:3001'

    def dev_env(self):
        self.server_run_addr = '192.168.222.128:3000'

    def home_env(self):
        self.server_run_addr = '192.168.222.128:3000'


class Consuming:
    def __init__(self):
        pass

    def start_consuming(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        def callback(ch, method, properties, body):
            da = json.loads(body)
            self.http_send(da['group_buying_id'], da['get_from'])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        channel.queue_declare(queue='send_wei_xin_rp', durable=True)
        channel.basic_consume(callback,queue='send_wei_xin_rp')
        channel.start_consuming()

    @staticmethod
    def http_send(group_buying_id, get_from):
        config = Config()
        url = 'http://' + config.server_run_addr + '/v2/api.rp.send'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTU3MzcxODMxMywiaWF0IjoxNTEzMjM4MzEzfQ.eyJpZCI6Nzh9.QdDieApGFoFgLJkvRs-SgWlpFaGKR5ZjLDE6378AIOI'
        }
        request = urllib2.Request(url=url, headers=headers, data=json.dumps({
            'group_buying_id': group_buying_id,
            'get_from': get_from
        }))
        res = urllib2.urlopen(request)
        res = json.loads(res.read())
        print '{now}\t group_buying_id: {group_buying_id}\t get_from: {get_from}\t post_status: {post_status}\n'.format(
            now = datetime.now(),
            group_buying_id = group_buying_id,
            get_from = get_from,
            post_status = res['code']
        )


if __name__ == '__main__':
    consu = Consuming()
    consu.start_consuming()