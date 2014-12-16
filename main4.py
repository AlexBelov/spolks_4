import sys
import socket
import argparse
import os

BUF_SIZE = 8192

def run_server(port, filename):
	
	if port in range(1024,65535):
		#s = socket.socket()	
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET family => net socket STREAM => potokovblu*
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('',port))
		s.listen(1)
		conn, addr = s.accept()
		print 'Connected with client. IP:{0}'.format(addr[0])
	else: 
		print 'Enter port in range 1024 <=> 65535'
		return 0
	
	f = open(filename, 'rb')
	filesize = os.stat(filename).st_size
	sentsize = 0
	perflag = 0

	try:
		number = conn.recv(1024)
		print number
	except:
		print "Lost Connection"
		conn.close()
		s.close()
		return 0
	f.seek(int(number),0)

	sentsize += int(number)
	
	while True:
		data = f.read(BUF_SIZE)
		sentsize += BUF_SIZE
		percent = int(float(sentsize)*100/float(filesize))
		#print "{0} Kb of {1} Kb sent ({2}%)".format(sentsize/1024, filesize/1024, percent)
		#sys.stdout.write('\033M') #  write all time in output in 1 string
		if not data:
			sys.stdout.write('\033D')
			print 'Data has been transfered'
			break
		try:
			conn.settimeout(5)
			conn.send(data)
		except socket.error:
			print 'Transfer fail'
			conn.close()
			s.close()	
			return 0  # sys.exit
		if (percent % 10 == 0) & (perflag != percent) & (percent <91):
			perflag = percent #  for non multiply output in terminal
			sys.stdout.write('\033D') # go next line
			print '\033[37;1;41m Urgent flag sent at {0}% \033[0m'.format(percent)
			conn.send(b'{}'.format(percent/10), socket.MSG_OOB) # flag urgent data
			
	f.close()
	conn.close()
	s.close()

def run_client(host, port):
	if port in range(1024,65535):
		#s = socket.socket()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
		try:
			s.connect((host,port))  # <= tuple = 1 argument, not 2!
		except:
			print "Server is OFF"
			s.close()
			return 0
	else:
		print 'Enter port in range 1024 <=> 65535'
		return 0
	
	f = open('rcvd.file','ab')
	rcvdsize = 0
	s.settimeout(5)

	temp=os.path.getsize('rcvd.file')
	print temp
	try:
		s.send(str(temp))
	except:
		print "Lost Connection"
		s.close()
		return 0
	rcvdsize += temp

	while True:
		try:
			s.settimeout(0)
			data = s.recv(2, socket.MSG_OOB) # catcing urgent data (2 bytes = 1 char)
		except Exception:
			data = None	
		if data:
		# 	#sys.stdout.write('\033D') # go next line
			print '\033[0;32m Urgent: {0} Kb ({1}0%) received \033[0m'.format(rcvdsize/1024, data)
		else:		#i.e. we haven't MSG_OOB
			try:
				s.settimeout(5)
				data = s.recv(BUF_SIZE)
			except Exception:
				data = None

			if not data:
				break	

			rcvdsize += BUF_SIZE
			f.write(data)
			#print BUF_SIZE
			#sys.stdout.write('\033M') #  write all time in output in 1 string
		
	print 'Done!'
	f.close()
	s.close()

def main():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group() # make sure that only one of the arguments exist
	group.add_argument("-s", "--server", help="Run as server", action="store_true") # return True in if statement
	group.add_argument("-c", "--client", help="Run as client", action="store_true")
	parser.add_argument("-a", "--address", help="Destination host (client mode)", default="127.0.0.1")
	parser.add_argument("-p", "--port", type=int, help="Port to listen/connect to", default=5005)
	parser.add_argument("-f", "--file", help="File to send (server mode)", default="send.file")
	args = parser.parse_args() # convert argument strings to objects and assign them as attributes of the namespace
	if args.server:
		print 'Server mode'
		run_server(args.port, args.file)
	if args.client:
		print 'Client mode'
		run_client(args.address, args.port)

if __name__ == '__main__':
        main()

'''
Server:
python main4.py -s [-p port] [-f filename]

Client:
python main.py4 -c [-a host] [-p port]

Default host: 127.0.0.1
Default port: 5005
Client saves file with name 'rcvd.file'.
Default filename for server to send: 'send.file'.
http://habrahabr.ru/post/119436/
'''