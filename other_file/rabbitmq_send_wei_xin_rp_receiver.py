#!/usr/bin/env python
import pika, json, time, urllib2
from datetime import datetime


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

    def http_send(self, group_buying_id, get_from):
        url = 'http://192.168.222.128:3000/v2/api.rp.send'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTU3MzcxODMxMywiaWF0IjoxNTEzMjM4MzEzfQ.eyJpZCI6Nzh9.QdDieApGFoFgLJkvRs-SgWlpFaGKR5ZjLDE6378AIOI'
        }
        data = json.dumps({
            'group_buying_id': group_buying_id,
            'get_from': get_from
        })
        request = urllib2.Request(url=url, headers=headers, data=data)
        res = urllib2.urlopen(request)
        res = json.loads(res.read())
        hg = '{now}\t group_buying_id: {group_buying_id}\t get_from: {get_from}\t post_status: {post_status}\n'.format(
            now = datetime.now(),
            group_buying_id = group_buying_id,
            get_from = get_from,
            post_status = res['code']
        )
        print hg
        self.write_log(hg)

    @staticmethod
    def write_log(hg):
        f = open('./rabbitmq_send_wei_xin_rp_receiver.log', 'a')
        f.write(hg)
        f.close()


if __name__ == '__main__':
    consu = Consuming()
    consu.start_consuming()