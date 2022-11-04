#!/usr/local/bin/perl

#-------------------------Welcome-----------------------------
#
# ClickGo
# Ver. 1.0
# By Luke and Mark Pfeifer
# http://www.staff.net/cgi-scripts/		
# Release 5-7-97
# Updated 5-7-97 
#
# Copyright Info: This application was written by Mark and Luke
# Pfeifer Feel free to copy, cite, reference, sample, borrow, resell 
# or plagiarize the contents.  However, if you
# don't mind, please let us know where it goes so that we can
# watch and take part in the development of it. Information wants
# to be free, support public domain freeware.  Donations are appreciated
# and will be spent on further upgrades and other public domain scripts.
#
# Finally, PLEASE SEND WORKING URL's to lpfeifer@mail.tcbi.com.  We
# would like to keep a list of these scripts in use.
#-------------------------------------------------------------

#-----------------------ReadMe--------------------------------
#
# Chmod this file to 755, if you have Unix.  For NT remove the
#  first line in this file.
#
# The script is called by creating a link like this
#    <form method="post" action="http://www.staff.net/cgi-bin/cgi-scripts/click-go/clickgo.pl"> 
#		<select name="goto" size="1">
#               <option value="www.railserve.com">RailServe</option>
#               <option value="www.staff.net">Staff.Net</option>
#		</select>
#		<input type="submit" value="GO!">
#	</form>
#	
#		***** Do not use http:\\ in the values*******
#
#-------------------------------------------------------------
#
#--------------- Variable Definition --------------------------
#
# $main - the url of the default page to go to.  If no data is recived in.
#
#-------------------------------------------------------------

#------- Start User Configuration ----------------------------
$main = 'falcon-pro.com';
#---End User Configuration -----------------------------------

#**************** DO NOT EDIT PAST THIS LINE *****************#

&FormInput(*input);

if($input{'goto'} eq "")
   {
	print ("Location: http://$main\n\n");
   }
else
    {
	print ("Location: http://$input{'goto'}\n\n");
    }

exit;
#-------------------------------------------------------------
# FormInput: Function
#-------------------------------------------------------------
sub FormInput
{
local (*qs) = @_ if @_;

if ($ENV{'REQUEST_METHOD'} eq "GET")
        {
        $qs = $ENV{'QUERY_STRING'};
        }
elsif ($ENV{'REQUEST_METHOD'} eq "POST")
        {
        read(STDIN,$qs,$ENV{'CONTENT_LENGTH'});
        }

@qs = split(/&/,$qs);

foreach $i (0 .. $#qs)
        {
        $qs[$i] =~ s/\+/ /g;
        $qs[$i] =~ s/%(..)/pack("c",hex($1))/ge;

        ($name,$value) = split(/=/,$qs[$i],2);

        if($qs{$name} ne "")
                {
                $qs{$name} = "$qs{$name}:$value";
                }
        else
                {
                $qs{$name} = $value;
                }
        }

return 1;
}
