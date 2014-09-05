from Crypto.Cipher import AES

import re
import util

def CBC_MAC(key, iv, p):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    c = cipher.encrypt(util.padPKCS7(p, 16))
    return c[-16:]

key = util.randbytes(16)

def backend_process_message(m):
    global key
    message = m[:-32]
    iv = m[-32:-16]
    mac = m[-16:]
    if CBC_MAC(key, iv, message) != mac:
        print('S: Discarding invalid message')
        return
    sender = ''
    recipient = ''
    amount = 0
    for pair in message.split(b'&'):
        k, v = pair.split(b'=')
        if k == b'from':
            sender = v
        elif k == b'to':
            recipient = v
        elif k == b'amount':
            m = re.match(b'[0-9]+', v)
            if m:
                amount = int(m.group(0))
    print('S: Transferring', amount, 'from', sender, 'to', recipient)

last_sent_message = b''

def frontend_send_message(sender, recipient, amount):
    global key
    global last_sent_message
    if not re.match(b'^[A-Za-z]+$', sender):
        raise Exception(b'Invalid sender ' + sender)
    if not re.match(b'^[A-Za-z]+$', recipient):
        raise Exception(b'Invalid recipient ' + recipient)
    amount = int(amount)
    message = b'from=' + sender + b'&to=' + recipient + b'&amount=' + str(amount).encode('ascii')
    iv = util.randbytes(16)
    last_sent_message = message + iv + CBC_MAC(key, iv, message)
    print('C:', last_sent_message)
    backend_process_message(last_sent_message)

def attacker_peek_last_sent_message():
    global last_sent_message
    return last_sent_message

def attacker_inject_message(m):
    print('A: Injecting', m)
    backend_process_message(m)

if __name__ == '__main__':
    frontend_send_message(b'Alice', b'Bob', b'4')
    print('A:', attacker_peek_last_sent_message())