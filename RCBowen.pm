############################################################
##  Module of functions that I frequently use.            ##
##  Replaces "httools.pl" for all purposes, and adds some ##
##  additional functionality                              ##
##                                                        ##
##  Rich Bowen - rbowen@rcbowen.com                       ##
##  RCBowen.com                                           ##
##  Feb 1998                                              ##
############################################################
package RCBowen;

require Exporter;
@ISA = Exporter;
@EXPORT = qw(FormParse
			 PrintTemplate
			 PrintHeader
			);
use vars qw($VERSION);
=head1 NAME

RCBowen - Routines typically used in scripts from RCBowen.com

=head1 SYNOPSIS

     PrintTemplate($basedir,$template,\%details);
     PrintHeader();
     FormParse(\%Form);

=head1 DESCRIPTION

These routines are used frequently in most software that RCBowen.com
develops for customers.

=over 5

=item PrintTemplate($basedir,$template,\%details);

PrintTemplate takes an HTML template file in the standard
RCBowen.com format and fills in the variables from the
%details hash.  Variables in the template file are indicated
by enclosing them in %%%, for example %%%name%%%

$basedir is the directory containing the template files.
$template is the name of the template file, without the .html extension.
%details is the hash containing the values to be put into the template.

=item PrintHeader();

PrintHeader prints a standard HTTP text/html MIME type header.

=item FormParse(\%FORM);

FormParse takes a pointer to a hash, and populates that hash
with the contents of the HTTP form post.  Form data can come
in via either the POST or GET method.

=cut

$VERSION = "1.00";

sub FormParse  {
#  Parse HTML form, POST or GET.  Returns pointer to hash of name,value
	my $form = shift;
	my ($buffer,@pairs,$pair,$name,$value);

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
	my ($template,$basedir);
	local $_;

	($basedir,$template, $_) = @_;
	my %details = %$_;

	open (TEMPLATE, "$basedir/$template.html");
	for $line (<TEMPLATE>)	{
		$line =~ s/%%%(.*?)%%%/$details{$1}/g;
		print $line;
	}  #  End for
	close TEMPLATE;
} #  End sub PrintTemplate

sub PrintHeader	{
	print "Content-type: text/html\n\n";
}
