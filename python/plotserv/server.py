# Copyright 2014-2026 open-source contributors
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys, os
import time
import psutil
import traceback
import multiprocessing

# core, Terminals -> imported by child process

import socket
from cStringIO import StringIO
import numpy as np

from . import errors

# "LKV" -> "LabVIEW Key-Value", i.e. an array of 2-string clusters

class ShouldStopException(Exception):
    pass

class MessageTruncatedError(Exception):

    """
        Raised when the complete message could not be read from a socket.
    """
    pass
    

def readall(sock, size, max_recv_size=4096):
    """ Read *size* bytes from socket and return a string.
    
    Raises MessageTruncatedError if the read fails to complete.
    """
        
    sio = StringIO()
    
    while sio.tell() < size:
        outstanding = size - sio.tell()
        recv_size = outstanding if outstanding <= max_recv_size else max_recv_size
        tmp = sock.recv(recv_size)
        if tmp == '':
            raise MessageTruncatedError("Socket message truncated (got %d bytes of %d)" % (sio.tell(), size))
        sio.write(tmp)
        
    sio.seek(0)
    return sio.read()


def read_packed_string(sio):
    """ Read a packed string from a file-like object """
    s = sio.read(4)
    if len(s) != 4:
        raise MessageTruncatedError("Packed string length header corrupted")
    slen = np.fromstring(s, dtype="=u4")

    s = sio.read(slen)
    if len(s) != slen:
        raise MessageTruncatedError("Packed string content corrupted")

    return s
        

def write_packed_string(sio, s):
    """ Write a packed string to a file-like object """
    sio.write(np.array(len(s), dtype='=u4').tostring())
    sio.write(s)
    
    
def read_lkv_socket(sock):
    """ Read an LKV message from the given socket and return it as a dict """
    
    msg_len = np.fromstring(readall(sock, 4), dtype="=u4")
    
    # Magic "stop" command
    if msg_len == (2**32)-1:
        raise ShouldStopException()
        
    msg = readall(sock, msg_len)
    
    sio = StringIO(msg)

    sio.read(4)  # discard array length header
    
    dct = {}

    while sio.tell() < msg_len:
        name = read_packed_string(sio)
        value = read_packed_string(sio)
        dct[name] = value
        
    return dct


def write_lkv_socket(sock, dct):
    """ Convert a dictionary of strings to an LKV message and write it to the
    socket. """
    
    sio = StringIO()
    sio.write('\x00'*4)   # reserve space for length header
    
    sio.write(np.array(len(dct), dtype='=u4').tostring()) # array length header
    
    for name, value in dct.iteritems():
        write_packed_string(sio, name)
        write_packed_string(sio, value)
        
    # Write length header
    msg_len = sio.tell() - 4
    sio.seek(0)
    sio.write(np.array(msg_len, dtype='=u4').tostring())
    sio.seek(0)
    
    sock.sendall(sio.read())
    

class FastServer(object):


    def __init__(self, port, callback):
        self.port = port
        self.callback = callback


    def serve(self):
        """ Serve until the EXIT message is received over TCP/IP. """
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', self.port))
        s.listen(5)
                
        print "FastServer bound and listening"
        
        try:
            while True:
                conn, addr = s.accept()
                
                try:
                    data = read_lkv_socket(conn)
                    response = self.callback(data)
                    write_lkv_socket(conn, response)
                    
                except ShouldStopException:
                    break
                    
                except Exception as e:
                    print e
                
                finally:
                    conn.close()
                
        finally:
            s.close()

    
def handler_callback(dct):
            
    def response(code, body):
        return {'!status': '%d'%code, '!body': body if body is not None else ''}
        
    resource = dct.pop('!resource')[4:]  # Discard string length header
    
    handler = core.RESOURCES.get(resource, None)
    
    if handler is None:
        print "Attempt to access illegal IPC resource %s" % resource
        return response(errors.GENERAL_ERROR, "Illegal plot command %s" % resource)
            
    print "Call %s "%resource
    
    # When an exception occurs in the handler, print a traceback
    # to the console and set the status code.
    # Response body is just the last line, e.g. "ValueError: foo".
    try:

        tstart = time.time()
        t = Terminals(dct)
        body = handler(context, t)      # Instantiate the handler object
        tstop = time.time()
            
    except Exception:
        
        exc_type, exc_value, exc_tb = sys.exc_info()
        
        # We take the first entry in the list, as the others are evidently
        # only needed for SyntaxError.
        exc_message = traceback.format_exception_only(exc_type, exc_value)[0].strip()
        
        # Strip off the exception type
        exc_message = ''.join([x for x in exc_message.split(':')][1:]).strip()

        # Pick the *second* entry in the list, because the first always
        # points to the handler() call above.
        exc_fname, exc_lineno, _x, _x = traceback.extract_tb(exc_tb)[1]
        
        # Don't return the whole path to the file.
        exc_fname = os.path.basename(exc_fname).replace('.py','')
        
        estr = "%s [%s %d]" % (exc_message, exc_fname, exc_lineno)

        # Print to console as well for debugging
        traceback.print_tb(exc_tb)
        print estr
        
        # Known errors -> return the code and the message
        # Unknown errors -> return code 5111, message, but also source information
        try:
            code = errors.CODES[exc_type]
        except KeyError:
            return response(errors.GENERAL_ERROR, estr)
        else:
            return response(code, exc_message)

    else:
    
        print "    %d msec" % ((tstop-tstart)*1000.)
    
    return response(0, body)


def run_server(port):
    """ Target function for the child process """
    
    # Doing the imports here saves memory in the parent process,
    # which won't be using matplotlib anyway.
    global core, context, Terminals
    from . import core
    from .terminals import Terminals
    context = core.PlotContext()
        
    print "Subprocess initialized successfully"
    s = FastServer(port, handler_callback)
    print "SHMEM/PIPE handshake successful"
    s.serve()
    
    
def run():
    """ Main function.
    
    Starts a server in a child process, and kills it once LabView goes away.
    """
    
    PORT = int(sys.argv[1])
    LVPROCESS = int(sys.argv[2])
    process_handle = psutil.Process(LVPROCESS)

    print "APLOT %d:%d" % (LVPROCESS, PORT)
    
    p = multiprocessing.Process(target=run_server, args=(PORT,))
    p.start()

    while True:
    
        time.sleep(1)
        
        # According to the docs, is_running() works correctly even if the PID
        # value was re-used between LabView exiting and our polling.
        if not process_handle.is_running():
            print "LabVIEW terminated; shutting down"
            p.terminate()
            break
    
        if not p.is_alive():
            print "Subprocess died mysteriously; exiting."
            break
            