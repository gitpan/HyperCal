package HyperCal;

require Exporter;
@ISA = Exporter;
@EXPORT = qw(body_tag
			month_txt
			EventSplit
			AnnounceSplit
			GetId
			convert_time
			AmPm
			FormParse
			PrintTemplate
			PrintHeader
			Switch			

			$Config
			);

use vars qw($Config
			);


$Config={};
#################################################
##  VARIABLES - SET THESE TO YOUR LOCAL CONFIG ##
#################################################
$Config->{VERSION}="3.2";
$Config->{server_name} = "www.rcbowen.com";
$Config->{delimiter} = "~~";

# URL of the directory in which these files live
$Config->{base_url}="/scripts/hypercal_dev/";

#  Location of the hypercal templates - you need to specify full path
$Config->{templates} = "/home/rbowen/public_html/scripts/hypercal_dev/templates";

#  Some sites only allow cgi's with a .cgi extension,
#  or you might need to change your file extension to "pl"
$Config->{ext} = "cgi";

#  Number of days to keep past dates
$Config->{old}=90;

# Title of the calendar.
$Config->{title}="HyperCal Version $Config->{VERSION}";

#  1 is on, 0 is off.  Should we display the number
#  of events on that day, or the event text.
#  For some very high traffic calendars, you 
#  might not want to display all the events.
$Config->{DisplayNumber}=1;
$Config->{DisplayEvents}=0;

###############################################################
#   Customize the colors and images appearing in the calendar: 
###############################################################

$Config->{highlight}="ivory";  # What color should "today" be highlighted in?
$Config->{td_color} = "lightblue"; #  How about the rest of the table cells?

#  This array contains the locations of images for the various
#  months.  The format is
#  [url_for_icon,url_for_background,bgcolor,text,link,visited link]
#  This array must contain 12 elements. Any field where you have 
#  no preference, indicate by 'none'
my $month_dir = "/images/months"; # URL of month directory
$Config->{month_images}= [
	["$month_dir/january.gif",'none','white','black','blue','green'],
	["$month_dir/february.gif",'none','white','black','blue','green'],
	["$month_dir/march.gif",'none','white','black','blue','green'],
	["$month_dir/april.gif",'none','white','black','blue','green'],
	["$month_dir/may.gif",'none','white','black','blue','green'],
	["$month_dir/june.gif",'none','white','black','blue','green'],
	["$month_dir/july.gif",'none','white','black','blue','green'],
	["$month_dir/august.gif",'none','white','black','blue','green'],
	["$month_dir/september.gif",'none','white','black','blue','green'],
	["$month_dir/october.gif",'none','white','black','blue','green'],
	["$month_dir/november.gif",'none','white','black','blue','green'],
	["$month_dir/december.gif",'none','white','black','blue','green']
	];

#  Data files
my $datadir = "/home/rbowen/public_html/scripts/hypercal_dev/datafiles";
$Config->{datebook}="$datadir/datebook";
$Config->{announce}="$datadir/announce";

$Config->{months} = ['December', 'January', 'February',
		 'March', 'April', 'May', 'June',
		 'July', 'August', 'September',
		 'October', 'November', 'December'
		 ];

#######
#  End Variables
#########################################################
sub body_tag	{
	my ($month,$details) = @_;

	$details->{month_text} = month_txt($month);

	my @fields=('image','background','bgcolor','text','link','vlink');

	for (0..5)	{
		$details->{$fields[$_]} = 
			" $fields[$_] = $Config->{month_images}[$month-1][$_] "
				unless ($Config->{month_images}[$month-1][$_] eq "none");
			}  #  End for
	$details->{month_image} = "<img src=\"$Config->{month_images}[$month-1][0]\">"
			 unless ($Config->{month_images}[$month-1][0] eq "none");
}  #  End sub body_tag

sub EventSplit	{
	my ($string) = @_;
	chomp $string;
	my %Event = ();

	($Event{day},
	 $Event{begin},
	 $Event{end},
	 $Event{annual},
	 $Event{description},
	 $Event{type},
	 $Event{recurringid},
	 $Event{id} ) = split (/$Config->{delimiter}/, $string);

	return \%Event;
}

sub AnnounceSplit	{
	my ($string) = @_;
	chomp $string;
	my %Announce = ();

	($Announce{month},
	 $Announce{year},
	 $Announce{announcement},
	 $Announce{id} ) = split (/$Config->{delimiter}/, $string);

	return \%Announce;
}

sub GetId	{
	my $idfile = shift;
	my ($lockfile, $id);

	#  Get a lock on the lock file
	$lockfile = $idfile . ".lock";
	open (LOCK, ">$lockfile");
	flock LOCK, 2;

	open (ID, "$idfile");
	$id=<ID>;
	close ID;
	$id++;
	if ($id > 999999) {
		$id=1
	} # Endif
	open (NEWID,">$idfile") || die
	             "Was unable to open $idfile for writing: $!";
	print NEWID $id;
	close NEWID;
	
	#  Release lock
	flock LOCK, 8;
	close LOCK;

	return $id;
}  #  End sub GetId

#  Rewrites time into 24hr format.
sub convert_time	{
	my ($HOUR, $MINS, $merid) = @_;

	if ($merid eq "pm") {
	 $HOUR+=12;
	 if ($HOUR==24) {$HOUR=12}
			}
	if ($HOUR==12 && $merid eq "am"){$HOUR=24};
	if ($HOUR>24){$HOUR=23};
	if ($MINS>59){$MINS=59};
	$HOUR=sprintf "%02.00f",$HOUR;
	$MINS=sprintf "%02.00f",$MINS;
	return ($HOUR, $MINS);
}

sub AmPm	{
	my $time_string = shift;
	my $ret;

	my ($hour, $min) = ($time_string =~ /(\d\d)(\d\d)/);
	$hour =~ s/^0//;
	if ($hour == 12)	{
		$ret = "12:$min pm";
	} elsif ($hour > 12)	{
		$hour -= 12;
		$ret = "$hour:$min pm";
	}  else  {
		$ret = "$hour:$min am";
	}
	return $ret;
}

sub month_txt   {  # converts number to month text
	return ( $Config->{months}->[$_[0]] );
}


sub FormParse  {
#  Parse HTML form, POST or GET.  Returns pointer to hash of name,value
	my ($buffer, @pairs, $pair, $name,
	    $value, $form,
		);

	if ($ENV{REQUEST_METHOD} eq "POST")	{
		read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}  else  {
		$buffer = $ENV{QUERY_STRING};
	}

	# Split the name-value pairs
	@pairs = split(/&/, $buffer);

	foreach $pair (@pairs)
	{
    	($name, $value) = split(/=/, $pair);
    	$value =~ tr/+/ /;
    	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    	$value =~ s/~!/ ~!/g;

		if ($form->{$name})	{
			$form->{$name} .= "\0$value"
		} else {
	    	$form->{$name} = $value;
		}
	}     # End of foreach

	return $form;
}	#  End of sub

sub PrintTemplate	{
#  Displays an HTML template file in canonical RCBowen format,
#  substituting values from %details.
	my ($basedir,$template, $tmp) = @_;
	my %details = %$tmp;

	open (TEMPLATE, "$basedir/$template.html") 
		or die "Could not open $basedir/$template.html: $!\n";
	for $line (<TEMPLATE>)	{
		$line =~ s/%%%(.*?)%%%/$details{$1}/g;
		print $line;
	}  #  End for
	close TEMPLATE;
} #  End sub PrintTemplate

sub PrintHeader	{
	print "Content-type: text/html\n\n";
}

sub Switch      {
#  Determine which routine is to be called
        my ($action,$actions,$default) = @_;
        my @Actions = @$actions;

        if (grep /^$action$/, @Actions) {
                return $action;
        }  else  {
                return $default;
        }
} # End sub switch

#########################################################
# Do not change this, Do not put anything below this.
# File must return "true" value at termination
1;
##########################################################