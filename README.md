## Link AEC data to AERIUS calculator

This project is for the Data Systems course at UvA. This project aims to use linked data to make nitrogen emmission calculations easier for users. 
This is done by creating an ontology that extens the NEN 2660 format with data necessary for AERIUS calculations. 
The project is made with Flask to build a user interface. 
The home page of the application consists of a SCHACL validation, which can be used to upload files and be validated by SCHACL. 
The AERIUS page, allows the user to upload a project file, which will fill out required fields for the AERIUS calculator. The user can then submit it to the AERIUS API, which will result in a result document. 
Example projects to be used in the application can be found in the 'projects' folder.

This project requires the following Python libraries:

Flask – Web framework for building the application (flask)

Requests – HTTP library for making API calls (requests)

rdflib – Library for working with RDF data (rdflib)

pySHACL – SHACL validation for RDF graphs (pyshacl)


In order to run the application, run 'main.py' and follow the link in the terminal. 
