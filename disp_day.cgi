#!/usr/bin/perl
#  Display Day.  Reads in database and prints appointments for the
#  selected day.  Allows option of adding new appointment.
#
require 'variables';
require 'httools.pl';
&header;

#  Determine if this is a personal calendar;
($sub=$ENV{'PATH_INFO'})=~s#^/##;
if ($sub=~/personal/){require $personal};

#   Read date from QUERY_STRING
$info=$ENV{'QUERY_STRING'};
($month,$day,$year)=split(/&/,$info);

#  Print titles to html page
&month_txt("$month");
&title("Appointments for $month_txt $day, $year.");
print "<h2>Appointments for $month_txt $day, $year.</h2><hr>";

#  Read in database.
$any="no";     #  Flag which determines if appts were found.
open (DATES, "$datebook");
@dates=<DATES>;
close DATES;

&julean($month,$day,$year);   #    Julean date of day in question.

#  Checks database for listings of that day.
print "<table border width=100%>";
print "<tr><th> Time <th> Event <th> Name <br>";
for $date (@dates)	{
($julean,$time,$endtime,$desc,$name,$id)=split(/~~~/,$date);
if ($julean==$jule) {
print "<tr><td>";
if ($time eq "00:00" && $endtime eq "00:00")  { print "(All day) ";}
else {
#  am/pm the time
($hr,$min)=split(/:/,$time);
if ($hr==24) {$hr="12";
		$ampm="am"}
else {
if ($hr<12) {$ampm="am"}
else {$hr-=12; 
	if ($hr==0){$hr=12};
	$ampm="pm"};
}	# end else
$time=$hr.":".$min." ".$ampm;
print "$time";}

if ($endtime eq "00:00") {}
else {
#  am/pm the time
($hr,$min)=split(/:/,$endtime);
if ($hr<=12) {$ampm="am"}
else {$hr-=12; $ampm="pm"};
if ($hr==0){$hr="12"};
$endtime=$hr.":".$min." ".$ampm;
print " - $endtime ";}

print "<td> $desc <td> $name <br>";
			$any="yes";}
			}
if ($any eq "no") {print "<tr><td colspan=3><center><b>** No appointments **</b></center><br>";}
print "</table>";

print "<hr>";
print "<a href=$base_url$add_date?$month&$day&$year>Add an appointment</a><br>";
print "<a href=$base_url$del_date?$month&$day&$year> Delete an appointment</a><br>" unless ($any eq "no");
print "<a href=$base_url$hypercal?$month&$year>Back</a> to the calendar.";
&footer;
