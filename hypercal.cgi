#!/usr/bin/perl
#	HyperCal   by   Richard Bowen
#  A HTML datebook.  
#  This part draws the calendar and links it to the other scripts.
#  Can be called as http://URL/hypercal, or with arguments
#  as http://URL/hypercal?month&year
require 'httools.pl';

#   Set a few basic variables in an easy-to find location.
require 'variables';

#  Reads arguments.  If no arguments, it will default to current month.
$args=$ENV{'QUERY_STRING'}; 
($sub=$ENV{'PATH_INFO'})=~ s#^/##;
# Read the path info and strip leading /

# Determine which part of hypercal has been called.
if ($sub=~/personal/) { &personal };
if ($sub eq "goto") { &goto }
else { &main };


# ______________________________
#
#	The main part here - This is the part that prints the
#  calendar as an HTML table, and links each day to listings of
#  appointments for that day.
#
# _______________________________

sub main	{
&header;
($this_month,$this_year)=split(/&/,$args);
if ($args eq "") {	#  Defaults to current date if none specified.
	&date;   #  Calls the todays date subroutine from httools.pl
	$this_month=$month;
	$this_year=$year;}

($junksec,$junkmin,$junkhour,$today_day,$today_month,$today_year,$junkwday,$junkyday,$junkisdst)=localtime(time);$today_year+=1900;$today_month+=1;
# Determine what "today" is.  Arrgh.  I hate all these variables!!


&month_txt("$this_month");
print "<html><head><title>$title - $month_txt, $this_year</title></head>\n";
print "<body";
$month_image=@month_images[$this_month-1];
($icon,$bg,$color,$text,$link,$vlink)=split(/~~/,$month_image);
print " background=\"$bg\"" unless ($bg eq "none");
print " bgcolor=\"$color\"" unless ($color eq "none");
print " text=\"$text\"" unless ($text eq "none");
print " link=\"$link\"" unless ($link eq "none");
print " vlink=\"$vlink\"" unless ($vlink eq "none");
print ">\n";


#	Read datebook into memory
#
open (DATES, $datebook);
@datebook=<DATES>;

#  This stuff taken from a script by David Pitts
#  Generated the html calendar

@months=("December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
@last_days=(31,31,28,31,30,31,30,31,31,30,31,30,31);
@days_of_week=("Sun","Mon","Tue","Wed","Thu","Fri","Sat");
@month_offset=(3,3,0,3,2,3,2,3,3,2,3,2,3);

print "<center>";
print "<table border=6 cellpadding=5 width=100%>\n";
print "<tr><td align=center colspan=7><center><h2>@months[$this_month], $this_year</h2>";

if ($multi_user eq "yes" && $personal_on eq "no") {
print "<form method=post action=\"$base_url$hypercal/personal\">";
print "<input type=submit value=\"Go To Personal Calendar\">";}
elsif ($personal_on eq "yes")	{
($link=$hypercal)=~s/\/personal//g;
print "<form method=post action=\"$base_url$link\">";
print "<input type=submit value=\"Go To Public Calendar\">";}

#  Month-appropriate icon
print "<img src=\"$icon\" alt=\"\" align=middle hspace=30>" unless ($icon eq "none");
print "</form>";
print "</center>";

$week_days=join(" <th> ",@days_of_week);
print "<tr><th>$week_days<br>\n";

for ($i=1906; $i<$this_year; $i++)	{
	$days_offset++;
	if (($i-1)%4==0)
		{$days_offset++}; # Leap years
	} # end for
if (($this_year%4)==0 && ($this_month>2))
	{$days_offset++}; #  Current year is leap year

for ($j=1; $j<($this_month);$j++)	{
	$days_offset+=@month_offset[$j]};

$first_day_of_month=($days_offset%7);

$last_day_in_month=@last_days[$this_month];
if (($this_month==2)&&($this_year%4==0)){$last_day_in_month=29};

$date_place=0;

while ($date_place<$last_day_in_month)	{
print "<tr>";
for ($j=0; $j<=6; $j++)	{
	if (($first_day_of_month>=0)||($date_place>=$last_day_in_month))
	{print "<td align=center>-";
	$first_day_of_month--}
	else	{
	$date_place++;
	print "<td align=center><a href=\"$base_url$disp_day?$this_month&$date_place&$this_year\"> $date_place </a>";
&appoints($this_month,$date_place,$this_year); 
if ($today_day==$date_place && $today_month==$this_month && $today_year==$this_year){print"<br><b><font color=red>TODAY</font></b>"};
} # end else
}	#end for
print "<br>\n";
}	#  end while



# Announcements for the month
open (ANNO, "$announce");
@announce=<ANNO>;
$search=$this_month."_".$this_year;
$any_announce="no";
for $announces (@announce)	{
($mo,$msg,$aid)=split(/&&/,$announces);
if ($mo eq $search){
if ($any_announce eq "no"){print "<br><tr><td align=center colspan=7>";}	# prints tr for first announce
print "<center><b>$msg</b></center><br>";
$any_announce="yes";}
		}


print "</table></center><br>\n";
print "<center>Select a day to see the appointments for that day.  Numbers in parentheses indicate how many appointments are on that day.</center>";
print "<hr>\n";

#  Print links to next month and previous month, as well as 
#  current month.

print "<center>Go to:</center><br>\n";
print "<center>";
# print "<table border=0 cellpadding=5 width=100%>";
$last_year=$this_year;
$last_month=($this_month-1);
if ($last_month == 0) {$last_month=12; $last_year=($this_year-1);}

print "[ <a href=\"$base_url$hypercal?$last_month&$last_year\">  Previous month  </a>|\n";

$next_year=$this_year;
$next_month=($this_month+1);
if ($next_month == 13) {$next_month=1; $next_year=($this_year+1);}

print "<a href=\"$base_url$hypercal?$next_month&$next_year\">  Next month  </a>|";

print "<a href=\"$base_url$hypercal\">  Current month  </a>]</center><br>\n";
print "<center><form method=get action=$base_url$hypercal/goto>";
print "<input type=submit value=\"Jump\"> to <input name=\"month\" size=2> \/ <input name=\"year\" size=4 value=\"$this_year\">";
print "<input type=hidden name=\"this_year\" value=\"$this_year\">";
print "</form></center><hr>";

print "<center>";
# print "<table width=100%><tr><td>";
print "[ <a href=\"$base_url$edit_announce?$this_month&$this_year\">Add an announcement</a> for this month. ";
print "| <a href=\"$base_url$edit_announce?$this_month&$this_year&delete\">Delete an announcement</a> from this month." unless ($any_announce eq "no");
print " ]";
print "</center>";

print "<center>";
print "<hr>[ <a href=\"http://www.rcbowen.com/perl/HyperCal.html\">About HyperCal</a>.";
foreach $item (@linkto)	{
($url, $page_title)=split(/~~/,$item);
print " | <a href=\"$url\">$page_title</a>";
			}
if ($multi_user eq "yes")	{
print " | <a href=\"$base_url$change_passwd\">Change your user password</a>"}
print " ]</center><br>\n";
print "HyperCal, Version $version, Copyright &copy; 1996, Richard Bowen.  All rights reserved.<br>\n";

&footer;
	}	#  End of sub main

#  Determines which days have appointments, and prints the number
#  of appointments in that cell.  This routine takes most of the run
#  time of this script.
sub appoints   {
$found=0;
&julean($_[0],$_[1],$_[2]);  #  Julean date of day
for $entry (@datebook)	{
@temporary=split(/~~~/,$entry);
if (@temporary[0]==$jule)  {$found++}};
if ($found != 0) {print "   ($found)"};	}


sub goto	{
#
#  Gets data from hypercal to go to a particular month
#  and redirects to that month.
#  Data comes in as QUERY_STRING
# &form_parse is not used

($pair1, $pair2, $pair3)=split(/&/,$args);
($junk, $month)=split(/=/, $pair1);
($junk, $year)=split(/=/, $pair2);
($junk, $this_year)=split(/=/, $pair3);
#  Need some error checking ...
if ($month eq ""){$month=1};
if ($year eq""){$year=$this_year};
if ($month>12) {$month=12};
if ($month<1) {$month=1};
if ($year<1) {$year=1};
if ($year>9999) {$year=9999};
$args="$month&$year";
&main
	}		#  End of &goto

sub personal	{
#
#	Determine if the personal part is being called, and alter 
# 	some variables accordingly.
#####

#  The string passed in from the main program is $sub
$sub=~s/personal\///;	# strip the "personal" off of the string;

$user_id=$ENV{'REMOTE_USER'};	# Get the user id from the auth info

$user_variables=~s/USERNAME/$user_id/;
require "$user_variables";
}	#  End of sub personal
