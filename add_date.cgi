#!/usr/bin/perl
#
#	Add Date
#
#	Prints html form for input of new appointment.  Sends the
#  form input to part_2 for processing.
#	Richard Bowen, 12/14/95
#	rbowen@aiclex.com
#_____________________________________________________
require 'httools.pl';
require 'variables';
&header;

# Determine if it is a personal calendar
($sub=$ENV{'PATH_INFO'})=~s#^/##;
if ($sub=~/personal/){require $personal};

#  Read in date from QUERY_STRING
$date=$ENV{'QUERY_STRING'};
($month,$day,$year,$command)=split(/&/,$date);

#
#	Determine which part of the script is being called
#__________________________________

if ($command eq "doit") {&part_2}
else { &part_1 };


#
#	Part One
#
#	Prints html form and sends results to part 2
#______________________________________________

sub part_1	{
#  Print some titles to browser.
&month_txt("$month");

&title ("Add an appointment for $month_txt $day, $year.");

print <<"HTML";

<h2>Add an appointment for $month_txt $day, $year.</h2>
<b>Note:</b> Only authorized users will be able to add and delete appointments.  Please contact your web adminstrator for a username and password.
<hr>

<form method=post action=$base_url$add_date?$month&$day&$year&doit>
<b>Time:</b>
<input name="hour" size=2 value="00"><b>: </b><input name="min" value="00" size=2>
<input type=radio name="ampm" value="am" CHECKED>AM
<input type=radio name="ampm" value="pm">PM
<br>
<b>Until:</b>
<input name="hour_done" size=2 value="00"><b>: </b><input name="min_done" value="00" size=2>
<input type=radio name="ampm_done" value="am" CHECKED>AM
<input type=radio name="ampm_done" value="pm">PM
<br>

<i>If no beginning time is specified, the event will be listed as the whole day.  If no end time is entered, the event will be listed with only the beginning time</i>
<br>
<b>Description</b><br>
<textarea name="desc" rows=5 cols=60></textarea><br>
<table><tr><td valign=top rowspan=5><b>Event occurs:</b><br>
<td><input type=radio name="freq" value="once" CHECKED>Once<br>
<tr><td><input type=radio name="freq" value="daily">Daily for : 
<input name="days" value="1" size="2"> days.<br>
<tr><td><input type=radio name="freq" value=\"weekly\">Weekly for : 
<input name="weeks" value="1" size=2> weeks.<br>
<tr><td><input type=radio name="freq" value="monthly">Monthly for : 
<input name="months" value="1" size=2> months.<br>
<tr><td><input type=radio name="freq" value="annual">Annually for : 
<input name="years" value="1" size=2> years.<br>
</table>

Please enter your name : <input name="perp" size="20"><br>
<input type=submit value="Add Appointment">
</form><hr>
Calendar entries will expire and be deleted $old days after the event.

HTML

&footer;
	}		#  End of part 1

sub part_2	{
#	Receives the post data from add_form and adds the information
#  to the database.  Format of database is currently:
#  Julean&time&endtime&event&name&id
#

# Get data from form post.
#  Variables are:
#  hour, min, ampm, desc, freq, perp
#  hour_done, min_done, ampm_done, days, weeks, months
#  freq = one of (once, daily, weekly, monthly)

&form_parse;

# Strip returns from description field to make it one continuous string.
$FORM{'desc'} =~ s/\n//g;

#  Print titles to HTML page.
&month_txt("$month");
&title ("Appointment added to $month_txt $day, $year");
print "<h1>Appointment added to $month_txt $day, $year</h1>";

#  Read in current contents of database.
open (DATES,"$datebook") || print "Was unable to open the datebook database for reading <br>\n";
@dates=<DATES>;
close DATES;

for (@dates){chop};
&julean($month,$day,$year);

#	Rewrite time
&time($FORM{'hour'},$FORM{'min'},$FORM{'ampm'});
$begin=$time;
&time($FORM{'hour_done'},$FORM{'min_done'},$FORM{'ampm_done'});
$done=$time;

# Get id number
open (ID, "$hypercal_id")  || print "Was unable to open the ID file for reading<br>\n";
@id=<ID>;
close ID;

for (@id){chop};
@id[0]++;
if (@id[0]>=999999) {@id[0]=1};
$id=@id[0];
open (NEWID,">$hypercal_id")  || print "Was unable to open the ID file ($hypercal_id) for writing<br>\n";
for $each (@id)	{
print NEWID "$each\n";}

#  Add the new appointment to the database.
$newappt="$jule~~~$begin~~~$done~~~$FORM{'desc'}~~~$FORM{'perp'}~~~$id";
push (@newdates,$newappt);

if ($FORM{'freq'} ne "once") { &many };

&julean($month,$day,$year);
&todayjulean;
for $date (@dates)	{
($juldate,$apptime,$appendtime,$appdesc,$perpname,$id)=split(/~~~/,$date);
if (($today-$juldate)<=$old) {push (@newdates,$date) }
		}
@dates=sort(@newdates);

#  Write database back to disk file.
open (NEWDATES,">$datebook") || print "Was unable to open the datebook file for writing.<br>\n";
foreach $date (@dates) {print NEWDATES "$date\n"}
close NEWDATES;

#  Links back to other pages.
print "Back to calendar for <a href=$base_url$hypercal?$month&$year>$month\/$year</a><br>";
print "Back to <a href=$base_url$disp_day?$month&$day&$year>$month\/$day\/$year</a>.";
&footer;
		}	# End of part_2

#
#	Sub time
#  Rewrites time into 24hr format.
#

sub time	{
$time="";
$HOUR=$_[0];
$MINS=$_[1];
$merid=$_[2];
if ($merid eq "pm") {
 $HOUR+=12;
 if ($HOUR==24) {$HOUR=12}
		}
if ($HOUR==12 && $merid eq "am"){$HOUR=24};
if ($HOUR>24){$HOUR=23};
if ($MINS>59){$MINS=59};
$HOUR=sprintf "%02.00f",$HOUR;
$MINS=sprintf "%02.00f",$MINS;
$time=$HOUR.":".$MINS;
		}

#
#	If frequency is more than once ...
#____________________________________________________
sub many	{
MANY:	{
	&daily, last MANY if ($FORM{'freq'} eq "daily");
	&weekly, last MANY if ($FORM{'freq'} eq "weekly");
	&monthly, last MANY if ($FORM{'freq'} eq "monthly");
	&annual, last MANY if ($FORM{'freq'} eq "annual");
	}
open (ID, ">$hypercal_id");
@id[0]=$id;
for $each(@id)	{
print ID "$each\n";}
		}

sub daily {
#	For daily appointments for $FORM{'days'} days
$days=$FORM{'days'};
for ($i=1; $i<$days; $i++)	{
$newjule=($jule+$i);
$id++;
$newappt="$newjule~~~$begin~~~$done~~~$FORM{'desc'}~~~$FORM{'perp'}~~~$id";
push (@newdates, $newappt);
				}  #  endfor
}	#	End daily

sub weekly {
#	For weekly appointments for $FORM{'weeks'} weeks.
$weeks=$FORM{'weeks'};
if ($weeks>156){$weeks=156};
for ($i=1;$i<$weeks;$i++)	{
$newjule=($jule+(7*$i));
$id++;
$newappt="$newjule~~~$begin~~~$done~~~$FORM{'desc'}~~~$FORM{'perp'}~~~$id";
push (@newdates, $newappt);
				}  #endfor
}   #	End weekly

sub annual	{
#  for annual appointments for $FORM{'years'} years.
$years=$FORM{'years'};
if ($years>10){$years=10};
for ($i=1;$i<$years;$i++)	{
$some_year=($year+$i);
&julean($month,$day,$some_year);
$id++;
$newappt="$jule~~~$begin~~~$done~~~$FORM{'desc'}~~~$FORM{'perp'}~~~$id";
push (@newdates, $newappt);
				}  #end for
}   #   End annual

sub monthly {
#	For monthly appointments for $FORM{'months'} months
#	This is the more difficult one
#________________________________________

$months=$FORM{'months'};
if ($months>36) {$months=36};
$this_month=$month;
$this_year=$year;
$this_day=$day;
for ($i=1;$i<$months;$i++)	{
$this_month++;
if ($this_month==13)	{$this_month=1;
			$this_year++;}

#  Check to see if this is a last-day-of-the-month thing
$this_day=$day;
if ($this_day>=28) { &last_days };

&julean($this_month,$this_day,$this_year);
$newjule=$jule;
$id++;
$newappt="$newjule~~~$begin~~~$done~~~$FORM{'desc'}~~~$FORM{'perp'}~~~$id";
push (@newdates, $newappt);
				} #  Endfor
}

sub last_days	{
#
#	If the day given is more than the days in the month,
#	it is reset to the last day of the month
#______________________________________________________

SWITCH:	 {
	$last=31, last SWITCH if ($this_month==1);
	$last=28, last SWITCH if ($this_month==2);
	$last=31, last SWITCH if ($this_month==3);
	$last=30, last SWITCH if ($this_month==4);
	$last=31, last SWITCH if ($this_month==5);
	$last=30, last SWITCH if ($this_month==6);
	$last=31, last SWITCH if ($this_month==7);
	$last=31, last SWITCH if ($this_month==8);
	$last=30, last SWITCH if ($this_month==9);
	$last=31, last SWITCH if ($this_month==10);
	$last=30, last SWITCH if ($this_month==11);
	$last=31, last SWITCH if ($this_month==12);
	}
if ($this_day>$last) {$this_day=$last};
		}

