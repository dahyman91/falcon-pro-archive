#!/usr/bin/perl -w
#=======================================[ WHCOUNTER ]==========================================#
# A simple page counter that will display in either text or image                              #
# formats.                                                                                     #
#                                                                                              #
# Copyright (c)2003 #***#***, Inc. http://www.########.com                                     #
# Developed by Phill Babbitt                                                                   #
#                                                                                              #
# Instructions:                                                                                #
# [FOR IMAGE COUNTER]                                                                          #
# The request MUST have the following parameters:                                              #
# --> display = image OR text                                                                  #
# --> page    = current page                                                                   #
# --> style   = style preset                                                                   #
# FOR EXAMPLE:                                                                                 #
# <script language="JavaScript" type="text/javascript"                                         #
# src="cgi-bin/counter/counter.cgi?display=image&page=index.html&style=odometer"></script>     #
#                                                                                              #
# [FOR TEXT COUNTER]                                                                           #
# The request MUST have the following parameters:                                              #
# --> display = image OR text                                                                  #
# --> page    = current page                                                                   #
# --> style   = style preset                                                                   #
# FOR EXAMPLE:                                                                                 #
# <script language="JavaScript" type="text/javascript"                                         #
# src="cgi-bin/counter/counter.cgi?display=text&page=index.html&style=text01"></script>        #
#                                                                                              #
# Add your own styles (image or text) by editing stats.dat.  BUT MAKE SURE YOU READ THE        #
# INSTRUCTIONS FIRST!  The instructions are at the top of the file (stats.dat).                #
#==============================================================================================#

use strict;

my $DATA_FILE    = "stats.dat";   # Counter text file
my $CONFIG_FILE  = "config.txt";  # The config file
my $IMAGE_DIR    = "images";      # Directory where all the counter images reside
my $request;                      # The request sent via GET
my %value;                        # Where we'll store the key/value pairs from the GET request
my %stats;                        # Key/value pairs of the stats file (if it exists)
my $SETUP_KEY    = "image_dir";
my $TEXT_COUNTER = "COUNTER";
my $DISPLAY_VAR  = "display";
my $PAGE_VAR     = "page";
my $STYLE_VAR    = "style";
my $IMAGE_VAR    = "image";
my $TEXT_VAR     = "text";
my $CONTENT_TYPE = "Content-type: ";
my $TYPE_GIF     = "image/gif";
my $TYPE_JPG     = "image/jpeg";
my $TYPE_PNG     = "image/png";
my $TYPE_TEXT    = "text-plain";
my $data_exists  = 0;
my ($config_found, $config_line, $style, $display, $page, $images_dir);
my (@config_file);

print "Content-type: text/html\n\n";

# Retrieve the GET request variables
if ( $ENV{REQUEST_METHOD} eq 'GET' && $ENV{'QUERY_STRING'} ne '') { 
  $request = $ENV{'QUERY_STRING'};
} elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
  printError("The counter is not meant to be run via POST.  Please read the documentation.");
  exit();
} else {
  printError("You need to provide parameters for the counter.  Please read the documentation.");
  exit();
}

cleanRequest(); # Escape unsafe characters from the GET request (see below)

open (CONFIG, "$CONFIG_FILE") or printError("The counter can't open config file!");
@config_file = <CONFIG>;
close(CONFIG);

#-------------------------------------------------------------------------------#
#                            GET THE IMAGES URL INFO                            #
#-------------------------------------------------------------------------------#
my $setup_found = 0;

foreach (@config_file) {
  if (/$SETUP_KEY/) {
    $setup_found = 1;
    next;
  } elsif ($setup_found == 1) {
    if ($_ ne '') {
      $images_dir = $_;
      $images_dir = cleanVar($images_dir);
      last;
    } else {
      printError("The setup line in the counter config file is not configured properly!");
    }
  }
}

unless ($setup_found) {
  printError("The setup line was missing from the counter config file!");
}

#-------------------------------------------------------------------------------#
#                    MATCH THE STYLE UP WITH THE CONFIG FILE                    #
#-------------------------------------------------------------------------------#
$config_found = 0;
foreach (@config_file) {
  if (/\[$style\]/) {
    $config_found = 1;
    next;
  } elsif ($config_found == 1) {
    if ($_ ne '') {
      $config_line = $_;
      $config_line = processConfig($config_line); # Clean up this line so JavaScript won't puke
      last;
    } else {
      printError("The counter can't find the style specified in the GET request!");
    }
  }
}

if ($config_found == 0) {
  printError("The counter can't find the style specified in the GET request!");
}

$style = cleanVar($style);

#-------------------------------------------------------------------------------#
#                        PROCESS IMAGE COUNTER REQUESTS                         #
#-------------------------------------------------------------------------------#
if ($display eq $IMAGE_VAR) {
  my @line;
  my ($img_name, $img_ext) = split(/\./, $config_line);
  $images_dir = cleanVar($images_dir);
  $img_name   = cleanVar($img_name);
  $img_ext    = cleanVar($img_ext);
  unless ($img_name && $img_ext) {
    printError("The counter's config file is set up improperly!");
  }
  
  loadStats();                        # Load the stats
  $stats{$page}++;                    # Add one for the requested page
  
  for (my $i = 0; $i < length($stats{$page}); $i++) {
    print "document.write(\"<img src=\\\"$images_dir/$img_name";
    print substr($stats{$page}, $i, 1);
    print ".$img_ext\\\" alt=".'\"\"'." />\");";
  }
  
  saveStats($page, $stats{$page});    # Save the stats

#-------------------------------------------------------------------------------#
#                         PROCESS TEXT COUNTER REQUESTS                         #
#-------------------------------------------------------------------------------#
} elsif ($display eq $TEXT_VAR) {
  loadStats();                        # Load the stats
  $stats{$page}++;                    # Add one for the requested page
  $config_line =~ s/$TEXT_COUNTER/$stats{$page}/;    # Find "COUNTER" in the config line for exclusion
  if ($config_line =~ /\r/) {
    chop($config_line);
    #chop($config_line);
  } else {
    chomp($config_line);
  }
  print "document.write(\"$config_line\");"; # Print out the line before and after "COUNTER"
  saveStats($page, $stats{$page});    # Save the stats
} else {
  printError("The style specified in the GET request does not match text or image!");
}

exit();

#================={SUBROUTENE}=================#
#                 cleanRequest                 #
#                 ************                 #
# Escapes all unsafe characters passed through #
# the GET reqest.                              #
#==============================================#
sub cleanRequest {
  if ($request =~ /$DISPLAY_VAR/ && $request =~ /$STYLE_VAR/) {
    foreach my $pair (split('&', $request)) {
      if ($pair =~ /(.*)=(.*)/) {
        my ($key, $value) = ($1, $2);
        $value =~ s/\+/ /g;
        $value =~ s/%(..)/pack('c', hex($1))/eg;
        if ($key eq $DISPLAY_VAR) {
          $display = $value;
        } elsif ($key eq $PAGE_VAR) {
          $page = $value;
        } elsif ($key eq $STYLE_VAR) {
          $style = $value;
        } else {
          $value{$key} = $value;
        }
      }
    }
  } else {
    printError("The counter received an improper GET request (you need to include $DISPLAY_VAR and $STYLE_VAR)!");
    exit();
  }
  
  unless ($request =~ /$PAGE_VAR/) {
    if ($page = $ENV{'HTTP_REFERER'}) {
      $page =~ s#.*/##; # If the "page" attribute was not specified, try to grab referrer info
    } else {
      $page = "UNKNOWN";
    }
  }
}

#================={SUBROUTENE}=================#
#                 processConfig                #
#                 ************                 #
# Escapes all unsafe characters passed through #
# the GET reqest.                              #
#==============================================#
sub processConfig {
  my $line = shift;
  my $find = '"';
  my $replacement = '\"';
  
  chomp($line);
  unless ($line =~ /\\\"/) {
    $line =~ s/(\")/\\$1/g;  # Escape the double-quotes (unless they're already escaped)
  }
  
  return ($line);  
}

#================={SUBROUTENE}=================#
#                  loadStats                   #
#                 ************                 #
# Loads the page stats from stats.dat and      #
# stores the results in %stats                 #
#==============================================#
sub loadStats {
  if (-f $DATA_FILE) {
    open (DATA, "$DATA_FILE");
	flock (DATA, 1);
    while (<DATA>) {
      if (/.*=.*/) {
        my ($key, $value) = split(/=/, $_);
        chomp($value);
        $stats{$key} = $value;
      }
    }
    close (DATA);
    $data_exists = 1;
  } else {
    $data_exists = 0;
  }
}

#================={SUBROUTENE}=================#
#                  saveStats                   #
#                 ************                 #
# Saves the page stats into stats.dat          #
#==============================================#
sub saveStats {
  my ($page, $counts) = @_;
  my @contents;
  my $found_page;
  
  if (-f $DATA_FILE) {
    open (DATA, "$DATA_FILE") or printError("The counter can't open $DATA_FILE!");
	flock (DATA, 2);
    @contents = <DATA>;
    close (DATA);
  }
  
  for (my $i = 0; $i < @contents; $i++) {
    if ($contents[$i] =~ /$page/) {
      $contents[$i] = $page."=".$counts."\n";
      $found_page = 1;
      last;
    }
  }
  
  unless ($found_page) {
    push(@contents, $page."=".$counts."\n");
  }
  
  open (DATA, ">$DATA_FILE") or printError("The counter can't open $DATA_FILE for writing!");
	flock (DATA, 2);
    foreach (@contents) {
      print DATA $_;
    }
  close(DATA);
}

#================={SUBROUTENE}=================#
#                  printError                  #
#                 ************                 #
# Prints messages as if from JavaScript so     #
# that the errors can be seen from a browser   #
# window                                       #
#==============================================#
sub printError {
  print "document.write(\"".(shift)."\");";
  exit();
}

#================={SUBROUTENE}=================#
#                   cleanVar                   #
#                 ************                 #
# Clean off those nasty browser-killing line-  #
# feeds!                                       #
#==============================================#
sub cleanVar {
  my $badVar = shift;

  if ($badVar =~ /\r/) {
    chop($badVar);
    #chop($badVar);
  } else {
    chomp($badVar);
  }

  return $badVar;
}
