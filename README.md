# Simple Proxy Gen
 Simple Proxy Gen is a python script that creates squid based proxies from various cloud providers. 

## Future Development
There are no plans to continue development for this proxy gen. I may come back and add further documentation for each individual proxy company but as of now, everything will be staying how it is. 


### Contributing and Reporting Bugs
If you would like to contribute, create a pull request and I'll review it at my earliest convenience. If there are bugs, open an issue and I'll help you resolve it. 

 ## Installation
This program requires python 3. 


 Clone the repository from either the github web interface or do it from the commandline with this command: `git clone https://github.com/panda2k/simple-proxy-gen.git`


 Navigate to the cloned directory and install the python dependencies by doing `pip install -r requirements.txt`


 ## Usage
 Run the script by executing the `aioproxygen.py` file. Do this from the terminal with `python aioproxygen.py`


 Upon running the script for the first time, it will ask you to input credentials for all the cloud services. You can set them all up now or do them at a later date. If you are confused about how to find certain access tokens, google the cloud provider name + the thing you're trying to find. For example, google "100TB API key" or something along the lines of that. 


After settings up credentials, follow the terminal prompts to create proxies. The proxies will be stored in json files inside the `proxylists` directory. 

