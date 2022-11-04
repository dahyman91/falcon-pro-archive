#!/usr/local/bin/perl

# Name: guestbook.cgi
#
# Version: 2.0
#
# Last Modified: 5-17-96
#
# Copyright Information: This script was written by Selena Sol
#
# Description: This guestbook script allows users to dynamically 
#     manipulate a guestbook HTML file by adding their own entries to the 
#     document.
#
# Installation: See guestbook.setup

#######################################################################
#                     Print Out the HTTP Header  .                    #
#######################################################################

# First, print out the HTTP header.  We'll output this quickly so that we
# will be able to do some of our debugging from the web and so that in
# the case of a bogged down server, we won't get timed-out.

  print "Content-type: text/html\n\n";

#######################################################################
#               Require Libraries and Parse Form Data                 #
#######################################################################

# First, get the customized information contained in the setup file. Then
# Use cgi-lib.pl to read the incoming form data.  However, send form_data
# as a parameter to the subroutine &ReadParse in cgi-lib.pl so that the
# associative array of form keys/values comes back with a descriptinve
# name rather than just $in. Also require the library which we will use
# to send out mail using sendmail

  require "./guestbook.setup";
  require "$cgi_lib_location";
  &ReadParse(*form_data);
  require "$mail_lib_location";

#######################################################################
#                       Create Add Form                               #
#######################################################################

# Now determine what the client wants.  If $form_data{'action'} eq "add" 
# (client clicked on a button somewhere) or (||) $ENV{'REQUEST_METHOD'} 
# eq "post" (client is accessing this script for the first time as a 
# link, not as a submit button) then it means that the client is asking 
# to see the form to "add" an item to the guestbook.

  if ($form_data{'action'} eq "add" || $ENV{'REQUEST_METHOD'} eq "GET")
    {

# Print out the form's header

    print <<"    end_of_html";
    <HTML><HEAD><TITLE>Guestbook (Add Form)</TITLE></HEAD>
    <BODY>
    <CENTER>
    <H2>Add to my Guestbook</H2>
    </CENTER>
    Please fill in the blanks below to add to my guestbook.  The only 
    blanks that you have to fill in are the comments and name section.  
    Thanks!
    <P><HR>
    end_of_html

# Utilize the routine in the subroutine output_add_form at the end of 
# this form to actually print out the form.  Then quit and let the user 
# submit their data.

    &output_add_form;
    exit;
    }

#######################################################################
#                       Get the Date                                  #
#######################################################################

# Use the get_date subroutine at the end of this script to get the 
# current date and time so that we can use it in our output.

  $date = &get_date;

#######################################################################
#                    Modify Incomming Form Data                       #
#######################################################################

# Now check to see if we were asked to censor any particular words.
# First, create an array of form variables by accessing the "keys" of the 
# associative array %form_data given to us by cgi-lib.pl.

   @form_variables = keys (%form_data);

# For every variable sent to us from the form, and for each word in our 
# list of bad words, replace (=~ s/) any occurance, case insensitively 
# (/gi) of the bad word ($word) with the word censored.  
# $form_data{$variable} should be equal to what the client filled in in 
# the input boxes...
#
# Further, if the admin has set allow_html to 0, (!= 1) it means that she 
# does not want the users to be able to use HTML tags...so, delete them.

   foreach $variable (@form_variables)
     {
     foreach $word (@bad_words)
       {
       $form_data{$variable} =~ s/\b$word\b/censored/gi;
       }
     if ($allow_html != 1) 
       {
       $form_data{$variable} =~ s/<([^>]|\n)*>//g;
       }
     }

#######################################################################
#                   Check Required Fields for Data                    #
#######################################################################

# For every field that was defined in our list of required fields, check 
# the form data to see if that variable has an empty value.  If so, jump to 
# missing_required_field_data which is a subroutine at the end of this 
# script passing as a parameter, the name of the field which was not filled 
# out.

  foreach $field (@required_fields)
    {
    if ($form_data{$field} eq "" )
      {
      &missing_required_field_data($field);
      }
    }

#######################################################################
#                      Edit the Guestbook File                        #
#######################################################################

# First open the guestbook html file.  Then, read each of the lines in 
# the guestbook file into an array called @LINES Then close the 
# guestbook file.  Finally, set the variable $SIZE equal to the number of 
# elements in the array (which is conveniently, the same number of lines in 
# the guestbook file)

  open (FILE,"$guestbookreal") || die "Can't Open $guestbookreal: $!\n";
  @LINES=<FILE>;
  close(FILE);

  $SIZE=@LINES;

# Now open up the guestbook file again, but this time open it for 
# writing...in fact we will overwrite the existing guestbook file with new 
# data (>)

  open (GUEST,">$guestbookreal") || die "Can't Open $guestbookreal: $!\n";

# Now we are goping to go through our @LINES array adding lines "back" to 
# out guestbook file one by one, inserting the new entry along the way.
# For every line in the guestbook file (remember that $SIZE = number of 
# lines) we'll assign the value of the line ($LINES[$i]) to the variable $_
# We'll start with the first line in the array ($i=0) and we'll end when 
# we have gone through all of the lines ($i<=$SIZE) counting by one ($i++).
# We reference the array in the standard form $arrayname[$element_number]

  for ($i=0;$i<=$SIZE;$i++) 
    {
    $_=$LINES[$i];

# Now, if the line hapens to be <!--begin--> we know that we are going to 
# need to add a new entry.  Thus, btw, it is essential that your 
# guestbook.html have that line, all on its own somewhere in the body when 
# you initialize your guestbook.

    if (/<!--begin-->/) 
      { 

# Let's add the entry.  First print <!--begin--> again so that we will be 
# able to find the top of the guestbook again the next time.

      print GUEST "<!--begin-->\n";

# Then begin adding the guest's information.  First, let's print the Name 
# of the guest.  However, if the guest left a URL, let's make their name 
# clickable top their URL.  If the guest did not submit a URL, just print 
# the name.

      if ($form_data{'url'}) 
        {
        print GUEST "<B>Name:</B>";
        print GUEST "<A HREF = \"$form_data{'url'}\">$form_data{'realname'}</A>";
        print GUEST "<BR>\n";
        }
      else 
        {
        print GUEST "<B>Name:</B> $form_data{'realname'}<BR>\n";
        }

# Now print the email of the guest...and, if the admin has set the 
# $linkmail tag to one in the setup file, then make the email link clickable.

      if ( $form_data{'email'} )
        {
        if ($linkmail eq '1') 
          {
          print GUEST "<B>Email:</B>";
	  print GUEST "<A HREF = \"mailto:$form_data{'email'}\">";
          print GUEST "$form_data{'email'}</A><BR>\n";
          }
        else 
          {
          print GUEST " $form_data{'email'}<BR>\n";
          }
        }

# Now print out the guest's address if they submitted the values.

      if ( $form_data{'city'} )
        {
        print GUEST "<B>Location:</B> $form_data{'city'},";
        }
     
      if ( $form_data{'state'} )
        {
        print GUEST " $form_data{'state'}";
        }

      if ( $form_data{'country'} )
        {
        print GUEST " $form_data{'country'}<BR>\n";
        }

# Finally, print up the date and the comments.

      print GUEST "<B>Date:</B> $date<BR>\n";

      print GUEST "<b>Comments:</B><BLOCKQUOTE>$form_data{'comments'}";
      print GUEST "</BLOCKQUOTE><HR>\n\n";
      }

# If the line was not <!--begin--> however, we should make sure to print 
# up the line so that we retain all of the HTML that was in the guestbook 
# before we added the entry.  Thus, the very long for loop will go 
# through each line...it will print the header...and get all the way down 
# through whatever HTML you've written until it gets to the guestbook 
# entries which begin with a <!--begin-->.  It will then print the new 
# entry and then print out all the old entries as well...When it gets to 
# the end of the file, it's over.

    else 
      {
      print GUEST $_;
     }
   }

# Close up the guestbook.

close (GUEST);

#######################################################################
#                  Send Email Note to the Admin                      #
#######################################################################
# Now prepare to email a note to the admin.  Rename $form_data{'email'} 
# to $email_of_sender, and split up that email into its two components, 
# the username and the email server.  Thus in selena@eff.org, selena 
# becomes username and eff.org becomes server.  We are going to need 
# these values later when we send our email.

    $email_of_guest = "$form_data{'email'}";

# Now, if the admin has set the $mail to 1 (admin wants to be mailed when 
# someone enters a guestbook entry), then let's begin creating an email body.
# We'll store the body in the variable $email_body and we will 
# continually append this variable by using .=

  if ($mail eq '1') 
    {

    $email_body .= "You have a new entry in your guestbook:\n\n";
    $email_body .= "------------------------------------------------------\n";
    $email_body .= "Name: $form_data{'realname'}\n";

# If the guest actually submitted values, write them too.

    if ($form_data{'email'} ne "")
      {
      $email_body .="Email: <$form_data{'email'}>\n";
      }

    if ($form_data{'url'} ne "")
      {
      $email_body .="URL: <$form_data{'url'}>\n";
      }

    if ($form_data{'city'} ne "")
      {
      $email_body .= "Location: $form_data{'city'},";
      }

   if ($form_data{'state'} ne "")
      {
      $email_body .= " $form_data{'state'}";
      }

   if ($form_data{'country'} ne "")
      {
      $email_body .= " $form_data{'country'}\n";
      }

# Finish off the message body...

   $email_body .= "Time: $date\n\n";
   $email_body .= "Comments: $form_data{'comments'}\n";

   $email_body .= "------------------------------------------------------\n";

# Use the send_mail subroutine in the mail-lib.pl library file to send 
# the email to the admin.  This routine takes 6 parameters, who is sending 
# the mail, the server of the sender, who it is being sent to and their 
# server, the subject and the body.

   &send_mail("$email_of_guest", "$recipient",
              "$email_subject", "$email_body");
   }

#######################################################################
#                  Send Thank You Email to the Guest                  #
#######################################################################

# Now, if the admin has set $remote_mail equal to 1 and (&&) the guest has 
# actually submitted an email, we should email the guest a thank you note 
# also.  The process is identical to the one above.

  if ($remote_mail eq '1' && $form_data{'email'} ne "") 
    {
    $email_body = "";
    $email_body .= <<"    end_of_message_to_guest";
    Thanks very much for stopping by my site and a
    double thanks you for taking the time to sign my guestbook.
    I hope you found something useful and please let other
    netizens know of the existence of my little corner of the
    net..
    end_of_message_to_guest
    $email_body .= "\n";
    $email_body .= "    By the way, you wrote...\n\n";
    $email_body .= "    Name: $form_data{'realname'}\n";

    if ($form_data{'email'} ne "")
      {
      $email_body .="    Email: <$form_data{'email'}>\n";
      }

    if ($form_data{'url'} ne "")
      {
      $email_body .="    URL: <$form_data{'url'}>\n";
      }

    if ($form_data{'city'} ne "")
      {
      $email_body .= "    Location: $form_data{'city'},";
      }

   if ($form_data{'state'} ne "")
      {
      $email_body .= " $form_data{'state'}";
      }

   if ($form_data{'country'} ne "")
      {
      $email_body .= " $form_data{'country'}\n";
      }

   $email_body .= "    Time: $date\n\n";
   $email_body .= "    Comments: $form_data{'comments'}\n";

# Send off the email!

   &send_mail("$recipient", "$email_of_guest",
              "$email_subject", "$email_body");
    }

#######################################################################
#                   Send back an HTML Thank you to Guest              #
#######################################################################

# Now send the guest a thank you note on the web and provide her with a 
# way to get back to where she was before.

  print <<"  end_of_html";  
  <HTML><HEAD><TITLE>Thank You</TITLE></HEAD>
  <BODY>
  <CENTER>
  <P>
  Thank you for signing the Guestbook, $form_data{'realname'}
  </CENTER>
  <P>
  Your entry has now been added to the guestbook as follows...<BLOCKQUOTE>
  end_of_html

# Print out a copy of their submissions.

  if ($form_data{'url'} ne "") 
    {
    print "<B>Name:</B>";
    print "<A HREF = \"$form_data{'url'}\">$form_data{'realname'}</A><BR>";
    }
  else 
    {
    print "<B>Name:</B> $form_data{'realname'}<BR>";
    }

  if ( $form_data{'email'} )
    {
    if ($linkmail eq '1') 
      {
      print "<B>Email:</B> (<a href=\"mailto:$form_data{'email'}\">";
      print "$form_data{'email'}</a>)<BR>";
      }
    else 
      {
      print "<B>Email:</B> ($form_data{'email'})<BR>";
      }
   }

   print "<B>Location:</B> ";

   if ( $form_data{'city'} )
     {
     print "$form_data{'city'},";
     }

   if ( $form_data{'state'} )
     {
     print " $form_data{'state'}";
     }

   if ( $form_data{'country'} ){
      print " $form_data{'country'}";
   }

   print "<BR><B>Time:</B> $date<P>";
   print "<B>Comments:</B> $form_data{'comments'}<BR>\n";
   print "</BLOCKQUOTE>";
   print "<a href=\"$guestbookurl\">Back to the Guestbook</a>\n";
   print "- You may need to reload it when you get there to see your\n";
   print "entry.\n";
   print "</body></html>\n";
   exit;

# Begin the subroutines...

#######################################################################
#                 missing_required_field_data subroutine              #
#######################################################################

  sub missing_required_field_data
    {

# Assign the passed $variable parameter to the local variable $field

    local($field) = @_;

# Now send the user an informative error message so that they can enter 
# the correct amount of information.

    print <<"    end_of_html";
    <HTML><HEAD><TITLE>Data Entry Error</TITLE></HEAD>
    <BODY>
    <BLOCKQUOTE>Woopsy, You forgot to fill out $field and I am not 
    allowed to add your guestbook entry without it.  Would you please 
    type something in below...</BLOCKQUOTE>
    end_of_html

# Now reprint out the add form with the subroutine output_add_form at the 
# end of this script.  Then exit.

    &output_add_form;
    exit;
    }

#######################################################################
#                     Output the Add Form                             #
#######################################################################

  sub output_add_form
    {

# This is pretty much straight forward printing...

    print <<"    end_of_html";
    <FORM METHOD = "POST" ACTION = "guestbook.cgi">
    <TABLE>
    <TR>
    <TH ALIGN = "left">Your Name:</TH>
    <TD><INPUT TYPE = "text" NAME = "realname" SIZE = "40"
	       VALUE = "$form_data{'realname'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">E-Mail:</TH>
    <TD><INPUT TYPE = "text" NAME = "email" SIZE = "40"
               VALUE = "$form_data{'email'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">URL:</TH>
    <TD><INPUT TYPE = "text" NAME = "url" SIZE = "50"
               VALUE = "$form_data{'url'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">City:</TH>
    <TD><INPUT TYPE = "text" NAME = "city" SIZE = "15"
               VALUE = "$form_data{'city'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">State:</TH>
    <TD><INPUT TYPE = "text" NAME = "state" SIZE = "4"
               VALUE = "$form_data{'state'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">Country:</TH>
    <TD><INPUT TYPE = "text" NAME = "country" SIZE = "15"
               VALUE = "$form_data{'country'}"></TD>
    </TR><TR>
    <TH ALIGN = "left">Comments:</TH>
    <TD><TEXTAREA NAME = "comments" COLS = "60" ROWS = "4">
    $form_data{'comments'}
    </textarea></TD>
    </TR></TABLE>
    <CENTER>
    <INPUT TYPE = "submit" VALUE = "Submit Addition"> 
    <INPUT TYPE = "reset">
    </FORM>
    <P>    
    <A HREF = "$guestbookurl">Back to the Guestbook Entries</A><BR>
    </CENTER>    
    </BODY>
    </HTML>
    end_of_html
    }

#######################################################################
#                            get_date                                 #
#######################################################################

  sub get_date
    {

   @days = ('Sunday','Monday','Tuesday','Wednesday','Thursday',
            'Friday','Saturday');
   @months = ('January','February','March','April','May','June','July',
              'August','September','October','November','December');

# Use the localtime command to get the current time, splitting it into
# variables.

   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);

# Format the variables and assign them to the final $date variable.

   if ($hour < 10) { $hour = "0$hour"; }
   if ($min < 10) { $min = "0$min"; }
   if ($sec < 10) { $sec = "0$sec"; }

   $date = "$days[$wday], $months[$mon] $mday, 19$year at $hour\:$min\:$sec";
   }

