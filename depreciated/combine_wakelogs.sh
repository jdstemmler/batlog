touch wakelogs.dat && rm wakelogs.dat
for i in `ls *-wakelog.dat`
do
	cat $i >> wakelogs.dat
done
