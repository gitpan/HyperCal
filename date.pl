#!/www/bin/perl
$date=localtime(time);
($day, $month, $num, $time, $year) = split(/\s+/,$date);
($hour, $min, $sec)=split(/:/,$time);
if ($hour > 12)	{$hour-=12;$am="pm"}	
	else {$am="am"};
$date="$day, $month $num, $year, $hour:$min $am (EST)";
print "content-type: text/html\n\n";
print $date;
