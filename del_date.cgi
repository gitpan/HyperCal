#!/usr/bin/perl
#
#	Delete a date, part 1
#	Will print an html form containing the entries for the 
#  day and allow the user select one or more for deletion.
#  Will then post this information to del_date_2 for 
#  processing.
#
require 'httools.pl';
require 'variables';
&header;

#  Determine if it is a personal calendar
($sub=$ENV{'PATH_INFO'})=~s#^/##;
if ($sub=~/personal/) {require $personal};

#  Get arguments
$date=$ENV{'QUERY_STRING'};
($month,$day,$year,$command)=split(/&/,$date);

#  This determines if this is being called the first or second time ...
if ($command eq "doit") { &part_2 }
else 	{ &part_1 };

sub part_1 	{
# 	Prints the HTML form and sends the data to part 2

&julean($month,$day,$year);

#  Print titles
&title("Delete an appointment from $month\/$day\/$year.\n");
print "<h3>Delete an appointment from $month\/$day\/$year.</h3>\n";
print "Select appointment(s) to delete.<hr>\n";

# Get appointments for that day
open (APPS, "$datebook");
@appoint=<APPS>;
for (@appoint){chop};
for $appt (@appoint)	{
(@stuff)=split(/~~~/,$appt);
$julean=@stuff[0];
if ($julean==$jule) {push (@candidates,$appt);}}

print "<form method=post action=$del_date?$month&$day&$year&doit>\n";
foreach $candidate (@candidates)	{
($julean,$time,$timeend,$description,$name,$id)=split(/~~~/,$candidate);
print "<input type=hidden name=\"month\" value=\"$month\">";
print "<input type=hidden name=\"day\" value=\"$day\">";
print "<input type=hidden name=\"year\" value=\"$year\">";
print "<input type=checkbox name=\"$id\">$description - ($time-$timeend)<br>\n";
		}
print "<hr>";
print "<input type=submit value=\"Delete\"> entry or entries.";
print "</form>";
&footer;
			}


sub part_2	{
#
#	Receives the date from del_date part 1, and does the dirty deed.
&form_parse;

#  Read in database;
open (DATES, "$datebook") || die "Was unable to open datebook for reading.<br>\n";
@dates=<DATES>;
for (@dates){chop};

for $date(@dates)	{
@info=split(/~~~/,$date);
$ID=@info[5];    # NOTE:  If the datebase format changes, this will
		  #    need to be changed also.  
$flag=0;
foreach $key (keys %FORM)	{
if ($ID==$key) {$flag=1};	}
push (@newdates,$date) unless ($flag);
		}	# end foreach $date

open (DATES, ">$datebook");
for (@newdates) {
print DATES;
print DATES "\n";	}
print "<h2>Date(s) deleted</h2>";
print "<hr>";
print "Back to <a href=$base_url$disp_day?$FORM{'month'}&$FORM{'day'}&$FORM{'year'}>$FORM{'month'}\/$FORM{'day'}\/$FORM{'year'}</a><br>";
print "Back to <a href=$base_url$hypercal?$FORM{'month'}&$FORM{'year'}>$FORM{'month'}\/$FORM{'year'}</a><br>";
&footer;
		}
