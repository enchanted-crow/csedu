import glob
import random
import socket
import CustomThrowables
import time
from urllib.parse import urlparse
from Decoder010 import Decoder010

root_servers = ['198.41.0.4',
                '199.9.14.201',
                '192.33.4.12',
                '199.7.91.13',
                '192.203.230.10',
                '192.5.5.241',
                '192.112.36.4',
                '198.97.190.53',
                '192.36.148.17',
                '192.58.128.30',
                '193.0.14.129',
                '199.7.83.42',
                '202.12.27.33']

bufferSize = 1024
DGRAM_str = None
user_q_type = ''
user_q_name = ''
q_history = []
time_st = 0


def main():
    global user_q_name
    global user_q_type

    user_q_type, user_q_name = valid_input()
    # print(q_type + ' ' + q_name)
    response = queryFromRoot(user_q_name, user_q_type)
    if(response):
        print('FOUND: {} of {} is {}'.format(
            user_q_type, user_q_name, response[1]))
    else:
        print("ERROR!")


def queryFromRoot(q_name, q_type):
    global root_servers
    nameserver_IP = root_server_IP = random.choice(root_servers)
    # nameserver_IP = '192.36.148.17'

    # print(nameserver_IP)

    UDPClientSocket = setupUDPSocket()

    domain = q_name.split('.')[-1]
    print('-> Contacting root ({}) for NS of '.format(nameserver_IP) +
          domain)

    while(1):
        requestDGRAMStr = createDNSQueryDGRAMStr(q_name, q_type)
        query = (q_name, nameserver_IP, q_type)

        try:
            sendDGRAM(UDPClientSocket, requestDGRAMStr, nameserver_IP, query)
        except CustomThrowables.TimeoutException as e:
            global q_history
            q_history.clear()
            print(e)

        responseDGRAMByte, responseDGRAMAddr = recieveDGRAM(UDPClientSocket)

        decoded_response = Decoder010(query, responseDGRAMByte)
        decoded_response.decode()

        # print('Query: ' + str(query))
        # print('Answer: ' + str(decoded_response.answer_rr))
        # print('Authoritative: ' + str(decoded_response.authoritative_rr))
        # print('Additional: ' + str(decoded_response.additional_rr))

        pr_query = getQuery(decoded_response)

        if(nameserver_IP != root_server_IP):
            print('-> Contacting {} for {} of {}'.format(nameserver_IP,
                                                         pr_query[2], pr_query[0]))

        response, answerFound = getResponse(decoded_response, pr_query)

        # print(query)
        # print(pr_query)
        # print(response)

        print(
            '<- {} of {} is {}'.format(pr_query[2], pr_query[0], response[1]))

        if(answerFound):
            return response
        else:
            nameserver_IP = response[1]


def getQuery(decoded_response):
    if(decoded_response.answer_count):
        return decoded_response.query_rr
    elif(decoded_response.authoritative_count):
        return decoded_response.authoritative_rr
    else:
        return decoded_response.query_rr


def getResponse(decoded_response, pr_query):
    global user_q_type
    if(decoded_response.answer_count):
        if(decoded_response.query_type == decoded_response.answer_rr[2]):
            return decoded_response.answer_rr, True
        else:
            print(
                '<- CNAME of {} is {}'.format(pr_query[0], decoded_response.answer_rr[1]))
            response = queryFromRoot(
                decoded_response.answer_rr[1], user_q_type)
            return response, True
    elif(decoded_response.additional_count):
        return decoded_response.additional_rr, False
    elif(decoded_response.authoritative_count):
        bool_ret = None
        if(decoded_response.authoritative_rr[2] == 'SOA'):
            if(decoded_response.query_type == 'CNAME'):
                bool_ret = True
            else:
                print(
                    '<- SOA of {} is {}'.format(decoded_response.query_name, decoded_response.authoritative_rr[1]))
                response = queryFromRoot(
                    decoded_response.authoritative_rr[1], decoded_response.query_type)
                return response, True
        else:
            bool_ret = False

        return decoded_response.authoritative_rr, bool_ret
    else:
        print('ERROR!')
        pass


def __isIPAddress(address):
    return address.replace('.', '').isnumeric()


def recieveDGRAM(UDPClientSocket):
    global bufferSize
    responseDGRAMByte = UDPClientSocket.recvfrom(bufferSize)
    return responseDGRAMByte


def sendDGRAM(UDPClientSocket, requestDGRAMStr, nameserver_IP, query):
    global q_history
    if query in q_history:
        raise CustomThrowables.TimeoutException
    UDPClientSocket.sendto(str.encode(requestDGRAMStr), (nameserver_IP, 53))
    q_history.append(query)
    global time_st
    time_st = time.perf_counter()


def createDNSQueryDGRAMStr(q_name, q_type):
    DGRAM_trxID = chr(random.choice(range(10, 20))) + chr(0)

    # Flags - do query recursively
    DGRAM_flags = chr(0) + chr(0)
    # Number of questions
    DGRAM_QDCOUNT = chr(0) + chr(1)
    # Number of answers
    DGRAM_ANCOUNT = chr(0) + chr(0)
    # Number of nameservers
    DGRAM_NSCOUNT = chr(0) + chr(0)
    # Number of additional information
    DGRAM_ARCOUNT = chr(0) + chr(0)

    q_labels = q_name.split('.')

    DGRAM_q_field = ''
    for label in q_labels:
        DGRAM_q_field += chr(len(label)) + label
    DGRAM_q_field += chr(0)

    DGRAM_qtype = chr(0)
    if(q_type == 'A'):
        DGRAM_qtype += chr(1)
    if(q_type == 'NS'):
        DGRAM_qtype += chr(2)
    if(q_type == 'CNAME'):
        DGRAM_qtype += chr(5)
    if(q_type == 'MX'):
        DGRAM_qtype += chr(15)

    DGRAM_qclass = chr(0) + chr(1)

    DGRAM_str = DGRAM_trxID + DGRAM_flags + \
        DGRAM_QDCOUNT + DGRAM_ANCOUNT + \
        DGRAM_NSCOUNT + DGRAM_ARCOUNT + \
        DGRAM_q_field + DGRAM_qtype + DGRAM_qclass

    return DGRAM_str


def setupUDPSocket():
    return socket.socket(
        family=socket.AF_INET, type=socket.SOCK_DGRAM)


def valid_input():
    while(True):    # Input until valid
        try:
            q_type, q_name = input_query()
            return q_type, q_name
        except Exception as e:
            print(e)


def input_query():
    str = input()
    arr = str.split()

    if(len(arr) != 2):
        raise CustomThrowables.InvalidInputException

    q_type = arr[0].upper()
    url = arr[1]
    if(not url.startswith('http://') and not url.startswith('http://')):
        # Otherwise urllib.parse won't take it.
        url = 'http://' + url

    if q_type not in ['A', 'AAAA', 'NS', 'CNAME', 'MX']:
        raise CustomThrowables.InvalidQueryTypeException

    parsed = urlparse(url)
    q_name = parsed.hostname
    if(q_name == None):
        raise CustomThrowables.InvalidHostnameException

    return q_type, q_name


if __name__ == '__main__':
    main()
