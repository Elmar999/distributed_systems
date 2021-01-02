for i in {1..3};
do
   curl -d 'entry=m1.' -X 'POST' 'http://10.1.0.1:80/board' &
   curl -d 'entry=m2.' -X 'POST' 'http://10.1.0.2:80/board' &
   curl -d 'entry=m3.' -X 'POST' 'http://10.1.0.3:80/board' &
   curl -d 'entry=m4.' -X 'POST' 'http://10.1.0.4:80/board' &
   curl -d 'entry=m5.' -X 'POST' 'http://10.1.0.5:80/board' &
   curl -d 'entry=m6.' -X 'POST' 'http://10.1.0.6:80/board' &
   curl -d 'entry=m7.' -X 'POST' 'http://10.1.0.7:80/board' 
done
