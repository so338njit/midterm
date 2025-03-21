# Advanced Calculator with command handler and plugin integration
This program uses REPL methods and integration throughout the code to execute the simple functions of a calculator.
This program follows the 12-Factor app taught in the IS601 course.

I. Codebase
    This entire program was built using git for revision control. The initial codebase was built using a command handler and plugins for integration. A logging branch, pandas branch, and testing branch were created to add further features to the program and merged once complete.

II. Dependencies
    This program was created and ran using a virtual enviroment. To use this program install a virtual enviroment with pip and activate then install the requirements.txt file.
    
III. Config
    The program uses a dotenv file to store dependencies that are ignored from git. To use this program install dotenv and setup the proper configuration. Also, the csv file path uses the configuration files to define the path and file name.
[link to specific code showing the program calling on enviromental variables from dotenv file](https://github.com/so338njit/midterm/blob/master/app/calculator.py#L60-L65)

The program has a robust logging implementation designed throughout the program with file path created through the config.py and logging_setup.py files. The logs are categorized through the 5 basic levels or logging and saved to a calculator.log file in the logs directory.  

The program uses many try/catch exceptions and multiple instances of LBYL and EAFP. Most notably in the calculator.py file LBYL programming style is exemplified in the history_file creation function. The program looks to see if the history_file exists before reading it. Also, before it loads the file there is a try/catch to load the file or throw an exception and a log error.  


