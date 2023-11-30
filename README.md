# Description
This repository contains the code for a small app that I initially developed as Perl-CGI app during my PhD-thesis somewhere around 2006 (but which is still active on the [Seitz-Group Homepage](https://www.chemie.hu-berlin.de/seitz/oligo-tools.htm)) and re-implemented as Python-CGI in 2011.  
  
A recent request by a former colleague triggered a recent re-implementation as Python 3 FastAPI implementation with a small HTML/JS single page application (SPA) as frontend which is now available here.  
  
The main branch is automatically deployed to fly.io and is available at https://pepmass.fly.dev
  
*NOTE: This is a side-project on a free plan on fly.io so feel free to use it or embed it as iFrame in your website but don't expect a five nine availability!*

Feel free to fork or submit pull requests e.g. if you want to add new residues (to Masses.csv)

# TO-DO
* update the SPA to also show the termination sequeces as the original CGI-app
* add checkboxes to allow to calculate only some features

# License
MIT-License
