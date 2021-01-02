curl -d 'delete=1' -X 'POST' 'http://10.1.0.6:80/board/5.5/' & curl -d 'entry=new&delete=0' -X 'POST' 'http://10.1.0.5:80/board/5.5/'
curl -d 'entry=new&delete=0' -X 'POST' 'http://10.1.0.5:80/board/2.2/' &
curl -d 'delete=1' -X 'POST' 'http://10.1.0.6:80/board/2.2/'
curl -d 'delete=1' -X 'POST' 'http://10.1.0.6:80/board/3.3/' &
curl -d 'entry=new&delete=0' -X 'POST' 'http://10.1.0.5:80/board/3.3/'
curl -d 'entry=new&delete=0' -X 'POST' 'http://10.1.0.5:80/board/5.4/' &
curl -d 'delete=1' -X 'POST' 'http://10.1.0.6:80/board/5.4/'

